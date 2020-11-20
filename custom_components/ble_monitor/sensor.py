"""Passive BLE monitor sensor platform."""
import asyncio
from datetime import timedelta
import logging
import queue
import statistics as sts
import struct
from threading import Thread

from Cryptodome.Cipher import AES

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_LIGHT,
    DEVICE_CLASS_OPENING,
    DEVICE_CLASS_POWER,
    BinarySensorEntity,
)
from homeassistant.const import (
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_ILLUMINANCE,
    DEVICE_CLASS_TEMPERATURE,
    CONDUCTIVITY,
    EVENT_HOMEASSISTANT_STOP,
    PERCENTAGE,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
    ATTR_BATTERY_LEVEL,
    STATE_OFF,
    STATE_ON,
)
from homeassistant.helpers.restore_state import RestoreEntity
import homeassistant.util.dt as dt_util

# It was decided to temporarily include this file in the integration bundle
# until the issue with checking the adapter's capabilities is resolved in the official aioblescan repo
# see https://github.com/frawau/aioblescan/pull/30, thanks to @vicamo
from . import aioblescan_ext as aiobs

from . import (
    CONF_DEVICES,
    CONF_DISCOVERY,
    CONF_ROUNDING,
    CONF_DECIMALS,
    CONF_PERIOD,
    CONF_LOG_SPIKES,
    CONF_USE_MEDIAN,
    CONF_ACTIVE_SCAN,
    CONF_HCI_INTERFACE,
    CONF_BATT_ENTITIES,
    CONF_REPORT_UNKNOWN,
    CONF_RESTORE_STATE,
)
from .const import (
    CONF_TMIN,
    CONF_TMAX,
    CONF_HMIN,
    CONF_HMAX,
    XIAOMI_TYPE_DICT,
    MMTS_DICT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

# Structured objects for data conversions
TH_STRUCT = struct.Struct("<hH")
H_STRUCT = struct.Struct("<H")
T_STRUCT = struct.Struct("<h")
CND_STRUCT = struct.Struct("<H")
ILL_STRUCT = struct.Struct("<I")
FMDH_STRUCT = struct.Struct("<H")


def setup_platform(hass, conf, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    _LOGGER.debug("Platform startup")
    config = hass.data[DOMAIN]
    monitor = BLEmonitor(config, add_entities)
    monitor.start()
    hass.bus.listen(EVENT_HOMEASSISTANT_STOP, monitor.shutdown_handler)
    _LOGGER.debug("Platform setup finished")
    # Return successful setup
    return True


class BLEmonitor(Thread):
    """BLE ADV messages parser and entities updater."""

    def __init__(self, config, add_entities):
        """Initiate BLE monitor."""
        def reverse_mac(rmac):
            """Change LE order to BE."""
            if len(rmac) != 12:
                return None
            return rmac[10:12] + rmac[8:10] + rmac[6:8] + rmac[4:6] + rmac[2:4] + rmac[0:2]
        Thread.__init__(self)
        _LOGGER.debug("BLE monitor initialization")
        self.dataqueue = queue.Queue()
        self.scanner = None
        self.config = config
        self.aeskeys = {}
        self.whitelist = []
        self.discovery = True
        self.period = config[CONF_PERIOD]
        self.log_spikes = config[CONF_LOG_SPIKES]
        self.batt_entities = config[CONF_BATT_ENTITIES]
        self.report_unknown = False
        if config[CONF_REPORT_UNKNOWN]:
            self.report_unknown = True
            _LOGGER.info(
                "Attention! Option report_unknown is enabled, be ready for a huge output..."
            )
        # prepare device:key lists to speedup parser
        if config[CONF_DEVICES]:
            for device in config[CONF_DEVICES]:
                if "encryption_key" in device:
                    p_mac = bytes.fromhex(
                        reverse_mac(device["mac"].replace(":", "")).lower()
                    )
                    p_key = bytes.fromhex(device["encryption_key"].lower())
                    self.aeskeys[p_mac] = p_key
                else:
                    continue
        _LOGGER.debug("%s encryptors mac:key pairs loaded.", len(self.aeskeys))
        if isinstance(config[CONF_DISCOVERY], bool):
            if config[CONF_DISCOVERY] is False:
                self.discovery = False
                if config[CONF_DEVICES]:
                    for device in config[CONF_DEVICES]:
                        self.whitelist.append(device["mac"])
        # remove duplicates from whitelist
        self.whitelist = list(dict.fromkeys(self.whitelist))
        _LOGGER.debug("whitelist: [%s]", ", ".join(self.whitelist).upper())
        for i, mac in enumerate(self.whitelist):
            self.whitelist[i] = bytes.fromhex(reverse_mac(mac.replace(":", "")).lower())
        _LOGGER.debug("%s whitelist item(s) loaded.", len(self.whitelist))
        self.add_entities = add_entities
        _LOGGER.debug("BLE monitor initialized")

    def shutdown_handler(self, event):
        """Run homeassistant_stop event handler."""
        _LOGGER.debug("Running homeassistant_stop event handler: %s", event)
        self.join()

    def join(self, timeout=10):
        """Join BLEmonitor thread."""
        _LOGGER.debug("BLE monitor thread: joining")
        if isinstance(self.scanner, BLEScanner):
            self.scanner.stop()
        self.dataqueue.put(None)
        Thread.join(self, timeout)
        _LOGGER.debug("BLE monitor thread: joined")

    def run(self):
        """Parser and entity update loop."""

        def parse_raw_message(data):
            """Parse the raw data."""
            # check if packet is Extended scan result
            is_ext_packet = True if data[3] == 0x0d else False
            # check for Xiaomi service data
            xiaomi_index = data.find(b'\x16\x95\xFE', 15 + 15 if is_ext_packet else 0)
            if xiaomi_index == -1:
                return None
            # check for no BR/EDR + LE General discoverable mode flags
            advert_start = 29 if is_ext_packet else 14
            adv_index = data.find(b"\x02\x01\x06", advert_start, 3 + advert_start)
            adv_index2 = data.find(b"\x15\x16\x95", advert_start, 3 + advert_start)
            if adv_index == -1 and adv_index2 == -1:
                return None
            if adv_index2 != -1:
                adv_index = adv_index2
            # check for BTLE msg size
            msg_length = data[2] + 3
            if msg_length != len(data):
                return None
            # check for MAC presence in message and in service data
            xiaomi_mac_reversed = data[xiaomi_index + 8:xiaomi_index + 14]
            mac_index = adv_index - 14 if is_ext_packet else adv_index
            source_mac_reversed = data[mac_index - 7:mac_index - 1]
            if xiaomi_mac_reversed != source_mac_reversed:
                return None
            # check for MAC presence in whitelist, if needed
            if self.discovery is False:
                if xiaomi_mac_reversed not in self.whitelist:
                    return None
            packet_id = data[xiaomi_index + 7]
            try:
                prev_packet = parse_raw_message.lpacket_id[xiaomi_mac_reversed]
            except KeyError:
                prev_packet = None
            if prev_packet == packet_id:
                return None
            parse_raw_message.lpacket_id[xiaomi_mac_reversed] = packet_id
            # extract RSSI byte
            rssi_index = 18 if is_ext_packet else msg_length - 1
            (rssi,) = struct.unpack("<b", data[rssi_index:rssi_index + 1])
            # strange positive RSSI workaround
            if rssi > 0:
                rssi = -rssi
            try:
                sensor_type = XIAOMI_TYPE_DICT[
                    data[xiaomi_index + 5:xiaomi_index + 7]
                ]
            except KeyError:
                if self.report_unknown:
                    _LOGGER.info(
                        "BLE ADV from UNKNOWN: RSSI: %s, MAC: %s, ADV: %s",
                        rssi,
                        ''.join('{:02X}'.format(x) for x in xiaomi_mac_reversed[::-1]),
                        data.hex()
                    )
                return None
            # frame control bits
            framectrl, = struct.unpack('>H', data[xiaomi_index + 3:xiaomi_index + 5])
            # check data is present
            if not (framectrl & 0x4000):
                return {
                    "rssi": rssi,
                    "mac": ''.join('{:02X}'.format(x) for x in xiaomi_mac_reversed[::-1]),
                    "type": sensor_type,
                    "packet": packet_id,
                    "data": False,
                }
                # return None
            xdata_length = 0
            xdata_point = 0
            # check capability byte present
            if framectrl & 0x2000:
                xdata_length = -1
                xdata_point = 1
            # xiaomi data length = message length
            #     -all bytes before XiaomiUUID
            #     -3 bytes Xiaomi UUID + ADtype
            #     -1 byte rssi
            #     -3+1 bytes sensor type
            #     -1 byte packet_id
            #     -6 bytes MAC
            #     - capability byte offset
            xdata_length += msg_length - xiaomi_index - 15
            if xdata_length < 3:
                return None
            xdata_point += xiaomi_index + 14
            # check if xiaomi data start and length is valid
            if xdata_length != len(data[xdata_point:-1]):
                return None
            # check encrypted data flags
            if framectrl & 0x0800:
                # try to find encryption key for current device
                try:
                    key = self.aeskeys[xiaomi_mac_reversed]
                except KeyError:
                    # no encryption key found
                    return None
                nonce = b"".join(
                    [
                        xiaomi_mac_reversed,
                        data[xiaomi_index + 5:xiaomi_index + 7],
                        data[xiaomi_index + 7:xiaomi_index + 8]
                    ]
                )
                encrypted_payload = data[xdata_point:msg_length - 1]
                aad = b"\x11"
                token = encrypted_payload[-4:]
                payload_counter = encrypted_payload[-7:-4]
                nonce = b"".join([nonce, payload_counter])
                cipherpayload = encrypted_payload[:-7]
                cipher = AES.new(key, AES.MODE_CCM, nonce=nonce, mac_len=4)
                cipher.update(aad)
                decrypted_payload = None
                try:
                    decrypted_payload = cipher.decrypt_and_verify(cipherpayload, token)
                except ValueError as error:
                    _LOGGER.error("Decryption failed: %s", error)
                    _LOGGER.error("token: %s", token.hex())
                    _LOGGER.error("nonce: %s", nonce.hex())
                    _LOGGER.error("encrypted_payload: %s", encrypted_payload.hex())
                    _LOGGER.error("cipherpayload: %s", cipherpayload.hex())
                    return None
                if decrypted_payload is None:
                    _LOGGER.error(
                        "Decryption failed for %s, decrypted payload is None",
                        "".join("{:02X}".format(x) for x in xiaomi_mac_reversed[::-1]),
                    )
                    return None
                # replace cipher with decrypted data
                msg_length -= len(data[xdata_point:msg_length - 1])
                data = b"".join((data[:xdata_point], decrypted_payload, data[-1:]))
                msg_length += len(decrypted_payload)
            result = {
                "rssi": rssi,
                "mac": ''.join('{:02X}'.format(x) for x in xiaomi_mac_reversed[::-1]),
                "type": sensor_type,
                "packet": packet_id,
                "data": True,
            }
            # loop through xiaomi payload
            # assume that the data may have several values of different types,
            # although I did not notice this behavior with my LYWSDCGQ sensors
            res = None
            while True:
                xvalue_typecode = data[xdata_point:xdata_point + 2]
                try:
                    xvalue_length = data[xdata_point + 2]
                except ValueError as error:
                    _LOGGER.error("xvalue_length conv. error: %s", error)
                    _LOGGER.error("xdata_point: %s", xdata_point)
                    _LOGGER.error("data: %s", data.hex())
                    result = {}
                    break
                except IndexError as error:
                    _LOGGER.error("Wrong xdata_point: %s", error)
                    _LOGGER.error("xdata_point: %s", xdata_point)
                    _LOGGER.error("data: %s", data.hex())
                    result = {}
                    break
                xnext_point = xdata_point + 3 + xvalue_length
                xvalue = data[xdata_point + 3:xnext_point]
                vlength = len(xvalue)
                if vlength == 4:
                    if xvalue_typecode == b'\x0D\x10':
                        (temp, humi) = TH_STRUCT.unpack(xvalue)
                        res = {"temperature": temp / 10, "humidity": humi / 10}
                if vlength == 2:
                    if xvalue_typecode == b'\x06\x10':
                        (humi,) = H_STRUCT.unpack(xvalue)
                        res = {"humidity": humi / 10}
                    if xvalue_typecode == b'\x04\x10':
                        (temp,) = T_STRUCT.unpack(xvalue)
                        res = {"temperature": temp / 10}
                    if xvalue_typecode == b'\x09\x10':
                        (cond,) = CND_STRUCT.unpack(xvalue)
                        res = {"conductivity": cond}
                    if xvalue_typecode == b'\x10\x10':
                        (fmdh,) = FMDH_STRUCT.unpack(xvalue)
                        res = {"formaldehyde": fmdh / 100}
                if vlength == 1:
                    if xvalue_typecode == b'\x0A\x10':
                        res = {"battery": xvalue[0]}
                    if xvalue_typecode == b'\x08\x10':
                        res = {"moisture": xvalue[0]}
                    if xvalue_typecode == b'\x12\x10':
                        res = {"switch": xvalue[0]}
                    if xvalue_typecode == b'\x18\x10':
                        res = {"light": xvalue[0]}
                    if xvalue_typecode == b'\x19\x10':
                        res = {"opening": xvalue[0]}
                    if xvalue_typecode == b'\x13\x10':
                        res = {"consumable": xvalue[0]}
                if vlength == 3:
                    if xvalue_typecode == b'\x07\x10':
                        (illum,) = ILL_STRUCT.unpack(xvalue + b'\x00')
                        res = {"illuminance": illum}
                if res:
                    result.update(res)
                else:
                    if self.report_unknown:
                        _LOGGER.info(
                            "UNKNOWN data from DEVICE: %s, MAC: %s, ADV: %s",
                            sensor_type,
                            ''.join('{:02X}'.format(x) for x in xiaomi_mac_reversed[::-1]),
                            data.hex()
                        )
                if xnext_point > msg_length - 3:
                    break
                xdata_point = xnext_point
            return result

        def temperature_limit(config, mac, temp):
            """Set limits for temperature measurement in °C or °F."""
            fmac = ':'.join(mac[i:i + 2] for i in range(0, len(mac), 2))

            if config[CONF_DEVICES]:
                for device in config[CONF_DEVICES]:
                    if fmac in device["mac"].upper():
                        if "temperature_unit" in device:
                            if device["temperature_unit"] == TEMP_FAHRENHEIT:
                                temp_fahrenheit = temp * 9 / 5 + 32
                                return temp_fahrenheit
                        break
            return temp

        _LOGGER.debug("Dataparser loop started!")
        self.scanner = BLEScanner(self.config, self.dataqueue)
        self.scanner.start()
        parse_raw_message.lpacket_id = {}
        sensors_by_mac = {}
        batt = {}  # batteries
        rssi = {}
        hcievent_cnt = 0
        mibeacon_cnt = 0
        hpriority = []
        ts_last = dt_util.now()
        ts_now = ts_last
        data = None
        while True:
            try:
                advevent = self.dataqueue.get(block=True, timeout=1)
                if advevent is None:
                    _LOGGER.debug("Dataparser loop stopped")
                    return True
                data = parse_raw_message(advevent)
                hcievent_cnt += 1
            except queue.Empty:
                pass
            if len(hpriority) > 0:
                for entity in hpriority:
                    if entity.ready_for_update is True:
                        hpriority.remove(entity)
                        entity.schedule_update_ha_state(True)
            if data:
                mibeacon_cnt += 1
                mac = data["mac"]
                # the RSSI value will be averaged for all valuable packets
                if mac not in rssi:
                    rssi[mac] = []
                rssi[mac].append(int(data["rssi"]))
                batt_attr = None
                sensortype = data["type"]
                t_i, h_i, m_i, c_i, i_i, f_i, cn_i, sw_i, op_i, l_i, b_i = MMTS_DICT[sensortype]
                if mac not in sensors_by_mac:
                    sensors = []
                    if t_i != 9:
                        sensors.insert(t_i, TemperatureSensor(self.config, mac, sensortype))
                    if h_i != 9:
                        sensors.insert(h_i, HumiditySensor(self.config, mac, sensortype))
                    if m_i != 9:
                        sensors.insert(m_i, MoistureSensor(self.config, mac, sensortype))
                    if c_i != 9:
                        sensors.insert(c_i, ConductivitySensor(self.config, mac, sensortype))
                    if i_i != 9:
                        sensors.insert(i_i, IlluminanceSensor(self.config, mac, sensortype))
                    if f_i != 9:
                        sensors.insert(f_i, FormaldehydeSensor(self.config, mac, sensortype))
                    if cn_i != 9:
                        sensors.insert(cn_i, ConsumableSensor(self.config, mac, sensortype))
                    if sw_i != 9:
                        sensors.insert(sw_i, PowerBinarySensor(self.config, mac, sensortype))
                    if op_i != 9:
                        sensors.insert(op_i, OpeningBinarySensor(self.config, mac, sensortype))
                    if l_i != 9:
                        sensors.insert(l_i, LightBinarySensor(self.config, mac, sensortype))
                    if self.batt_entities and (b_i != 9):
                        sensors.insert(b_i, BatterySensor(self.config, mac, sensortype))
                    sensors_by_mac[mac] = sensors
                    self.add_entities(sensors)
                else:
                    sensors = sensors_by_mac[mac]

                if data["data"] is False:
                    data = None
                    continue

                # store found readings per device
                if (b_i != 9):
                    if "battery" in data:
                        batt[mac] = int(data["battery"])
                        batt_attr = batt[mac]
                        if self.batt_entities:
                            sensors[b_i].collect(data)
                    else:
                        try:
                            batt_attr = batt[mac]
                        except KeyError:
                            batt_attr = None
                # schedule an immediate update of binary sensors
                if "switch" in data:
                    switch = sensors[sw_i]
                    switch.collect(data, batt_attr)
                    if switch.ready_for_update is True:
                        switch.schedule_update_ha_state(True)
                    else:
                        hpriority.append(switch)
                if "opening" in data:
                    opening = sensors[op_i]
                    opening.collect(data, batt_attr)
                    if opening.ready_for_update is True:
                        opening.schedule_update_ha_state(True)
                    else:
                        hpriority.append(opening)
                if "light" in data:
                    light = sensors[l_i]
                    light.collect(data, batt_attr)
                    if light.ready_for_update is True:
                        light.schedule_update_ha_state(True)
                    else:
                        hpriority.append(light)
                # measuring sensors
                if "temperature" in data:
                    if (
                        temperature_limit(self.config, mac, CONF_TMAX)
                        >= data["temperature"]
                        >= temperature_limit(self.config, mac, CONF_TMIN)
                    ):
                        sensors[t_i].collect(data, batt_attr)
                    elif self.log_spikes:
                        _LOGGER.error(
                            "Temperature spike: %s (%s)",
                            data["temperature"],
                            mac,
                        )
                if "humidity" in data:
                    if CONF_HMAX >= data["humidity"] >= CONF_HMIN:
                        sensors[h_i].collect(data, batt_attr)
                    elif self.log_spikes:
                        _LOGGER.error(
                            "Humidity spike: %s (%s)",
                            data["humidity"],
                            mac,
                        )
                if "conductivity" in data:
                    sensors[c_i].collect(data, batt_attr)
                if "moisture" in data:
                    sensors[m_i].collect(data, batt_attr)
                if "illuminance" in data:
                    sensors[i_i].collect(data, batt_attr)
                if "formaldehyde" in data:
                    sensors[f_i].collect(data, batt_attr)
                if "consumable" in data:
                    sensors[cn_i].collect(data, batt_attr)
                data = None
            ts_now = dt_util.now()
            if ts_now - ts_last < timedelta(seconds=self.period):
                continue
            ts_last = ts_now
            # restarting scanner
            jres = self.scanner.stop()
            if jres is False:
                _LOGGER.error("HCIdump thread(s) is not completed, interrupting data processing!")
                continue
            self.scanner.start()
            # for every updated device
            upd_evt = False
            for mac, elist in sensors_by_mac.items():
                for entity in elist:
                    if entity.pending_update is True:
                        if entity.ready_for_update is True:
                            entity.rssi_values = rssi[mac].copy()
                            entity.schedule_update_ha_state(True)
                            upd_evt = True
                if upd_evt:
                    rssi[mac].clear()
                upd_evt = False
            rssi.clear()

            _LOGGER.debug(
                "%i HCI Events parsed, %i valuable MiBeacon BLE ADV messages. Found %i known device(s) total. Priority queue = %i",
                hcievent_cnt,
                mibeacon_cnt,
                len(sensors_by_mac),
                len(hpriority),
            )
            hcievent_cnt = 0
            mibeacon_cnt = 0


class HCIdump(Thread):
    """Mimic deprecated hcidump tool."""

    def __init__(self, config, dataqueue):
        """Initiate HCIdump thread."""
        Thread.__init__(self)
        _LOGGER.debug("HCIdump thread: Init")
        self._interfaces = config[CONF_HCI_INTERFACE]
        self._active = int(config[CONF_ACTIVE_SCAN] is True)
        self.dataqueue = dataqueue
        self._event_loop = None

    def process_hci_events(self, data):
        """Collect HCI events."""
        self.dataqueue.put(data)

    def run(self):
        """Run HCIdump thread."""
        _LOGGER.debug("HCIdump thread: Run")
        mysocket = {}
        fac = {}
        conn = {}
        btctrl = {}
        self._event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._event_loop)
        for hci in self._interfaces:
            try:
                mysocket[hci] = aiobs.create_bt_socket(hci)
            except OSError as error:
                _LOGGER.error("HCIdump thread: OS error (hci%i): %s", hci, error)
            else:
                fac[hci] = getattr(self._event_loop, "_create_connection_transport")(
                    mysocket[hci], aiobs.BLEScanRequester, None, None
                )
                conn[hci], btctrl[hci] = self._event_loop.run_until_complete(fac[hci])
                _LOGGER.debug("HCIdump thread: connected to hci%i", hci)
                btctrl[hci].process = self.process_hci_events
                self._event_loop.run_until_complete(btctrl[hci].send_scan_request(self._active))
        _LOGGER.debug("HCIdump thread: start main event_loop")
        try:
            self._event_loop.run_forever()
        finally:
            _LOGGER.debug("HCIdump thread: main event_loop stopped, finishing")
            for hci in self._interfaces:
                self._event_loop.run_until_complete(btctrl[hci].stop_scan_request())
                conn[hci].close()
            self._event_loop.run_until_complete(asyncio.sleep(0))
            self._event_loop.close()
            _LOGGER.debug("HCIdump thread: Run finished")

    def join(self, timeout=10):
        """Join HCIdump thread."""
        _LOGGER.debug("HCIdump thread: joining")
        try:
            self._event_loop.call_soon_threadsafe(self._event_loop.stop)
        except AttributeError as error:
            _LOGGER.debug("%s", error)
        finally:
            Thread.join(self, timeout)
            _LOGGER.debug("HCIdump thread: joined")


class BLEScanner:
    """BLE scanner."""

    def __init__(self, config, dataqueue):
        """Init."""
        self.dataqueue = dataqueue
        self.dumpthread = None
        self.config = config

    def start(self):
        """Start receiving broadcasts."""
        _LOGGER.debug("Spawning HCIdump thread")
        self.dumpthread = HCIdump(
            config=self.config,
            dataqueue=self.dataqueue,
        )
        self.dumpthread.start()

    def stop(self):
        """Stop HCIdump thread(s)."""
        result = True
        if self.dumpthread is None:
            return True
        if self.dumpthread.is_alive():
            self.dumpthread.join()
            if self.dumpthread.is_alive():
                result = False
                _LOGGER.error(
                    "Waiting for the HCIdump thread to finish took too long! (>10s)"
                )
        return result


class MeasuringSensor(RestoreEntity):
    """Base class for measuring sensor entity."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        self.ready_for_update = False
        self._config = config
        self._mac = mac
        self._name = ""
        self._state = None
        self._unit_of_measurement = ""
        self._device_class = None
        self._device_type = devtype
        self._device_state_attributes = {}
        self._device_state_attributes["sensor type"] = devtype
        self._device_state_attributes["mac address"] = (
            ':'.join(mac[i:i + 2] for i in range(0, len(mac), 2))
        )
        self._unique_id = ""
        self._measurement = "measurement"
        self._measurements = []
        self.rssi_values = []
        self.pending_update = False
        self._rdecimals = config[CONF_DECIMALS]
        self._jagged = False
        self._fmdh_dec = 0
        self._rounding = config[CONF_ROUNDING]
        self._use_median = config[CONF_USE_MEDIAN]
        self._restore_state = config[CONF_RESTORE_STATE]
        self._err = None

    async def async_added_to_hass(self):
        """Handle entity which will be added."""
        _LOGGER.debug("async_added_to_hass called for %s", self.name)
        await super().async_added_to_hass()

        # Restore the old state if available
        if self._restore_state is False:
            self.ready_for_update = True
            return
        old_state = await self.async_get_last_state()
        if not old_state:
            self.ready_for_update = True
            return
        self._state = old_state.state
        if "median" in old_state.attributes:
            self._device_state_attributes["median"] = old_state.attributes["median"]
        if "mean" in old_state.attributes:
            self._device_state_attributes["mean"] = old_state.attributes["mean"]
        if "last median of" in old_state.attributes:
            self._device_state_attributes["last median of"] = old_state.attributes["last median of"]
        if "last mean of" in old_state.attributes:
            self._device_state_attributes["last mean of"] = old_state.attributes["last mean of"]
        if "rssi" in old_state.attributes:
            self._device_state_attributes["rssi"] = old_state.attributes["rssi"]
        if "last packet id" in old_state.attributes:
            self._device_state_attributes["last packet id"] = old_state.attributes["last packet id"]
        if ATTR_BATTERY_LEVEL in old_state.attributes:
            self._device_state_attributes[ATTR_BATTERY_LEVEL] = old_state.attributes[ATTR_BATTERY_LEVEL]
        self.ready_for_update = True

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def device_class(self):
        """Return the device class."""
        return self._device_class

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._device_state_attributes

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._unique_id

    @property
    def force_update(self):
        """Force update."""
        return True

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self._jagged is True:
            self._measurements.append(int(data[self._measurement]))
        else:
            self._measurements.append(data[self._measurement])
        self._device_state_attributes["last packet id"] = data["packet"]
        if batt_attr is not None:
            self._device_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True

    def update(self):
        """Updates sensor state and attributes."""
        textattr = ""
        rdecimals = self._rdecimals
        # formaldehyde decimals workaround
        if self._fmdh_dec > 0:
            rdecimals = self._fmdh_dec
        try:
            measurements = self._measurements
            if self._rounding:
                state_median = round(sts.median(measurements), rdecimals)
                state_mean = round(sts.mean(measurements), rdecimals)
            else:
                state_median = sts.median(measurements)
                state_mean = sts.mean(measurements)
            if self._use_median:
                textattr = "last median of"
                self._state = state_median
            else:
                textattr = "last mean of"
                self._state = state_mean
            self._device_state_attributes[textattr] = len(measurements)
            self._measurements.clear()
            self._device_state_attributes["median"] = state_median
            self._device_state_attributes["mean"] = state_mean
            self._device_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
            self.rssi_values.clear()
        except (AttributeError, AssertionError):
            _LOGGER.debug("Sensor %s not yet ready for update", self._name)
        except ZeroDivisionError as err:
            self._err = err
        except IndexError as err:
            self._err = err
        except RuntimeError as err:
            self._err = err
        if self._err:
            _LOGGER.error("Sensor %s (%s) update error: %s", self._name, self._device_type, self._err)
        self.pending_update = False

    def get_sensorname(self):
        """Set sensor name."""
        fmac = ":".join(self._mac[i:i + 2] for i in range(0, len(self._mac), 2))

        if self._config[CONF_DEVICES]:
            for device in self._config[CONF_DEVICES]:
                if fmac in device["mac"].upper():
                    if "name" in device:
                        custom_name = device["name"]
                        _LOGGER.debug(
                            "Name of %s sensor with mac adress %s is set to: %s",
                            self._measurement,
                            fmac,
                            custom_name,
                        )
                        return custom_name
                    break
        return self._mac


class TemperatureSensor(MeasuringSensor):
    """Representation of a sensor."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype)
        self._measurement = "temperature"
        self._sensor_name = self.get_sensorname()
        self._name = "ble temperature {}".format(self._sensor_name)
        self._unique_id = "t_" + self._sensor_name
        self._unit_of_measurement = self.get_temperature_unit()
        self._device_class = DEVICE_CLASS_TEMPERATURE

    def get_temperature_unit(self):
        """Set temperature unit to °C or °F."""
        fmac = ":".join(self._mac[i:i + 2] for i in range(0, len(self._mac), 2))

        if self._config[CONF_DEVICES]:
            for device in self._config[CONF_DEVICES]:
                if fmac in device["mac"].upper():
                    if "temperature_unit" in device:
                        _LOGGER.debug(
                            "Temperature sensor with mac address %s is set to receive data in %s",
                            fmac,
                            device["temperature_unit"],
                        )
                        return device["temperature_unit"]
                    break
        _LOGGER.debug(
            "Temperature sensor with mac address %s is set to receive data in °C",
            fmac,
        )
        return TEMP_CELSIUS


class HumiditySensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype)
        self._measurement = "humidity"
        self._sensor_name = self.get_sensorname()
        self._name = "ble humidity {}".format(self._sensor_name)
        self._unique_id = "h_" + self._sensor_name
        self._unit_of_measurement = PERCENTAGE
        self._device_class = DEVICE_CLASS_HUMIDITY
        # LYWSD03MMC / MHO-C401 "jagged" humidity workaround
        if devtype in ('LYWSD03MMC', 'MHO-C401'):
            self._jagged = True


class MoistureSensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype)
        self._measurement = "moisture"
        self._sensor_name = self.get_sensorname()
        self._name = "ble moisture {}".format(self._sensor_name)
        self._unique_id = "m_" + self._sensor_name
        self._unit_of_measurement = PERCENTAGE
        self._device_class = DEVICE_CLASS_HUMIDITY


class ConductivitySensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype)
        self._measurement = "conductivity"
        self._sensor_name = self.get_sensorname()
        self._name = "ble conductivity {}".format(self._sensor_name)
        self._unique_id = "c_" + self._sensor_name
        self._unit_of_measurement = CONDUCTIVITY
        self._device_class = None

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:flash-circle"


class IlluminanceSensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype)
        self._measurement = "illuminance"
        self._sensor_name = self.get_sensorname()
        self._name = "ble illuminance {}".format(self._sensor_name)
        self._unique_id = "l_" + self._sensor_name
        self._unit_of_measurement = "lx"
        self._device_class = DEVICE_CLASS_ILLUMINANCE


class FormaldehydeSensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype)
        self._measurement = "formaldehyde"
        self._sensor_name = self.get_sensorname()
        self._name = "ble formaldehyde {}".format(self._sensor_name)
        self._unique_id = "f_" + self._sensor_name
        self._unit_of_measurement = "mg/m³"
        self._device_class = None
        self._fmdh_dec = 3

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:chemical-weapon"


class BatterySensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype)
        self._measurement = "battery"
        self._sensor_name = self.get_sensorname()
        self._name = "ble battery {}".format(self._sensor_name)
        self._unique_id = "batt_" + self._sensor_name
        self._unit_of_measurement = PERCENTAGE
        self._device_class = DEVICE_CLASS_BATTERY

    def collect(self, data, batt_attr=None):
        """Battery measurements collector."""
        self._state = data[self._measurement]
        self._device_state_attributes["last packet id"] = data["packet"]
        self.pending_update = True

    def update(self):
        """Update sensor state and attributes."""
        self._device_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
        self.rssi_values.clear()
        self.pending_update = False


class ConsumableSensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype)
        self._measurement = "consumable"
        self._sensor_name = self.get_sensorname()
        self._name = "ble consumable {}".format(self._sensor_name)
        self._unique_id = "cn_" + self._sensor_name
        self._unit_of_measurement = PERCENTAGE
        self._device_class = None

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:mdi-recycle-variant"

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        self._state = data[self._measurement]
        self._device_state_attributes["last packet id"] = data["packet"]
        if batt_attr is not None:
            self._device_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True

    def update(self):
        """Update."""
        self._device_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
        self.rssi_values.clear()
        self.pending_update = False


class SwitchingSensor(RestoreEntity, BinarySensorEntity):
    """Representation of a Sensor."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        self.ready_for_update = False
        self._sensor_name = ""
        self._mac = mac
        self._config = config
        self._restore_state = config[CONF_RESTORE_STATE]
        self._name = ""
        self._state = None
        self._unique_id = ""
        self._device_type = devtype
        self._device_state_attributes = {}
        self._device_state_attributes["sensor type"] = devtype
        self._device_state_attributes["mac address"] = (
            ':'.join(mac[i:i + 2] for i in range(0, len(mac), 2))
        )
        self._device_class = None
        self._newstate = None
        self._measurement = "measurement"
        self.pending_update = False

    async def async_added_to_hass(self):
        """Handle entity which will be added."""
        _LOGGER.debug("async_added_to_hass called for %s", self.name)
        await super().async_added_to_hass()
        # Restore the old state if available
        if self._restore_state is False:
            self.ready_for_update = True
            return
        old_state = await self.async_get_last_state()
        _LOGGER.info(old_state)
        if not old_state:
            self.ready_for_update = True
            return
        self._state = True if old_state.state == STATE_ON else False
        if "ext_state" in old_state.attributes:
            self._device_state_attributes["ext_state"] = old_state.attributes["ext_state"]
        if "rssi" in old_state.attributes:
            self._device_state_attributes["rssi"] = old_state.attributes["rssi"]
        if "last packet id" in old_state.attributes:
            self._device_state_attributes["last packet id"] = old_state.attributes["last packet id"]
        if ATTR_BATTERY_LEVEL in old_state.attributes:
            self._device_state_attributes[ATTR_BATTERY_LEVEL] = old_state.attributes[ATTR_BATTERY_LEVEL]
        self.ready_for_update = True

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return bool(self._state) if self._state is not None else None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the binary sensor."""
        if self.is_on is None:
            return None
        return STATE_ON if self.is_on else STATE_OFF

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._device_state_attributes

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._unique_id

    @property
    def device_class(self):
        """Return the device class."""
        return self._device_class

    @property
    def force_update(self):
        """Force update."""
        return True

    def get_sensorname(self):
        """Set sensor name."""
        fmac = ":".join(self._mac[i:i + 2] for i in range(0, len(self._mac), 2))

        if self._config[CONF_DEVICES]:
            for device in self._config[CONF_DEVICES]:
                if fmac in device["mac"].upper():
                    if "name" in device:
                        custom_name = device["name"]
                        _LOGGER.debug(
                            "Name of %s sensor with mac adress %s is set to: %s",
                            self._measurement,
                            fmac,
                            custom_name,
                        )
                        return custom_name
                    break
        return self._mac

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        self._newstate = data[self._measurement]
        self._device_state_attributes["last packet id"] = data["packet"]
        self._device_state_attributes["rssi"] = data["rssi"]
        if batt_attr is not None:
            self._device_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr

    def update(self):
        """Update sensor state and attribute."""
        self._state = self._newstate


class PowerBinarySensor(SwitchingSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype)
        self._measurement = "switch"
        self._sensor_name = self.get_sensorname()
        self._name = "ble switch {}".format(self._sensor_name)
        self._unique_id = "sw_" + self._sensor_name
        self._device_class = DEVICE_CLASS_POWER


class LightBinarySensor(SwitchingSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype)
        self._measurement = "light"
        self._sensor_name = self.get_sensorname()
        self._name = "ble light {}".format(self._sensor_name)
        self._unique_id = "lt_" + self._sensor_name
        self._device_class = DEVICE_CLASS_LIGHT


class OpeningBinarySensor(SwitchingSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype)
        self._measurement = "opening"
        self._sensor_name = self.get_sensorname()
        self._name = "ble opening {}".format(self._sensor_name)
        self._unique_id = "op_" + self._sensor_name
        self._ext_state = None
        self._device_class = DEVICE_CLASS_OPENING

    def update(self):
        """Update sensor state and attributes."""
        self._ext_state = self._newstate
        self._state = not bool(self._newstate) if self._ext_state < 2 else bool(self._newstate)
        self._device_state_attributes["ext_state"] = self._ext_state
