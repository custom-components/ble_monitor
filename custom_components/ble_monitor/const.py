"""Constants for the Passive BLE monitor integration."""

DOMAIN = "ble_monitor"

# Configuration options
CONF_ROUNDING = "rounding"
CONF_DECIMALS = "decimals"
CONF_PERIOD = "period"
CONF_LOG_SPIKES = "log_spikes"
CONF_USE_MEDIAN = "use_median"
CONF_ACTIVE_SCAN = "active_scan"
CONF_HCI_INTERFACE = "hci_interface"
CONF_BATT_ENTITIES = "batt_entities"
CONF_REPORT_UNKNOWN = "report_unknown"
CONF_RESTORE_STATE = "restore_state"
CONF_ENCRYPTION_KEY = "encryption_key"
CONFIG_IS_FLOW = "is_flow"

SERVICE_CLEANUP_ENTRIES = "cleanup_entries"

# Default values for configuration options
DEFAULT_ROUNDING = True
DEFAULT_DECIMALS = 1
DEFAULT_PERIOD = 60
DEFAULT_LOG_SPIKES = False
DEFAULT_USE_MEDIAN = False
DEFAULT_ACTIVE_SCAN = False
DEFAULT_HCI_INTERFACE = 0
DEFAULT_BATT_ENTITIES = False
DEFAULT_REPORT_UNKNOWN = False
DEFAULT_DISCOVERY = True
DEFAULT_RESTORE_STATE = False

# regex constants for configuration schema
MAC_REGEX = "(?i)^(?:[0-9A-F]{2}[:]){5}(?:[0-9A-F]{2})$"
AES128KEY_REGEX = "(?i)^[A-F0-9]{32}$"

"""Fixed constants."""

# Sensor measurement limits to exclude erroneous spikes from the results (temperature in °C)
CONF_TMIN = -40.0
CONF_TMAX = 60.0
CONF_HMIN = 0.0
CONF_HMAX = 99.9

# Xiaomi sensor types dictionary for adv parser
#                              binary?
XIAOMI_TYPE_DICT = {
    b'\x98\x00': ("HHCCJCY01", False),
    b'\xAA\x01': ("LYWSDCGQ", False),
    b'\x5B\x04': ("LYWSD02", False),
    b'\x47\x03': ("CGG1", False),
    b'\x5D\x01': ("HHCCPOT002", False),
    b'\xBC\x03': ("GCLS002", False),
    b'\x5B\x05': ("LYWSD03MMC", False),
    b'\x76\x05': ("CGD1", False),
    b'\xDF\x02': ("JQJCY01YM", False),
    b'\x0A\x04': ("WX08ZM", True),
    b'\x87\x03': ("MHO-C401", False),
    b'\xd3\x06': ("MHO-C303", False),
    b'\x8B\x09': ("MCCGQ02HL", True),
    b'\x83\x00': ("YM-K1501", True),
}


# Sensor type indexes dictionary for sensor platform
# Temperature, Humidity, Moisture, Conductivity, Illuminance, Formaldehyde, Consumable, Battery, Switch, Opening, Light
#                          sensor               binary
# Measurement type [T  H  M  C  I  F  Cn B]  [Sw O  L  B]     (start from 0, 9 - no data)
MMTS_DICT = {
    'HHCCJCY01' : [[0, 9, 1, 2, 3, 9, 9, 9], [9, 9, 9, 9]],
    'GCLS002'   : [[0, 9, 1, 2, 3, 9, 9, 9], [9, 9, 9, 9]],
    'HHCCPOT002': [[9, 9, 0, 1, 9, 9, 9, 9], [9, 9, 9, 9]],
    'LYWSDCGQ'  : [[0, 1, 9, 9, 9, 9, 9, 2], [9, 9, 9, 9]],
    'LYWSD02'   : [[0, 1, 9, 9, 9, 9, 9, 2], [9, 9, 9, 9]],
    'CGG1'      : [[0, 1, 9, 9, 9, 9, 9, 2], [9, 9, 9, 9]],
    'LYWSD03MMC': [[0, 1, 9, 9, 9, 9, 9, 2], [9, 9, 9, 9]],
    'CGD1'      : [[0, 1, 9, 9, 9, 9, 9, 2], [9, 9, 9, 9]],
    'JQJCY01YM' : [[0, 1, 9, 9, 9, 2, 9, 3], [9, 9, 9, 9]],
    'WX08ZM'    : [[9, 9, 9, 9, 9, 9, 0, 1], [0, 9, 9, 1]],
    'MHO-C401'  : [[0, 1, 9, 9, 9, 9, 9, 2], [9, 9, 9, 9]],
    'MHO-C303'  : [[0, 1, 9, 9, 9, 9, 9, 2], [9, 9, 9, 9]],
    'MCCGQ02HL' : [[9, 9, 9, 9, 9, 9, 9, 0], [9, 0, 1, 2]],
    'YM-K1501'  : [[0, 9, 9, 9, 9, 9, 9, 9], [0, 9, 9, 9]],
}

# Sensor manufacturer dictionary
MANUFACTURER_DICT = {
    'HHCCJCY01' : 'Xiaomi',
    'GCLS002'   : 'Xiaomi',
    'HHCCPOT002': 'Xiaomi',
    'LYWSDCGQ'  : 'Xiaomi',
    'LYWSD02'   : 'Xiaomi',
    'CGG1'      : 'Xiaomi',
    'LYWSD03MMC': 'Xiaomi',
    'CGD1'      : 'ClearGrass',
    'JQJCY01YM' : 'Honeywell',
    'WX08ZM'    : 'Xiaomi',
    'MHO-C401'  : 'Miaomiaoce',
    'MHO-C303'  : 'Miaomiaoce',
    'MCCGQ02HL' : 'Xiaomi',
    'YM-K1501'  : 'Xiaomi',
}

# The use of the following dictionaries is lost when changing the sensor naming system
# Left here as a reminder, as we will probably return to this with the HA 0.118.x update
# Switch binary sensor classes dict
#  SW_CLASS_DICT = {
#     'WX08ZM'    : DEVICE_CLASS_POWER
# }

# Consumable sensor name dict
# CN_NAME_DICT = {
#     'WX08ZM'    : "tablet_"
# }
