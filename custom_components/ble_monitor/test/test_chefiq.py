"""The tests for the Chef iQ ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestChefiQ:
    """Tests for the Chef iQ  parser"""

    def test_chefiq_cq60(self):
        """Test Chef iQ  parser for CQ60 Chef iQ wireless meat thermometer"""
        data_string = "043E250201000073332e3638d91902010615ffcd0501406313c000c900c900ca00cb00c0008d11CC"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Chef iQ"
        assert sensor_msg["type"] == "CQ60"
        assert sensor_msg["mac"] == "D938362E3373"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["meat temperature"] == 20.1
        assert sensor_msg["temperature probe tip"] == 20.1
        assert sensor_msg["temperature probe 1"] == 20.2
        assert sensor_msg["temperature probe 2"] == 20.3
        assert sensor_msg["temperature probe 3"] == 19
        assert sensor_msg["ambient temperature"] == 19.2
        assert sensor_msg["battery"] == 99
        assert sensor_msg["rssi"] == -52

    def test_chefiq_cq60_sentinels(self):
        """CQ60 emits 0x7FFB / 0xFE on probe rings that are not in contact
        with anything. The parser should mask these as ``None`` so that the
        downstream Home Assistant entities become *unavailable* instead of
        reporting bogus 3,276 °C values that trip the temperature
        device-class limits.
        """
        # Same packet header as the working test, but every ring temperature
        # is the not-measured sentinel:
        #   meat / tip / probe 1 / probe 2 / ambient = 0xFB7F (LE 0x7FFB)
        #   probe 3 = 0xFE
        data_string = "043E250201000073332e3638d91902010615ffcd05014063FEFB7FFB7FFB7FFB7FFB7FFB7F8d11CC"
        data = bytes(bytearray.fromhex(data_string))
        ble_parser = BleParser()
        sensor_msg, _ = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Chef iQ"
        assert sensor_msg["type"] == "CQ60"
        assert sensor_msg["meat temperature"] is None
        assert sensor_msg["temperature probe tip"] is None
        assert sensor_msg["temperature probe 1"] is None
        assert sensor_msg["temperature probe 2"] is None
        assert sensor_msg["temperature probe 3"] is None
        assert sensor_msg["ambient temperature"] is None
        # Battery and identity fields still populate normally
        assert sensor_msg["battery"] == 99
