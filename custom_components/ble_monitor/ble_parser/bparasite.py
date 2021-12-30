"""Parser for BParasite BLE advertisements"""
import logging
from struct import unpack

_LOGGER = logging.getLogger(__name__)


def parse_bparasite(self, data, source_mac, rssi):
    """Check for adstruc length"""
    device_type = "b-parasite"
    msg_length = len(data)
    if msg_length == 22: # TODO: Use version bits?
        bpara_mac = data[14:20]
        firmware = "v2"
        (protocol, packet_id, batt, temp, humi, moist, mac, light) = unpack(">BBHHHH6sH", data[4:])
        result = {
            "temperature": temp / 1000,
            "humidity": (humi / 65536) * 100,
            "voltage": batt / 1000,
            "moisture": (moist / 65536) * 100,
            "illuminance": light,
            "data": True
        }
        adv_priority = 39
    elif msg_length == 20:
        bpara_mac = data[14:20]
        firmware = "v1"
        (protocol, packet_id, batt, temp, humi, moist, mac) = unpack(">BBHHHH6s", data[4:])
        result = {
            "temperature": temp / 1000,
            "humidity": (humi / 65536) * 100,
            "voltage": batt / 1000,
            "moisture": (moist / 65536) * 100,
            "data": True
        }
        adv_priority = 29

    else:
        if self.report_unknown == "b-parasite":
            _LOGGER.info(
                "BLE ADV from UNKNOWN b-parasite DEVICE: RSSI: %s, MAC: %s, AdStruct(%d): %s",
                rssi,
                (source_mac),
                msg_length,
                data.hex()
            )
        return None

    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and bpara_mac not in self.sensor_whitelist:
        return None

    try:
        prev_packet = self.lpacket_ids[bpara_mac]
    except KeyError:
        # start with empty first packet
        prev_packet = None
    try:
        old_adv_priority = self.adv_priority[bpara_mac]
    except KeyError:
        # start with initial adv priority
        old_adv_priority = 0
    if adv_priority > old_adv_priority:
        # always process advertisements with a higher priority
        self.adv_priority[bpara_mac] = adv_priority
    elif adv_priority == old_adv_priority:
        if self.filter_duplicates is True:
            # only process messages with same priority that have a changed packet id
            if prev_packet == packet_id:
                return None
    else:
        # do not process advertisements with lower priority
        old_adv_priority -= 1
        self.adv_priority[bpara_mac] = old_adv_priority
        return None
    self.lpacket_ids[bpara_mac] = packet_id

    result.update({
        "rssi": rssi,
        "mac": ''.join('{:02X}'.format(x) for x in bpara_mac),
        "type": device_type,
        "packet": packet_id,
        "firmware": firmware,
    })

    return result

