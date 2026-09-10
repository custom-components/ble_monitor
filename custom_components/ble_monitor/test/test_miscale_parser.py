"""The tests for the Mi Scale ble_parser."""
from types import SimpleNamespace

from ble_monitor.binary_sensor import BaseBinarySensor
from ble_monitor.ble_parser import BleParser
from ble_monitor.const import BINARY_SENSOR_TYPES, MEASUREMENT_DICT
from ble_monitor.sensor import WeightSensor


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

        weight_removed_sensor = BaseBinarySensor.__new__(BaseBinarySensor)
        weight_removed_sensor._type = "mac"
        weight_removed_sensor._device_type = "Mi Scale V1"
        weight_removed_sensor.entity_description = SimpleNamespace(
            key="weight removed"
        )
        weight_removed_sensor._extra_state_attributes = {}
        weight_removed_sensor.collect(sensor_msg)
        assert weight_removed_sensor._newstate == 1
        assert weight_removed_sensor._extra_state_attributes["weight"] == 87.2

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
        assert sensor_msg["stabilized weight"] == 85.15
        assert sensor_msg["weight"] == 85.15
        assert sensor_msg["impedance"] == 428
        assert sensor_msg["rssi"] == -66

        weight_sensor = WeightSensor.__new__(WeightSensor)
        weight_sensor._type = "mac"
        weight_sensor.entity_description = SimpleNamespace(
            key="non-stabilized weight"
        )
        weight_sensor._extra_state_attributes = {}
        weight_sensor.pending_update = False
        weight_sensor.collect(sensor_msg, period_cnt=0)
        assert weight_sensor._extra_state_attributes["stabilized"] is True

    def test_miscale_stabilized_binary_sensor_mapping(self):
        """Test Mi Scale V1 and V2 expose the parsed stabilization flag."""
        for device_type in ("Mi Scale V1", "Mi Scale V2"):
            assert MEASUREMENT_DICT[device_type][2] == [
                "weight removed",
                "stabilized",
            ]

        description = next(
            item for item in BINARY_SENSOR_TYPES if item.key == "stabilized"
        )
        assert description.sensor_class == "BaseBinarySensor"
        assert description.update_behavior == "Instantly"
        assert description.unique_id == "stabilized_"
        assert description.device_class is None
