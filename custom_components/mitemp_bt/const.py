"""Constants for the Xiaomi BLE monitor sensor integration."""

# Configuration options
CONF_ROUNDING = "rounding"
CONF_DECIMALS = "decimals"
CONF_PERIOD = "period"
CONF_LOG_SPIKES = "log_spikes"
CONF_USE_MEDIAN = "use_median"
CONF_ACTIVE_SCAN = "active_scan"
CONF_HCI_INTERFACE = "hci_interface"

# Default values for configuration options
DEFAULT_ROUNDING = True
DEFAULT_DECIMALS = 2
DEFAULT_PERIOD = 60
DEFAULT_LOG_SPIKES = False
DEFAULT_USE_MEDIAN = False
DEFAULT_ACTIVE_SCAN = False
DEFAULT_HCI_INTERFACE = 0


"""Fixed constants."""

# Sensor measurement limits to exclude erroneous spikes from the results
CONF_TMIN = -40.0
CONF_TMAX = 60.0
CONF_HMIN = 0.0
CONF_HMAX = 99.9

# Xiaomi sensor types dictionary with offset for parser
XIAOMI_TYPE_DICT = {
    '209800': ["HHCCJCY01", 1],
    '20AA01': ["LYWSDCGQ", 0],
    '205B04': ["LYWSD02", 1],
    '304703': ["CGG1", 0],
    '205D01': ["HHCCPOT002", 1]
}
