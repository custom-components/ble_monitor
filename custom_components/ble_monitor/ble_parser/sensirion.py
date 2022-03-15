"""Parser for Sensirion BLE advertisements"""
import logging

_LOGGER = logging.getLogger(__name__)

SENSIRION_DEVICES = [
    "MyCO2",
    "SHT40 Gadget",
    "SHT41 Gadget",
    "SHT45 Gadget",
]


def parse_sensirion(self, data, complete_local_name, source_mac, rssi):
    """Sensirion parser"""
    result = {"firmware": "Sensirion"}
    sensirion_mac = source_mac
    device_type = complete_local_name

    if device_type not in SENSIRION_DEVICES:
        if self.report_unknown == "Sensirion":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Sensirion DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and source_mac not in self.sensor_whitelist:
        _LOGGER.debug(
            "Discovery is disabled. MAC: %s is not whitelisted!", to_mac(source_mac))
        return None

    # not all of the following values are used yet, but this explains the full protocol
    # bytes 1+2 (length and type) are part of the header
    advertisementLength = data[0]  # redundant
    advertisementType0 = data[1]  # redundant (also encoded in body - see below)
    companyId = data[2:3]  # redundant (already part of the metadata)
    advertisementType = int(data[4])
    advSampleType = int(data[5])
    deviceName = f'{data[6]:x}:{data[7]:x}'  # as shown in Sensirion MyAmbience app (last 4 bytes of MAC address)

    if advertisementType == 0:
        samples = _parse_dataType(advSampleType, data[8:])
        if not samples:
            return None
        else:
            result.update(samples)
            result.update({
                "rssi": rssi,
                "mac": ''.join('{:02X}'.format(x) for x in sensirion_mac[:]),
                "type": device_type,
                "packet": "no packet id",
                "data": True
            })

        return result
    else:
        _LOGGER.debug("Advertisement Type %s not supported ", advertisementType)
        return None


def to_mac(addr: int):
    """Return formatted MAC address"""
    return ':'.join(f'{i:02X}' for i in addr)


'''
The following functions are based on Sensirion_GadgetBle_Lib.cpp from  https://github.com/Sensirion/arduino-ble-gadget/
support from other devices should be easily added by looking at GadgetBle::setDataType and updating _parse_dataType accordingly
'''


def _parse_dataType(advSampleType, byte_data):
    if (advSampleType == 6):
        return {'temperature': _decodeTemperatureV1(byte_data[0:2]),
                'humidity': _decodeHumidityV1(byte_data[2:4])}
    elif (advSampleType == 8):
        return {'temperature': _decodeTemperatureV1(byte_data[0:2]),
                'humidity': _decodeHumidityV1(byte_data[2:4]),
                'co2': _decodeSimple(byte_data[4:6])}
    else:
        _LOGGER.debug("Advertisement SampleType %s not supported", advSampleType)


def _decodeSimple(byte_data):
    # GadgetBle::_convertSimple - return static_cast<uint16_t>(value + 0.5f);
    return int.from_bytes(byte_data, byteorder='little')


def _decodeTemperatureV1(byte_data):
    # GadgetBle::_convertTemperatureV1 - return static_cast<uint16_t>((((value + 45) / 175) * 65535) + 0.5f);
    return round((int.from_bytes(byte_data, byteorder='little') / 65535) * 175 - 45, 2)


def _decodeHumidityV1(byte_data):
    # GadgetBle::_convertHumidityV1 - return static_cast<uint16_t>(((value / 100) * 65535) + 0.5f);
    return round((int.from_bytes(byte_data, byteorder='little') / 65535) * 100, 2)


def _decodeHumidityV2(byte_data):
    # GadgetBle::_convertHumidityV2 - return static_cast<uint16_t>((((value + 6.0) * 65535) / 125.0) + 0.5f);
    return


def _decodePM2p5V1(byte_data):
    # GadgetBle::_convertPM2p5V1 - return static_cast<uint16_t>(((value / 1000) * 65535) + 0.5f);
    return


def _decodePM2p5V2(byte_data):
    # GadgetBle::_convertPM2p5V2 - return static_cast<uint16_t>((value * 10) + 0.5f);
    return


def _decodeHCHOV1(byte_data):
    # GadgetBle::_convertHCHOV1 - return static_cast<uint16_t>((value * 5) + 0.5f);
    return
