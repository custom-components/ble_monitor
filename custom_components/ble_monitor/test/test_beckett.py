"""The tests for the Beckett ble_parser."""

import logging

from ble_monitor.ble_parser import BleParser

MFG_BLE_PREFIX = [0x06, 0x1A]  # 0x061A aka 1562
MFG_ID = 0x061A


def unhex(data_string):
    return bytes(bytearray.fromhex(data_string))


# [NEW] Device F5:42:81:A8:14:8E rwb_77100200426

# USE sudo hcidump -x -R -m=0x061a

INPUT_PACKET = "043E390D011300018E14A88142F50100FF7FBC0000000000000000001F0201061BFF1A0606CCC408C0CD0BDECD2BB3DA6582F160611063411B615029"

# The packet above, re-encoded with product key 6308 (not supported,
# reported in issue #1501)
UNKNOWN_PRODUCT_PACKET = "043E390D011300018E14A88142F50100FF7FBC0000000000000000001F0201061BFF1A0606CCDCB757EBB645FBB4FE1E143F1D537E1A8AA61582A931"

UNKNOWN_PRODUCT_LOG = (
    "BLE ADV from UNKNOWN Beckett DEVICE: MAC: F5:42:81:A8:14:8E, "
    "ADV: 1bff1a0606ccdcb757ebb645fbb4fe1e143f1d537e1a8aa61582a931"
)

# Beckett manufacturer record with only two bytes after the company id
SHORT_PACKET = "043E15020100018E14A88142F50902010605FF1A060102BC"

KNOWN_OUTPUT = {
    "firmware": "Beckett",
    "data": True,
    "packet": "no packet id",
    "type": "Genisys7505",
    "burner_product": "Genisys7505",
    "burner_device": "Genisys_7505_7575",
    "burner_serial": 77100,
    "burner_is_bootloader": False,
    "burner_advertisement_version": 1,
    "burner_connectable": True,
    "burner_state": "Standby",
    "burner_last_end_cause": "CFHEnded",
    "burner_cycle_count": 20319,
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

    def test_beckett_unknown_product(self, caplog):
        """Unknown product key: no data, no warning (issue #1501)."""
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(
            unhex(UNKNOWN_PRODUCT_PACKET)
        )
        assert sensor_msg is None
        assert tracker_msg is None
        assert not [r for r in caplog.records if r.levelno >= logging.WARNING]

    def test_beckett_unknown_product_report_unknown(self, caplog):
        """Unknown product key with report_unknown logs the advertisement."""
        ble_parser = BleParser(report_unknown="Beckett")
        with caplog.at_level(logging.INFO):
            sensor_msg, tracker_msg = ble_parser.parse_raw_data(
                unhex(UNKNOWN_PRODUCT_PACKET)
            )
        assert sensor_msg is None
        assert tracker_msg is None
        assert [
            r for r in caplog.records
            if r.levelno == logging.INFO and r.getMessage() == UNKNOWN_PRODUCT_LOG
        ]
        assert not [r for r in caplog.records if r.levelno >= logging.WARNING]

    def test_beckett_report_unknown_known_device(self, caplog):
        """report_unknown does not drop the data of a supported device."""
        ble_parser = BleParser(report_unknown="Beckett")
        with caplog.at_level(logging.INFO):
            sensor_msg, tracker_msg = ble_parser.parse_raw_data(
                unhex(INPUT_PACKET)
            )
        assert sensor_msg == KNOWN_OUTPUT
        assert "UNKNOWN Beckett DEVICE" not in caplog.text

    def test_beckett_short_payload(self, caplog):
        """A too short manufacturer record gives no data and no warning."""
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(unhex(SHORT_PACKET))
        assert sensor_msg is None
        assert tracker_msg is None
        assert not [r for r in caplog.records if r.levelno >= logging.WARNING]
