'''The tests for the AltBeacon ble_parser.'''
from ble_monitor.ble_parser import BleParser
from uuid import UUID

class TestAltBeacon:
    '''Tests for the AltBeacon parser'''

    def test_altbeacon_sensor(self):
        '''Test AltBeacon parser only sensor '''
        data_string = '043E280201020105988527406D1C1BFFFFFFBEACD3162F5AF3EE494799DB09756062D0FC005A0005C400D4'
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg['type'] == 'AltBeacon'
        assert sensor_msg['packet'] == 'no packet id'
        assert sensor_msg['firmware'] == 'AltBeacon'
        assert sensor_msg['manufacturer'] == 'Other'
        assert sensor_msg['rssi'] == -44
        assert sensor_msg['mac'] == '6D:40:27:85:98:05'
        assert str(UUID(sensor_msg['uuid'])) == 'd3162f5a-f3ee-4947-99db-09756062d0fc'
        assert sensor_msg['uuid'] == 'd3162f5af3ee494799db09756062d0fc'
        assert sensor_msg['major'] == 90
        assert sensor_msg['minor'] == 5
        assert sensor_msg['measured power'] == -60
        assert tracker_msg is None
    
    def test_altbeacon_tracker(self):
        '''Test AltBeacon parser only tracker '''
        data_string = '043E280201020105988527406D1C1BFFFFFFBEACD3162F5AF3EE494799DB09756062D0FC005A0005C400D4'
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser(tracker_whitelist=[bytearray.fromhex('d3162f5af3ee494799db09756062d0fc')])
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg['type'] == 'AltBeacon'
        assert sensor_msg['packet'] == 'no packet id'
        assert sensor_msg['firmware'] == 'AltBeacon'
        assert sensor_msg['manufacturer'] == 'Other'
        assert sensor_msg['rssi'] == -44
        assert sensor_msg['mac'] == '6D:40:27:85:98:05'
        assert str(UUID(sensor_msg['uuid'])) == 'd3162f5a-f3ee-4947-99db-09756062d0fc'
        assert sensor_msg['uuid'] == 'd3162f5af3ee494799db09756062d0fc'
        assert sensor_msg['major'] == 90
        assert sensor_msg['minor'] == 5
        assert sensor_msg['measured power'] == -60
        assert tracker_msg['tracker_id'] == b'\xd3\x16/Z\xf3\xeeIG\x99\xdb\tu`b\xd0\xfc'
        assert sensor_msg is not None