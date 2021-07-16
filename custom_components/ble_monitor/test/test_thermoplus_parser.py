"""The tests for the Thermoplus ble_parser."""
import unittest
from ble_monitor.ble_parser import ble_parser


class TestThermoplus(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.lpacket_ids = {}
        cls.movements_list = {}
        cls.adv_priority = {}
        cls.trackerlist = []
        cls.report_unknown = "other"
        cls.discovery = True

    def test_thermoplus_smart_hygrometer(self):
        """Test thermoplus Smart hygrometer parser."""
        data_string = "043e29020100002716000088061d0201060302f0ff15ff110000002716000088063c0c8f01a103b9d70300c8"
        data = bytes(bytearray.fromhex(data_string))
        sensor_msg, tracker_msg = ble_parser(self, data)

        self.assertEqual(sensor_msg["firmware"], "Thermoplus")
        self.assertEqual(sensor_msg["type"], "Smart hygrometer")
        self.assertEqual(sensor_msg["mac"], "068800001627")
        self.assertEqual(sensor_msg["packet"], "no packet id")
        self.assertTrue(sensor_msg["data"])
        self.assertEqual(sensor_msg["temperature"], 24.9375)
        self.assertEqual(sensor_msg["humidity"], 58.0625)
        self.assertEqual(sensor_msg["voltage"], 3.132)
        self.assertEqual(sensor_msg["battery"], 100)
        self.assertEqual(sensor_msg["rssi"], -56)

    def test_thermoplus_Lanyard_mini_hygrometer(self):
        """Test thermoplus Lanyard/mini hygrometer parser."""
        data_string = "043e2902010000dc0e0000f1701d0201060302f0ff15ff10000000dc0e0000f1706a0b8101d70283270500b2"
        data = bytes(bytearray.fromhex(data_string))
        sensor_msg, tracker_msg = ble_parser(self, data)

        self.assertEqual(sensor_msg["firmware"], "Thermoplus")
        self.assertEqual(sensor_msg["type"], "Lanyard/mini hygrometer")
        self.assertEqual(sensor_msg["mac"], "70F100000EDC")
        self.assertEqual(sensor_msg["packet"], "no packet id")
        self.assertTrue(sensor_msg["data"])
        self.assertEqual(sensor_msg["temperature"], 24.0625)
        self.assertEqual(sensor_msg["humidity"], 45.4375)
        self.assertEqual(sensor_msg["voltage"], 2.922)
        self.assertEqual(sensor_msg["battery"], 92.2)
        self.assertEqual(sensor_msg["rssi"], -78)


if __name__ == '__main__':
    unittest.main()
