"""The tests for the iNode ble_parser."""
import unittest
from ble_monitor.ble_parser import ble_parser


class TestInode(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.lpacket_ids = {}
        cls.movements_list = {}
        cls.adv_priority = {}
        cls.trackerlist = []
        cls.report_unknown = "other"
        cls.discovery = True

    def test_inode_energy_meter(self):
        """Test inode parser for iNode Energy Monitor."""
        data_string = "043E2102010000473A6D6F1200150201060EFF90820400CFE40000DC05B0ED10020A08A5"
        data = bytes(bytearray.fromhex(data_string))

        # get the mac to fill in an initial packet id
        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        self.lpacket_ids[mac] = "0400cfe40000dc05b0ed20"

        sensor_msg, tracker_msg = ble_parser(self, data)

        self.assertEqual(sensor_msg["firmware"], "iNode")
        self.assertEqual(sensor_msg["type"], "iNode Energy Meter")
        self.assertEqual(sensor_msg["mac"], "00126F6D3A47")
        self.assertEqual(sensor_msg["packet"], "0400cfe40000dc05b0ed10")
        self.assertTrue(sensor_msg["data"])
        self.assertEqual(sensor_msg["energy"], 39.05)
        self.assertEqual(sensor_msg["energy unit"], "kWh")
        self.assertEqual(sensor_msg["power"], 160.0)
        self.assertEqual(sensor_msg["power unit"], "W")
        self.assertEqual(sensor_msg["constant"], 1500)
        self.assertEqual(sensor_msg["battery"], 100)
        self.assertEqual(sensor_msg["voltage"], 2.88)
        self.assertEqual(sensor_msg["light level"], 0.0)
        self.assertEqual(sensor_msg["week day"], 0)
        self.assertEqual(sensor_msg["week day total"], 4333)
        self.assertEqual(sensor_msg["rssi"], -91)


if __name__ == '__main__':
    unittest.main()
