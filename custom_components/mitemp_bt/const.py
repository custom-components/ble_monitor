"""Constants for the Xiaomi passive BLE monitor sensor integration."""

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

# Default values for configuration options
DEFAULT_ROUNDING = True
DEFAULT_DECIMALS = 2
DEFAULT_PERIOD = 60
DEFAULT_LOG_SPIKES = False
DEFAULT_USE_MEDIAN = False
DEFAULT_ACTIVE_SCAN = False
DEFAULT_HCI_INTERFACE = 0
DEFAULT_BATT_ENTITIES = False
DEFAULT_REPORT_UNKNOWN = False


"""Fixed constants."""

# Sensor measurement limits to exclude erroneous spikes from the results
CONF_TMIN = -40.0
CONF_TMAX = 60.0
CONF_HMIN = 0.0
CONF_HMAX = 99.9

# Xiaomi sensor types dictionary with offset for adv parser
XIAOMI_TYPE_DICT = {
    b'\x98\x00': "HHCCJCY01",
    b'\xAA\x01': "LYWSDCGQ",
    b'\x5B\x04': "LYWSD02",
    b'\x47\x03': "CGG1",
    b'\x5D\x01': "HHCCPOT002",
    b'\xBC\x03': "GCLS002",
    b'\x5B\x05': "LYWSD03MMC",
    b'\x76\x05': "CGD1"
}


# Sensor type indexes dictionary
# Temperature, Humidity, Moisture, Conductivity, Illuminance, Battery
# Measurement type T  H  M  C  I  B   9 - no measurement
MMTS_DICT = {
    'HHCCJCY01' : [0, 9, 1, 2, 3, 9],
    'GCLS002'   : [0, 9, 1, 2, 3, 9],
    'HHCCPOT002': [9, 9, 0, 1, 9, 9],
    'LYWSDCGQ'  : [0, 1, 9, 9, 9, 2],
    'LYWSD02'   : [0, 1, 9, 9, 9, 9],
    'CGG1'      : [0, 1, 9, 9, 9, 2],
    'LYWSD03MMC': [0, 1, 9, 9, 9, 2],
    'CGD1'      : [0, 1, 9, 9, 9, 2]
}
