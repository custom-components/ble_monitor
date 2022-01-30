"""Constants for the Passive BLE monitor integration."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    CONDUCTIVITY,
    CONCENTRATION_MILLIGRAMS_PER_CUBIC_METER,
    ELECTRIC_POTENTIAL_VOLT,
    ENERGY_KILO_WATT_HOUR,
    ENTITY_CATEGORY_DIAGNOSTIC,
    LIGHT_LUX,
    MASS_KILOGRAMS,
    PERCENTAGE,
    POWER_KILO_WATT,
    PRESSURE_HPA,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    TEMP_CELSIUS,
    VOLUME_LITERS,
    Platform,
)

DOMAIN = "ble_monitor"
PLATFORMS = [
    Platform.DEVICE_TRACKER,
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
]

# Configuration options
CONF_BT_AUTO_RESTART = "bt_auto_restart"
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
CONF_DEVICE_ENCRYPTION_KEY = "encryption_key"
CONF_DEVICE_DECIMALS = "decimals"
CONF_DEVICE_USE_MEDIAN = "use_median"
CONF_DEVICE_RESTORE_STATE = "restore_state"
CONF_DEVICE_RESET_TIMER = "reset_timer"
CONF_DEVICE_TRACK = "track_device"
CONF_DEVICE_TRACKER_SCAN_INTERVAL = "tracker_scan_interval"
CONF_DEVICE_TRACKER_CONSIDER_HOME = "consider_home"
CONF_DEVICE_DELETE_DEVICE = "delete device"
CONF_PACKET = "packet"
CONF_GATEWAY_ID = "gateway_id"
CONF_UUID = "uuid"
CONFIG_IS_FLOW = "is_flow"

SERVICE_CLEANUP_ENTRIES = "cleanup_entries"
SERVICE_PARSE_DATA = "parse_data"

# Default values for configuration options
DEFAULT_BT_AUTO_RESTART = False
DEFAULT_DECIMALS = 1
DEFAULT_PERIOD = 60
DEFAULT_LOG_SPIKES = False
DEFAULT_USE_MEDIAN = False
DEFAULT_ACTIVE_SCAN = False
DEFAULT_BATT_ENTITIES = True
DEFAULT_REPORT_UNKNOWN = "Off"
DEFAULT_DISCOVERY = True
DEFAULT_RESTORE_STATE = False
DEFAULT_DEVICE_MAC = ""
DEFAULT_DEVICE_UUID = ""
DEFAULT_DEVICE_ENCRYPTION_KEY = ""
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
CONF_TMAX = 85.0
CONF_TMIN_KETTLES = -20.0
CONF_TMAX_KETTLES = 120.0
CONF_TMIN_PROBES = 0.0
CONF_TMAX_PROBES = 300.0
CONF_HMIN = 0.0
CONF_HMAX = 99.9

# Beacon types


# Sensors with deviating temperature range
KETTLES = ('YM-K1501', 'YM-K1501EU', 'V-SK152')
PROBES = ('iBBQ-2', 'iBBQ-4', 'H5183')

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
        device_class=BinarySensorDeviceClass.POWER,
        force_update=True,
    ),
    BLEMonitorBinarySensorEntityDescription(
        key="opening",
        sensor_class="BaseBinarySensor",
        name="ble opening",
        unique_id="op_",
        device_class=BinarySensorDeviceClass.OPENING,
        force_update=False,
    ),
    BLEMonitorBinarySensorEntityDescription(
        key="light",
        sensor_class="BaseBinarySensor",
        name="ble light",
        unique_id="lt_",
        device_class=BinarySensorDeviceClass.LIGHT,
        force_update=False,
    ),
    BLEMonitorBinarySensorEntityDescription(
        key="moisture",
        sensor_class="BaseBinarySensor",
        name="ble moisture",
        unique_id="mo_",
        device_class=BinarySensorDeviceClass.MOISTURE,
        force_update=False,
    ),
    BLEMonitorBinarySensorEntityDescription(
        key="motion",
        sensor_class="MotionBinarySensor",
        name="ble motion",
        unique_id="mn_",
        device_class=BinarySensorDeviceClass.MOTION,
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
        device_class=BinarySensorDeviceClass.SMOKE,
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
        device_class=BinarySensorDeviceClass.LOCK,
        force_update=True,
    ),
    BLEMonitorBinarySensorEntityDescription(
        key="toothbrush",
        sensor_class="BaseBinarySensor",
        name="ble toothbrush",
        unique_id="tb_",
        icon="mdi:toothbrush-electric",
        device_class=BinarySensorDeviceClass.POWER,
        force_update=False,
    ),
)


SENSOR_TYPES: tuple[BLEMonitorSensorEntityDescription, ...] = (
    BLEMonitorSensorEntityDescription(
        key="mac",
        sensor_class="StateChangedSensor",
        name="ble mac",
        unique_id="mac_",
        icon="mdi:alpha-m-circle-outline",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=None,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    BLEMonitorSensorEntityDescription(
        key="uuid",
        sensor_class="StateChangedSensor",
        name="ble uuid",
        unique_id="uuid_",
        icon="mdi:alpha-u-circle-outline",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=None,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    BLEMonitorSensorEntityDescription(
        key="temperature",
        sensor_class="TemperatureSensor",
        name="ble temperature",
        unique_id="t_",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="cypress temperature",
        sensor_class="TemperatureSensor",
        name="ble cypress temperature",
        unique_id="t_cypress_",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="temperature probe 1",
        sensor_class="TemperatureSensor",
        name="ble temperature probe 1",
        unique_id="t_probe_1_",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="temperature probe 2",
        sensor_class="TemperatureSensor",
        name="ble temperature probe 2",
        unique_id="t_probe_2_",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="temperature probe 3",
        sensor_class="TemperatureSensor",
        name="ble temperature probe 3",
        unique_id="t_probe_3_",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="temperature probe 4",
        sensor_class="TemperatureSensor",
        name="ble temperature probe 4",
        unique_id="t_probe_4_",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="temperature probe 5",
        sensor_class="TemperatureSensor",
        name="ble temperature probe 5",
        unique_id="t_probe_5_",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="temperature probe 6",
        sensor_class="TemperatureSensor",
        name="ble temperature probe 6",
        unique_id="t_probe_6_",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="temperature outdoor",
        sensor_class="TemperatureSensor",
        name="ble temperature outdoor",
        unique_id="t_outdoor_",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="temperature alarm",
        sensor_class="TemperatureSensor",
        name="ble temperature alarm",
        unique_id="t_alarm_",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="humidity",
        sensor_class="HumiditySensor",
        name="ble humidity",
        unique_id="h_",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="cypress humidity",
        sensor_class="HumiditySensor",
        name="ble cypress humidity",
        unique_id="h_cypress_",
        native_unit_of_measurement="RH%",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="humidity outdoor",
        sensor_class="HumiditySensor",
        name="ble humidity outdoor",
        unique_id="h_outdoor_",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="moisture",
        sensor_class="MeasuringSensor",
        name="ble moisture",
        unique_id="m_",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="pressure",
        sensor_class="MeasuringSensor",
        name="ble pressure",
        unique_id="p_",
        native_unit_of_measurement=PRESSURE_HPA,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="conductivity",
        sensor_class="MeasuringSensor",
        name="ble conductivity",
        unique_id="c_",
        icon="mdi:lightning-bolt-circle",
        native_unit_of_measurement=CONDUCTIVITY,
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="illuminance",
        sensor_class="MeasuringSensor",
        name="ble illuminance",
        unique_id="l_",
        device_class=SensorDeviceClass.ILLUMINANCE,
        native_unit_of_measurement=LIGHT_LUX,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="formaldehyde",
        sensor_class="MeasuringSensor",
        name="ble formaldehyde",
        unique_id="f_",
        icon="mdi:chemical-weapon",
        native_unit_of_measurement=CONCENTRATION_MILLIGRAMS_PER_CUBIC_METER,
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="dewpoint",
        sensor_class="MeasuringSensor",
        name="ble dewpoint",
        unique_id="d_",
        icon="mdi:water",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="rssi",
        sensor_class="MeasuringSensor",
        name="ble rssi",
        unique_id="rssi_",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    BLEMonitorSensorEntityDescription(
        key="measured power",
        sensor_class="MeasuringSensor",
        name="ble measured power",
        unique_id="measured_power_",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    BLEMonitorSensorEntityDescription(
        key="major",
        sensor_class="StateChangedSensor",
        name="ble major",
        unique_id="major_",
        icon="mdi:counter",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=None,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    BLEMonitorSensorEntityDescription(
        key="minor",
        sensor_class="StateChangedSensor",
        name="ble minor",
        unique_id="minor_",
        icon="mdi:counter",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=None,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    BLEMonitorSensorEntityDescription(
        key="battery",
        sensor_class="BatterySensor",
        name="ble battery",
        unique_id="batt_",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    BLEMonitorSensorEntityDescription(
        key="voltage",
        sensor_class="MeasuringSensor",
        name="ble voltage",
        unique_id="v_",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    BLEMonitorSensorEntityDescription(
        key="consumable",
        sensor_class="InstantUpdateSensor",
        name="ble consumable",
        unique_id="cn_",
        icon="mdi:recycle-variant",
        native_unit_of_measurement=PERCENTAGE,
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="acceleration",
        sensor_class="AccelerationSensor",
        name="ble acceleration",
        unique_id="ac_",
        icon="mdi:axis-arrow",
        native_unit_of_measurement="mG",
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="weight",
        sensor_class="WeightSensor",
        name="ble weight",
        unique_id="w_",
        icon="mdi:scale-bathroom",
        native_unit_of_measurement=MASS_KILOGRAMS,
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="non-stabilized weight",
        sensor_class="WeightSensor",
        name="ble non-stabilized weight",
        unique_id="nw_",
        icon="mdi:scale-bathroom",
        native_unit_of_measurement=MASS_KILOGRAMS,
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="impedance",
        sensor_class="InstantUpdateSensor",
        name="ble impedance",
        unique_id="im_",
        icon="mdi:omega",
        native_unit_of_measurement="Ohm",
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="energy",
        sensor_class="EnergySensor",
        name="ble energy",
        unique_id="e_",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    BLEMonitorSensorEntityDescription(
        key="power",
        sensor_class="PowerSensor",
        name="ble power",
        unique_id="pow_",
        native_unit_of_measurement=POWER_KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="magnetic field",
        sensor_class="InstantUpdateSensor",
        name="ble magnetic field",
        unique_id="mf_",
        icon="mdi:magnet",
        native_unit_of_measurement="µT",
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="magnetic field direction",
        sensor_class="InstantUpdateSensor",
        name="ble magnetic field direction",
        unique_id="mfd_",
        icon="mdi:compass",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
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
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BLEMonitorSensorEntityDescription(
        key="volume dispensed port 2",
        sensor_class="VolumeDispensedSensor",
        name="ble volume dispensed port 2",
        unique_id="vd2_",
        icon="mdi:keg",
        native_unit_of_measurement=VOLUME_LITERS,
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
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
    'XMWSDJ04MMC'             : [["temperature", "humidity", "battery", "rssi"], [], []],
    'XMMF01JQD'               : [["rssi"], ["button"], []],
    'HHCCJCY01'               : [["temperature", "moisture", "conductivity", "illuminance", "battery", "rssi"], [], []],
    'GCLS002'                 : [["temperature", "moisture", "conductivity", "illuminance", "rssi"], [], []],
    'HHCCPOT002'              : [["moisture", "conductivity", "rssi"], [], []],
    'WX08ZM'                  : [["consumable", "battery", "rssi"], [], ["switch"]],
    'MCCGQ02HL'               : [["battery", "rssi"], [], ["opening", "light"]],
    'YM-K1501'                : [["rssi"], ["temperature"], ["switch"]],
    'YM-K1501EU'              : [["rssi"], ["temperature"], ["switch"]],
    'V-SK152'                 : [["rssi"], ["temperature"], ["switch"]],
    'SJWS01LM'                : [["battery", "rssi"], ["button"], ["moisture"]],
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
    'CGPR1'                   : [["illuminance", "battery", "rssi"], [], ["light", "motion"]],
    'MHO-C401'                : [["temperature", "humidity", "battery", "rssi"], [], []],
    'MHO-C303'                : [["temperature", "humidity", "battery", "rssi"], [], []],
    'JQJCY01YM'               : [["temperature", "humidity", "battery", "formaldehyde", "rssi"], [], []],
    'JTYJGD03MI'              : [["rssi"], ["button", "battery"], ["smoke detector"]],
    'K9B-1BTN'                : [["rssi"], ["one btn switch"], []],
    'K9B-2BTN'                : [["rssi"], ["two btn switch left", "two btn switch right"], []],
    'K9B-3BTN'                : [["rssi"], ["three btn switch left", "three btn switch middle", "three btn switch right"], []],
    'YLAI003'                 : [["rssi", "battery"], ["button"], []],
    'YLYK01YL'                : [["rssi"], ["remote"], ["remote single press", "remote long press"]],
    'YLYK01YL-FANCL'          : [["rssi"], ["fan remote"], []],
    'YLYK01YL-VENFAN'         : [["rssi"], ["ventilator fan remote"], []],
    'YLYB01YL-BHFRC'          : [["rssi"], ["bathroom heater remote"], []],
    'YLKG07YL/YLKG08YL'       : [["rssi"], ["dimmer"], []],
    'ATC'                     : [["temperature", "humidity", "battery", "voltage", "rssi"], [], ["switch", "opening"]],
    'Mi Scale V1'             : [["rssi"], ["weight", "non-stabilized weight"], ["weight removed"]],
    'Mi Scale V2'             : [["rssi"], ["weight", "non-stabilized weight", "impedance"], ["weight removed"]],
    'TZC4'                    : [["rssi"], ["weight", "non-stabilized weight", "impedance"], []],
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
    'H5183'                   : [["temperature probe 1", "temperature alarm", "rssi"], [], []],
    'Ruuvitag'                : [["temperature", "humidity", "pressure", "battery", "voltage", "rssi"], ["acceleration"], ["motion"]],
    'iNode Energy Meter'      : [["battery", "voltage", "rssi"], ["energy", "power"], []],
    "iNode Care Sensor 1"     : [["temperature", "battery", "voltage", "rssi"], ["acceleration"], ["motion"]],
    "iNode Care Sensor 2"     : [["temperature", "battery", "voltage", "rssi"], ["acceleration"], ["motion"]],
    "iNode Care Sensor 3"     : [["temperature", "humidity", "battery", "voltage", "rssi"], ["acceleration"], ["motion"]],
    "iNode Care Sensor 4"     : [["temperature", "battery", "voltage", "rssi"], ["acceleration"], ["motion"]],
    "iNode Care Sensor 5"     : [["temperature", "battery", "voltage", "rssi"], ["acceleration", "magnetic field", "magnetic field direction"], ["motion"]],
    "iNode Care Sensor 6"     : [["temperature", "battery", "voltage", "rssi"], ["acceleration"], ["motion"]],
    "iNode Care Sensor T"     : [["temperature", "battery", "voltage", "rssi"], [], []],
    "iNode Care Sensor HT"    : [["temperature", "humidity", "battery", "voltage", "rssi"], [], []],
    "iNode Care Sensor PT"    : [["temperature", "pressure", "battery", "voltage", "rssi"], [], []],
    "iNode Care Sensor PHT"   : [["temperature", "humidity", "pressure", "battery", "voltage", "rssi"], [], []],
    'Blue Puck T'             : [["temperature", "rssi"], [], []],
    'Blue Coin T'             : [["temperature", "rssi"], [], []],
    'Blue Puck RHT'           : [["temperature", "humidity", "rssi"], [], []],
    'HTP.xw'                  : [["temperature", "humidity", "pressure", "rssi"], [], []],
    'HT.w'                    : [["temperature", "humidity", "pressure", "rssi"], [], []],
    'Moat S2'                 : [["temperature", "humidity", "battery", "rssi"], [], []],
    'Tempo Disc THD'          : [["temperature", "humidity", "dewpoint", "battery", "rssi"], [], []],
    'Tempo Disc THPD'         : [["temperature", "humidity", "pressure", "battery", "rssi"], [], []],
    'b-parasite V1.0.0'       : [["temperature", "humidity", "moisture", "voltage", "rssi"], [], []],
    'b-parasite V1.1.0'       : [["temperature", "humidity", "moisture", "voltage", "rssi", "illuminance"], [], []],
    'SmartSeries 7000'        : [["rssi"], [], ["toothbrush"]],
    'iBBQ-1'                  : [["temperature probe 1", "rssi"], [], []],
    'iBBQ-2'                  : [["temperature probe 1", "temperature probe 2", "rssi"], [], []],
    'iBBQ-4'                  : [["temperature probe 1", "temperature probe 2", "temperature probe 3", "temperature probe 4", "rssi"], [], []],
    'iBBQ-6'                  : [["temperature probe 1", "temperature probe 2", "temperature probe 3", "temperature probe 4", "temperature probe 5", "temperature probe 6", "rssi"], [], []],
    'IBS-TH'                  : [["temperature", "humidity", "battery", "rssi"], [], []],
    'BEC07-5'                 : [["temperature", "humidity", "rssi"], [], []],
    'iBeacon'                 : [["rssi", "measured power", "cypress temperature", "cypress humidity"], ["uuid", "mac", "major", "minor"], []], # mac can be dynamic
    'AltBeacon'               : [["rssi", "measured power"], ["uuid", "mac", "major", "minor"], []], # mac can be dynamic
}


# Sensor manufacturer dictionary
MANUFACTURER_DICT = {
    'LYWSDCGQ'                : 'Xiaomi',
    'LYWSD02'                 : 'Xiaomi',
    'LYWSD03MMC'              : 'Xiaomi',
    'XMWSDJ04MMC'             : 'Xiaomi',
    'XMMF01JQD'               : 'Xiaomi',
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
    'TZC4'                    : 'Xiaogui',
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
    'H5183'                   : 'Govee',
    'Ruuvitag'                : 'Ruuvitag',
    'iNode Energy Meter'      : 'iNode',
    "iNode Care Sensor 1"     : 'iNode',
    "iNode Care Sensor 2"     : 'iNode',
    "iNode Care Sensor 3"     : 'iNode',
    "iNode Care Sensor 4"     : 'iNode',
    "iNode Care Sensor 5"     : 'iNode',
    "iNode Care Sensor 6"     : 'iNode',
    "iNode Care Sensor T"     : 'iNode',
    "iNode Care Sensor HT"    : 'iNode',
    "iNode Care Sensor PT"    : 'iNode',
    "iNode Care Sensor PHT"   : 'iNode',
    'Blue Puck T'             : 'Teltonika',
    'Blue Coin T'             : 'Teltonika',
    'Blue Puck RHT'           : 'Teltonika',
    'HTP.xw'                  : 'SensorPush',
    'HT.w'                    : 'SensorPush',
    'Moat S2'                 : 'Moat',
    'Tempo Disc THD'          : 'BlueMaestro',
    'Tempo Disc THPD'         : 'BlueMaestro',
    'b-parasite V1.0.0'       : 'rbaron',
    'b-parasite V1.1.0'       : 'rbaron',
    'SmartSeries 7000'        : 'Oral-B',
    'iBBQ-1'                  : 'Inkbird',
    'iBBQ-2'                  : 'Inkbird',
    'iBBQ-4'                  : 'Inkbird',
    'iBBQ-6'                  : 'Inkbird',
    'IBS-TH'                  : 'Inkbird',
    'BEC07-5'                 : 'Jinou',
    'iBeacon'                 : 'Apple',
    'AltBeacon'               : 'Radius Networks',
}

# Renamed model dictionary
RENAMED_MODEL_DICT = {
    'H5051/H5074': 'H5074',
    'IBS-TH2': 'IBS-TH',
}

# Selection list for report_uknown
REPORT_UNKNOWN_LIST = [
    "ATC",
    "BlueMaestro",
    "Brifit",
    "Govee",
    "Inkbird",
    "iNode",
    "iBeacon",
    "Jinou"
    "Kegtron",
    "Mi Scale",
    "Moat",
    "Oral-B",
    "Qingping",
    "rbaron",
    "Ruuvitag",
    "SensorPush",
    "Teltonika",
    "Thermoplus",
    "Xiaogui",
    "Xiaomi",
    "Other",
    "Off",
    False,
]
