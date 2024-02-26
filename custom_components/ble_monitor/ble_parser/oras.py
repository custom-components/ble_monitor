"""Parser for Oras/Garnet BLE advertisements."""
import logging

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


def parse_oras(self, data: bytes, mac: str):
    """Parser for Oras toothbrush or Garnet tank."""
    msg_length = len(data)
    result = {"mac": to_unformatted_mac(mac)}

    if msg_length == 18:
        firmware = "Garnet"
        device_type = "Garnet 709BT"

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
        if sensor_id == 13:
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
