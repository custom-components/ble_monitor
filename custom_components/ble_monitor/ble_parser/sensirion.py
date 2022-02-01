"""Parser for Sensirion CO2 gadget advertisements"""
from struct import unpack

def parse_sensirion(self, data, source_mac, rssi):
    """Sensirion parser"""
    msg_length = len(data)
    firmware = "Sensirion"
    device_id = data[3]
    xvalue = data[4:]
    result = {"firmware": firmware}

    if msg_length == 14 and device_id == 0x06:
        """Sensirion CO2 gadget"""
        # based on https://github.com/sparkfun/SparkFun_SCD4x_Arduino_Library/blob/main/src/SparkFun_SCD4x_Arduino_Library.cpp#L239-L242
        (unk1, unk2, temperature, humidity, co2) = unpack("<HHHHH", xvalue)

        result.update({
            "carbon_dioxide": float(co2),
            "humidity": humidity*100/65536.0,
            "temperature": -45 + temperature*175/65536.0
        })

    packet_id = xvalue.hex()

    result.update({
        "rssi": rssi,
        "mac": ''.join('{:02X}'.format(x) for x in source_mac[:]),
        "type": "Sensirion CO2 Gadget",
        "packet": packet_id,
        "firmware": firmware,
        "data": True
    })
    return result
