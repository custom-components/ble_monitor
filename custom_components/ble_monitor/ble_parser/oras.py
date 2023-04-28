"""Parser for Oras BLE advertisements."""
import logging

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


def parse_oras(self, data, source_mac, rssi):
    """Parser for Oras toothbrush."""
    msg_length = len(data)
    firmware = "Oras"
    oras_mac = source_mac
    result = {"firmware": firmware}
    if msg_length == 22:
        device_type = "Electra Washbasin Faucet"
        battery = data[5]
        result.update({"battery": battery})
    else:
        if self.report_unknown == "Oras":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Oras DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # check for MAC presence in whitelist, if needed
    if self.discovery is False and oras_mac not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(oras_mac))
        return None

    result.update({
        "rssi": rssi,
        "mac": to_unformatted_mac(oras_mac),
        "type": device_type,
        "packet": "no packet id",
        "firmware": firmware,
        "data": True
    })
    return result
