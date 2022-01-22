'''The tests for the iBeacon ble_parser.'''
from ble_monitor.ble_parser import BleParser
from uuid import UUID

class TestIBeacon:
    '''Tests for the iBeacon parser'''

    def test_ibeacon_sensor(self):
        '''Test iBeacon parser only sensor '''
        data_string = '043E2A02010001433EA2C96B6A1E02011A1AFF4C000215E2C56DB5DFFB48D2B060D0F5A71096E000640000C5B3'
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg['type'] == 'iBeacon'
        assert sensor_msg['packet'] == 'no packet id'
        assert sensor_msg['firmware'] == 'iBeacon'
        assert sensor_msg['rssi'] == -77
        assert sensor_msg['mac'] == '6A:6B:C9:A2:3E:43'
        assert str(UUID(sensor_msg['uuid'])) == 'e2c56db5-dffb-48d2-b060-d0f5a71096e0'
        assert sensor_msg['uuid'] == 'e2c56db5dffb48d2b060d0f5a71096e0'
        assert sensor_msg['major'] == 100
        assert sensor_msg['minor'] == 0
        assert sensor_msg['measured power'] == -59
        assert sensor_msg['cypress temperature'] == -46.85
        assert sensor_msg['cypress humidity'] == -6.0
        assert tracker_msg is None

    def test_ibeacon_tracker(self):
        '''Test iBeacon parser only tracker '''
        data_string = '043E2A02010001433EA2C96B6A1E02011A1AFF4C000215E2C56DB5DFFB48D2B060D0F5A71096E000640000C5B3'
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser(tracker_whitelist=[bytearray.fromhex('e2c56db5dffb48d2b060d0f5a71096e0')])
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert tracker_msg['is connected']
        assert tracker_msg['rssi'] == -77
        assert tracker_msg['mac'] == '6A:6B:C9:A2:3E:43'
        assert str(UUID(tracker_msg['uuid'])) == 'e2c56db5-dffb-48d2-b060-d0f5a71096e0'
        assert tracker_msg['uuid'] == 'e2c56db5dffb48d2b060d0f5a71096e0'
        assert tracker_msg['tracker_id'] == b'\xe2\xc5m\xb5\xdf\xfbH\xd2\xb0`\xd0\xf5\xa7\x10\x96\xe0'
        assert tracker_msg['major'] == 100
        assert tracker_msg['minor'] == 0
        assert tracker_msg['measured power'] == -59
        assert tracker_msg['cypress temperature'] == -46.85
        assert tracker_msg['cypress humidity'] == -6.0
        assert sensor_msg is not None

    def test_ibeacon_iphone_ble_packet_var_1(self):
        '''Test iBeacon parser incorrect iphone ble packet '''
        data_string = '043E2202010001433EA2C96B6A1602011A020A0C0FFF4C000F06A033BD08C5001002440CC4'
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg is None
        assert tracker_msg is None

    def test_ibeacon_iphone_ble_packet_var_2(self):
        '''Test iBeacon parser incorrect iphone ble packet '''
        data_string = '043E1D02010001433EA2C96B6A1102011A020A0C0AFF4C001005441CBD08C5BB'
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg is None
        assert tracker_msg is None
