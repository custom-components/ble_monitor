"""Parser for Mikrotik BLE advertisements"""
import logging
import math
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


def convert_8_8_to_float(val_1, val_2):
    """8.8 to float converter"""
    if val_1 == 0xFF and val_2 == 0xFF:
        return 0.0
    else:
        return val_1 + (val_2 / 256)


def parse_mikrotik(self, data: bytes, mac: bytes):
    """Mikrotik parser"""
    msg_length = len(data)
    firmware = "Mikrotik"
    result = {"firmware": firmware}
    if msg_length == 22:
        xvalue = data[4:]
        (
            version,
            user_data,
            _,
            acc_x_frac, acc_x,
            acc_y_frac, acc_y,
            acc_z_frac, acc_z,
            temp_frac, temp,
            uptime,
            flags,
            batt
        ) = unpack("<BBHBBBBBBBbIBB", xvalue)

        # Check if the device uses encryption
        is_encrypted = user_data & 1
        if is_encrypted is True:
            _LOGGER.info(
                "Mikrotik device with MAC address %s uses encryption, which is not supported (yet)"
                "Disable encryption if you want to use this device in Home Assistant",
                to_mac(mac),
            )
            return None

        acceleration_x = convert_8_8_to_float(acc_x, acc_x_frac)
        acceleration_y = convert_8_8_to_float(acc_y, acc_y_frac)
        acceleration_z = convert_8_8_to_float(acc_z, acc_z_frac)
        temperature = convert_8_8_to_float(temp, temp_frac)

        reed_switch = flags & 1   # if set to 1, shows that the reed switch was closed at the moment of advertising
        accel_tilt = flags & 2    # if set to 1, shows that the advertisement was sent by tilting the device
        accel_drop = flags & 4    # if set to 1, shows that the advertisement was sent by dropping the device
        impact_x = flags & 8      # if set to 1, shows that there was an impact on the x-axis at the moment of advertising
        impact_y = flags & 16     # if set to 1, shows that there was an impact on the y-axis at the moment of advertising
        impact_z = flags & 32     # if set to 1, shows that there was an impact on the z-axis at the moment of advertising

        if impact_x or impact_y or impact_z:
            impact = 1
        else:
            impact = 0

        result.update(
            {
                "version": version,
                "user data": user_data,
                "acceleration x": acceleration_x,
                "acceleration y": acceleration_y,
                "acceleration z": acceleration_z,
                "acceleration": math.sqrt(acceleration_x ** 2 + acceleration_y ** 2 + acceleration_z ** 2),
                "uptime": uptime,
                "battery": batt,
                "switch": reed_switch,
                "tilt": accel_tilt,
                "dropping": accel_drop,
                "impact": impact,
                "impact x": impact_x,
                "impact y": impact_y,
                "impact z": impact_z,
            }
        )
        if temperature == -128:
            device_type = "TG-BT5-IN"
        else:
            device_type = "TG-BT5-OUT"
        result.update({"temperature": temperature})

    else:
        if self.report_unknown == "Mikrotik":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Mikrotik DEVICE: MAC: %s, ADV: %s",
                to_mac(mac),
                data.hex()
            )
        return None

    result.update({
        "mac": to_unformatted_mac(mac),
        "type": device_type,
        "packet": "no packet id",
        "firmware": firmware,
        "data": True
    })
    return result
