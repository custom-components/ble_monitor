"""Constants for the Passive BLE monitor integration."""

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

# Dictionary with the available sensors
SENSOR_DICT = {
    "temperature":              "TemperatureSensor",
    "temperature outdoor":      "TemperatureOutdoorSensor",
    "humidity":                 "HumiditySensor",
    "humidity outdoor":         "HumidityOutdoorSensor",
    "moisture":                 "MoistureSensor",
    "pressure":                 "PressureSensor",
    "conductivity":             "ConductivitySensor",
    "illuminance":              "IlluminanceSensor",
    "formaldehyde":             "FormaldehydeSensor",
    "acceleration":             "AccelerationSensor",
    "consumable":               "ConsumableSensor",
    "button":                   "ButtonSensor",
    "remote":                   "RemoteSensor",
    "fan remote":               "FanRemoteSensor",
    "ventilator fan remote":    "VentilatorFanRemoteSensor",
    "bathroom heater remote":   "BathroomHeaterRemoteSensor",
    "dimmer":                   "DimmerSensor",
    "weight":                   "WeightSensor",
    "non-stabilized weight":    "NonStabilizedWeightSensor",
    "impedance":                "ImpedanceSensor",
    "toothbrush mode":          "ToothbrushModeSensor",
    "volume dispensed port 1":  "VolumeDispensedPort1Sensor",
    "volume dispensed port 2":  "VolumeDispensedPort2Sensor",
    "energy":                   "EnergySensor",
    "power" :                   "PowerSensor",
    "voltage":                  "VoltageSensor",
    "battery":                  "BatterySensor",
    "one btn switch":           "SingleSwitchSensor",
    "two btn switch left":      "DoubleSwitchLeftSensor",
    "two btn switch right":     "DoubleSwitchRightSensor",
    "three btn switch left":    "TripleSwitchLeftSensor",
    "three btn switch middle":  "TripleSwitchMiddleSensor",
    "three btn switch right":   "TripleSwitchRightSensor",
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


# Dictionary with supported sensors
# Format {device: [averaging sensor list], [instantly updating sensor list],[binary sensor list]}:
# - [averaging sensor list]:            sensors that update the state after avering of the data
# - [instantly updating sensor list]:   sensors that update the state instantly after new data
# - [binary sensor list]:               binary sensors
MEASUREMENT_DICT = {
    'LYWSDCGQ'                : [["temperature", "humidity", "battery"], [], []],
    'LYWSD02'                 : [["temperature", "humidity", "battery"], [], []],
    'LYWSD03MMC'              : [["temperature", "humidity", "battery", "voltage"], [], []],
    'HHCCJCY01'               : [["temperature", "moisture", "conductivity", "illuminance"], [], []],
    'GCLS002'                 : [["temperature", "moisture", "conductivity", "illuminance"], [], []],
    'HHCCPOT002'              : [["moisture", "conductivity"], [], []],
    'WX08ZM'                  : [["consumable", "battery"], [], ["switch"]],
    'MCCGQ02HL'               : [["battery"], [], ["opening", "light"]],
    'YM-K1501'                : [[], ["temperature"], ["switch"]],
    'YM-K1501EU'              : [[], ["temperature"], ["switch"]],
    'V-SK152'                 : [[], ["temperature"], ["switch"]],
    'SJWS01LM'                : [["battery"], [], ["moisture"]],
    'MJYD02YL'                : [["battery"], [], ["light", "motion"]],
    'MUE4094RT'               : [[], [], ["motion"]],
    'RTCGQ02LM'               : [["battery"], ["button"], ["light", "motion"]],
    'MMC-T201-1'              : [["temperature", "battery"], [], []],
    'M1S-T500'                : [["battery"], ["toothbrush mode"], []],
    'CGC1'                    : [["temperature", "humidity", "battery"], [], []],
    'CGD1'                    : [["temperature", "humidity", "battery"], [], []],
    'CGDK2'                   : [["temperature", "humidity", "battery"], [], []],
    'CGG1'                    : [["temperature", "humidity", "battery"], [], []],
    'CGG1-ENCRYPTED'          : [["temperature", "humidity", "battery"], [], []],
    'CGH1'                    : [["battery"], [], ["opening"]],
    'CGP1W'                   : [["temperature", "humidity", "battery", "pressure"], [], []],
    'CGPR1'                   : [["illuminance", "battery"], [], ["motion"]],
    'MHO-C401'                : [["temperature", "humidity", "battery"], [], []],
    'MHO-C303'                : [["temperature", "humidity", "battery"], [], []],
    'JQJCY01YM'               : [["temperature", "humidity", "battery", "formaldehyde"], [], []],
    'JTYJGD03MI'              : [[], ["button", "battery"], ["smoke detector"]],
    'K9B-1BTN'                : [[], ["one btn switch"], []],
    'K9B-2BTN'                : [[], ["two btn switch left", "two btn switch right"], []],
    'K9B-3BTN'                : [[], ["three btn switch left", "three btn switch middle", "three btn switch right"], []],
    'YLAI003'                 : [[], ["button", "battery"], []],
    'YLYK01YL'                : [[], ["remote"], ["remote single press", "remote long press"]],
    'YLYK01YL-FANCL'          : [[], ["fan remote"], []],
    'YLYK01YL-VENFAN'         : [[], ["ventilator fan remote"], []],
    'YLYB01YL-BHFRC'          : [[], ["bathroom heater remote"], []],
    'YLKG07YL/YLKG08YL'       : [[], ["dimmer"], []],
    'ATC'                     : [["temperature", "humidity", "battery", "voltage"], [], []],
    'Mi Scale V1'             : [[], ["weight", "non-stabilized weight"], ["weight removed"]],
    'Mi Scale V2'             : [[], ["weight", "non-stabilized weight", "impedance"], ["weight removed"]],
    'Kegtron KT-100'          : [[], ["volume dispensed port 1"], []],
    'Kegtron KT-200'          : [[], ["volume dispensed port 1", "volume dispensed port 2"], []],
    'Smart hygrometer'        : [["temperature", "humidity", "battery", "voltage"], [], []],
    'Lanyard/mini hygrometer' : [["temperature", "humidity", "battery", "voltage"], [], []],
    'T201'                    : [["temperature", "humidity", "battery", "voltage"], [], []],
    'H5072/H5075'             : [["temperature", "humidity", "battery"], [], []],
    'H5101/H5102/H5177'       : [["temperature", "humidity", "battery"], [], []],
    'H5051'                   : [["temperature", "humidity", "battery"], [], []],
    'H5074'                   : [["temperature", "humidity", "battery"], [], []],
    'H5178'                   : [["temperature", "temperature outdoor", "humidity", "humidity outdoor", "battery"], [], []],
    'H5179'                   : [["temperature", "humidity", "battery"], [], []],
    'Ruuvitag'                : [["temperature", "humidity", "pressure", "battery", "voltage"], ["acceleration"], ["motion"]],
    'iNode Energy Meter'      : [["battery", "voltage"], ["energy", "power"], []],
    'Blue Puck T'             : [["temperature"], [], []],
    'Blue Puck RHT'           : [["temperature", "humidity"], [], []],
    'HTP.xw'                  : [["temperature", "humidity", "pressure"], [], []],
    'HT.w'                    : [["temperature", "humidity", "pressure"], [], []]
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
    'Blue Puck RHT'           : 'Teltonika',
    'HTP.xw'                  : 'SensorPush',
    'HT.w'                    : 'SensorPush',
}

# Renamed model dictionary
RENAMED_MODEL_DICT = {
    'H5051/H5074': 'H5074'
}
