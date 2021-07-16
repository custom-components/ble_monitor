"""The tests for the Govee ble_parser."""
import unittest
from ble_monitor.ble_parser import ble_parser


class TestGovee(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.lpacket_ids = {}
        cls.movements_list = {}
        cls.adv_priority = {}
        cls.trackerlist = []
        cls.report_unknown = "other"
        cls.discovery = True

    def test_Govee_H5074(self):
        """Test Govee H5074 parser."""
        data_string = "043e1702010400aabb611d12e00b0aff88ec0088078c116402a6"
        data = bytes(bytearray.fromhex(data_string))
        sensor_msg, tracker_msg = ble_parser(self, data)

        self.assertEqual(sensor_msg["firmware"], "Govee")
        self.assertEqual(sensor_msg["type"], "H5051/H5074")
        self.assertEqual(sensor_msg["mac"], "E0121D61BBAA")
        self.assertEqual(sensor_msg["packet"], "no packet id")
        self.assertTrue(sensor_msg["data"])
        self.assertEqual(sensor_msg["temperature"], 19.28)
        self.assertEqual(sensor_msg["humidity"], 44.92)
        self.assertEqual(sensor_msg["battery"], 100)
        self.assertEqual(sensor_msg["rssi"], -90)

    def test_Govee_H5102(self):
        """Test Govee H5102 parser."""
        data_string = "043e2b02010000aabb611d12e11f0d09475648353130325f43423942030388ec02010509ff0100010103cb0164aa"
        data = bytes(bytearray.fromhex(data_string))
        sensor_msg, tracker_msg = ble_parser(self, data)

        self.assertEqual(sensor_msg["firmware"], "Govee")
        self.assertEqual(sensor_msg["type"], "H5101/H5102/H5177")
        self.assertEqual(sensor_msg["mac"], "E1121D61BBAA")
        self.assertEqual(sensor_msg["packet"], "no packet id")
        self.assertTrue(sensor_msg["data"])
        self.assertEqual(sensor_msg["temperature"], 24.8577)
        self.assertEqual(sensor_msg["humidity"], 57.7)
        self.assertEqual(sensor_msg["battery"], 100)
        self.assertEqual(sensor_msg["rssi"], -86)

    def test_Govee_H5075(self):
        """Test Govee H5075 parser."""
        data_string = "043e2b02010000aabb6138c1a41f0d09475648353037355f43423942030388ec02010509ff88ec0003215d6400aa"
        data = bytes(bytearray.fromhex(data_string))
        sensor_msg, tracker_msg = ble_parser(self, data)

        self.assertEqual(sensor_msg["firmware"], "Govee")
        self.assertEqual(sensor_msg["type"], "H5072/H5075")
        self.assertEqual(sensor_msg["mac"], "A4C13861BBAA")
        self.assertEqual(sensor_msg["packet"], "no packet id")
        self.assertTrue(sensor_msg["data"])
        self.assertEqual(sensor_msg["temperature"], 20.5149)
        self.assertEqual(sensor_msg["humidity"], 14.9)
        self.assertEqual(sensor_msg["battery"], 100)
        self.assertEqual(sensor_msg["rssi"], -86)


if __name__ == '__main__':
    unittest.main()
