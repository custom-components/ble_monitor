"""The tests for the Ruuvitag ble_parser."""
import unittest
from ble_monitor.ble_parser import ble_parser


class TestRuuviTag(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.lpacket_ids = {}
        cls.movements_list = {}
        cls.adv_priority = {}
        cls.trackerlist = []
        cls.report_unknown = "other"
        cls.discovery = True

    def test_ruuvitag_v2(self):
        """Test ruuvitag v2 parser."""
        data_string = "043E2A0201030157168974A5F41E0201060303AAFE1616AAFE10EE037275752E76692F23416A7759414D4666CD"
        data = bytes(bytearray.fromhex(data_string))
        sensor_msg, tracker_msg = ble_parser(self, data)

        self.assertEqual(sensor_msg["firmware"], "Ruuvitag V2")
        self.assertEqual(sensor_msg["type"], "Ruuvitag")
        self.assertEqual(sensor_msg["mac"], "F4A574891657")
        self.assertEqual(sensor_msg["packet"], "no packet id")
        self.assertTrue(sensor_msg["data"])
        self.assertEqual(sensor_msg["temperature"], 24.0)
        self.assertEqual(sensor_msg["humidity"], 30.0)
        self.assertEqual(sensor_msg["pressure"], 995.03)
        self.assertEqual(sensor_msg["rssi"], -51)

    def test_ruuvitag_v3(self):
        """Test ruuvitag v3 parser."""
        data_string = "043E2502010301F27A52FAD4CD1902010415FF990403291A1ECE1EFC18F94202CA0B53000000009E"
        data = bytes(bytearray.fromhex(data_string))
        sensor_msg, tracker_msg = ble_parser(self, data)

        self.assertEqual(sensor_msg["firmware"], "Ruuvitag V3")
        self.assertEqual(sensor_msg["type"], "Ruuvitag")
        self.assertEqual(sensor_msg["mac"], "CDD4FA527AF2")
        self.assertEqual(sensor_msg["packet"], "no packet id")
        self.assertTrue(sensor_msg["data"])
        self.assertEqual(sensor_msg["temperature"], 26.3)
        self.assertEqual(sensor_msg["humidity"], 20.5)
        self.assertEqual(sensor_msg["pressure"], 1027.66)
        self.assertEqual(sensor_msg["acceleration"], 2118.6958252660997)
        self.assertEqual(sensor_msg["acceleration x"], -1000)
        self.assertEqual(sensor_msg["acceleration y"], -1726)
        self.assertEqual(sensor_msg["acceleration z"], 714)
        self.assertEqual(sensor_msg["voltage"], 2.899)
        self.assertEqual(sensor_msg["battery"], 89.9)
        self.assertEqual(sensor_msg["rssi"], -98)

    def test_ruuvitag_v4(self):
        """Test ruuvitag v4 parser."""
        data_string = "043E2B02010301C4C437D31ED01F0201060303AAFE1716AAFE10F6037275752E76692F2342475159414D71387798"
        data = bytes(bytearray.fromhex(data_string))
        sensor_msg, tracker_msg = ble_parser(self, data)

        self.assertEqual(sensor_msg["firmware"], "Ruuvitag V4")
        self.assertEqual(sensor_msg["type"], "Ruuvitag")
        self.assertEqual(sensor_msg["mac"], "D01ED337C4C4")
        self.assertEqual(sensor_msg["packet"], "no packet id")
        self.assertTrue(sensor_msg["data"])
        self.assertEqual(sensor_msg["temperature"], 24.0)
        self.assertEqual(sensor_msg["humidity"], 50.0)
        self.assertEqual(sensor_msg["pressure"], 1019.0)
        self.assertEqual(sensor_msg["rssi"], -104)

    def test_ruuvitag_v5(self):
        """Test ruuvitag v5 parser."""
        data_string = "043E2B02010301F27A52FAD4CD1F0201061BFF990405138A5F61C4F0FFE4FFDC0414C5B6EC29B3F27A52FAD4CDBC"
        data = bytes(bytearray.fromhex(data_string))

        # get the mac to fill in an initial packet id and movement
        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        self.lpacket_ids[mac] = "10674"
        self.movements_list[mac] = "1"

        sensor_msg, tracker_msg = ble_parser(self, data)

        self.assertEqual(sensor_msg["firmware"], "Ruuvitag V5")
        self.assertEqual(sensor_msg["type"], "Ruuvitag")
        self.assertEqual(sensor_msg["mac"], "CDD4FA527AF2")
        self.assertEqual(sensor_msg["packet"], 10675)
        self.assertTrue(sensor_msg["data"])
        self.assertEqual(sensor_msg["temperature"], 25.01)
        self.assertEqual(sensor_msg["humidity"], 61.04)
        self.assertEqual(sensor_msg["pressure"], 1004.16)
        self.assertEqual(sensor_msg["acceleration"], 1044.9956937710317)
        self.assertEqual(sensor_msg["acceleration x"], -28)
        self.assertEqual(sensor_msg["acceleration y"], -36)
        self.assertEqual(sensor_msg["acceleration z"], 1044)
        self.assertEqual(sensor_msg["voltage"], 3.181)
        self.assertEqual(sensor_msg["battery"], 100)
        self.assertEqual(sensor_msg["tx power"], 4)
        self.assertEqual(sensor_msg["motion"], 1)
        self.assertEqual(sensor_msg["motion timer"], 1)
        self.assertEqual(sensor_msg["rssi"], -68)


if __name__ == '__main__':
    unittest.main()
