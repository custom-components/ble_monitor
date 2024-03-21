"""Parser for Oras/Garnet BLE advertisements."""
import logging

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPE = {
    0: "fresh tank",
    1: "black tank",
    2: "grey tank",
    3: "lpg tank",
    4: "lpg tank 2",
    5: "galley tank",
    6: "galley tank 2",
    7: "temperature",
    8: "temperature probe 2",
    9: "temperature probe 3",
    10: "temperature probe 4",
    11: "chemical tank",
    12: "chemical tank 2",
    13: "voltage",
}


def parse_oras(self, data: bytes, mac: str):
    """Parser for Oras toothbrush or Garnet tank."""
    msg_length = len(data)
    result = {"mac": to_unformatted_mac(mac)}

    if msg_length == 18:
        firmware = "Garnet"
        device_type = "SeeLevel II 709-BTP3"

        sensor_id = data[7]
        try:
            sensor_type = SENSOR_TYPE[sensor_id]
        except ValueError:
            return None

        try:
            sensor_data = int(data[8:11].decode("ASCII"))
        except ValueError:
            error_code = data[8:11].decode("ASCII")
            _LOGGER.error(
                "Garnet SeeLevel II 709-BTP3 is reporting error %s for sensor %s",
                error_code,
                sensor_type
            )
            return None

        if sensor_id == 13:
            sensor_data /= 10

        sensor_volume = data[11:14].decode("ASCII")
        sensor_total = data[14:17].decode("ASCII")
        sensor_alarm = int(chr(data[17]))

        result.update({
            sensor_type: sensor_data,
            "problem": sensor_alarm,
        })
        _LOGGER.debug(
            "BLE ADV from Garnet DEVICE: %s, result: %s, not implemented volume %s, total %s",
            device_type,
            result,
            sensor_volume,
            sensor_total
        )
    elif msg_length == 22:
        firmware = "Oras"
        device_type = "Electra Washbasin Faucet"
        battery = data[5]
        result.update({"battery": battery})
    else:
        if self.report_unknown in ["Oras", "Garnet"]:
            _LOGGER.info(
                "BLE ADV from UNKNOWN Oras/Garnet DEVICE: MAC: %s, ADV: %s",
                to_mac(mac),
                data.hex()
            )
        return None

    result.update({
        "type": device_type,
        "packet": "no packet id",
        "firmware": firmware,
        "data": True
    })
    return result
