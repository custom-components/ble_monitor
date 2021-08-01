# Parser for Kegtron BLE advertisements
import logging
from struct import unpack

_LOGGER = logging.getLogger(__name__)


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


def parse_kegtron(self, data, source_mac, rssi):
    # check for adstruc length
    msg_length = len(data)
    if msg_length == 31:
        firmware = "Kegtron"
        kegtron_mac = source_mac
        (device_id,) = unpack(">B", data[10:11])
        if device_id & (1 << 6):
            device_type = "Kegtron KT-200"
        else:
            device_type = "Kegtron KT-100"

        xvalue = data[4:]

        (keg_size, vol_start, vol_disp, port, port_name) = unpack(">HHHB20s", xvalue)

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

        result = {
            "keg size": keg_size,
            "volume start": vol_start / 1000,
            "port state": port_state,
            "port index": port_index,
            "port count": port_count,
            "port name": port_name
        }

        if port_index == 1:
            result.update({"volume dispensed port 1": vol_disp / 1000})
        elif port_index == 2:
            result.update({"volume dispensed port 2": vol_disp / 1000})
        else:
            return None

        # check for MAC presence in sensor whitelist, if needed
        if self.discovery is False and kegtron_mac.lower() not in self.sensor_whitelist:
            _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(kegtron_mac))
            return None

        result.update({
            "type": device_type,
            "firmware": firmware,
            "mac": ''.join('{:02X}'.format(x) for x in kegtron_mac),
            "packet": "no packet id",
            "rssi": rssi,
            "data": True,
        })
        return result
    else:
        if self.report_unknown == "Kegtron":
            _LOGGER.debug(
                "UNKNOWN dataobject from Kegtron DEVICE: MAC: %s, ADV: %s",
                to_mac(source_mac),
                data.hex()
            )
        return None


def to_mac(addr: int):
    return ':'.join('{:02x}'.format(x) for x in addr).upper()
