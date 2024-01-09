"""Parser for Inkbird BLE advertisements"""
import logging
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


def convert_temperature(temp):
    """Temperature converter"""
    if temp > 0:
        temperature = temp / 10.0
    else:
        temperature = 0
    return temperature


def parse_inkbird(self, data: bytes, complete_local_name: str, mac: str):
    """Inkbird parser"""
    msg_length = len(data)
    firmware = "Inkbird"
    result = {"firmware": firmware}
    if msg_length == 11 and complete_local_name in ["sps", "tps"]:
        xvalue = data[2:10]
        (temp, hum, probe, modbus, bat) = unpack("<hHBHB", xvalue[0:8])

        if probe == 0:
            result.update({"temperature": temp / 100})
        elif probe == 1:
            result.update({"temperature probe 1": temp / 100})
        elif probe == 3:
            # User has reported that the external probe sometimes reports as probe 3
            result.update({"temperature probe 1": temp / 100})
        else:
            _LOGGER.error(
                "Inkbird is reporting different probe number. Please report the "
                "following data to the developers. data: %s ",
                data.hex()
            )
            return None

        result.update({"battery": bat})

        if complete_local_name == "sps":
            device_type = "IBS-TH"
            result.update({"humidity": hum / 100})
        elif complete_local_name == "tps":
            device_type = "IBS-TH2/P01B"
        else:
            return None
    elif msg_length == 14:
        device_type = "iBBQ-1"
        inkbird_mac = data[6:12]
        xvalue = data[12:14]
        if mac not in [inkbird_mac, inkbird_mac[::-1]]:
            _LOGGER.debug(
                "Inkbird MAC address doesn't match data MAC address. Data: %s",
                data.hex()
            )
            return None
        (temp_1,) = unpack("<h", xvalue)
        result.update(
            {
                "temperature probe 1": convert_temperature(temp_1),
            }
        )
    elif msg_length == 16:
        device_type = "iBBQ-2"
        inkbird_mac = data[6:12]
        xvalue = data[12:16]
        if mac not in [inkbird_mac, inkbird_mac[::-1]]:
            _LOGGER.debug(
                "Inkbird MAC address doesn't match data MAC address. Data: %s",
                data.hex()
            )
            return None
        (temp_1, temp_2) = unpack("<HH", xvalue)
        result.update(
            {
                "temperature probe 1": convert_temperature(temp_1),
                "temperature probe 2": convert_temperature(temp_2),
            }
        )
    elif msg_length == 20:
        inkbird_mac = data[6:12]
        xvalue = data[12:20]
        if mac not in [inkbird_mac, inkbird_mac[::-1]]:
            _LOGGER.debug(
                "Inkbird MAC address doesn't match data MAC address. Data: %s",
                data.hex()
            )
            return None
        device_type = "iBBQ-4"
        (temp_1, temp_2, temp_3, temp_4) = unpack("<hhhh", xvalue)
        result.update(
            {
                "temperature probe 1": convert_temperature(temp_1),
                "temperature probe 2": convert_temperature(temp_2),
                "temperature probe 3": convert_temperature(temp_3),
                "temperature probe 4": convert_temperature(temp_4),
            }
        )
    elif msg_length == 24:
        inkbird_mac = data[6:12]
        xvalue = data[12:24]
        if mac not in [inkbird_mac, inkbird_mac[::-1]]:
            _LOGGER.debug("Inkbird MAC address doesn't match data MAC address. Data: %s", data.hex())
            return None
        device_type = "iBBQ-6"
        (temp_1, temp_2, temp_3, temp_4, temp_5, temp_6) = unpack("<hhhhhh", xvalue)
        result.update(
            {
                "temperature probe 1": convert_temperature(temp_1),
                "temperature probe 2": convert_temperature(temp_2),
                "temperature probe 3": convert_temperature(temp_3),
                "temperature probe 4": convert_temperature(temp_4),
                "temperature probe 5": convert_temperature(temp_5),
                "temperature probe 6": convert_temperature(temp_6),
            }
        )
    else:
        if self.report_unknown == "Inkbird":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Inkbird DEVICE: MAC: %s, ADV: %s",
                to_mac(mac),
                data.hex()
            )
        return None

    result.update({
        "mac": to_unformatted_mac(mac),
        "type": device_type,
        "packet": "no packet id",
        "firmware": firmware,
        "data": True
    })
    return result
