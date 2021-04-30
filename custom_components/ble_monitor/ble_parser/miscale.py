# Parser for Xiaomi Mi Scale BLE advertisements
import logging
import struct

_LOGGER = logging.getLogger(__name__)

# Sensors type dictionary
# {device type code: (device name, binary?)}
MISCALE_TYPE_DICT = {
    b'\x1D\x18': ("Mi Scale V1", True),
    b'\x1B\x18': ("Mi Scale V2", True),
}

# Structured objects for data conversions
SCALE_V1_STRUCT = struct.Struct("<BH7x")
SCALE_V2_STRUCT = struct.Struct("<BB7xHH")


# Advertisement conversion of measurement data
def obj1d18(xobj):
    # MI Scale V1 BLE advertisements
    if len(xobj) == 10:
        (controlByte, weight) = SCALE_V1_STRUCT.unpack(xobj)
        isStabilized = controlByte & (1 << 5)
        weightRemoved = controlByte & (1 << 7)

        if controlByte & (1 << 0):
            weight = weight / 100
            weight_unit = 'lbs'
        elif controlByte & (1 << 4):
            weight = weight / 100
            weight_unit = 'jin'
        else:
            weight = weight / 200
            weight_unit = 'kg'

        if isStabilized:
            return {
                "weight": weight,
                "non-stabilized weight": weight,
                "weight unit": weight_unit,
                "weight removed": 0 if weightRemoved == 0 else 1,
                "stabilized": 0 if isStabilized == 0 else 1
            }
        else:
            return {
                "non-stabilized weight": weight,
                "weight unit": weight_unit,
                "weight removed": 0 if weightRemoved == 0 else 1,
                "stabilized": 0 if isStabilized == 0 else 1
            }
    else:
        return {}


def obj1b18(xobj):
    # MI Scale V2 BLE advertisements
    if len(xobj) == 13:
        (measunit, controlByte, impedance, weight) = SCALE_V2_STRUCT.unpack(xobj)
        hasImpedance = controlByte & (1 << 1)
        isStabilized = controlByte & (1 << 5)
        weightRemoved = controlByte & (1 << 7)

        if measunit & (1 << 4):
            # measurement in Chinese Catty unit
            weight = weight / 100
            weight_unit = "jin"
        elif measunit == 3:
            # measurement in lbs
            weight = weight / 100
            weight_unit = "lbs"
        elif measunit == 2:
            # measurement in kg
            weight = weight / 200
            weight_unit = "kg"
        else:
            # measurement in unknown unit
            weight = weight / 100
            weight_unit = None

        if isStabilized:
            if hasImpedance:
                return {
                    "weight": weight,
                    "non-stabilized weight": weight,
                    "weight unit": weight_unit,
                    "impedance": impedance,
                    "weight removed": 0 if weightRemoved == 0 else 1,
                    "stabilized": 0 if isStabilized == 0 else 1
                }
            else:
                return {
                    "weight": weight,
                    "non-stabilized weight": weight,
                    "weight unit": weight_unit,
                    "weight removed": 0 if weightRemoved == 0 else 1,
                    "stabilized": 0 if isStabilized == 0 else 1
                }
        else:
            return {
                "non-stabilized weight": weight,
                "weight unit": weight_unit,
                "weight removed": 0 if weightRemoved == 0 else 1,
                "stabilized": 0 if isStabilized == 0 else 1
            }
    else:
        return {}


# Dataobject dictionary
# {dataObject_id: (converter, binary, measuring)
miscale_dataobject_dict = {
    b'\x1B\x18': (obj1b18, True, True),
    b'\x1D\x18': (obj1d18, True, True),
}


def parse_miscale(self, data, miscale_index, is_ext_packet):
    try:
        # parse BLE advertisement in Xiaomi Mi Scale (v1 or v2) format

        # check for no BR/EDR + LE General discoverable mode flags
        advert_start = 29 if is_ext_packet else 14
        adv_index = data.find(b"\x02\x01\x06", advert_start, 3 + advert_start)
        if adv_index == -1:
            raise NoValidError("Invalid index")

        # check for BTLE msg size
        msg_length = data[2] + 3
        if msg_length != len(data):
            raise NoValidError("Invalid msg size")

        # extract device type
        device_type = data[miscale_index + 5:miscale_index + 7]

        # check for MAC presence in message and in service data
        mac_index = adv_index - 14 if is_ext_packet else adv_index
        miscale_mac_reversed = data[mac_index - 7:mac_index - 1]
        miscale_mac = miscale_mac_reversed[::-1]

        # check for MAC presence in whitelist, if needed
        if self.discovery is False and miscale_mac not in self.whitelist:
            return None, None, None

        # extract RSSI byte
        rssi_index = 18 if is_ext_packet else msg_length - 1
        (rssi,) = struct.unpack("<b", data[rssi_index:rssi_index + 1])

        # strange positive RSSI workaround
        if rssi > 0:
            rssi = -rssi
        device_type = data[miscale_index + 1:miscale_index + 3]
        try:
            sensor_type, binary_data = MISCALE_TYPE_DICT[device_type]
        except KeyError:
            if self.report_unknown == "Mi Scale":
                _LOGGER.info(
                    "BLE ADV from UNKNOWN MI SCALE SENSOR: RSSI: %s, MAC: %s, ADV: %s",
                    rssi,
                    ''.join('{:02X}'.format(x) for x in miscale_mac[:]),
                    data.hex()
                )
            raise NoValidError("Device unkown")

        firmware = sensor_type

        # Mi Scale data length = message length
        # -all bytes before Mi Scale UUID
        # -3 bytes UUID + ADtype
        # -1 RSSI (normal, not extended packet only)
        xdata_length = msg_length - miscale_index - 3 - (0 if is_ext_packet else 1)
        if xdata_length != (10 if sensor_type == "Mi Scale V1" else 13):
            raise NoValidError("Xdata length invalid")

        xdata_point = miscale_index + 3
        xnext_point = xdata_point + xdata_length
        xvalue = data[xdata_point:xnext_point]

        packet_id = xvalue.hex()
        try:
            prev_packet = self.lpacket_ids[miscale_index]
        except KeyError:
            # start with empty first packet
            prev_packet = None, None, None
        if prev_packet == packet_id:
            # only process new messages
            return None, None, None
        self.lpacket_ids[miscale_index] = packet_id

        result = {
            "rssi": rssi,
            "mac": ''.join('{:02X}'.format(x) for x in miscale_mac[:]),
            "type": sensor_type,
            "packet": packet_id,
            "firmware": firmware,
            "data": True,
        }

        binary = False
        measuring = False
        xvalue_typecode = data[miscale_index + 1:miscale_index + 3]

        resfunc, tbinary, tmeasuring = miscale_dataobject_dict.get(xvalue_typecode, (None, None, None))
        if resfunc:
            binary = binary or tbinary
            measuring = measuring or tmeasuring
            result.update(resfunc(xvalue))
        else:
            if self.report_unknown == "Mi Scale":
                _LOGGER.info(
                    "UNKNOWN dataobject from Mi Scale DEVICE: %s, MAC: %s, ADV: %s",
                    sensor_type,
                    ''.join('{:02X}'.format(x) for x in miscale_mac[:]),
                    data.hex()
                )
        binary = binary and binary_data
        return result, binary, measuring

    except NoValidError as nve:
        _LOGGER.debug("Invalid data: %s", nve)

    return None, None, None


class NoValidError(Exception):
    pass
