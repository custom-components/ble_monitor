# Parser for Sensirion BLE advertisements
import logging

_LOGGER = logging.getLogger(__name__)


def parse_sensirion(self, data, complete_local_name, source_mac, rssi):
    """Sensirion parser"""
    result = {"firmware": "Sensirion"}
    sensirion_mac = source_mac
    device_type = complete_local_name

    if device_type != "MyCO2":
        if self.report_unknown == "Sensirion":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Sensirion DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None
    
    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and source_mac.lower() not in self.sensor_whitelist:
        _LOGGER.debug(
            "Discovery is disabled. MAC: %s is not whitelisted!", to_mac(source_mac))
        return None
        
    # not all of the following values are used yet, but this explains the full protocol
    advertisementLength = data[0]  # redundant
    advertisementType0 = data[1]   # redundant (see below)
    companyId = data[2:3]  # redundant
    byte_data = data[4:]
    advertisementType = int(byte_data[0])
    advSampleType = int(byte_data[1])
    deviceName = f'{byte_data[2]:x}:{byte_data[3]:x}'  # shown in Sensirion MyAmbience app

    if(advertisementType == 0):
        samples = _parse_dataType(advSampleType, byte_data[4:])
        
        if not samples:
            return None
        else:
            result.update(samples)
            result.update({
                "rssi": rssi,
                "mac": to_mac(source_mac),
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
    return ':'.join('{:02x}'.format(x) for x in addr).upper()


'''
The following functions are based on Sensirion_GadgetBle_Lib.cpp from  https://github.com/Sensirion/arduino-ble-gadget/
support from other devices should be easily added by looking at GadgetBle::setDataType and updating _parse_dataType accordingly
'''


def _parse_dataType(advSampleType, byte_data):
    if(advSampleType == 8):
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
    return (int.from_bytes(byte_data, byteorder='little') / 65535) * 175 - 45


def _decodeHumidityV1(byte_data):
    # GadgetBle::_convertHumidityV1 - return static_cast<uint16_t>(((value / 100) * 65535) + 0.5f);
    return (int.from_bytes(byte_data, byteorder='little') / 65535) * 100


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
