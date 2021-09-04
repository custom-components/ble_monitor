# Parser for Cleargrass or Qingping BLE advertisements
import logging
from struct import unpack

_LOGGER = logging.getLogger(__name__)


def parse_qingping(self, data, source_mac, rssi):
    # check for adstruc length
    msg_length = len(data)
    if msg_length > 12 and data[4] == 0x08:
        firmware = "Qingping"
        device_id = data[5]
        if device_id == 0x01:
            device_type = "CGG1"
        elif device_id == 0x07:
            device_type = "CGG1"
        elif device_id == 0x09:
            device_type = "CGP1W"
        elif device_id == 0x0C:
            device_type = "CGD1"
        else:
            device_type = None

        qingping_mac_reversed = data[6:12]
        qingping_mac = qingping_mac_reversed[::-1]

        result = {"rssi": rssi}
        xdata_point = 14
        while xdata_point < msg_length:
            xdata_id = data[xdata_point - 2]
            xdata_size = data[xdata_point - 1]
            if xdata_point + xdata_size <= msg_length:
                if xdata_id == 0x01 and xdata_size == 4:
                    (temp, humi) = unpack("<hH", data[xdata_point:xdata_point + xdata_size])
                    result.update({"temperature": temp / 10, "humidity": humi / 10})
                elif xdata_id == 0x02 and xdata_size == 1:
                    batt = data[xdata_point]
                    result.update({"battery": batt})
                elif xdata_id == 0x07 and xdata_size == 2:
                    (pres,) = unpack("<H", data[xdata_point:xdata_point + xdata_size])
                    result.update({"pressure": pres / 10})
                else:
                    _LOGGER.debug(
                        "Unknown data received from Qingping device: %s",
                        data[xdata_point - 2:].hex()
                    )
            xdata_point += xdata_size + 2
    else:
        device_type = None
    if device_type is None:
        if self.report_unknown == "Qingping":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Qingping DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # check for MAC presence in message and in service data
    if qingping_mac != source_mac:
        _LOGGER.debug("Invalid MAC address for Qingping device")
        return None

    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and qingping_mac not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(qingping_mac))
        return None

    result.update({
        "rssi": rssi,
        "mac": ''.join('{:02X}'.format(x) for x in qingping_mac[:]),
        "type": device_type,
        "packet": "no packet id",
        "firmware": firmware,
        "data": True
    })
    return result


def to_mac(addr: int):
    return ':'.join('{:02x}'.format(x) for x in addr).upper()
