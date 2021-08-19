# Parser for SensorPush BLE advertisements
import logging
from struct import unpack

_LOGGER = logging.getLogger(__name__)

SENSORPUSH_DEVICE_TYPES = {
    64: "HTP.xw",
    65: "HT.w"
}

SENSORPUSH_PACK_PARAMS = {
    64: [
        [-40.0, 140.0, 0.0025],
        [0.0, 100.0, 0.0025],
        [30000.0, 125000.0, 1.0]
    ],
    65: [
        [-40.0, 125.0, 0.0025],
        [0.0, 100.0, 0.0025]
    ]
}

SENSORPUSH_DATA_TYPES = {
    64: [
        "temperature",
        "humidity",
        "pressure"
    ],
    65: [
        "temperature",
        "humidity"
    ]
}
    
def decode_values(mfg_data: bytes, device_type_id: int) -> dict:
    pack_params = SENSORPUSH_PACK_PARAMS.get(device_type_id, None)
    if pack_params is None:
        _LOGGER.error("SensorPush device type id %d unknown" % device_type_id)
        return {}
        
    values = {}
    
    packed_values = 0
    for i in range(1,len(mfg_data)):
        packed_values += mfg_data[i] << (8 * (i-1))
    
    mod = 1
    div = 1
    for i in range(0,len(pack_params)):
        vp = pack_params[i]
        min_value = vp[0]
        max_value = vp[1]
        step = vp[2]
        mod *= int((max_value - min_value) / step + step / 2.0) + 1
        value_count = int((packed_values % mod) / div)
        data_type = SENSORPUSH_DATA_TYPES[device_type_id][i]
        value = round(value_count * step + min_value, 2)
        if data_type == "pressure":
            value = value / 100.0
        values[data_type] = value
        div *= int((max_value - min_value) / step + step / 2.0) + 1
        
    return values


def parse_sensorpush(self, data, source_mac, rssi):
    result = {"firmware": "SensorPush"}
    sensorpush_mac = source_mac
    device_type = None
    
    # SensorPush puts encoded data in manufacturer data (0xFF)
    adpayload_start = 0
    adpayload_size = len(data)
    while adpayload_size > 1:
        adstuct_size = data[adpayload_start] + 1
        if adstuct_size > 1 and adstuct_size <= adpayload_size:
            adstruct = data[adpayload_start:adpayload_start + adstuct_size]
            adstuct_type = adstruct[1]
            if adstuct_type == 0xFF and adstuct_size >= 6:
                page_id = adstruct[2] & 0x03
                if page_id == 0:
                    device_type_id = 64 + (adstruct[2] >> 2)
                    device_type = SENSORPUSH_DEVICE_TYPES.get(device_type_id, None)
                    result.update(decode_values(adstruct[2:], device_type_id))
        adpayload_size -= adstuct_size
        adpayload_start += adstuct_size

    if device_type is None:
        if self.report_unknown == "SensorPush":
            _LOGGER.info(
                "BLE ADV from UNKNOWN SensorPush DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and sensorpush_mac.lower() not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(sensorpush_mac))
        return None

    result.update({
        "rssi": rssi,
        "mac": ''.join('{:02X}'.format(x) for x in sensorpush_mac[:]),
        "type": device_type,
        "packet": "no packet id",
        "data": True
    })
    return result


def to_mac(addr: int):
    return ':'.join('{:02x}'.format(x) for x in addr).upper()
