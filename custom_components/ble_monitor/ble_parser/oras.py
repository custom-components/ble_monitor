"""Parser for Oras BLE advertisements."""
import logging

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


def parse_oras(self, data: bytes, mac: str):
    """Parser for Oras toothbrush."""
    msg_length = len(data)
    firmware = "Oras"
    result = {"firmware": firmware}
    if msg_length == 22:
        device_type = "Electra Washbasin Faucet"
        battery = data[5]
        result.update({"battery": battery})
    else:
        if self.report_unknown == "Oras":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Oras DEVICE: MAC: %s, ADV: %s",
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
