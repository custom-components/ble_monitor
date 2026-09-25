"""Parser for HolyIOT BLE advertisements"""
import logging
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


def parse_holyiot(self, data: str, mac: bytes):
    """HolyIOT parser"""
    msg_length = len(data)
    firmware = "HolyIOT"
    result = {"firmware": firmware}

    if msg_length == 17:
        device_type = "HolyIOT BLE tracker"
        holyiot_mac = data[6:12]
        if holyiot_mac != mac:
            _LOGGER.debug(
                "HolyIOT MAC address doesn't match data MAC address. Data: %s with source mac: %s and HolyIOT mac: %s",
                data.hex(),
                mac,
                holyiot_mac,
            )
            return None
        batt = data[5]
        meas_type = data[14]

        if meas_type == 0:
            return None
        elif meas_type == 1:
            measurement_type = "temperature"
            value, fraction = unpack(">bB", data[15:17])
            if value >= 0:
                meas_value = value + fraction / 100
            else:
                meas_value = value - fraction / 100
        elif meas_type == 2:
            measurement_type = "pressure"
            value, = unpack(">h", data[15:17])
            meas_value = 80000 + value
        elif meas_type == 3:
            measurement_type = "humidity"
            meas_value = data[15]
        elif meas_type == 4:
            measurement_type = "vibration"
            meas_value = data[15]
        elif meas_type == 5:
            measurement_type = "side"
            meas_value = data[15]
        elif meas_type == 6:
            measurement_type = "button"
            if data[15] == 1:
                meas_value = "toggle"
            else:
                meas_value = "no press"
        else:
            return None
        result.update(
            {
                measurement_type: meas_value,
                "battery": batt
            }
        )
    elif msg_length == 13:
        # HolyIOT B1 (B1-B, B1-S, holyiot-25055 board) status frame on
        # 0x180A service data: <frame type> <MAC> <settings byte> <battery %>
        # frame type: 0x01 = beacon mode, 0x02 = iBeacon mode (observed);
        # the settings byte changes with adv interval/tx power config (0x04 -> 0xf8),
        # meaning not fully reverse-engineered - not parsed.
        device_type = "HolyIOT Beacon"
        if data[4] not in (0x01, 0x02):
            return None
        holyiot_mac = data[5:11]
        if holyiot_mac != mac:
            _LOGGER.debug(
                "HolyIOT MAC address doesn't match data MAC address. Data: %s with source mac: %s and HolyIOT mac: %s",
                data.hex(),
                mac,
                holyiot_mac,
            )
            return None
        result.update({"battery": data[12]})
    else:
        if self.report_unknown == "HolyIOT":
            _LOGGER.info(
                "BLE ADV from UNKNOWN HolyIOT DEVICE: MAC: %s, ADV: %s",
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
