# Parser for Kegtron BLE advertisements
import logging
import struct

_LOGGER = logging.getLogger(__name__)

# Sensors type dictionary
# {device type code: (device name, binary?)}
KEGTRON_TYPE_DICT = {b'\x1E\xFF\xFF\xFF': ("Kegtron", False)}

KEGTRON_SIZE_DICT = {
    9464: "Half Corny (2.5 gal)",
    18927: "Corny (5.0 gal)",
    19711: "1/6 Barrel (5.167 gal)",
    19550: "1/6 Barrel (5.167 gal)",
    20000: "20L (5.283 gal)",
    20457: "Pin (5.404 gal)",
    29337: "1/4 Barrel (7.75 gal)",
    40915: "Firkin (10.809 gal)",
    50000: "50L (13.209 gal)",
    58674: "1/2 Barrel (15.5 gal)",
}

# Structured objects for data conversions
KEGTRON_STRUCT = struct.Struct(">HHHB20s")


# Advertisement conversion of measurement data
def objKegtron(xobj):
    if len(xobj) == 27:
        (keg_size, vol_start, vol_disp, port, port_name) = KEGTRON_STRUCT.unpack(xobj)

        if keg_size in KEGTRON_SIZE_DICT:
            keg_size = KEGTRON_SIZE_DICT[keg_size]
        else:
            keg_size = "Other (" + str(keg_size / 1000) + " L)"

        if port & (1 << 0):
            port_state = "configured"
        else:
            port_state = "unconfigured (new device)"

        if port & (1 << 4):
            port_index = 2
        else:
            port_index = 1

        if port & (1 << 6):
            port_count = "Dual port device"
        else:
            port_count = "Single port device"

        port_name = str(port_name.decode("utf-8").rstrip('\x00'))

        return {
            "keg size": keg_size,
            "volume start": vol_start / 1000,
            "volume dispensed": vol_disp / 1000,
            "port state": port_state,
            "port index": port_index,
            "port count": port_count,
            "port name": port_name
        }
    else:
        return {}


# Dataobject dictionary
# {dataObject_id: (converter, binary, measuring)
kegtron_dataobject_dict = {b'\xFF\xFF': (objKegtron, False, True)}


def parse_kegtron(self, data, kegtron_index, is_ext_packet):
    try:
        # parse BLE message in Kegtron format
        firmware = "Kegtron"

        # check for no BR/EDR + LE General discoverable mode flags
        advert_start = 29 if is_ext_packet else 14
        adv_index = data.find(b"\x1E\xFF\xFF", advert_start, advert_start + 3)
        if adv_index == -1:
            raise NoValidError("Invalid index")

        # check for BTLE msg size
        msg_length = data[2] + 3
        if msg_length != len(data):
            raise NoValidError("Invalid msg size")

        # extract sensor type
        (sensor_type_id,) = struct.Struct(">B").unpack(data[kegtron_index + 10:kegtron_index + 11])
        if sensor_type_id & (1 << 6):
            sensor_type = "Kegtron KT-200"
        else:
            sensor_type = "Kegtron KT-100"

        # check for MAC presence in message and in service data
        mac_index = adv_index - 14 if is_ext_packet else adv_index
        kegtron_mac_reversed = data[mac_index - 7:mac_index - 1]

        # check for MAC presence in whitelist, if needed
        if self.discovery is False and kegtron_mac_reversed not in self.whitelist:
            return None, None, None
        packet_id = "no packed id"

        # extract RSSI byte
        rssi_index = 18 if is_ext_packet else msg_length - 1
        (rssi,) = struct.unpack("<b", data[rssi_index:rssi_index + 1])

        # strange positive RSSI workaround
        if rssi > 0:
            rssi = -rssi

        # kegtron data length = message length
        #     -all bytes before Kegtron UUID
        #     -1 Len byte
        #     -3 bytes kegtron UUID + ADtype
        #     -1 RSSI (normal, not extended packet only)
        xdata_length = msg_length - kegtron_index - (4 if is_ext_packet else 5)
        if xdata_length != 27:
            raise NoValidError("Xdata length invalid")

        xdata_point = kegtron_index + 4

        # check if kegtron data start and length is valid
        if xdata_length != len(data[xdata_point:-1]):
            raise NoValidError("Invalid data length")
        result = {
            "rssi": rssi,
            "mac": ''.join('{:02X}'.format(x) for x in kegtron_mac_reversed[::-1]),
            "type": sensor_type,
            "packet": packet_id,
            "firmware": firmware,
            "data": True,
        }
        binary = False
        measuring = False

        xvalue_typecode = data[xdata_point - 2:xdata_point]
        xvalue_length = xdata_length
        xnext_point = xdata_point + xvalue_length
        xvalue = data[xdata_point:xnext_point]
        resfunc, tbinary, tmeasuring = kegtron_dataobject_dict.get(xvalue_typecode, (None, None, None))
        if resfunc:
            binary = binary or tbinary
            measuring = measuring or tmeasuring
            result.update(resfunc(xvalue))
        else:
            if self.report_unknown == "Kegtron":
                _LOGGER.info(
                    "UNKNOWN dataobject from Kegtron DEVICE: %s, MAC: %s, ADV: %s",
                    sensor_type,
                    ''.join('{:02X}'.format(x) for x in kegtron_mac_reversed[::-1]),
                    data.hex()
                )
        return result, binary, measuring

    except NoValidError as nve:
        _LOGGER.debug("Invalid data: %s", nve)

    return None, None, None


class NoValidError(Exception):
    pass
