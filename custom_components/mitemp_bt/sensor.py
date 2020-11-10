"""Platform for sensor integration."""
import asyncio
from datetime import timedelta
import logging
import statistics as sts
import struct
from threading import Thread
from time import sleep

import aioblescan as aiobs
from Cryptodome.Cipher import AES

from homeassistant.const import (
    CONF_DEVICES,
    CONF_DISCOVERY,
    CONF_MAC,
    CONF_NAME,
    CONF_TEMPERATURE_UNIT,
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_ILLUMINANCE,
    DEVICE_CLASS_TEMPERATURE,
    CONDUCTIVITY,
    PERCENTAGE,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
    ATTR_BATTERY_LEVEL,
    STATE_OFF,
    STATE_ON,
)

from homeassistant.components.binary_sensor import BinarySensorEntity
#from homeassistant.components.sensor import PLATFORM_SCHEMA
#import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import track_point_in_utc_time
import homeassistant.util.dt as dt_util

from .const import (
#    DEFAULT_ROUNDING,
#    DEFAULT_DECIMALS,
#    DEFAULT_PERIOD,
#    DEFAULT_LOG_SPIKES,
#    DEFAULT_USE_MEDIAN,
#    DEFAULT_ACTIVE_SCAN,
#    DEFAULT_HCI_INTERFACE,
#    DEFAULT_BATT_ENTITIES,
#    DEFAULT_REPORT_UNKNOWN,
#    DEFAULT_DISCOVERY,
    CONF_ROUNDING,
    CONF_DECIMALS,
    CONF_PERIOD,
    CONF_LOG_SPIKES,
    CONF_USE_MEDIAN,
    CONF_ACTIVE_SCAN,
    CONF_HCI_INTERFACE,
    CONF_BATT_ENTITIES,
    CONF_REPORT_UNKNOWN,
    CONF_TMIN,
    CONF_TMAX,
    CONF_HMIN,
    CONF_HMAX,
    CONF_ENCRYPTION_KEY,
    DOMAIN,
    XIAOMI_TYPE_DICT,
    MMTS_DICT,
    SW_CLASS_DICT,
    CN_NAME_DICT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    def reverse_mac(rmac):
        """Change LE order to BE."""
        if len(rmac) != 12:
            return None
        return rmac[10:12] + rmac[8:10] + rmac[6:8] + rmac[4:6] + rmac[2:4] + rmac[0:2]

    def lpacket(mac, packet=None):
        """Last_packet static storage."""
        if packet is not None:
            lpacket.cntr[mac] = packet
        else:
            try:
                cntr = lpacket.cntr[mac]
            except KeyError:
                cntr = None
            return cntr

    _LOGGER.debug("Starting")
    firstrun = True
    scanner = BLEScanner()
    hass.bus.listen("homeassistant_stop", scanner.shutdown_handler)
    scanner.start(config)
    sensors_by_mac = {}
    if config[DOMAIN][CONF_REPORT_UNKNOWN]:
        _LOGGER.info(
            "Attention! Option report_unknown is enabled, be ready for a huge output..."
        )
    # prepare device:key lists to speedup parser
    aeskeys = {}
    if config[DOMAIN][CONF_DEVICES]:
        for device in config[DOMAIN][CONF_DEVICES]:
            if "encryption_key" in device:
                p_mac = bytes.fromhex(
                    reverse_mac(device["mac"].replace(":", "")).lower()
                )
                p_key = bytes.fromhex(device["encryption_key"].lower())
                aeskeys[p_mac] = p_key
            else:
                continue
    _LOGGER.debug("%s encryptors mac:key pairs loaded.", len(aeskeys))

    whitelist = []
    if isinstance(config[DOMAIN][CONF_DISCOVERY], bool):
        if config[DOMAIN][CONF_DISCOVERY] is False:
            if config[DOMAIN][CONF_DEVICES]:
                for device in config[DOMAIN][CONF_DEVICES]:
                    whitelist.append(device["mac"])
    # remove duplicates from whitelist
    whitelist = list(dict.fromkeys(whitelist))
    _LOGGER.debug("whitelist: [%s]", ", ".join(whitelist).upper())
    for i, mac in enumerate(whitelist):
        whitelist[i] = bytes.fromhex(reverse_mac(mac.replace(":", "")).lower())
    _LOGGER.debug("%s whitelist item(s) loaded.", len(whitelist))
    lpacket.cntr = {}
    sleep(1)

    def calc_update_state(
        entity_to_update,
        sensor_mac,
        config,
        measurements_list,
        stype=None,
        fdec=0,
    ):
        """Averages according to options and updates the entity state."""
        textattr = ""
        success = False
        error = ""
        rdecimals = config[DOMAIN][CONF_DECIMALS]
        # formaldehyde decimals workaround
        if fdec > 0:
            rdecimals = fdec
        # LYWSD03MMC / MHO-C401 "jagged" humidity workaround
        if stype in ('LYWSD03MMC', 'MHO-C401'):
            measurements = [int(item) for item in measurements_list]
        else:
            measurements = measurements_list
        try:
            if config[DOMAIN][CONF_ROUNDING]:
                state_median = round(sts.median(measurements), rdecimals)
                state_mean = round(sts.mean(measurements), rdecimals)
            else:
                state_median = sts.median(measurements)
                state_mean = sts.mean(measurements)
            if config[DOMAIN][CONF_USE_MEDIAN]:
                textattr = "last median of"
                setattr(entity_to_update, "_state", state_median)
            else:
                textattr = "last mean of"
                setattr(entity_to_update, "_state", state_mean)
            getattr(entity_to_update, "_device_state_attributes")[
                textattr
            ] = len(measurements)
            getattr(entity_to_update, "_device_state_attributes")[
                "median"
            ] = state_median
            getattr(entity_to_update, "_device_state_attributes")[
                "mean"
            ] = state_mean
            entity_to_update.schedule_update_ha_state()
            success = True
        except (AttributeError, AssertionError):
            _LOGGER.debug("Sensor %s not yet ready for update", sensor_mac)
            success = True
        except ZeroDivisionError as err:
            error = err
        except IndexError as err:
            error = err
        except RuntimeError as err:
            error = err
        return success, error

    def discover_ble_devices(config, aeskeyslist, whitelist):
        """Discover Bluetooth LE devices."""
        nonlocal firstrun
        if firstrun:
            firstrun = False
            _LOGGER.debug("First run, skip parsing.")
            return []
        _LOGGER.debug("Discovering Bluetooth LE devices")
        log_spikes = config[DOMAIN][CONF_LOG_SPIKES]
        _LOGGER.debug("Time to analyze...")
        stype = {}
        hum_m_data = {}
        temp_m_data = {}
        illum_m_data = {}
        moist_m_data = {}
        cond_m_data = {}
        formaldehyde_m_data = {}
        cons_m_data = {}
        switch_m_data = {}
        batt = {}  # battery
        rssi = {}
        macs = {}  # all found macs
        _LOGGER.debug("Getting data from HCIdump thread")
        jres = scanner.stop()
        if jres is False:
            _LOGGER.error("HCIdump thread(s) is not completed, interrupting data processing!")
            return []
        hcidump_raw = [*scanner.hcidump_data]
        scanner.start()  # minimum delay between HCIdumps
        report_unknown = config[DOMAIN][CONF_REPORT_UNKNOWN]
        for msg in hcidump_raw:
            data = parse_raw_message(msg, aeskeyslist, whitelist, report_unknown)
            if data and "mac" in data:
                # ignore duplicated message
                packet = data["packet"]
                mac = data["mac"]
                prev_packet = lpacket(mac)
                if prev_packet == packet:
                    # _LOGGER.debug("DUPLICATE: %s, IGNORING!", data)
                    continue
                lpacket(mac, packet)
                # store found readings per device
                if "temperature" in data:
                    if (
                        temperature_limit(config, mac, CONF_TMAX)
                        >= data["temperature"]
                        >= temperature_limit(config, mac, CONF_TMIN)
                    ):
                        if mac not in temp_m_data:
                            temp_m_data[mac] = []
                        temp_m_data[mac].append(data["temperature"])
                        macs[mac] = mac
                    elif log_spikes:
                        _LOGGER.error(
                            "Temperature spike: %s (%s)",
                            data["temperature"],
                            mac,
                        )
                if "humidity" in data:
                    if CONF_HMAX >= data["humidity"] >= CONF_HMIN:
                        if mac not in hum_m_data:
                            hum_m_data[mac] = []
                        hum_m_data[mac].append(data["humidity"])
                        macs[mac] = mac
                    elif log_spikes:
                        _LOGGER.error(
                            "Humidity spike: %s (%s)",
                            data["humidity"],
                            mac,
                        )
                if "conductivity" in data:
                    if mac not in cond_m_data:
                        cond_m_data[mac] = []
                    cond_m_data[mac].append(data["conductivity"])
                    macs[mac] = mac
                if "moisture" in data:
                    if mac not in moist_m_data:
                        moist_m_data[mac] = []
                    moist_m_data[mac].append(data["moisture"])
                    macs[mac] = mac
                if "illuminance" in data:
                    if mac not in illum_m_data:
                        illum_m_data[mac] = []
                    illum_m_data[mac].append(data["illuminance"])
                    macs[mac] = mac
                if "formaldehyde" in data:
                    if mac not in formaldehyde_m_data:
                        formaldehyde_m_data[mac] = []
                    formaldehyde_m_data[mac].append(data["formaldehyde"])
                    macs[mac] = mac
                if "consumable" in data:
                    cons_m_data[mac] = int(data["consumable"])
                    macs[mac] = mac
                if "switch" in data:
                    switch_m_data[mac] = int(data["switch"])
                    macs[mac] = mac
                if "battery" in data:
                    batt[mac] = int(data["battery"])
                    macs[mac] = mac
                if mac not in rssi:
                    rssi[mac] = []
                rssi[mac].append(int(data["rssi"]))
                stype[mac] = data["type"]
            else:
                # "empty" loop high cpu usage workaround
                sleep(0.0001)
        # for every seen device
        for mac in macs:
            # fixed entity index for every measurement type
            # according to the sensor implementation
            sensortype = stype[mac]
            t_i, h_i, m_i, c_i, i_i, f_i, cn_i, sw_i, b_i = MMTS_DICT[
                sensortype
            ]
            # if necessary, create a list of entities
            # according to the sensor implementation
            if mac in sensors_by_mac:
                sensors = sensors_by_mac[mac]
            else:
                sensors = []
                if t_i != 9:
                    sensors.insert(t_i, TemperatureSensor(config, mac))
                if h_i != 9:
                    sensors.insert(h_i, HumiditySensor(config, mac))
                if m_i != 9:
                    sensors.insert(m_i, MoistureSensor(config, mac))
                if c_i != 9:
                    sensors.insert(c_i, ConductivitySensor(config, mac))
                if i_i != 9:
                    sensors.insert(i_i, IlluminanceSensor(config, mac))
                if f_i != 9:
                    sensors.insert(f_i, FormaldehydeSensor(config, mac))
                if cn_i != 9:
                    sensors.insert(cn_i, ConsumableSensor(config, mac))
                    try:
                        setattr(
                            sensors[cn_i], "_cn_name", CN_NAME_DICT[sensortype]
                        )
                    except KeyError:
                        pass
                if sw_i != 9:
                    sensors.insert(sw_i, SwitchBinarySensor(config, mac))
                    try:
                        setattr(
                            sensors[sw_i], "_swclass", SW_CLASS_DICT[sensortype]
                        )
                    except KeyError:
                        pass
                if config[DOMAIN][CONF_BATT_ENTITIES] and (b_i != 9):
                    sensors.insert(b_i, BatterySensor(config, mac))
                sensors_by_mac[mac] = sensors
                add_entities(sensors)
            # append joint attributes
            for sensor in sensors:
                getattr(sensor, "_device_state_attributes")[
                    "last packet id"
                ] = lpacket(mac)
                getattr(sensor, "_device_state_attributes")["rssi"] = round(
                    sts.mean(rssi[mac])
                )
                getattr(sensor, "_device_state_attributes")[
                    "sensor type"
                ] = sensortype
                getattr(sensor, "_device_state_attributes")[
                    "mac address"
                ] = ":".join(mac[i:i+2] for i in range(0, len(mac), 2))
                if not isinstance(sensor, BatterySensor) and mac in batt:
                    getattr(sensor, "_device_state_attributes")[
                        ATTR_BATTERY_LEVEL
                    ] = batt[mac]

            # averaging and states updating
            if mac in batt:
                if config[DOMAIN][CONF_BATT_ENTITIES]:
                    setattr(sensors[b_i], "_state", batt[mac])
                    try:
                        sensors[b_i].schedule_update_ha_state()
                    except (AttributeError, AssertionError):
                        _LOGGER.debug(
                            "Sensor %s (%s, batt.) not yet ready for update",
                            mac,
                            sensortype,
                        )
                    except RuntimeError as err:
                        _LOGGER.error(
                            "Sensor %s (%s, batt.) update error:",
                            mac,
                            sensortype,
                        )
                        _LOGGER.error(err)
            if mac in temp_m_data:
                success, error = calc_update_state(
                    sensors[t_i], mac, config, temp_m_data[mac]
                )
                if not success:
                    _LOGGER.error(
                        "Sensor %s (%s, temp.) update error:", mac, sensortype
                    )
                    _LOGGER.error(error)
            if mac in hum_m_data:
                success, error = calc_update_state(
                    sensors[h_i], mac, config, hum_m_data[mac], sensortype
                )
                if not success:
                    _LOGGER.error(
                        "Sensor %s (%s, hum.) update error:", mac, sensortype
                    )
                    _LOGGER.error(error)
            if mac in moist_m_data:
                success, error = calc_update_state(
                    sensors[m_i], mac, config, moist_m_data[mac]
                )
                if not success:
                    _LOGGER.error(
                        "Sensor %s (%s, moist.) update error:", mac, sensortype
                    )
                    _LOGGER.error(error)
            if mac in cond_m_data:
                success, error = calc_update_state(
                    sensors[c_i], mac, config, cond_m_data[mac]
                )
                if not success:
                    _LOGGER.error(
                        "Sensor %s (%s, cond.) update error:", mac, sensortype
                    )
                    _LOGGER.error(error)
            if mac in illum_m_data:
                success, error = calc_update_state(
                    sensors[i_i], mac, config, illum_m_data[mac]
                )
                if not success:
                    _LOGGER.error(
                        "Sensor %s (%s, illum.) update error:", mac, sensortype
                    )
                    _LOGGER.error(error)
            if mac in formaldehyde_m_data:
                success, error = calc_update_state(
                    sensors[f_i], mac, config, formaldehyde_m_data[mac], fdec=3
                )
                if not success:
                    _LOGGER.error(
                        "Sensor %s (%s, formaldehyde) update error:",
                        mac,
                        sensortype,
                    )
                    _LOGGER.error(error)
            if mac in cons_m_data:
                setattr(sensors[cn_i], "_state", cons_m_data[mac])
                try:
                    sensors[cn_i].schedule_update_ha_state()
                except (AttributeError, AssertionError):
                    _LOGGER.debug(
                        "Sensor %s (%s, cons.) not yet ready for update",
                        mac,
                        sensortype,
                    )
                except RuntimeError as err:
                    _LOGGER.error(
                        "Sensor %s (%s, cons.) update error:",
                        mac,
                        sensortype,
                    )
                    _LOGGER.error(err)
            if mac in switch_m_data:
                setattr(sensors[sw_i], "_state", switch_m_data[mac])
                try:
                    sensors[sw_i].schedule_update_ha_state()
                except (AttributeError, AssertionError):
                    _LOGGER.debug(
                        "Sensor %s (%s, switch) not yet ready for update",
                        mac,
                        sensortype,
                    )
                except RuntimeError as err:
                    _LOGGER.error(
                        "Sensor %s (%s, switch) update error:", mac, sensortype
                    )
                    _LOGGER.error(err)
        _LOGGER.debug(
            "Finished. Parsed: %i hci events, %i xiaomi devices.",
            len(hcidump_raw),
            len(macs),
        )
        return []

    def update_ble(now):
        """Lookup Bluetooth LE devices and update status."""
        period = config[DOMAIN][CONF_PERIOD]
        _LOGGER.debug("update_ble called")
        try:
            discover_ble_devices(config, aeskeys, whitelist)
        except RuntimeError as error:
            _LOGGER.error("Error during Bluetooth LE scan: %s", error)
        track_point_in_utc_time(
            hass, update_ble, dt_util.utcnow() + timedelta(seconds=period)
        )

    update_ble(dt_util.utcnow())
    # Return successful setup
    return True


def sensor_name(config, mac, sensor_type):
    """Set sensor name."""
    fmac = ":".join(mac[i:i+2] for i in range(0, len(mac), 2))

    if config[DOMAIN][CONF_DEVICES]:
        for device in config[DOMAIN][CONF_DEVICES]:
            if fmac in device["mac"].upper():
                if "name" in device:
                    custom_name = device["name"]
                    _LOGGER.debug(
                        "Name of %s sensor with mac adress %s is set to: %s",
                        sensor_type,
                        fmac,
                        custom_name,
                    )
                    return custom_name
                break
    return mac


def temperature_unit(config, mac):
    """Set temperature unit to °C or °F."""
    fmac = ":".join(mac[i:i+2] for i in range(0, len(mac), 2))

    if config[DOMAIN][CONF_DEVICES]:
        for device in config[DOMAIN][CONF_DEVICES]:
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


class MeasuringSensor(Entity):
    """Base class for measuring sensor entity."""

    def __init__(self, config, mac):
        """Initialize the sensor."""
        self._name = ""
        self._state = None
        self._unit_of_measurement = ""
        self._device_class = None
        self._device_state_attributes = {}
        self._unique_id = ""

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


class TemperatureSensor(MeasuringSensor):
    """Representation of a sensor."""

    def __init__(self, config, mac):
        """Initialize the sensor."""
        super().__init__(config, mac)
        self._sensor_name = sensor_name(config, mac, "temperature")
        self._name = "mi temperature {}".format(self._sensor_name)
        self._unique_id = "t_" + self._sensor_name
        self._unit_of_measurement = temperature_unit(config, mac)
        self._device_class = DEVICE_CLASS_TEMPERATURE


class HumiditySensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac):
        """Initialize the sensor."""
        super().__init__(config, mac)
        self._sensor_name = sensor_name(config, mac, "humidity")
        self._name = "mi humidity {}".format(self._sensor_name)
        self._unique_id = "h_" + self._sensor_name
        self._unit_of_measurement = PERCENTAGE
        self._device_class = DEVICE_CLASS_HUMIDITY


class MoistureSensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac):
        """Initialize the sensor."""
        super().__init__(config, mac)
        self._sensor_name = sensor_name(config, mac, "moisture")
        self._name = "mi moisture {}".format(self._sensor_name)
        self._unique_id = "m_" + self._sensor_name
        self._unit_of_measurement = PERCENTAGE
        self._device_class = DEVICE_CLASS_HUMIDITY


class ConductivitySensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac):
        """Initialize the sensor."""
        super().__init__(config, mac)
        self._sensor_name = sensor_name(config, mac, "conductivity")
        self._name = "mi conductivity {}".format(self._sensor_name)
        self._unique_id = "c_" + self._sensor_name
        self._unit_of_measurement = CONDUCTIVITY
        self._device_class = None

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:flash-circle"


class IlluminanceSensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac):
        """Initialize the sensor."""
        super().__init__(config, mac)
        self._sensor_name = sensor_name(config, mac, "illuminance")
        self._name = "mi llluminance {}".format(self._sensor_name)
        self._unique_id = "l_" + self._sensor_name
        self._unit_of_measurement = "lx"
        self._device_class = DEVICE_CLASS_ILLUMINANCE


class FormaldehydeSensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac):
        """Initialize the sensor."""
        super().__init__(config, mac)
        self._sensor_name = sensor_name(config, mac, "formaldehyde")
        self._name = "mi formaldehyde {}".format(self._sensor_name)
        self._unique_id = "f_" + self._sensor_name
        self._unit_of_measurement = "mg/m³"
        self._device_class = None

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:chemical-weapon"


class BatterySensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac):
        """Initialize the sensor."""
        super().__init__(config, mac)
        self._sensor_name = sensor_name(config, mac, "battery")
        self._name = "mi battery {}".format(self._sensor_name)
        self._unique_id = "batt__" + self._sensor_name
        self._unit_of_measurement = PERCENTAGE
        self._device_class = DEVICE_CLASS_BATTERY


class ConsumableSensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac):
        """Initialize the sensor."""
        super().__init__(config, mac)
        self._sensor_name = sensor_name(config, mac, "consumbable")
        self._name = "mi consumable {}".format(self._sensor_name)
        self._unique_id = "cn__" + self._sensor_name
        self._unit_of_measurement = PERCENTAGE
        self._device_class = None

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:mdi-recycle-variant"


class SwitchBinarySensor(BinarySensorEntity):
    """Representation of a Sensor."""

    def __init__(self, config, mac):
        """Initialize the sensor."""
        self._sensor_name = sensor_name(config, mac, "switch")
        self._name = "mi switch {}".format(self._sensor_name)
        self._state = None
        self._unique_id = "sw_" + self._sensor_name
        self._device_state_attributes = {}
        self._device_class = None

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return bool(self._state)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the binary sensor."""
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
    
