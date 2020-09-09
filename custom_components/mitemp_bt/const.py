"""Constants for the Xiaomi passive BLE monitor sensor integration."""
from homeassistant.const import (
    DEVICE_CLASS_POWER,
)

# Configuration options
CONF_ROUNDING = "rounding"
CONF_DECIMALS = "decimals"
CONF_PERIOD = "period"
CONF_LOG_SPIKES = "log_spikes"
CONF_USE_MEDIAN = "use_median"
CONF_ACTIVE_SCAN = "active_scan"
CONF_HCI_INTERFACE = "hci_interface"
CONF_BATT_ENTITIES = "batt_entities"
CONF_ENCRYPTORS = "encryptors"
CONF_REPORT_UNKNOWN = "report_unknown"
CONF_WHITELIST = "whitelist"

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
DEFAULT_WHITELIST = False


"""Fixed constants."""

# Sensor measurement limits to exclude erroneous spikes from the results
CONF_TMIN = -40.0
CONF_TMAX = 60.0
CONF_HMIN = 0.0
CONF_HMAX = 99.9

# Xiaomi sensor types dictionary for adv parser
XIAOMI_TYPE_DICT = {
    b'\x98\x00': "HHCCJCY01",
    b'\xAA\x01': "LYWSDCGQ",
    b'\x5B\x04': "LYWSD02",
    b'\x47\x03': "CGG1",
    b'\x5D\x01': "HHCCPOT002",
    b'\xBC\x03': "GCLS002",
    b'\x5B\x05': "LYWSD03MMC",
    b'\x76\x05': "CGD1",
    b'\xDF\x02': "JQJCY01YM",
    b'\x0A\x04': "WX08ZM",
    b'\x87\x03': "MHO-C401",
    b'\xd3\x06': "MHO-C303"
}


# Sensor type indexes dictionary
# Temperature, Humidity, Moisture, Conductivity, Illuminance, Formaldehyde, Consumable, Switch, Battery
# Measurement type T  H  M  C  I  F  Cn Sw B   9 - no measurement
MMTS_DICT = {
    'HHCCJCY01' : [0, 9, 1, 2, 3, 9, 9, 9, 9],
    'GCLS002'   : [0, 9, 1, 2, 3, 9, 9, 9, 9],
    'HHCCPOT002': [9, 9, 0, 1, 9, 9, 9, 9, 9],
    'LYWSDCGQ'  : [0, 1, 9, 9, 9, 9, 9, 9, 2],
    'LYWSD02'   : [0, 1, 9, 9, 9, 9, 9, 9, 9],
    'CGG1'      : [0, 1, 9, 9, 9, 9, 9, 9, 2],
    'LYWSD03MMC': [0, 1, 9, 9, 9, 9, 9, 9, 2],
    'CGD1'      : [0, 1, 9, 9, 9, 9, 9, 9, 2],
    'JQJCY01YM' : [0, 1, 9, 9, 9, 2, 9, 9, 3],
    'WX08ZM'    : [9, 9, 9, 9, 9, 9, 0, 1, 2],
    'MHO-C401'  : [0, 1, 9, 9, 9, 9, 9, 9, 2],
    'MHO-C303'  : [0, 1, 9, 9, 9, 9, 9, 9, 2]
}

# Switch binary sensor classes dict
SW_CLASS_DICT = {
    'WX08ZM'    : DEVICE_CLASS_POWER
}

# Consumable sensor name dict
CN_NAME_DICT = {
    'WX08ZM'    : "tablet_"
}
