"""Parser for HA BLE (DIY sensors) advertisements"""
import logging
import struct

_LOGGER = logging.getLogger(__name__)


def to_int(value):
    """Convert to integer"""
    return value & 0xFF


def unsigned_to_signed(unsigned, size):
    """Convert unsigned to signed"""
    if (unsigned & (1 << size - 1)) != 0:
        unsigned = -1 * ((1 << size - 1) - (unsigned & ((1 << size - 1) - 1)))
    return unsigned


def to_sfloat(value):
    """Convert sfloat to integer"""
    if len(value) != 2:
        _LOGGER.debug("conversion to sfloat failed")
        return 0
    else:
        byte_0 = value[0]
        byte_1 = value[1]

        mantissa = unsigned_to_signed(to_int(byte_0) + ((to_int(byte_1) & 0x0F) << 8), 12)
        exponent = unsigned_to_signed(to_int(byte_1) >> 4, 4)

        return mantissa * pow(10, exponent)


def parse_ha_ble(self, service_data_list, source_mac, rssi):
    """Home Assistant BLE parser"""
    firmware = "HA BLE"
    device_type = "HA BLE DIY"
    ha_ble_mac = source_mac
    result = {}
    packet_id = None

    for service_data in service_data_list:
        if len(service_data) == service_data[0] + 1:
            meas_type = (service_data[3] << 8) | service_data[2]
            xobj = service_data[4:]
            if meas_type == 0x2A4D and len(xobj) == 1:
                (packet_id,) = struct.Struct("<B").unpack(xobj)
                result.update({"packet": packet_id})
            elif meas_type == 0x2A19 and len(xobj) == 1:
                (batt,) = struct.Struct("<B").unpack(xobj)
                result.update({"battery": batt})
            elif meas_type == 0x2A6D and len(xobj) == 4:
                (press,) = struct.Struct("<I").unpack(xobj)
                result.update({"pressure": press * 0.001})
            elif meas_type == 0x2A6E and len(xobj) == 2:
                (temp,) = struct.Struct("<h").unpack(xobj)
                result.update({"temperature": temp * 0.01})
            elif meas_type == 0x2A6F and len(xobj) == 2:
                (humi,) = struct.Struct("<H").unpack(xobj)
                result.update({"humidity": humi * 0.01})
            elif meas_type == 0x2A7B and len(xobj) == 1:
                (dewp,) = struct.Struct("<b").unpack(xobj)
                result.update({"dewpoint": dewp})
            elif meas_type == 0x2A98 and len(xobj) == 3:
                (flag, weight) = struct.Struct("<bH").unpack(xobj)
                if flag << 0 == 0:
                    weight_unit = "kg"
                    factor = 0.005
                elif flag << 0 == 1:
                    weight_unit = "lbs"
                    factor = 0.01
                else:
                    weight_unit = "kg"
                    factor = 0.005
                result.update({"weight": weight * factor, "weight unit": weight_unit})
            elif meas_type == 0X2AE2 and len(xobj) == 1:
                (value,) = struct.Struct("<B").unpack(xobj)
                result.update({"binary": bool(value)})
            elif meas_type == 0X2AEA and len(xobj) == 2:
                (count,) = struct.Struct("<H").unpack(xobj)
                if count == 0xFFFF:
                    count = "unknown"
                result.update({"count": count})
            elif meas_type == 0X2AEB and len(xobj) == 3:
                count = int.from_bytes(xobj, "little")
                if count == 0xFFFFFF:
                    count = "unknown"
                result.update({"count": count})
            elif meas_type == 0X2AF2 and len(xobj) == 4:
                (enrg,) = struct.Struct("<I").unpack(xobj)
                result.update({"energy": enrg * 0.001})
            elif meas_type == 0X2AFB and len(xobj) == 3:
                illu = int.from_bytes(xobj, "little")
                result.update({"illuminance": illu * 0.01})
            elif meas_type == 0x2B05 and len(xobj) == 3:
                power = int.from_bytes(xobj, "little")
                result.update({"power": power * 0.1})
            elif meas_type == 0x2B18 and len(xobj) == 2:
                (volt,) = struct.Struct("<H").unpack(xobj)
                result.update({"voltage": volt / 64})
            elif meas_type == 0x2BD6 and len(xobj) == 2:
                pm25 = to_sfloat(xobj)
                result.update({"pm2.5": pm25})
            elif meas_type == 0x2BD7 and len(xobj) == 2:
                pm10 = to_sfloat(xobj)
                result.update({"pm10": pm10})
            else:
                _LOGGER.debug(
                    "Unknown data received from Home Assistant BLE DIY sensor device: %s",
                    service_data.hex()
                )

    if not result:
        if self.report_unknown == "HA BLE":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Home Assistant BLE DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                service_data_list
            )
        return None

    # Check for duplicate messages
    if packet_id:
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
