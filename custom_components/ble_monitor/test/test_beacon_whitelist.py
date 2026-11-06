"""Regression tests for discovery-disabled beacon sensor filtering."""
import pytest
from ble_monitor.ble_parser import BleParser

IBEACON = bytes.fromhex(
    "043E2A02010001433EA2C96B6A1E02011A1AFF4C000215"
    "E2C56DB5DFFB48D2B060D0F5A71096E000640000C5B3"
)
ALTBEACON = bytes.fromhex(
    "043E280201020105988527406D1C1BFFFFFFBEAC"
    "D3162F5AF3EE494799DB09756062D0FC005A0005C400D4"
)
THERMOBEACON = bytes.fromhex(
    "043e29020100002716000088061d0201060302f0ff"
    "15ff110000002716000088063c0c8f01a103b9d70300c8"
)
IBEACON_UUID = bytes.fromhex("e2c56db5dffb48d2b060d0f5a71096e0")
IBEACON_MAC = bytes.fromhex("6a6bc9a23e43")
ALTBEACON_UUID = bytes.fromhex("d3162f5af3ee494799db09756062d0fc")
THERMOBEACON_MAC = bytes.fromhex("068800001627")
OTHER = bytes.fromhex("000000000000")


@pytest.mark.parametrize(
    "packet, whitelist, expected",
    [
        (IBEACON, [IBEACON_UUID], True),
        (IBEACON, [IBEACON_UUID, IBEACON_MAC], True),
        (IBEACON, [IBEACON_MAC], False),
        (IBEACON, [OTHER], False),
        (ALTBEACON, [ALTBEACON_UUID], True),
        (ALTBEACON, [OTHER], False),
        (THERMOBEACON, [THERMOBEACON_MAC], True),
        (THERMOBEACON, [OTHER], False),
    ],
)
def test_sensor_whitelist_with_discovery_disabled(packet, whitelist, expected):
    parser = BleParser(discovery=False, sensor_whitelist=whitelist)
    sensor, _ = parser.parse_raw_data(packet)
    assert (sensor is not None) is expected
    if sensor and packet in (IBEACON, ALTBEACON):
        assert sensor["rssi"] < 0
        assert sensor["measured power"] < 0


def test_tracker_allowed_independently_of_sensor_whitelist():
    parser = BleParser(
        discovery=False,
        sensor_whitelist=[OTHER],
        tracker_whitelist=[IBEACON_UUID],
    )
    sensor, tracker = parser.parse_raw_data(IBEACON)
    assert sensor is None
    assert tracker["is connected"] is True


def test_discovery_allows_unlisted_beacon():
    parser = BleParser(discovery=True, sensor_whitelist=[OTHER])
    sensor, _ = parser.parse_raw_data(IBEACON)
    assert sensor is not None
