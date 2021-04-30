# Parser for ATC BLE advertisements
import logging
import struct

_LOGGER = logging.getLogger(__name__)

# Sensors type dictionary
# {device type code: (device name, binary?)}
ATC_TYPE_DICT = {b'\x1A\x18': ("LYWSD03MMC", False)}

# Structured objects for data conversions
THBV_STRUCT = struct.Struct(">hBBH")
THVB_STRUCT = struct.Struct("<hHHB")


# Advertisement conversion of measurement data
def objATC_short(xobj):
    if len(xobj) == 6:
        (temp, humi, batt, volt) = THBV_STRUCT.unpack(xobj)
        return {"temperature": temp / 10, "humidity": humi, "voltage": volt / 1000, "battery": batt}
    else:
        return {}


def objATC_long(xobj):
    if len(xobj) == 7:
        (temp, humi, volt, batt) = THVB_STRUCT.unpack(xobj)
        return {"temperature": temp / 100, "humidity": humi / 100, "voltage": volt / 1000, "battery": batt}
    else:
        return {}


# Dataobject dictionary
# {dataObject_id: (converter, binary, measuring)
atc_dataobject_dict = {
    b'\x10\x16': (objATC_short, False, True),
    b'\x12\x16': (objATC_long, False, True),
}


def parse_atc(self, data, atc_index, is_ext_packet):
    try:
        # Parse BLE message in ATC format
        # Check for the atc1441 or custom format
        is_custom_adv = True if data[atc_index - 1] == 18 else False
        if is_custom_adv:
            firmware = "ATC firmware (custom)"
        else:
            firmware = "ATC firmware (ATC1441)"
        # Check for old format (ATC firmware <= 2.8)
        old_format = True if data.find(b"\x02\x01\x06", atc_index - 4, atc_index - 1) == -1 else False

        # check for BTLE msg size
        msg_length = data[2] + 3
        if msg_length != len(data):
            raise NoValidError("Invalid index")

        # check for MAC presence in message and in service data
        if is_custom_adv is True:
            atc_mac_reversed = data[atc_index + 3:atc_index + 9]
            atc_mac = atc_mac_reversed[::-1]
        else:
            atc_mac = data[atc_index + 3:atc_index + 9]

        mac_index = atc_index - (22 if is_ext_packet else 8) - (0 if old_format else 3)
        source_mac_reversed = data[mac_index:mac_index + 6]
        source_mac = source_mac_reversed[::-1]
        if atc_mac != source_mac:
            raise NoValidError("Invalid MAC address")

        # check for MAC presence in whitelist, if needed
        if self.discovery is False and source_mac_reversed not in self.whitelist:
            return None, None, None

        packet_id = data[atc_index + 16 if is_custom_adv else atc_index + 15]
        try:
            prev_packet = self.lpacket_ids[atc_index]
        except KeyError:
            # start with empty first packet
            prev_packet = None, None, None
        if prev_packet == packet_id:
            # only process new messages
            return None, None, None
        self.lpacket_ids[atc_index] = packet_id

        # extract RSSI byte
        rssi_index = 18 if is_ext_packet else msg_length - 1
        (rssi,) = struct.unpack("<b", data[rssi_index:rssi_index + 1])

        # strange positive RSSI workaround
        if rssi > 0:
            rssi = -rssi
        device_type = data[atc_index + 1:atc_index + 3]
        try:
            sensor_type, binary_data = ATC_TYPE_DICT[device_type]
        except KeyError:
            if self.report_unknown == "ATC":
                _LOGGER.info(
                    "BLE ADV from UNKNOWN ATC SENSOR: RSSI: %s, MAC: %s, ADV: %s",
                    rssi,
                    ''.join('{:02X}'.format(x) for x in atc_mac[:]),
                    data.hex()
                )
            raise NoValidError("Device unkown")

        # ATC data length = message length
        # -all bytes before ATC UUID
        # -3 bytes ATC UUID + ADtype
        # -6 bytes MAC
        # -1 Frame packet counter
        # -1 byte flags (custom adv only)
        # -1 RSSI (normal, not extended packet only)
        xdata_length = msg_length - atc_index - (11 if is_custom_adv else 10) - (0 if is_ext_packet else 1)
        if xdata_length < 6:
            raise NoValidError("Xdata length invalid")

        xdata_point = atc_index + 9

        # check if parse_atc data start and length is valid
        xdata_end_offset = (-1 if is_ext_packet else -2) + (-1 if is_custom_adv else 0)
        if xdata_length != len(data[xdata_point:xdata_end_offset]):
            raise NoValidError("Invalid data length")

        result = {
            "rssi": rssi,
            "mac": ''.join('{:02X}'.format(x) for x in atc_mac[:]),
            "type": sensor_type,
            "packet": packet_id,
            "firmware": firmware,
            "data": True,
        }
        binary = False
        measuring = False
        xvalue_typecode = data[atc_index - 1:atc_index + 1]
        xnext_point = xdata_point + xdata_length
        xvalue = data[xdata_point:xnext_point]
        resfunc, tbinary, tmeasuring = atc_dataobject_dict.get(xvalue_typecode, (None, None, None))
        if resfunc:
            binary = binary or tbinary
            measuring = measuring or tmeasuring
            result.update(resfunc(xvalue))
        else:
            if self.report_unknown == "ATC":
                _LOGGER.info(
                    "UNKNOWN dataobject from ATC DEVICE: %s, MAC: %s, ADV: %s",
                    sensor_type,
                    ''.join('{:02X}'.format(x) for x in atc_mac[:]),
                    data.hex()
                )
        binary = binary and binary_data
        return result, binary, measuring

    except NoValidError as nve:
        _LOGGER.debug("Invalid data: %s", nve)

    return None, None, None


class NoValidError(Exception):
    pass
