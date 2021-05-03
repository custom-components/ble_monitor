# Parser for Qingping BLE advertisements
import logging
import struct

_LOGGER = logging.getLogger(__name__)

# Sensors type dictionary
# {device type code: (device name, binary?)}
QINGPING_TYPE_DICT = {
    b'\x08\x01': ("CGG1", False),
    b'\x08\x07': ("CGG1", False),
    b'\x08\x09': ("CGP1W", False),
    b'\x08\x0C': ("CGD1", False),
}

# Structured objects for data conversions
TH_STRUCT = struct.Struct("<hH")
P_STRUCT = struct.Struct("<H")


# Advertisement conversion of measurement data
def obj0104(xobj):
    if len(xobj) == 4:
        (temp, humi) = TH_STRUCT.unpack(xobj)
        return {"temperature": temp / 10, "humidity": humi / 10}
    else:
        return {}


def obj0201(xobj):
    return {"battery": xobj[0]}


def obj0702(xobj):
    if len(xobj) == 2:
        (pres,) = P_STRUCT.unpack(xobj)
        return {"pressure": pres / 10}
    else:
        return {}


# Dataobject dictionary
# {dataObject_id: (converter, binary, measuring)
qingping_dataobject_dict = {
    b'\x01\x04': (obj0104, False, True),
    b'\x02\x01': (obj0201, False, True),
    b'\x07\x02': (obj0702, False, True),
}


def parse_qingping(self, data, qingping_index, is_ext_packet):
    # parse BLE message in Qingping format
    try:
        firmware = "Qingping"

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
        device_type = data[qingping_index + 3:qingping_index + 5]

        # check for MAC presence in message and in service data
        mac_index = adv_index - 14 if is_ext_packet else adv_index
        qingping_mac_reversed = data[qingping_index + 5:qingping_index + 11]
        source_mac_reversed = data[mac_index - 7:mac_index - 1]
        if qingping_mac_reversed != source_mac_reversed:
            raise NoValidError("Invalid MAC address")

        # check for MAC presence in whitelist, if needed
        if self.discovery is False and qingping_mac_reversed not in self.whitelist:
            return None, None, None
        packet_id = "no packed id"

        # extract RSSI byte
        rssi_index = 18 if is_ext_packet else msg_length - 1
        (rssi,) = struct.unpack("<b", data[rssi_index:rssi_index + 1])

        # strange positive RSSI workaround
        if rssi > 0:
            rssi = -rssi
        try:
            sensor_type, binary_data = QINGPING_TYPE_DICT[device_type]
        except KeyError:
            if self.report_unknown == "Qingping":
                _LOGGER.info(
                    "BLE ADV from UNKNOWN Qingping sensor: RSSI: %s, MAC: %s, ADV: %s",
                    rssi,
                    ''.join('{:02X}'.format(x) for x in qingping_mac_reversed[::-1]),
                    data.hex()
                )
            raise NoValidError("Device unkown")
        xdata_length = 0
        xdata_point = 0

        # parse_qingping data length = message length
        #     -all bytes before Qingping UUID
        #     -3 bytes Qingping UUID + ADtype
        #     -1 byte rssi
        #     -2 bytes sensor type
        #     -6 bytes MAC
        xdata_length += msg_length - qingping_index - 12
        if xdata_length < 3:
            raise NoValidError("Xdata length invalid")

        xdata_point += qingping_index + 11

        # check if parse_qingping data start and length is valid
        if xdata_length != len(data[xdata_point:-1]):
            raise NoValidError("Invalid data length")
        result = {
            "rssi": rssi,
            "mac": ''.join('{:02X}'.format(x) for x in qingping_mac_reversed[::-1]),
            "type": sensor_type,
            "packet": packet_id,
            "firmware": firmware,
            "data": True,
        }
        binary = False
        measuring = False

        # loop through parse_qingping payload
        # assume that the data may have several values of different types
        while True:
            xvalue_typecode = data[xdata_point:xdata_point + 2]
            try:
                xvalue_length = data[xdata_point + 1]
            except ValueError as error:
                _LOGGER.error("xvalue_length conv. error: %s", error)
                _LOGGER.error("xdata_point: %s", xdata_point)
                _LOGGER.error("data: %s", data.hex())
                result = {}
                break
            except IndexError as error:
                _LOGGER.error("Wrong xdata_point: %s", error)
                _LOGGER.error("xdata_point: %s", xdata_point)
                _LOGGER.error("data: %s", data.hex())
                result = {}
                break
            xnext_point = xdata_point + 2 + xvalue_length
            xvalue = data[xdata_point + 2:xnext_point]
            resfunc, tbinary, tmeasuring = qingping_dataobject_dict.get(xvalue_typecode, (None, None, None))
            if resfunc:
                binary = binary or tbinary
                measuring = measuring or tmeasuring
                result.update(resfunc(xvalue))
            else:
                if self.report_unknown == "Qingping":
                    _LOGGER.info(
                        "UNKNOWN dataobject from Qingping DEVICE: %s, MAC: %s, ADV: %s",
                        sensor_type,
                        ''.join('{:02X}'.format(x) for x in qingping_mac_reversed[::-1]),
                        data.hex()
                    )
            if xnext_point > msg_length - 3:
                break
            xdata_point = xnext_point
        binary = binary and binary_data
        return result, binary, measuring

    except NoValidError as nve:
        _LOGGER.debug("Invalid data: %s", nve)

    return None, None, None


class NoValidError(Exception):
    pass
