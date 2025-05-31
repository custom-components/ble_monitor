"""The tests for the Beckett ble_parser."""

from ble_monitor.ble_parser import BleParser

MFG_BLE_PREFIX = [0x06, 0x1A]  # 0x061A aka 1562
MFG_ID = 0x061A


def unhex(data_string):
    return bytes(bytearray.fromhex(data_string))


# [NEW] Device F5:42:81:A8:14:8E rwb_77100200426

# USE sudo hcidump -x -R -m=0x061a

INPUT_PACKET = "043E390D011300018E14A88142F50100FF7FBC0000000000000000001F0201061BFF1A0606CCC408C0CD0BDECD2BB3DA6582F160611063411B615029"

KNOWN_OUTPUT = {
    "firmware": "Beckett",
    "data": True,
    "packet": "no packet id",
    "type": "Genisys7505",
    "product_id": "Genisys7505",
    "device_name_key": "Genisys_7505_7575",
    "serial": 77100,
    "is_bootloader": False,
    "advertisement_version": 1,
    "connectable": True,
    "state": "Standby",
    "last_end_cause": "CFHEnded",
    "cycle_count": 20319,
    "mac": "F54281A8148E",
    "rssi": -68,
    "local_name": "",
}


class TestBeckett:
    """Tests for the Backett parser"""

    def test_beckett(self):
        ble_parser = BleParser()
        # I think actually it is not like this, just padded, but whatever
        # bleak strips off the mfg id -
        hass_mfg_data = unhex(INPUT_PACKET)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(hass_mfg_data)
        assert sensor_msg
        assert sensor_msg == KNOWN_OUTPUT
