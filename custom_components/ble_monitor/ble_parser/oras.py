"""Parser for Oras/Garnet BLE advertisements."""
import logging

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPE = {
    0: "fresh tank",
    1: "black tank",
    2: "grey tank",
    3: "LPG tank",
    4: "LPG tank 2",
    5: "galley tank",
    6: "galley tank 2",
    7: "temperature",
    8: "temperature 2",
    9: "temperature 3",
    10: "temperature 4",
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
        sensor_data = data[8:11].decode("ASCII")
        sensor_volume = data[11:14].decode("ASCII")
        sensor_total = data[14:17].decode("ASCII")
        sensor_alarm = chr(data[17])

        # remove later
        result.update({
            "sensor_id": sensor_id,
            "sensor_data": sensor_data,
            "sensor_volume": sensor_volume,
            "sensor_total": sensor_total,
            "sensor_alarm": sensor_alarm,
        })
        _LOGGER.info(
            "BLE ADV from Oras DEVICE: %s, result: %s",
            device_type,
            result
        )
        if sensor_id <= 12:
            result.update({SENSOR_TYPE[sensor_id]: int(sensor_data)})
        elif sensor_id == 13:
            result.update({"voltage": int(sensor_data) / 10})
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
