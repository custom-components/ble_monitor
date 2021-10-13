"""Passive BLE monitor integration."""
import asyncio
import copy
import json
import logging
from threading import Thread
import voluptuous as vol

import aioblescan as aiobs
import janus

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import (
    CONF_DEVICES,
    CONF_DISCOVERY,
    CONF_MAC,
    CONF_NAME,
    CONF_TEMPERATURE_UNIT,
    CONF_UNIQUE_ID,
    EVENT_HOMEASSISTANT_STOP,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_registry import (
    async_entries_for_device,
)

from .ble_parser import BleParser
from .const import (
    DEFAULT_DECIMALS,
    DEFAULT_PERIOD,
    DEFAULT_LOG_SPIKES,
    DEFAULT_USE_MEDIAN,
    DEFAULT_ACTIVE_SCAN,
    DEFAULT_BATT_ENTITIES,
    DEFAULT_REPORT_UNKNOWN,
    DEFAULT_DISCOVERY,
    DEFAULT_RESTORE_STATE,
    DEFAULT_DEVICE_DECIMALS,
    DEFAULT_DEVICE_USE_MEDIAN,
    DEFAULT_DEVICE_RESTORE_STATE,
    DEFAULT_DEVICE_RESET_TIMER,
    DEFAULT_DEVICE_TRACK,
    DEFAULT_DEVICE_TRACKER_SCAN_INTERVAL,
    DEFAULT_DEVICE_TRACKER_CONSIDER_HOME,
    CONF_DECIMALS,
    CONF_PERIOD,
    CONF_LOG_SPIKES,
    CONF_USE_MEDIAN,
    CONF_ACTIVE_SCAN,
    CONF_HCI_INTERFACE,
    CONF_BT_INTERFACE,
    CONF_BATT_ENTITIES,
    CONF_REPORT_UNKNOWN,
    CONF_RESTORE_STATE,
    CONF_ENCRYPTION_KEY,
    CONF_DEVICE_DECIMALS,
    CONF_DEVICE_USE_MEDIAN,
    CONF_DEVICE_RESTORE_STATE,
    CONF_DEVICE_RESET_TIMER,
    CONF_DEVICE_TRACK,
    CONFIG_IS_FLOW,
    CONF_DEVICE_TRACKER_SCAN_INTERVAL,
    CONF_DEVICE_TRACKER_CONSIDER_HOME,
    DOMAIN,
    PLATFORMS,
    MAC_REGEX,
    AES128KEY24_REGEX,
    AES128KEY32_REGEX,
    MEASUREMENT_DICT,
    SERVICE_CLEANUP_ENTRIES,
)

from .bt_helpers import (
    BT_INTERFACES,
    BT_MAC_INTERFACES,
    DEFAULT_BT_INTERFACE,
)

_LOGGER = logging.getLogger(__name__)

CONFIG_YAML = {}
UPDATE_UNLISTENER = None

DEVICE_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_MAC): cv.matches_regex(MAC_REGEX),
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional(CONF_ENCRYPTION_KEY): vol.Any(
            cv.matches_regex(AES128KEY24_REGEX), cv.matches_regex(AES128KEY32_REGEX)
        ),
        vol.Optional(CONF_TEMPERATURE_UNIT): cv.temperature_unit,
        vol.Optional(CONF_DEVICE_DECIMALS, default=DEFAULT_DEVICE_DECIMALS): vol.In(
            [DEFAULT_DEVICE_DECIMALS, 0, 1, 2, 3, 4]
        ),
        vol.Optional(CONF_DEVICE_USE_MEDIAN, default=DEFAULT_DEVICE_USE_MEDIAN): vol.In(
            [DEFAULT_DEVICE_USE_MEDIAN, True, False]
        ),
        vol.Optional(
            CONF_DEVICE_RESTORE_STATE, default=DEFAULT_DEVICE_RESTORE_STATE
        ): vol.In([DEFAULT_DEVICE_RESTORE_STATE, True, False]),
        vol.Optional(
            CONF_DEVICE_RESET_TIMER, default=DEFAULT_DEVICE_RESET_TIMER
        ): cv.positive_int,
        vol.Optional(CONF_DEVICE_TRACK, default=DEFAULT_DEVICE_TRACK): cv.boolean,
        vol.Optional(
            CONF_DEVICE_TRACKER_SCAN_INTERVAL,
            default=DEFAULT_DEVICE_TRACKER_SCAN_INTERVAL,
        ): cv.positive_int,
        vol.Optional(
            CONF_DEVICE_TRACKER_CONSIDER_HOME,
            default=DEFAULT_DEVICE_TRACKER_CONSIDER_HOME,
        ): cv.positive_int,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.All(
            cv.deprecated(CONF_BATT_ENTITIES),
            vol.Schema(
                {
                    vol.Optional(
                        CONF_DECIMALS, default=DEFAULT_DECIMALS
                    ): cv.positive_int,
                    vol.Optional(CONF_PERIOD, default=DEFAULT_PERIOD): cv.positive_int,
                    vol.Optional(
                        CONF_LOG_SPIKES, default=DEFAULT_LOG_SPIKES
                    ): cv.boolean,
                    vol.Optional(
                        CONF_USE_MEDIAN, default=DEFAULT_USE_MEDIAN
                    ): cv.boolean,
                    vol.Optional(
                        CONF_ACTIVE_SCAN, default=DEFAULT_ACTIVE_SCAN
                    ): cv.boolean,
                    vol.Optional(CONF_HCI_INTERFACE, default=[]): vol.All(
                        cv.ensure_list, [cv.positive_int]
                    ),
                    vol.Optional(
                        CONF_BT_INTERFACE, default=DEFAULT_BT_INTERFACE
                    ): vol.All(cv.ensure_list, [cv.matches_regex(MAC_REGEX)]),
                    vol.Optional(
                        CONF_BATT_ENTITIES, default=DEFAULT_BATT_ENTITIES
                    ): cv.boolean,
                    vol.Optional(CONF_DISCOVERY, default=DEFAULT_DISCOVERY): cv.boolean,
                    vol.Optional(
                        CONF_RESTORE_STATE, default=DEFAULT_RESTORE_STATE
                    ): cv.boolean,
                    vol.Optional(CONF_DEVICES, default=[]): vol.All(
                        cv.ensure_list, [DEVICE_SCHEMA]
                    ),
                    vol.Optional(
                        CONF_REPORT_UNKNOWN, default=DEFAULT_REPORT_UNKNOWN
                    ): vol.In(
                        [
                            "ATC",
                            "BlueMaestro",
                            "Brifit",
                            "Govee",
                            "iNode",
                            "Kegtron",
                            "Mi Scale",
                            "Moat",
                            "Qingping",
                            "Ruuvitag",
                            "SensorPush",
                            "Teltonika",
                            "Thermoplus",
                            "Xiaomi",
                            "Other",
                            False,
                        ]
                    ),
                }
            ),
        )
    },
    extra=vol.ALLOW_EXTRA,
)

SERVICE_CLEANUP_ENTRIES_SCHEMA = vol.Schema({})


async def async_setup(hass: HomeAssistant, config):
    """Set up integration."""

    async def service_cleanup_entries(service_call):
        service_data = service_call.data

        await async_cleanup_entries_service(hass, service_data)

    hass.services.async_register(
        DOMAIN,
        SERVICE_CLEANUP_ENTRIES,
        service_cleanup_entries,
        schema=SERVICE_CLEANUP_ENTRIES_SCHEMA,
    )

    if DOMAIN not in config:
        return True

    if DOMAIN in hass.data:
        # One instance only
        return False

    # Save and set default for the YAML config
    global CONFIG_YAML
    CONFIG_YAML = json.loads(json.dumps(config[DOMAIN]))
    CONFIG_YAML[CONFIG_IS_FLOW] = False
    CONFIG_YAML["ids_from_name"] = True

    _LOGGER.debug("Initializing BLE Monitor integration (YAML): %s", CONFIG_YAML)

    hass.async_add_job(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_IMPORT}, data=copy.deepcopy(CONFIG_YAML)
        )
    )

    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Set up BLE Monitor from a config entry."""
    _LOGGER.debug("Initializing BLE Monitor entry (config entry): %s", config_entry)

    # Prevent unload to be triggered each time we update the config entry
    global UPDATE_UNLISTENER
    if UPDATE_UNLISTENER:
        UPDATE_UNLISTENER()

    if not config_entry.unique_id:
        hass.config_entries.async_update_entry(
            config_entry, unique_id=config_entry.title
        )

    _LOGGER.debug("async_setup_entry: domain %s", CONFIG_YAML)

    config = {}
    hci_list = []
    bt_mac_list = []

    if not CONFIG_YAML:
        # Configuration in UI
        for key, value in config_entry.data.items():
            config[key] = value

        for key, value in config_entry.options.items():
            config[key] = value

        config[CONFIG_IS_FLOW] = True
        if CONF_DEVICES not in config:
            config[CONF_DEVICES] = []
        else:
            # device configuration is taken from yaml, but yaml config already removed
            # save unique IDs (only once)
            if "ids_from_name" in config:
                devlist = config[CONF_DEVICES]
                for dev_idx, dev_conf in enumerate(devlist):
                    if CONF_NAME in dev_conf:
                        devlist[dev_idx][CONF_UNIQUE_ID] = dev_conf[CONF_NAME]
                del config["ids_from_name"]

        if not config[CONF_BT_INTERFACE]:
            default_hci = list(BT_INTERFACES.keys())[
                list(BT_INTERFACES.values()).index(DEFAULT_BT_INTERFACE)
            ]
            hci_list.append(int(default_hci))
            bt_mac_list.append(str(DEFAULT_BT_INTERFACE))
        else:
            bt_interface_list = config[CONF_BT_INTERFACE]
            for bt_mac in bt_interface_list:
                hci = list(BT_INTERFACES.keys())[
                    list(BT_INTERFACES.values()).index(bt_mac)
                ]
                hci_list.append(int(hci))
                bt_mac_list.append(str(bt_mac))
    else:
        # Configuration in YAML
        for key, value in CONFIG_YAML.items():
            config[key] = value
        _LOGGER.info(
            "Available Bluetooth interfaces for BLE monitor: %s", BT_MAC_INTERFACES
        )

        if config[CONF_HCI_INTERFACE]:
            # Configuration of BT interface with hci number
            for hci in CONFIG_YAML[CONF_HCI_INTERFACE]:
                try:
                    hci_list.append(int(hci))
                    bt_mac = BT_INTERFACES.get(hci)
                    if bt_mac:
                        bt_mac_list.append(str(bt_mac))
                    else:
                        _LOGGER.error("Bluetooth interface hci%i is not available", hci)
                except ValueError:
                    _LOGGER.error("Bluetooth interface hci%i is not available", hci)
        else:
            # Configuration of BT interface with mac address
            conf_bt_interfaces = [x.upper() for x in CONFIG_YAML[CONF_BT_INTERFACE]]
            for bt_mac in conf_bt_interfaces:
                try:
                    hci = list(BT_INTERFACES.keys())[
                        list(BT_INTERFACES.values()).index(bt_mac)
                    ]
                    hci_list.append(int(hci))
                    bt_mac_list.append(str(bt_mac))
                except ValueError:
                    _LOGGER.error(
                        "Bluetooth interface with MAC address %s is not available",
                        bt_mac,
                    )

    if not hci_list:
        # Fall back in case no hci interfaces are added
        default_hci = list(BT_INTERFACES.keys())[
            list(BT_INTERFACES.values()).index(DEFAULT_BT_INTERFACE)
        ]
        hci_list.append(int(default_hci))
        bt_mac_list.append(str(DEFAULT_BT_INTERFACE))
        _LOGGER.warning(
            "No configured Bluetooth interfaces was found, using default interface instead"
        )

    config[CONF_HCI_INTERFACE] = hci_list
    config[CONF_BT_INTERFACE] = bt_mac_list

    hass.config_entries.async_update_entry(config_entry, data={}, options=config)

    _LOGGER.debug("async_setup_entry: %s", config)

    UPDATE_UNLISTENER = config_entry.add_update_listener(_async_update_listener)

    _LOGGER.debug("HCI interface is %s", config[CONF_HCI_INTERFACE])

    blemonitor = BLEmonitor(config)
    hass.bus.async_listen(EVENT_HOMEASSISTANT_STOP, blemonitor.shutdown_handler)
    blemonitor.start()

    hass.data[DOMAIN] = {}
    hass.data[DOMAIN]["blemonitor"] = blemonitor
    hass.data[DOMAIN]["config_entry_id"] = config_entry.entry_id

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, component)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    _LOGGER.debug("async_unload_entry: %s", entry)

    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    blemonitor: BLEmonitor = hass.data[DOMAIN]["blemonitor"]
    if blemonitor:
        blemonitor.stop()

    return unload_ok


async def async_migrate_entry(hass, config_entry):
    """Migrate config entry to new version."""
    if config_entry.version == 1:
        options = dict(config_entry.options)
        hci_list = options.get(CONF_HCI_INTERFACE)
        bt_mac_list = []
        for hci in hci_list:
            try:
                bt_mac = BT_INTERFACES.get(hci)
                if bt_mac:
                    bt_mac_list.append(str(bt_mac))
                else:
                    _LOGGER.error(
                        "HCI%i is not migrated, check the BLE monitor options", hci
                    )
            except ValueError:
                _LOGGER.error(
                    "HCI%i is not migrated, check the BLE monitor options", hci
                )
        if not bt_mac_list:
            # Fall back in case no hci interfaces are added
            bt_mac_list.append(str(DEFAULT_BT_INTERFACE))
            _LOGGER.warning(
                "Migration of hci interface to Bluetooth mac address failed, using default MAC address"
            )
        options[CONF_BT_INTERFACE] = bt_mac_list

        config_entry.version = 2
        hass.config_entries.async_update_entry(config_entry, options=options)
        _LOGGER.info("Migrated config entry to version %d", config_entry.version)
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_cleanup_entries_service(hass: HomeAssistant, data):
    """Remove orphaned entries from device and entity registries."""
    _LOGGER.debug("async_cleanup_entries_service")

    entity_registry = await hass.helpers.entity_registry.async_get_registry()
    device_registry = await hass.helpers.device_registry.async_get_registry()
    config_entry_id = hass.data[DOMAIN]["config_entry_id"]

    devices_to_be_removed = [
        entry.id
        for entry in device_registry.devices.values()
        if config_entry_id in entry.config_entries
    ]

    # Remove devices that don't belong to any entity
    for device_id in devices_to_be_removed:
        if len(async_entries_for_device(entity_registry, device_id)) == 0:
            device_registry.async_remove_device(device_id)
            _LOGGER.debug("device %s will be deleted", device_id)


class BLEmonitor:
    """BLE scanner."""

    def __init__(self, config):
        """Init."""
        self.dataqueue = {
            "binary": janus.Queue(),
            "measuring": janus.Queue(),
            "tracker": janus.Queue(),
        }
        self.config = config
        self.dumpthread = None

    def shutdown_handler(self, event):
        """Run homeassistant_stop event handler."""
        _LOGGER.debug("Shutdown event fired: %s", event)
        self.stop()

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
        self.dataqueue["binary"].sync_q.put_nowait(None)
        self.dataqueue["measuring"].sync_q.put_nowait(None)
        self.dataqueue["tracker"].sync_q.put_nowait(None)
        result = True
        if self.dumpthread is None:
            _LOGGER.debug("BLE monitor stopped")
            return True
        if self.dumpthread.is_alive():
            self.dumpthread.join()
            if self.dumpthread.is_alive():
                result = False
                _LOGGER.error(
                    "Waiting for the HCIdump thread to finish took too long! (>10s)"
                )
        _LOGGER.debug("BLE monitor stopped")
        return result

    def restart(self):
        """Restart scanning."""
        if self.dumpthread.is_alive():
            self.dumpthread.restart()
        else:
            self.start()


class HCIdump(Thread):
    """Mimic deprecated hcidump tool."""

    def __init__(self, config, dataqueue):
        """Initiate HCIdump thread."""
        Thread.__init__(self)
        _LOGGER.debug("HCIdump thread: Init")
        self.dataqueue_bin = dataqueue["binary"]
        self.dataqueue_meas = dataqueue["measuring"]
        self.dataqueue_tracker = dataqueue["tracker"]
        self._event_loop = None
        self._joining = False
        self.evt_cnt = 0
        self.config = config
        self._interfaces = config[CONF_HCI_INTERFACE]
        self._active = int(config[CONF_ACTIVE_SCAN] is True)
        self.discovery = True
        self.filter_duplicates = True
        self.aeskeys = {}
        self.sensor_whitelist = []
        self.tracker_whitelist = []
        self.report_unknown = False
        if self.config[CONF_REPORT_UNKNOWN]:
            self.report_unknown = self.config[CONF_REPORT_UNKNOWN]
            _LOGGER.info(
                "Attention! Option report_unknown is enabled for %s sensors, be ready for a huge output",
                self.report_unknown,
            )
        # prepare device:key lists to speedup parser
        if self.config[CONF_DEVICES]:
            for device in self.config[CONF_DEVICES]:
                if CONF_ENCRYPTION_KEY in device and device[CONF_ENCRYPTION_KEY]:
                    p_mac = bytes.fromhex(device["mac"].replace(":", "").lower())
                    p_key = bytes.fromhex(device[CONF_ENCRYPTION_KEY].lower())
                    self.aeskeys[p_mac] = p_key
                else:
                    continue
        _LOGGER.debug("%s encryptors mac:key pairs loaded", len(self.aeskeys))

        # prepare sensor whitelist to speedup parser
        if (
            isinstance(self.config[CONF_DISCOVERY], bool)
            and self.config[CONF_DISCOVERY] is False
        ):
            self.discovery = False
            if self.config[CONF_DEVICES]:
                for device in self.config[CONF_DEVICES]:
                    self.sensor_whitelist.append(device["mac"])

        # remove duplicates from sensor whitelist
        self.sensor_whitelist = list(dict.fromkeys(self.sensor_whitelist))
        _LOGGER.debug(
            "sensor whitelist: [%s]", ", ".join(self.sensor_whitelist).upper()
        )
        for i, mac in enumerate(self.sensor_whitelist):
            self.sensor_whitelist[i] = bytes.fromhex(mac.replace(":", ""))
        _LOGGER.debug("%s sensor whitelist item(s) loaded", len(self.sensor_whitelist))

        # prepare device tracker list to speedup parser
        if self.config[CONF_DEVICES]:
            for device in self.config[CONF_DEVICES]:
                if CONF_DEVICE_TRACK in device and device[CONF_DEVICE_TRACK]:
                    track_mac = bytes.fromhex(device["mac"].replace(":", ""))
                    self.tracker_whitelist.append(track_mac)
                else:
                    continue
        _LOGGER.debug(
            "%s device tracker(s) being monitored", len(self.tracker_whitelist)
        )

        # prepare the ble_parser
        self.ble_parser = BleParser(
            report_unknown=self.report_unknown,
            discovery=self.discovery,
            filter_duplicates=self.filter_duplicates,
            sensor_whitelist=self.sensor_whitelist,
            tracker_whitelist=self.tracker_whitelist,
            aeskeys=self.aeskeys,
        )

    def process_hci_events(self, data):
        """Parse HCI events."""
        self.evt_cnt += 1
        if len(data) < 12:
            return
        sensor_msg, tracker_msg = self.ble_parser.parse_data(data)
        if sensor_msg:
            measurements = list(sensor_msg.keys())
            device_type = sensor_msg["type"]
            sensor_list = (
                MEASUREMENT_DICT[device_type][0] + MEASUREMENT_DICT[device_type][1]
            )
            binary_list = MEASUREMENT_DICT[device_type][2] + ["battery"]
            measuring = any(x in measurements for x in sensor_list)
            binary = any(x in measurements for x in binary_list)
            if binary == measuring:
                self.dataqueue_bin.sync_q.put_nowait(sensor_msg)
                self.dataqueue_meas.sync_q.put_nowait(sensor_msg)
            else:
                if binary is True:
                    self.dataqueue_bin.sync_q.put_nowait(sensor_msg)
                if measuring is True:
                    self.dataqueue_meas.sync_q.put_nowait(sensor_msg)
        if tracker_msg:
            self.dataqueue_tracker.sync_q.put_nowait(tracker_msg)

    def run(self):
        """Run HCIdump thread."""
        while True:
            _LOGGER.debug("HCIdump thread: Run")
            mysocket = {}
            fac = {}
            conn = {}
            btctrl = {}
            if self._event_loop is None:
                self._event_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._event_loop)
            for hci in self._interfaces:
                try:
                    mysocket[hci] = aiobs.create_bt_socket(hci)
                except OSError as error:
                    _LOGGER.error("HCIdump thread: OS error (hci%i): %s", hci, error)
                else:
                    fac[hci] = getattr(
                        self._event_loop, "_create_connection_transport"
                    )(mysocket[hci], aiobs.BLEScanRequester, None, None)
                    conn[hci], btctrl[hci] = self._event_loop.run_until_complete(
                        fac[hci]
                    )
                    _LOGGER.debug("HCIdump thread: connected to hci%i", hci)
                    btctrl[hci].process = self.process_hci_events
                    try:
                        self._event_loop.run_until_complete(
                            btctrl[hci].send_scan_request(self._active)
                        )
                    except RuntimeError as error:
                        _LOGGER.error(
                            "HCIdump thread: Runtime error while sending scan request on hci%i: %s",
                            hci,
                            error,
                        )
            _LOGGER.debug("HCIdump thread: start main event_loop")
            try:
                self._event_loop.run_forever()
            finally:
                _LOGGER.debug("HCIdump thread: main event_loop stopped, finishing")
                for hci in self._interfaces:
                    try:
                        self._event_loop.run_until_complete(
                            btctrl[hci].stop_scan_request()
                        )
                    except RuntimeError as error:
                        _LOGGER.error(
                            "HCIdump thread: Runtime error while stop scan request on hci%i: %s",
                            hci,
                            error,
                        )
                    except KeyError:
                        _LOGGER.debug(
                            "HCIdump thread: Key error while stop scan request on hci%i",
                            hci,
                        )
                    try:
                        conn[hci].close()
                    except KeyError:
                        _LOGGER.debug(
                            "HCIdump thread: Key error while closing connection on hci%i",
                            hci,
                        )
                self._event_loop.run_until_complete(asyncio.sleep(0))
            if self._joining is True:
                break
            _LOGGER.debug("HCIdump thread: Scanning will be restarted")
            _LOGGER.debug("%i HCI events processed for previous period", self.evt_cnt)
            self.evt_cnt = 0
        self._event_loop.close()
        _LOGGER.debug("HCIdump thread: Run finished")

    def join(self, timeout=10):
        """Join HCIdump thread."""
        _LOGGER.debug("HCIdump thread: joining")
        self._joining = True
        try:
            self._event_loop.call_soon_threadsafe(self._event_loop.stop)
        except AttributeError as error:
            _LOGGER.debug("%s", error)
        finally:
            Thread.join(self, timeout)
            _LOGGER.debug("HCIdump thread: joined")

    def restart(self):
        """Restarting scanner."""
        try:
            self._event_loop.call_soon_threadsafe(self._event_loop.stop)
        except AttributeError as error:
            _LOGGER.debug("%s", error)
