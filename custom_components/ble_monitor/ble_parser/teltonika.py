# Parser for Teltonika BLE advertisements
import logging
from struct import unpack

_LOGGER = logging.getLogger(__name__)


def parse_teltonika(self, data, source_mac, rssi):
    result = {"firmware": "Teltonika"}
    teltonika_mac = source_mac

    # teltonika adv contain a name (0x09) and one or two 0x16 payloads (temperature/humidity)
    adpayload_start = 0
    adpayload_size = len(data)
    while adpayload_size > 1:
        adstuct_size = data[adpayload_start] + 1
        if adstuct_size > 1 and adstuct_size <= adpayload_size:
            adstruct = data[adpayload_start:adpayload_start + adstuct_size]
            adstuct_type = adstruct[1]
            if adstuct_type == 0x09 and adstuct_size > 4:
                dev_type = adstruct[2:].decode("utf-8")
                if dev_type == "PUCK_T1":
                    device_type = "Blue Puck T"
                elif dev_type == "PUCK_TH":
                    device_type = "Blue Puck RHT"
                else:
                    device_type = None
            elif adstuct_type == 0x16 and adstuct_size > 4:
                uuid16 = (adstruct[3] << 8) | adstruct[2]
                if uuid16 == 0x2A6E:
                    # Temperature
                    (temp,) = unpack("<h", adstruct[4:])
                    result.update({"temperature": temp / 100})
                elif uuid16 == 0x2A6F:
                    # Humidity
                    (humi,) = unpack("<B", adstruct[4:])
                    result.update({"humidity": humi})
        adpayload_size -= adstuct_size
        adpayload_start += adstuct_size

    if device_type is None:
        if self.report_unknown == "Teltonika":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Teltonika DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and teltonika_mac.lower() not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(teltonika_mac))
        return None

    result.update({
        "rssi": rssi,
        "mac": ''.join('{:02X}'.format(x) for x in teltonika_mac[:]),
        "type": device_type,
        "packet": "no packet id",
        "data": True
    })
    return result


def to_mac(addr: int):
    return ':'.join('{:02x}'.format(x) for x in addr).upper()
