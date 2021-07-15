"""The tests for the Brifit ble_parser."""
import unittest
from ble_monitor.ble_parser import ble_parser


class TestBrifit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.lpacket_ids = {}
        cls.movements_list = {}
        cls.adv_priority = {}
        cls.trackerlist = []
        cls.report_unknown = "other"
        cls.discovery = True

    def test_brifit(self):
        """Test brifit parser."""
        data_string = "043E2B0201000085B07438C1A41F05095432303102010614FF55AA0101A4C13874B08501070A1D10F064000100D6"
        data = bytes(bytearray.fromhex(data_string))
        sensor_msg, tracker_msg = ble_parser(self, data)

        self.assertEqual(sensor_msg["firmware"], "Brifit")
        self.assertEqual(sensor_msg["type"], "T201")
        self.assertEqual(sensor_msg["mac"], "A4C13874B085")
        self.assertEqual(sensor_msg["packet"], "no packet id")
        self.assertTrue(sensor_msg["data"])
        self.assertEqual(sensor_msg["temperature"], 25.89)
        self.assertEqual(sensor_msg["humidity"], 43.36)
        self.assertEqual(sensor_msg["voltage"], 2.63)
        self.assertEqual(sensor_msg["battery"], 100)
        self.assertEqual(sensor_msg["rssi"], -42)


if __name__ == '__main__':
    unittest.main()
