"""Constants for the Passive BLE monitor integration."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_LIGHT,
    DEVICE_CLASS_MOISTURE,
    DEVICE_CLASS_MOTION,
    DEVICE_CLASS_OPENING,
    DEVICE_CLASS_SMOKE,
    DEVICE_CLASS_LOCK,
    BinarySensorEntityDescription,
)
from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
    SensorEntityDescription,
)
from homeassistant.const import (
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_ILLUMINANCE,
    DEVICE_CLASS_PRESSURE,
    DEVICE_CLASS_SIGNAL_STRENGTH,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_VOLTAGE,
    CONDUCTIVITY,
    CONCENTRATION_MILLIGRAMS_PER_CUBIC_METER,
    ELECTRIC_POTENTIAL_VOLT,
    ENERGY_KILO_WATT_HOUR,
    LIGHT_LUX,
    MASS_KILOGRAMS,
    PERCENTAGE,
    POWER_KILO_WATT,
    PRESSURE_HPA,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    TEMP_CELSIUS,
    VOLUME_LITERS,
)

DOMAIN = "ble_monitor"
PLATFORMS = ["binary_sensor", "device_tracker", "sensor"]

# Configuration options
CONF_DECIMALS = "decimals"
CONF_PERIOD = "period"
CONF_LOG_SPIKES = "log_spikes"
CONF_USE_MEDIAN = "use_median"
CONF_ACTIVE_SCAN = "active_scan"
CONF_HCI_INTERFACE = "hci_interface"
CONF_BT_INTERFACE = "bt_interface"
CONF_BATT_ENTITIES = "batt_entities"
CONF_REPORT_UNKNOWN = "report_unknown"
CONF_RESTORE_STATE = "restore_state"
CONF_ENCRYPTION_KEY = "encryption_key"
CONF_DEVICE_DECIMALS = "decimals"
CONF_DEVICE_USE_MEDIAN = "use_median"
CONF_DEVICE_RESTORE_STATE = "restore_state"
CONF_DEVICE_RESET_TIMER = "reset_timer"
CONF_DEVICE_TRACK = "track_device"
CONF_DEVICE_TRACKER_SCAN_INTERVAL = "tracker_scan_interval"
CONF_DEVICE_TRACKER_CONSIDER_HOME = "consider_home"
CONF_DEVICE_DELETE_DEVICE = "delete device"
CONFIG_IS_FLOW = "is_flow"

SERVICE_CLEANUP_ENTRIES = "cleanup_entries"

# Default values for configuration options
DEFAULT_DECIMALS = 1
DEFAULT_PERIOD = 60
DEFAULT_LOG_SPIKES = False
DEFAULT_USE_MEDIAN = False
DEFAULT_ACTIVE_SCAN = False
DEFAULT_BATT_ENTITIES = True
DEFAULT_REPORT_UNKNOWN = False
DEFAULT_DISCOVERY = True
DEFAULT_RESTORE_STATE = False
DEFAULT_DEVICE_DECIMALS = "default"
DEFAULT_DEVICE_USE_MEDIAN = "default"
DEFAULT_DEVICE_RESTORE_STATE = "default"
DEFAULT_DEVICE_RESET_TIMER = 35
DEFAULT_DEVICE_TRACKER_SCAN_INTERVAL = 20
DEFAULT_DEVICE_TRACKER_CONSIDER_HOME = 180
DEFAULT_DEVICE_TRACK = False
DEFAULT_DEVICE_DELETE_DEVICE = False

# regex constants for configuration schema
MAC_REGEX = "(?i)^(?:[0-9A-F]{2}[:]){5}(?:[0-9A-F]{2})$"
# MiBeacon V2/V3 uses 24 character long key
AES128KEY24_REGEX = "(?i)^[A-F0-9]{24}$"
# MiBeacon V4/V5 uses 32 character long key
AES128KEY32_REGEX = "(?i)^[A-F0-9]{32}$"

"""Fixed constants."""

# Sensor measurement limits to exclude erroneous spikes from the results (temperature in °C)
CONF_TMIN = -40.0
CONF_TMAX = 60.0
CONF_TMIN_KETTLES = -20.0
CONF_TMAX_KETTLES = 120.0
CONF_HMIN = 0.0
CONF_HMAX = 99.9

# Sensor entity description
@dataclass
class BLEMonitorRequiredKeysMixin:
    """Mixin for required keys."""

    sensor_class: str
    unique_id: str

@dataclass
class BLEMonitorSensorEntityDescription(
    SensorEntityDescription, BLEMonitorRequiredKeysMixin
):
    """Describes BLE Monitor sensor entity."""


@dataclass
class BLEMonitorBinarySensorEntityDescription(
    BinarySensorEntityDescription, BLEMonitorRequiredKeysMixin
):
    """Describes BLE Monitor binary sensor entity."""


BINARY_SENSOR_TYPES: tuple[BLEMonitorBinarySensorEntityDescription, ...] = (
    BLEMonitorBinarySensorEntityDescription(
        key="remote single press",
        sensor_class="BaseBinarySensor",
        name="ble remote binary single press",
        unique_id="rb_single_press_",
        device_class=None,
        force_update=True,
    ),
    BLEMonitorBinarySensorEntityDescription(
        key="remote long press",
        sensor_class="BaseBinarySensor",
        name="ble remote binary long press",
        unique_id="rb_long_press_",
        device_class=None,
        force_update=True,
    ),
    BLEMonitorBinarySensorEntityDescription(
        key="switch",
        sensor_class="BaseBinarySensor",
        name="ble switch",
        unique_id="sw_",
        device_class=DEVICE_CLASS_POWER,
        force_update=True,
    ),
    BLEMonitorBinarySensorEntityDescription(
        key="opening",
        sensor_class="BaseBinarySensor",
        name="ble opening",
        unique_id="op_",
        device_class=DEVICE_CLASS_OPENING,
        force_update=False,
    ),
    BLEMonitorBinarySensorEntityDescription(
        key="light",
        sensor_class="BaseBinarySensor",
        name="ble light",
        unique_id="lt_",
        device_class=DEVICE_CLASS_LIGHT,
        force_update=False,
    ),
    BLEMonitorBinarySensorEntityDescription(
        key="moisture",
        sensor_class="BaseBinarySensor",
        name="ble moisture",
        unique_id="mo_",
        device_class=DEVICE_CLASS_MOISTURE,
        force_update=False,
    ),
    BLEMonitorBinarySensorEntityDescription(
        key="motion",
        sensor_class="MotionBinarySensor",
        name="ble motion",
        unique_id="mn_",
        device_class=DEVICE_CLASS_MOTION,
        force_update=False,
    ),
    BLEMonitorBinarySensorEntityDescription(
        key="weight removed",
        sensor_class="BaseBinarySensor",
        name="ble weight removed",
        icon="mdi:weight",
        unique_id="wr_",
        device_class=None,
        force_update=False,
    ),
    BLEMonitorBinarySensorEntityDescription(
        key="smoke detector",
        sensor_class="BaseBinarySensor",
        name="ble smoke detector",
        unique_id="sd_",
        device_class=DEVICE_CLASS_SMOKE,
        force_update=False,
    ),
    BLEMonitorBinarySensorEntityDescription(
        key="fingerprint",
        sensor_class="BaseBinarySensor",
        name="ble fingerprint",
        icon="mdi:fingerprint",
        unique_id="fp_",
        device_class=None,
        force_update=True,
    ),
    BLEMonitorBinarySensorEntityDescription(
        key="lock",
        sensor_class="BaseBinarySensor",
        name="ble lock",
        unique_id="lock_",
        device_class=DEVICE_CLASS_LOCK,
        force_update=True,
    ),
    BLEMonitorBinarySensorEntityDescription(
        key="toothbrush",
        sensor_class="BaseBinarySensor",
        name="ble toothbrush",
        unique_id="tb_",
        icon="mdi:toothbrush-electric",
        device_class=DEVICE_CLASS_POWER,
        force_update=False,
    ),
)


SENSOR_TYPES: tuple[BLEMonitorSensorEntityDescription, ...] = (
    BLEMonitorSensorEntityDescription(
        key="temperature",
        sensor_class="TemperatureSensor",
        name="ble temperature",
        unique_id="t_",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=DEVICE_CLASS_TEMPERATURE,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="temperature outdoor",
        sensor_class="TemperatureSensor",
        name="ble temperature outdoor",
        unique_id="t_outdoor_",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=DEVICE_CLASS_TEMPERATURE,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="humidity",
        sensor_class="HumiditySensor",
        name="ble humidity",
        unique_id="h_",
        native_unit_of_measurement=PERCENTAGE,
        device_class=DEVICE_CLASS_HUMIDITY,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="humidity outdoor",
        sensor_class="HumiditySensor",
        name="ble temperature outdoor",
        unique_id="h_outdoor_",
        native_unit_of_measurement=PERCENTAGE,
        device_class=DEVICE_CLASS_HUMIDITY,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="moisture",
        sensor_class="MeasuringSensor",
        name="ble moisture",
        unique_id="m_",
        native_unit_of_measurement=PERCENTAGE,
        device_class=DEVICE_CLASS_HUMIDITY,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="pressure",
        sensor_class="MeasuringSensor",
        name="ble pressure",
        unique_id="p_",
        native_unit_of_measurement=PRESSURE_HPA,
        device_class=DEVICE_CLASS_PRESSURE,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="conductivity",
        sensor_class="MeasuringSensor",
        name="ble conductivity",
        unique_id="c_",
        icon="mdi:lightning-bolt-circle",
        native_unit_of_measurement=CONDUCTIVITY,
        device_class=None,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="illuminance",
        sensor_class="MeasuringSensor",
        name="ble illuminance",
        unique_id="l_",
        device_class=DEVICE_CLASS_ILLUMINANCE,
        native_unit_of_measurement=LIGHT_LUX,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="formaldehyde",
        sensor_class="MeasuringSensor",
        name="ble formaldehyde",
        unique_id="f_",
        icon="mdi:chemical-weapon",
        native_unit_of_measurement=CONCENTRATION_MILLIGRAMS_PER_CUBIC_METER,
        device_class=None,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="dewpoint",
        sensor_class="MeasuringSensor",
        name="ble dewpoint",
        unique_id="d_",
        icon="mdi:water",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=DEVICE_CLASS_TEMPERATURE,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="rssi",
        sensor_class="MeasuringSensor",
        name="ble rssi",
        unique_id="rssi_",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=DEVICE_CLASS_SIGNAL_STRENGTH,
        state_class=STATE_CLASS_MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    BLEMonitorSensorEntityDescription(
        key="battery",
        sensor_class="BatterySensor",
        name="ble battery",
        unique_id="batt_",
        native_unit_of_measurement=PERCENTAGE,
        device_class=DEVICE_CLASS_BATTERY,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="voltage",
        sensor_class="MeasuringSensor",
        name="ble voltage",
        unique_id="v_",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=DEVICE_CLASS_VOLTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="consumable",
        sensor_class="InstantUpdateSensor",
        name="ble consumable",
        unique_id="cn_",
        icon="mdi:recycle-variant",
        native_unit_of_measurement=PERCENTAGE,
        device_class=None,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="acceleration",
        sensor_class="AccelerationSensor",
        name="ble acceleration",
        unique_id="ac_",
        icon="mdi:axis-arrow",
        native_unit_of_measurement="mG",
        device_class=None,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="weight",
        sensor_class="WeightSensor",
        name="ble weight",
        unique_id="w_",
        icon="mdi:scale-bathroom",
        native_unit_of_measurement=MASS_KILOGRAMS,
        device_class=None,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="non-stabilized weight",
        sensor_class="WeightSensor",
        name="ble non-stabilized weight",
        unique_id="nw_",
        icon="mdi:scale-bathroom",
        native_unit_of_measurement=MASS_KILOGRAMS,
        device_class=None,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="impedance",
        sensor_class="InstantUpdateSensor",
        name="ble impedance",
        unique_id="im_",
        icon="mdi:omega",
        native_unit_of_measurement="Ohm",
        device_class=None,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="energy",
        sensor_class="EnergySensor",
        name="ble energy",
        unique_id="e_",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="power",
        sensor_class="PowerSensor",
        name="ble power",
        unique_id="pow_",
        native_unit_of_measurement=POWER_KILO_WATT,
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="button",
        sensor_class="ButtonSensor",
        name="ble button",
        unique_id="bu_",
        icon="mdi:gesture-tap-button",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=None,
    ),
    BLEMonitorSensorEntityDescription(
        key="dimmer",
        sensor_class="DimmerSensor",
        name="ble dimmer",
        unique_id="di_",
        icon="mdi:rotate-right",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=None,
    ),
    BLEMonitorSensorEntityDescription(
        key="one btn switch",
        sensor_class="SwitchSensor",
        name="ble one button switch",
        unique_id="switch_",
        icon="mdi:gesture-tap-button",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=None,
    ),
    BLEMonitorSensorEntityDescription(
        key="two btn switch left",
        sensor_class="SwitchSensor",
        name="ble two button switch left",
        unique_id="left_switch_",
        icon="mdi:gesture-tap-button",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=None,
    ),
    BLEMonitorSensorEntityDescription(
        key="two btn switch right",
        sensor_class="SwitchSensor",
        name="ble two button switch right",
        unique_id="right_switch_",
        icon="mdi:gesture-tap-button",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=None,
    ),
    BLEMonitorSensorEntityDescription(
        key="three btn switch left",
        sensor_class="SwitchSensor",
        name="ble three button switch left",
        unique_id="left_switch_",
        icon="mdi:gesture-tap-button",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=None,
    ),
    BLEMonitorSensorEntityDescription(
        key="three btn switch middle",
        sensor_class="SwitchSensor",
        name="ble three button switch middle",
        unique_id="middle_switch_",
        icon="mdi:gesture-tap-button",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=None,
    ),
    BLEMonitorSensorEntityDescription(
        key="three btn switch right",
        sensor_class="SwitchSensor",
        name="ble three button switch right",
        unique_id="right_switch_",
        icon="mdi:gesture-tap-button",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=None,
    ),
    BLEMonitorSensorEntityDescription(
        key="remote",
        sensor_class="BaseRemoteSensor",
        name="ble remote",
        unique_id="re_",
        icon="mdi:remote",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=None,
    ),
    BLEMonitorSensorEntityDescription(
        key="fan remote",
        sensor_class="BaseRemoteSensor",
        name="ble fan remote",
        unique_id="fa_",
        icon="mdi:remote",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=None,
    ),
    BLEMonitorSensorEntityDescription(
        key="ventilator fan remote",
        sensor_class="BaseRemoteSensor",
        name="ble ventilator fan remote",
        unique_id="fr_",
        icon="mdi:remote",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=None,
    ),
    BLEMonitorSensorEntityDescription(
        key="bathroom heater remote",
        sensor_class="BaseRemoteSensor",
        name="ble bathroom heater remote",
        unique_id="bh_",
        icon="mdi:remote",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=None,
    ),
    BLEMonitorSensorEntityDescription(
        key="volume dispensed port 1",
        sensor_class="VolumeDispensedSensor",
        name="ble volume dispensed port 1",
        unique_id="vd1_",
        icon="mdi:keg",
        native_unit_of_measurement=VOLUME_LITERS,
        device_class=None,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="volume dispensed port 2",
        sensor_class="VolumeDispensedSensor",
        name="ble volume dispensed port 2",
        unique_id="vd2_",
        icon="mdi:keg",
        native_unit_of_measurement=VOLUME_LITERS,
        device_class=None,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
)


# Dictionary with supported sensors
# Format {device: [averaging sensor list], [instantly updating sensor list],[binary sensor list]}:
# - [averaging sensor list]:            sensors that update the state after avering of the data
# - [instantly updating sensor list]:   sensors that update the state instantly after new data
# - [binary sensor list]:               binary sensors
MEASUREMENT_DICT = {
    'LYWSDCGQ'                : [["temperature", "humidity", "battery", "rssi"], [], []],
    'LYWSD02'                 : [["temperature", "humidity", "battery", "rssi"], [], []],
    'LYWSD03MMC'              : [["temperature", "humidity", "battery", "voltage", "rssi"], [], []],
    'HHCCJCY01'               : [["temperature", "moisture", "conductivity", "illuminance", "rssi"], [], []],
    'GCLS002'                 : [["temperature", "moisture", "conductivity", "illuminance", "rssi"], [], []],
    'HHCCPOT002'              : [["moisture", "conductivity", "rssi"], [], []],
    'WX08ZM'                  : [["consumable", "battery", "rssi"], [], ["switch"]],
    'MCCGQ02HL'               : [["battery", "rssi"], [], ["opening", "light"]],
    'YM-K1501'                : [["rssi"], ["temperature"], ["switch"]],
    'YM-K1501EU'              : [["rssi"], ["temperature"], ["switch"]],
    'V-SK152'                 : [["rssi"], ["temperature"], ["switch"]],
    'SJWS01LM'                : [["battery", "rssi"], [], ["moisture"]],
    'MJYD02YL'                : [["battery", "rssi"], [], ["light", "motion"]],
    'MUE4094RT'               : [["rssi"], [], ["motion"]],
    'RTCGQ02LM'               : [["battery", "rssi"], ["button"], ["light", "motion"]],
    'MMC-T201-1'              : [["temperature", "battery", "rssi"], [], []],
    'M1S-T500'                : [["battery", "rssi"], [], ["toothbrush"]],
    'ZNMS16LM'                : [["battery", "rssi"], [], ["lock", "fingerprint"]],
    'ZNMS17LM'                : [["battery", "rssi"], [], ["lock", "fingerprint"]],
    'CGC1'                    : [["temperature", "humidity", "battery", "rssi"], [], []],
    'CGD1'                    : [["temperature", "humidity", "battery", "rssi"], [], []],
    'CGDK2'                   : [["temperature", "humidity", "battery", "rssi"], [], []],
    'CGG1'                    : [["temperature", "humidity", "battery", "rssi"], [], []],
    'CGG1-ENCRYPTED'          : [["temperature", "humidity", "battery", "rssi"], [], []],
    'CGH1'                    : [["battery", "rssi"], [], ["opening"]],
    'CGP1W'                   : [["temperature", "humidity", "battery", "pressure", "rssi"], [], []],
    'CGPR1'                   : [["illuminance", "battery", "rssi"], [], ["motion"]],
    'MHO-C401'                : [["temperature", "humidity", "battery", "rssi"], [], []],
    'MHO-C303'                : [["temperature", "humidity", "battery", "rssi"], [], []],
    'JQJCY01YM'               : [["temperature", "humidity", "battery", "formaldehyde", "rssi"], [], []],
    'JTYJGD03MI'              : [["rssi"], ["button", "battery"], ["smoke detector"]],
    'K9B-1BTN'                : [["rssi"], ["one btn switch"], []],
    'K9B-2BTN'                : [["rssi"], ["two btn switch left", "two btn switch right"], []],
    'K9B-3BTN'                : [["rssi"], ["three btn switch left", "three btn switch middle", "three btn switch right"], []],
    'YLAI003'                 : [["rssi"], ["button", "battery"], []],
    'YLYK01YL'                : [["rssi"], ["remote"], ["remote single press", "remote long press"]],
    'YLYK01YL-FANCL'          : [["rssi"], ["fan remote"], []],
    'YLYK01YL-VENFAN'         : [["rssi"], ["ventilator fan remote"], []],
    'YLYB01YL-BHFRC'          : [["rssi"], ["bathroom heater remote"], []],
    'YLKG07YL/YLKG08YL'       : [["rssi"], ["dimmer"], []],
    'ATC'                     : [["temperature", "humidity", "battery", "voltage", "rssi"], [], []],
    'Mi Scale V1'             : [["rssi"], ["weight", "non-stabilized weight"], ["weight removed"]],
    'Mi Scale V2'             : [["rssi"], ["weight", "non-stabilized weight", "impedance"], ["weight removed"]],
    'Kegtron KT-100'          : [["rssi"], ["volume dispensed port 1"], []],
    'Kegtron KT-200'          : [["rssi"], ["volume dispensed port 1", "volume dispensed port 2"], []],
    'Smart hygrometer'        : [["temperature", "humidity", "battery", "voltage", "rssi"], [], []],
    'Lanyard/mini hygrometer' : [["temperature", "humidity", "battery", "voltage", "rssi"], [], []],
    'T201'                    : [["temperature", "humidity", "battery", "voltage", "rssi"], [], []],
    'H5072/H5075'             : [["temperature", "humidity", "battery", "rssi"], [], []],
    'H5101/H5102/H5177'       : [["temperature", "humidity", "battery", "rssi"], [], []],
    'H5051'                   : [["temperature", "humidity", "battery", "rssi"], [], []],
    'H5074'                   : [["temperature", "humidity", "battery", "rssi"], [], []],
    'H5178'                   : [["temperature", "temperature outdoor", "humidity", "humidity outdoor", "battery", "rssi"], [], []],
    'H5179'                   : [["temperature", "humidity", "battery", "rssi"], [], []],
    'Ruuvitag'                : [["temperature", "humidity", "pressure", "battery", "voltage", "rssi"], ["acceleration"], ["motion"]],
    'iNode Energy Meter'      : [["battery", "voltage", "rssi"], ["energy", "power"], []],
    'Blue Puck T'             : [["temperature", "rssi"], [], []],
    'Blue Coin T'             : [["temperature", "rssi"], [], []],
    'Blue Puck RHT'           : [["temperature", "humidity", "rssi"], [], []],
    'HTP.xw'                  : [["temperature", "humidity", "pressure", "rssi"], [], []],
    'HT.w'                    : [["temperature", "humidity", "pressure", "rssi"], [], []],
    'Moat S2'                 : [["temperature", "humidity", "battery", "rssi"], [], []],
    'Tempo Disc THD'          : [["temperature", "humidity", "dewpoint", "battery", "rssi"], [], []],
    'Tempo Disc THPD'         : [["temperature", "humidity", "pressure", "battery", "rssi"], [], []],
}

KETTLES = ('YM-K1501', 'YM-K1501EU', 'V-SK152')

# Sensor manufacturer dictionary
MANUFACTURER_DICT = {
    'LYWSDCGQ'                : 'Xiaomi',
    'LYWSD02'                 : 'Xiaomi',
    'LYWSD03MMC'              : 'Xiaomi',
    'HHCCJCY01'               : 'Xiaomi',
    'GCLS002'                 : 'Xiaomi',
    'HHCCPOT002'              : 'Xiaomi',
    'WX08ZM'                  : 'Xiaomi',
    'MCCGQ02HL'               : 'Xiaomi',
    'YM-K1501'                : 'Xiaomi',
    'YM-K1501EU'              : 'Xiaomi',
    'V-SK152'                 : 'Viomi',
    'SJWS01LM'                : 'Xiaomi',
    'MJYD02YL'                : 'Xiaomi',
    'MUE4094RT'               : 'Xiaomi',
    'RTCGQ02LM'               : 'Xiaomi',
    'MMC-T201-1'              : 'Xiaomi',
    'M1S-T500'                : 'Xiaomi Soocas',
    'ZNMS16LM'                : 'Xiaomi Aqara',
    'ZNMS17LM'                : 'Xiaomi Aqara',
    'CGC1'                    : 'Qingping',
    'CGD1'                    : 'Qingping',
    'CGDK2'                   : 'Qingping',
    'CGG1'                    : 'Qingping',
    'CGG1-ENCRYPTED'          : 'Qingping',
    'CGH1'                    : 'Qingping',
    'CGP1W'                   : 'Qingping',
    'CGPR1'                   : 'Qingping',
    'MHO-C401'                : 'Miaomiaoce',
    'MHO-C303'                : 'Miaomiaoce',
    'JQJCY01YM'               : 'Honeywell',
    'JTYJGD03MI'              : 'Honeywell',
    'YLAI003'                 : 'Yeelight',
    'YLYK01YL'                : 'Yeelight',
    'YLYK01YL-FANCL'          : 'Yeelight',
    'YLYK01YL-VENFAN'         : 'Yeelight',
    'YLYB01YL-BHFRC'          : 'Yeelight',
    'YLKG07YL/YLKG08YL'       : 'Yeelight',
    'K9B-1BTN'                : 'Linptech',
    'K9B-2BTN'                : 'Linptech',
    'K9B-3BTN'                : 'Linptech',
    'ATC'                     : 'ATC',
    'Mi Scale V1'             : 'Xiaomi',
    'Mi Scale V2'             : 'Xiaomi',
    'Kegtron KT-100'          : 'Kegtron',
    'Kegtron KT-200'          : 'Kegtron',
    'Smart hygrometer'        : 'Thermoplus',
    'Lanyard/mini hygrometer' : 'Thermoplus',
    'T201'                    : 'Brifit',
    'H5072/H5075'             : 'Govee',
    'H5101/H5102/H5177'       : 'Govee',
    'H5051'                   : 'Govee',
    'H5074'                   : 'Govee',
    'H5178'                   : 'Govee',
    'H5179'                   : 'Govee',
    'Ruuvitag'                : 'Ruuvitag',
    'iNode Energy Meter'      : 'iNode',
    'Blue Puck T'             : 'Teltonika',
    'Blue Coin T'             : 'Teltonika',
    'Blue Puck RHT'           : 'Teltonika',
    'HTP.xw'                  : 'SensorPush',
    'HT.w'                    : 'SensorPush',
    'Moat S2'                 : 'Moat',
    'Tempo Disc THD'          : 'BlueMaestro',
    'Tempo Disc THPD'         : 'BlueMaestro',
}

# Renamed model dictionary
RENAMED_MODEL_DICT = {
    'H5051/H5074': 'H5074'
}
