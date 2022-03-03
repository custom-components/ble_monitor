"""Parser for HA BLE (DIY sensors) advertisements"""
import logging
import struct

_LOGGER = logging.getLogger(__name__)


def parse_uint(data_obj, factor=1):
    """convert bytes (as unsigned integer) and factor to float"""
    decimal_places = -int(f'{factor:e}'.split('e')[-1])
    return round(int.from_bytes(data_obj, "little", signed=False) * factor, decimal_places)


def parse_int(data_obj, factor=1):
    """convert bytes (as signed integer) and factor to float"""
    decimal_places = -int(f'{factor:e}'.split('e')[-1])
    return round(int.from_bytes(data_obj, "little", signed=True) * factor, decimal_places)


def parse_float(data_obj, factor=1):
    """convert bytes (as float) and factor to float"""
    decimal_places = -int(f'{factor:e}'.split('e')[-1])
    if len(data_obj) == 2:
        [val] = struct.unpack('e', data_obj)
    if len(data_obj) == 4:
        [val] = struct.unpack('f', data_obj)
    elif len(data_obj) == 8:
        [val] = struct.unpack('d', data_obj)
    else:
        _LOGGER.error("only 2, 4 or 8 byte long floats are supported in HA BLE")
        return None
    return round(val * factor, decimal_places)


def parse_string(data_obj, factor=None):
    """convert bytes to string"""
    return data_obj.decode('UTF-8')


def parse_mac(data_obj, factor=None):
    """convert bytes to mac"""
    return data_obj  # TO DO


dispatch = {
    0x00: parse_uint,
    0x01: parse_int,
    0x02: parse_float,
    0x03: parse_string,
    0x04: parse_mac,
}

DATA_MEAS_DICT = {
    0x00: ["packet", 1],
    0x01: ["battery", 1],
    0x02: ["temperature", 0.01],
    0x03: ["humidity", 0.01],
    0x04: ["pressure", 0.01],
    0x05: ["illuminance", 0.01],
    0x06: ["weight", 0.01],
    0x07: ["weight unit", None],
    0x08: ["dew point", 0.01],
    0x09: ["count", 1],
    0x0A: ["energy", 0.001],
    0x0B: ["power", 0.01],
    0x0C: ["voltage", 0.001],
    0x0D: ["pm2.5", 1],
    0x0E: ["pm10", 1],
    0x0F: ["binary", 1],
    0x10: ["switch", 1],
    0x11: ["opening", 1],
}


def parse_ha_ble(self, data, source_mac, rssi):
    """Home Assistant BLE parser"""
    firmware = "HA BLE"
    device_type = "HA BLE DIY"
    ha_ble_mac = source_mac
    result = {}
    packet_id = None

    payload = data[4:]
    payload_length = len(payload)
    payload_start = 0

    while payload_length >= payload_start + 1:
        obj_control_byte = payload[payload_start]
        obj_data_length = (obj_control_byte >> 0) & 31  # 5 bits (0-4)
        obj_data_format = (obj_control_byte >> 5) & 7  # 3 bits (5-7)
        obj_meas_type = payload[payload_start + 1]
        next_start = payload_start + 1 + obj_data_length
        if payload_length < next_start:
            _LOGGER.debug("Invalid payload data length, payload: %s", payload.hex())
            break

        if obj_data_length != 0:
            if obj_meas_type in DATA_MEAS_DICT:
                meas_data = payload[payload_start + 2:next_start]
                meas_type = DATA_MEAS_DICT[obj_meas_type][0]
                meas_factor = DATA_MEAS_DICT[obj_meas_type][1]
                meas = dispatch[obj_data_format](meas_data, meas_factor)
                result.update({meas_type: meas})
            else:
                if self.report_unknown == "HA BLE":
                    _LOGGER.error("UNKNOWN dataobject in HA BLE payload! Adv: %s", data.hex())
        payload_start = next_start

    if not result:
        if self.report_unknown == "HA BLE":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Home Assistant BLE DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # Check for duplicate messages
    if "packet" in result:
        packet_id = result["packet"]
        try:
            prev_packet = self.lpacket_ids[ha_ble_mac]
        except KeyError:
            # start with empty first packet
            prev_packet = None
        if prev_packet == packet_id:
            # only process new messages
            if self.filter_duplicates is True:
                return None
        self.lpacket_ids[ha_ble_mac] = packet_id
    else:
        result.update({"packet": "no packet id"})

    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and ha_ble_mac not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(ha_ble_mac))
        return None

    result.update({
        "rssi": rssi,
        "mac": ''.join(f'{i:02X}' for i in ha_ble_mac),
        "type": device_type,
        "firmware": firmware,
        "data": True
    })
    return result


def to_mac(addr: int):
    """Return formatted MAC address"""
    return ':'.join(f'{i:02X}' for i in addr)
