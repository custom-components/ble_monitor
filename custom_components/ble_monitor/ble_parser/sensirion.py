"""Parser for Sensirion BLE advertisements"""
import logging

from .helpers import (
    to_mac,
    to_unformatted_mac,
)

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
                "BLE ADV from UNKNOWN Sensirion DEVICE: %s RSSI: %s, MAC: %s, ADV: %s",
                device_type,
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
    deviceId = f'{data[6]:x}:{data[7]:x}'  # as shown in Sensirion MyAmbience app (last 4 bytes of MAC address)

    if advertisementType == 0:
        samples = _parse_data_type(advSampleType, data[8:])
        if not samples:
            return None
        else:
            result.update(samples)
            result.update({
                "rssi": rssi,
                "mac": to_unformatted_mac(sensirion_mac),
                "type": device_type,
                "packet": "no packet id",
                "data": True
            })

        return result
    else:
        _LOGGER.debug("Advertisement Type %s not supported ", advertisementType)
        return None


'''
The following functions are based on Sensirion_GadgetBle_Lib.cpp from  https://github.com/Sensirion/arduino-ble-gadget/
support from other devices should be easily added by looking at GadgetBle::setDataType and updating _parse_data_type 
accordingly. Note that the device name also has to be added to the SENSIRION_DEVICES list.
'''


def _parse_data_type(advSampleType, byte_data):
    if (advSampleType == 3):
        return {
            'temperature': _decodeTemperatureV1(byte_data[0:2]),
            'humidity': _decodeHumidityV1(byte_data[2:4]),
            'voc': _decodeSimple(byte_data[4:6]),
            'voc-raw': _decodeSimple(byte_data[6:8])
        }
    elif (advSampleType == 4):
        return {
            'temperature': _decodeTemperatureV1(byte_data[0:2]),
            'humidity': _decodeHumidityV1(byte_data[2:4])
        }
    elif (advSampleType == 6):
        return {
            'temperature': _decodeTemperatureV1(byte_data[0:2]),
            'humidity': _decodeHumidityV2(byte_data[2:4])
        }
    elif (advSampleType == 8):
        return {
            'temperature': _decodeTemperatureV1(byte_data[0:2]),
            'humidity': _decodeHumidityV1(byte_data[2:4]),
            'co2': _decodeSimple(byte_data[4:6])
        }
    elif (advSampleType == 10):
        return {
            'temperature': _decodeTemperatureV1(byte_data[0:2]),
            'humidity': _decodeHumidityV1(byte_data[2:4]),
            'co2': _decodeSimple(byte_data[4:6])
        }
    elif (advSampleType == 12):
        return {
            'temperature': _decodeTemperatureV1(byte_data[0:2]),
            'humidity': _decodeHumidityV1(byte_data[2:4]),
            'co2': _decodeSimple(byte_data[4:6]),
            'pm2.5': _decodePM2p5V1(byte_data[6:8])
        }
    elif (advSampleType == 14):
        return {
            'temperature': _decodeTemperatureV1(byte_data[0:2]),
            'humidity': _decodeHumidityV1(byte_data[2:4]),
            'hcho': _decodeHCHOV1(byte_data[4:6])
        }
    elif (advSampleType == 16):
        return {
            'temperature': _decodeTemperatureV1(byte_data[0:2]),
            'humidity': _decodeHumidityV1(byte_data[2:4]),
            'voc': _decodeSimple(byte_data[4:6]),
            'pm2.5': _decodePM2p5V1(byte_data[6:8])
        }
    elif (advSampleType == 20):
        return {
            'temperature': _decodeTemperatureV1(byte_data[0:2]),
            'humidity': _decodeHumidityV1(byte_data[2:4]),
            'c02': _decodeSimple(byte_data[4:6]),
            'voc': _decodeSimple(byte_data[6:8]),
            'pm2.5': _decodePM2p5V1(byte_data[8:10]),
            'hcho': _decodeHCHOV1(byte_data[10:12])
        }
    elif (advSampleType == 22):
        return {
            'temperature': _decodeTemperatureV1(byte_data[0:2]),
            'humidity': _decodeHumidityV1(byte_data[2:4]),
            'voc': _decodeSimple(byte_data[4:6]),
            'nox': _decodeSimple(byte_data[6:8])
        }
    elif (advSampleType == 24):
        return {
            'temperature': _decodeTemperatureV1(byte_data[0:2]),
            'humidity': _decodeHumidityV1(byte_data[2:4]),
            'voc': _decodeSimple(byte_data[4:6]),
            # 'nox': _decodeSimple(byte_data[6:8]),
            'pm2.5': _decodePM2p5V2(byte_data[8:10])
        }
    elif (advSampleType == 26):
        return {
            'temperature': _decodeTemperatureV1(byte_data[0:2]),
            'humidity': _decodeHumidityV1(byte_data[2:4]),
            'co2': _decodeSimple(byte_data[4:6]),
            'voc': _decodeSimple(byte_data[6:8]),
            # 'nox': _decodePM2p5V2(byte_data[8:10]),
            'pm2.5': _decodePM2p5V2(byte_data[10:12])
        }
    elif (advSampleType == 28):
        return {
            'temperature': _decodeTemperatureV1(byte_data[0:2]),
            'humidity': _decodeHumidityV1(byte_data[2:4]),
            'co2': _decodeSimple(byte_data[4:6]),
            'pm2.5': _decodePM2p5V2(byte_data[6:8])
        }
    elif (advSampleType == 30):
        return {
            'temperature': _decodeTemperatureV1(byte_data[0:2]),
            'humidity': _decodeHumidityV1(byte_data[2:4]),
            'voc': _decodeSimple(byte_data[4:6]),
            'pm2.5': _decodePM2p5V2(byte_data[6:8])
        }
    elif (advSampleType == 32):
        return {
            'temperature': _decodeTemperatureV1(byte_data[0:2]),
            'humidity': _decodeHumidityV1(byte_data[2:4]),
            'co2': _decodeSimple(byte_data[4:6]),
            'voc': _decodeSimple(byte_data[6:8]),
            'pm2.5': _decodePM2p5V2(byte_data[8:10]),
            'hcho': _decodeHCHOV1(byte_data[10:12])
        }
    elif (advSampleType == 32):
        return {
            'pm1': _decodeSimple(byte_data[0:2]),
            'pm2.5': _decodeSimple(byte_data[2:4]),
            'pm4': _decodeSimple(byte_data[4:6]),
            'pm10': _decodeSimple(byte_data[6:8]),
        }
    elif (advSampleType == 34):
        return {
            'co2': _decodeSimple(byte_data[0:2])
        }
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
    return round(((int.from_bytes(byte_data, byteorder='little') * 125 / 65535) - 6), 2)


def _decodePM2p5V1(byte_data):
    # GadgetBle::_convertPM2p5V1 - return static_cast<uint16_t>(((value / 1000) * 65535) + 0.5f);
    return round((int.from_bytes(byte_data, byteorder='little') / 65535) * 1000, 2)


def _decodePM2p5V2(byte_data):
    # GadgetBle::_convertPM2p5V2 - return static_cast<uint16_t>((value * 10) + 0.5f);
    return round(int.from_bytes(byte_data, byteorder='little') / 10, 2)


def _decodeHCHOV1(byte_data):
    # GadgetBle::_convertHCHOV1 - return static_cast<uint16_t>((value * 5) + 0.5f);
    return round(int.from_bytes(byte_data, byteorder='little') / 5, 2)
