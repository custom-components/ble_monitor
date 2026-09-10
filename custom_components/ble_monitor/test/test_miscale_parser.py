"""The tests for the Mi Scale ble_parser."""
from ble_monitor.ble_parser import BleParser

# Real Mi Scale V1 advertisements from
# https://github.com/custom-components/ble_monitor/issues/366
ISSUE_366_STALE_WEIGHT_REMOVED = bytes.fromhex(
    "043E2B020100008995C08C47C81F02010603021D1809FF5701C8478CC095890D161D18A29844"
    "E507051B162135C6"
)
ISSUE_366_LIVE_NON_STABILIZED = bytes.fromhex(
    "043E2B020100008995C08C47C81F02010603021D1809FF5701C8478CC095890D161D18024844"
    "E507051C110C09CC"
)

# Real Mi Scale V2 advertisements from
# https://github.com/custom-components/ble_monitor/issues/1094
ISSUE_1094_NON_STABILIZED = bytes.fromhex(
    "043E3502010001C81555E346F12902010603021B1810161B180204B2070103131A130000AC49"
    "06094D4942435309FF5701F146E35515C8B0"
)
ISSUE_1094_STABILIZED = bytes.fromhex(
    "043E3502010001C81555E346F12902010603021B1810161B180226B2070103131A15E601604A"
    "06094D4942435309FF5701F146E35515C8B6"
)
ISSUE_1094_WEIGHT_REMOVED = bytes.fromhex(
    "043E3502010001C81555E346F12902010603021B1810161B1802A6B2070103131A15E601604A"
    "06094D4942435309FF5701F146E35515C8B9"
)


class TestMiscale:
    """Tests for the MiScale parser"""
    def test_miscale_v1(self):
        """Test Mi Scale v1 parser."""
        data_string = "043e2b020100008995c08c47c81f02010603021d1809ff5701c8478cc095890d161d18a22044b20701010a1a15c5"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Mi Scale V1"
        assert sensor_msg["type"] == "Mi Scale V1"
        assert sensor_msg["mac"] == "C8478CC09589"
        assert sensor_msg["packet"] == "a22044b20701010a1a15"
        assert sensor_msg["data"]
        assert sensor_msg["non-stabilized weight"] == 87.2
        assert sensor_msg["weight unit"] == "kg"
        assert sensor_msg["weight removed"] == 1
        assert sensor_msg["stabilized"] == 1
        assert sensor_msg["rssi"] == -59

    def test_miscale_v1_ext(self):
        """Test Mi Scale v1 parser (extended advertisement)."""
        data_string = "043e390d011300008995c08c47c80100ff7fc70000000000000000001f02010603021d1809ff5701c8478cc095890d161d18821400e507040b101708"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Mi Scale V1"
        assert sensor_msg["type"] == "Mi Scale V1"
        assert sensor_msg["mac"] == "C8478CC09589"
        assert sensor_msg["packet"] == "821400e507040b101708"
        assert sensor_msg["data"]
        assert sensor_msg["non-stabilized weight"] == 0.1
        assert sensor_msg["weight unit"] == "kg"
        assert sensor_msg["weight removed"] == 1
        assert sensor_msg["stabilized"] == 0
        assert sensor_msg["rssi"] == -57

    def test_miscale_v1_ext_weight(self):
        """Test Mi Scale v1 parser (extended advertisement) with stabilized weight."""
        data_string = "043e390d011300008995c08c47c80100ff7fba0000000000000000001f02010603021d1809ff5701c8478cc095890d161d18229e43e507040b101301"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Mi Scale V1"
        assert sensor_msg["type"] == "Mi Scale V1"
        assert sensor_msg["mac"] == "C8478CC09589"
        assert sensor_msg["packet"] == "229e43e507040b101301"
        assert sensor_msg["data"]
        assert sensor_msg["non-stabilized weight"] == 86.55
        assert sensor_msg["weight unit"] == "kg"
        assert sensor_msg["weight removed"] == 0
        assert sensor_msg["stabilized"] == 1
        assert sensor_msg["weight"] == 86.55
        assert sensor_msg["rssi"] == -70

    def test_miscale_v2(self):
        """Test Mi Scale v2 parser."""
        data_string = "043e2402010001ef148244dedf1802010603021b1810161b180204b207010112101a0000a852ae"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Mi Scale V2"
        assert sensor_msg["type"] == "Mi Scale V2"
        assert sensor_msg["mac"] == "DFDE448214EF"
        assert sensor_msg["packet"] == "0204b207010112101a0000a852"
        assert sensor_msg["data"]
        assert sensor_msg["non-stabilized weight"] == 105.8
        assert sensor_msg["weight unit"] == "kg"
        assert sensor_msg["weight removed"] == 0
        assert sensor_msg["stabilized"] == 0
        assert sensor_msg["rssi"] == -82

    def test_miscale_v2_impedance(self):
        """Test Mi Scale v2 parser."""
        data_string = "043e2402010001ef148244dedf1802010603021b1810161b180226b20705040f0201ac018642be"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Mi Scale V2"
        assert sensor_msg["type"] == "Mi Scale V2"
        assert sensor_msg["mac"] == "DFDE448214EF"
        assert sensor_msg["packet"] == "0226b20705040f0201ac018642"
        assert sensor_msg["data"]
        assert sensor_msg["non-stabilized weight"] == 85.15
        assert sensor_msg["weight unit"] == "kg"
        assert sensor_msg["weight removed"] == 0
        assert sensor_msg["stabilized"] == 1
        assert sensor_msg["impedance"] == 428
        assert sensor_msg["rssi"] == -66

    def test_miscale_v1_stale_first_packet(self):
        """Test that the stale first packet from issue 366 remains suppressed."""
        ble_parser = BleParser(filter_duplicates=True)

        sensor_msg, _ = ble_parser.parse_raw_data(ISSUE_366_STALE_WEIGHT_REMOVED)
        assert sensor_msg is None

        sensor_msg, _ = ble_parser.parse_raw_data(ISSUE_366_STALE_WEIGHT_REMOVED)
        assert sensor_msg is None

        sensor_msg, _ = ble_parser.parse_raw_data(ISSUE_366_LIVE_NON_STABILIZED)
        assert sensor_msg["non-stabilized weight"] == 87.4
        assert sensor_msg["stabilized"] == 0
        assert sensor_msg["weight removed"] == 0
        assert "weight" not in sensor_msg

    def test_miscale_v2_first_stabilized_packet_and_duplicate(self):
        """Test that the first stable packet is accepted and its repeat is ignored."""
        ble_parser = BleParser(filter_duplicates=True)

        sensor_msg, _ = ble_parser.parse_raw_data(ISSUE_1094_STABILIZED)
        assert sensor_msg["weight"] == 95.2
        assert sensor_msg["impedance"] == 486

        sensor_msg, _ = ble_parser.parse_raw_data(ISSUE_1094_STABILIZED)
        assert sensor_msg is None

    def test_miscale_v2_duplicate_sequence(self):
        """Test duplicate filtering with the real sequence from issue 1094."""
        ble_parser = BleParser(filter_duplicates=True)

        sensor_msg, _ = ble_parser.parse_raw_data(ISSUE_1094_NON_STABILIZED)
        assert sensor_msg["non-stabilized weight"] == 94.3
        assert "weight" not in sensor_msg

        sensor_msg, _ = ble_parser.parse_raw_data(ISSUE_1094_STABILIZED)
        assert sensor_msg["weight"] == 95.2
        assert sensor_msg["impedance"] == 486

        sensor_msg, _ = ble_parser.parse_raw_data(ISSUE_1094_STABILIZED)
        assert sensor_msg is None

        sensor_msg, _ = ble_parser.parse_raw_data(ISSUE_1094_WEIGHT_REMOVED)
        assert sensor_msg["weight removed"] == 1
        assert "weight" not in sensor_msg

    def test_miscale_v2_same_measurement_different_timestamp(self):
        """Test that timestamps distinguish otherwise identical measurements."""
        # Create a protocol-valid synthetic variant of the real stable packet by
        # changing only the timestamp's seconds byte.
        second_timestamp = bytearray(ISSUE_1094_STABILIZED)
        service_payload = bytes.fromhex("0226B2070103131A15E601604A")
        payload_start = ISSUE_1094_STABILIZED.index(service_payload)
        second_timestamp[payload_start + 8] = 0x16

        ble_parser = BleParser(filter_duplicates=True)
        first_msg, _ = ble_parser.parse_raw_data(ISSUE_1094_STABILIZED)
        second_msg, _ = ble_parser.parse_raw_data(bytes(second_timestamp))

        assert first_msg["weight"] == second_msg["weight"] == 95.2
        assert first_msg["impedance"] == second_msg["impedance"] == 486
        assert first_msg["packet"] != second_msg["packet"]
