"""The tests for the kegtron ble_parser."""
import importlib
from pathlib import Path
import unittest
import sys


def import_parents(level=1):
    global __package__
    file = Path(__file__).resolve()
    parent, top = file.parent, file.parents[level]

    sys.path.append(str(top))
    try:
        sys.path.remove(str(parent))
    except ValueError:
        pass

    __package__ = '.'.join(parent.parts[len(top.parts):])
    importlib.import_module(__package__)


if __name__ == '__main__' and __package__ is None:
    import_parents(level=2)

from ble_monitor.ble_parser import ble_parser


class TestKegtron(unittest.TestCase):

    @classmethod
    def setUpClass(TestKegtron):
        TestKegtron.lpacket_ids = {}
        TestKegtron.movements_list = {}
        TestKegtron.adv_priority = {}
        TestKegtron.trackerlist = []
        TestKegtron.report_unknown = "other"
        TestKegtron.discovery = True

    def test_kegtron_kt100(self):
        """Test kegtron parser for KT-100."""
        data_string = "043e2b02010400759b5c5ecfd01f1effffff49ef138802e20153696e676c6520506f7274000000000000000000ae"
        data = bytes(bytearray.fromhex(data_string))
        sensor_msg, tracker_msg = ble_parser(self, data)

        self.assertEqual(sensor_msg["firmware"], "Kegtron")
        self.assertEqual(sensor_msg["type"], "Kegtron KT-100")
        self.assertEqual(sensor_msg["mac"], "D0CF5E5C9B75")
        self.assertEqual(sensor_msg["packet"], "no packet id")
        self.assertTrue(sensor_msg["data"])
        self.assertEqual(sensor_msg["keg size"], "Corny (5.0 gal)")
        self.assertEqual(sensor_msg["volume start"], 5.0)
        self.assertEqual(sensor_msg["port state"], "configured")
        self.assertEqual(sensor_msg["port index"], 1)
        self.assertEqual(sensor_msg["port count"], "Single port device")
        self.assertEqual(sensor_msg["port name"], "Single Port")
        self.assertEqual(sensor_msg["volume dispensed port 1"], 0.738)
        self.assertEqual(sensor_msg["rssi"], -82)

    def test_kegtron_kt200(self):
        """Test kegtron parser for KT-200."""
        data_string = "043e2b02010400759b5c5ecfd01f1effffff49ef138802e251326e6420506f7274000000000000000000000000af"
        data = bytes(bytearray.fromhex(data_string))
        sensor_msg, tracker_msg = ble_parser(self, data)

        self.assertEqual(sensor_msg["firmware"], "Kegtron")
        self.assertEqual(sensor_msg["type"], "Kegtron KT-200")
        self.assertEqual(sensor_msg["mac"], "D0CF5E5C9B75")
        self.assertEqual(sensor_msg["packet"], "no packet id")
        self.assertTrue(sensor_msg["data"])
        self.assertEqual(sensor_msg["keg size"], "Corny (5.0 gal)")
        self.assertEqual(sensor_msg["volume start"], 5.0)
        self.assertEqual(sensor_msg["port state"], "configured")
        self.assertEqual(sensor_msg["port index"], 2)
        self.assertEqual(sensor_msg["port count"], "Dual port device")
        self.assertEqual(sensor_msg["port name"], "2nd Port")
        self.assertEqual(sensor_msg["volume dispensed port 2"], 0.738)
        self.assertEqual(sensor_msg["rssi"], -81)


if __name__ == '__main__':
    unittest.main()