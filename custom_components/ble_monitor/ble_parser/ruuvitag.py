# Parser for Ruuvi Tag BLE advertisements
import base64
import logging
import math
from struct import unpack


_LOGGER = logging.getLogger(__name__)


def parse_ruuvitag(self, data, source_mac, rssi):
    ruuvitag_mac = source_mac
    device_type = "Ruuvitag"
    result = {
        "mac": "".join("{:02X}".format(x) for x in ruuvitag_mac[:]),
        "type": device_type,
        "rssi": rssi,
        "data": False,
    }
    adstuct_type = data[1]
    if adstuct_type == 0x16:
        # version 2 and 4
        uuid16 = (data[3] << 8) | data[2]
        if uuid16 == 0xFEAA and len(data) >= 23:
            try:
                encoded = data[15:]
                if len(encoded) == 8:
                    version = 2
                if len(encoded) > 8:
                    version = 4
                    encoded = encoded[:8]
                decoded = bytearray(base64.b64decode(encoded, "-_"))

                (version, humi, temp, frac, pres) = unpack(">BBbBH", decoded)

                temp_val = (temp & 127) + frac / 100
                sign = (temp >> 7) & 1
                if sign == 0:
                    temperature = round(temp_val, 2)
                else:
                    temperature = round(-1 * temp_val, 2)
                result.update(
                    {
                        "humidity": humi * 0.5,
                        "temperature": temperature,
                        "pressure": round((pres + 50000) / 100, 2),
                        "firmware": "Ruuvitag V" + str(version),
                        "packet": "no packet id",
                        "data": True,
                    }
                )
            except base64.binascii.Error:
                _LOGGER.debug("Encoded value: %s not valid", encoded)
                return None
        else:
            result = None
    elif adstuct_type == 0xFF:
        # version 3 and 5
        comp_id = (data[3] << 8) | data[2]
        if comp_id == 0x0499:
            version = data[4]
            if version == 3:
                # Ruuvitag V3 format
                (version, humi, temp, frac, pres, accx, accy, accz, volt) = unpack(
                    ">BBbBHhhhH", data[4:18]
                )

                # See https://github.com/ttu/ruuvitag-sensor/blob/master/ruuvitag_sensor/decoder.py
                # The temperature is in two bytes, one for the integer part,
                # one for the fraction
                #
                # The integer part was decoded as a signed two's complement number,
                # but this isn't how it's really stored. The MSB is a sign, the lower
                # 7 bits are the unsigned temperature value.
                #
                # To convert from the decoded value we have to add 128 and then negate,
                # if the decoded value was negative
                if temp < 0:
                    temperature = -(temp + 128 + frac / 100)
                else:
                    temperature = temp + frac / 100
                result.update(
                    {
                        "humidity": humi * 0.5,
                        "temperature": temperature,
                        "pressure": round((pres + 50000) / 100, 2),
                        "acceleration": math.sqrt(accx ** 2 + accy ** 2 + accz ** 2),
                        "acceleration x": accx,
                        "acceleration y": accy,
                        "acceleration z": accz,
                        "voltage": volt / 1000,
                        "firmware": "Ruuvitag V3",
                        "packet": "no packet id",
                        "data": True,
                    }
                )
            elif version == 5:
                # Ruuvitag V5 format
                (version, temp, humi, pres, accx, accy, accz, power, move_cnt, packet_id) = unpack(
                    ">BhHHhhhHBH", data[4:22]
                )

                # Check for duplicate messages
                try:
                    prev_packet = self.lpacket_ids[ruuvitag_mac]
                except KeyError:
                    # start with empty first packet
                    prev_packet = None
                if prev_packet == packet_id:
                    if self.filter_duplicates is True:
                        # only process new messages
                        return None
                self.lpacket_ids[ruuvitag_mac] = packet_id
                if prev_packet is None:
                    if self.filter_duplicates is True:
                        # ignore first message after a restart
                        return None
                # Check for an increased movement counter
                try:
                    prev_movement = self.movements_list[ruuvitag_mac]
                except KeyError:
                    # start with empty movement first
                    prev_movement = None
                if prev_movement == move_cnt or prev_movement is None:
                    motion = 0
                else:
                    motion = 1
                self.movements_list[ruuvitag_mac] = move_cnt

                result.update(
                    {
                        "temperature": round(temp / 200, 2),
                        "humidity": round(humi / 400, 2),
                        "pressure": round((pres + 50000) / 100, 2),
                        "acceleration": math.sqrt(accx ** 2 + accy ** 2 + accz ** 2),
                        "acceleration x": accx,
                        "acceleration y": accy,
                        "acceleration z": accz,
                        "voltage": (1600 + (power >> 5)) / 1000,
                        "tx power": -40 + ((power & 0x001F) * 2),
                        "motion": motion,
                        "motion timer": motion,
                        "packet": packet_id,
                        "firmware": "Ruuvitag V5",
                        "data": True,
                    }
                )
                # Remove false data from result
                if result["temperature"] == -163.84:
                    result.pop("temperature")
                if result["humidity"] == 163.84:
                    result.pop("humidity")
                if result["pressure"] == 1155.35:
                    result.pop("pressure")
                if (
                    result["acceleration x"] == -32768 or (
                        result["acceleration y"] == -32768 or (
                            result["acceleration z"] == -32768
                        )
                    )
                ):
                    result.pop("acceleration")
                    result.pop("acceleration x")
                    result.pop("acceleration y")
                    result.pop("acceleration z")
            else:
                result = None
    else:
        result = None
    if result is None:
        if self.report_unknown == "Ruuvitag":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Ruuvitag DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex(),
            )
        return None
    # reformat battery info to match BLE monitor format
    if "voltage" in result:
        voltage = result["voltage"]
        # calculate battery in %
        if voltage >= 3.00:
            batt = 100
        elif voltage >= 2.60:
            batt = 60 + (voltage - 2.60) * 100
        elif voltage >= 2.50:
            batt = 40 + (voltage - 2.50) * 200
        elif voltage >= 2.45:
            batt = 20 + (voltage - 2.45) * 400
        else:
            batt = 0
        result["battery"] = round(batt, 1)
    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and ruuvitag_mac.lower() not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(ruuvitag_mac))
        return None
    if version < 5:
        _LOGGER.info(
            "Firmware version %i is outdated, consider updating your ruuvitag with MAC: %s to view all sensors",
            version,
            to_mac(ruuvitag_mac),
        )
    return result


def to_mac(addr: int):
    return ":".join("{:02x}".format(x) for x in addr).upper()
