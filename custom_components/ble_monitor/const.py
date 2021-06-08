"""Constants for the Passive BLE monitor integration."""

DOMAIN = "ble_monitor"
PLATFORMS = ["binary_sensor", "sensor"]

# Configuration options
CONF_ROUNDING = "rounding"
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
CONFIG_IS_FLOW = "is_flow"

SERVICE_CLEANUP_ENTRIES = "cleanup_entries"

# Default values for configuration options
DEFAULT_ROUNDING = True
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
CONF_HMIN = 0.0
CONF_HMAX = 99.9

# Dictionary with the available sensors
SENSOR_DICT = {
    "temperature":             "TemperatureSensor",
    "humidity":                "HumiditySensor",
    "moisture":                "MoistureSensor",
    "pressure":                "PressureSensor",
    "conductivity":            "ConductivitySensor",
    "illuminance":             "IlluminanceSensor",
    "formaldehyde":            "FormaldehydeSensor",
    "consumable":              "ConsumableSensor",
    "button":                  "ButtonSensor",
    "remote":                  "RemoteSensor",
    "fan remote":              "FanRemoteSensor",
    "ventilator fan remote":   "VentilatorFanRemoteSensor",
    "bathroom heater remote":  "BathroomHeaterRemoteSensor",
    "dimmer":                  "DimmerSensor",
    "weight":                  "WeightSensor",
    "non-stabilized weight":   "NonStabilizedWeightSensor",
    "impedance":               "ImpedanceSensor",
    "toothbrush mode":         "ToothbrushModeSensor",
    "volume dispensed port 1": "VolumeDispensedPort1Sensor",
    "volume dispensed port 2": "VolumeDispensedPort2Sensor",
    "voltage":                 "VoltageSensor",
    "battery":                 "BatterySensor",
}


# Dictionary with the available binary sensors
BINARY_SENSOR_DICT = {
    "remote single press":     "RemoteSinglePressBinarySensor",
    "remote long press":       "RemoteLongPressBinarySensor",
    "switch":                  "PowerBinarySensor",
    "opening":                 "OpeningBinarySensor",
    "light":                   "LightBinarySensor",
    "moisture":                "MoistureBinarySensor",
    "motion":                  "MotionBinarySensor",
    "weight removed":          "WeightRemovedBinarySensor",
    "smoke detector":          "SmokeDetectorBinarySensor",
}


# Dictionary with supported (binary) sensors
# Format {device: [sensor list], [binary sensor list], "updating behavior"}:
# - [sensor list]:        supported sensors of the device
# - [binary sensor list]: supported binary sensors of the device
# - "updating beharior":  type of updating behavior for device sensor ("averaging" or "instant")
MEASUREMENT_DICT = {
    'LYWSDCGQ'                : [["temperature", "humidity", "battery"], [], "averaging"],
    'LYWSD02'                 : [["temperature", "humidity", "battery"], [], "averaging"],
    'LYWSD03MMC'              : [["temperature", "humidity", "battery", "voltage"], [], "averaging"],
    'HHCCJCY01'               : [["temperature", "moisture", "conductivity", "illuminance"], [], "averaging"],
    'GCLS002'                 : [["temperature", "moisture", "conductivity", "illuminance"], [], "averaging"],
    'HHCCPOT002'              : [["moisture", "conductivity"], [], "averaging"],
    'WX08ZM'                  : [["consumable", "battery"], ["switch"], "averaging"],
    'MCCGQ02HL'               : [["battery"], ["opening", "light"], "averaging"],
    'YM-K1501'                : [["temperature"], ["switch"], "instant"],
    'YM-K1501EU'              : [["temperature"], ["switch"], "instant"],
    'V-SK152'                 : [["temperature"], ["switch"], "instant"],
    'SJWS01LM'                : [["battery"], ["moisture"], "averaging"],
    'MJYD02YL'                : [["battery"], ["light", "motion"], "averaging"],
    'MUE4094RT'               : [[], ["motion"], "averaging"],
    'RTCGQ02LM'               : [["button"], ["light", "motion"], "instant"],
    'MMC-T201-1'              : [["temperature", "battery"], [], "averaging"],
    'M1S-T500'                : [["toothbrush mode", "battery"], [], "instant"],
    'CGC1'                    : [["temperature", "humidity", "battery"], [], "averaging"],
    'CGD1'                    : [["temperature", "humidity", "battery"], [], "averaging"],
    'CGDK2'                   : [["temperature", "humidity", "battery"], [], "averaging"],
    'CGG1'                    : [["temperature", "humidity", "battery"], [], "averaging"],
    'CGG1-ENCRYPTED'          : [["temperature", "humidity", "battery"], [], "averaging"],
    'CGH1'                    : [["battery"], ["opening"], "averaging"],
    'CGP1W'                   : [["temperature", "humidity", "battery", "pressure"], [], "averaging"],
    'CGPR1'                   : [["illuminance", "battery"], ["motion"], "averaging"],
    'MHO-C401'                : [["temperature", "humidity", "battery"], [], "averaging"],
    'MHO-C303'                : [["temperature", "humidity", "battery"], [], "averaging"],
    'JQJCY01YM'               : [["temperature", "humidity", "battery", "formaldehyde"], [], "averaging"],
    'JTYJGD03MI'              : [["button", "battery"], ["smoke detector"], "instant"],
    'YLAI003'                 : [["button", "battery"], [], "instant"],
    'YLYK01YL'                : [["remote"], ["remote single press", "remote long press"], "instant"],
    'YLYK01YL-FANCL'          : [["fan remote"], [], "instant"],
    'YLYK01YL-VENFAN'         : [["ventilator fan remote"], [], "instant"],
    'YLYB01YL-BHFRC'          : [["bathroom heater remote"], [], "instant"],
    'YLKG07YL/YLKG08YL'       : [["dimmer"], [], "instant"],
    'ATC'                     : [["temperature", "humidity", "battery", "voltage"], [], "averaging"],
    'Mi Scale V1'             : [["weight", "non-stabilized weight"], ["weight removed"], "instant"],
    'Mi Scale V2'             : [["weight", "non-stabilized weight", "impedance"], ["weight removed"], "instant"],
    'Kegtron KT-100'          : [["volume dispensed port 1"], [], "instant"],
    'Kegtron KT-200'          : [["volume dispensed port 1", "volume dispensed port 2"], [], "instant"],
    'Smart hygrometer'        : [["temperature", "humidity", "battery", "voltage"], [], "averaging"],
    'Lanyard/mini hygrometer' : [["temperature", "humidity", "battery", "voltage"], [], "averaging"],
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
    'ATC'                     : 'ATC',
    'Mi Scale V1'             : 'Xiaomi',
    'Mi Scale V2'             : 'Xiaomi',
    'Kegtron KT-100'          : 'Kegtron',
    'Kegtron KT-200'          : 'Kegtron',
    'Smart hygrometer'        : 'Thermoplus',
    'Lanyard/mini hygrometer' : 'Thermoplus',
}
