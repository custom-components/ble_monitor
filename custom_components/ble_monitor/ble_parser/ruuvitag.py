# Parser for Ruuvi Tag BLE advertisements
import logging
from ruuvitag_sensor.data_formats import DataFormats
from ruuvitag_sensor.decoder import get_decoder

_LOGGER = logging.getLogger(__name__)


def parse_ruuvitag(self, data, source_mac, rssi):
    ruuvitag_mac = source_mac
    device_type = "Ruuvitag"

    # convert data
    full_data = data.hex()
    data = full_data[26:].upper()
    (data_format, encoded) = DataFormats.convert_data(data)
    result = get_decoder(data_format).decode_data(encoded)

    if result is None:
        if self.report_unknown == "Ruuvitag":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Ruuvitag DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # reformat battery info to match BLE monitor format
    if "battery" in result:
        voltage = result["battery"] / 1000
        # replace battery key with voltage key
        del result["battery"]
        result["voltage"] = voltage
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
        result["battery"] = batt

    # check for MAC presence in whitelist, if needed
    if self.discovery is False and ruuvitag_mac.lower() not in self.whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(ruuvitag_mac))
        return None

    if result["data_format"] < 5:
        _LOGGER.info("Data type %i is obsolete, update your ruuvitag", result["data_format"])
    firmware = "Ruuvitag (V" + str(result["data_format"]) + ")"

    if "measurement_sequence_number" in result:
        packet_id = result["measurement_sequence_number"]
        del result["measurement_sequence_number"]
        # Check for duplicate messages
        try:
            prev_packet = self.lpacket_ids[ruuvitag_mac]
        except KeyError:
            # start with empty first packet
            prev_packet = None
        if prev_packet == packet_id:
            # only process new messages
            return None
        self.lpacket_ids[ruuvitag_mac] = packet_id
        if prev_packet is None:
            # ignore first message after a restart
            return None
    else:
        packet_id = "no packet id"

    if "movement_counter" in result:
        movement_cnt = result["movement_counter"]
        # Check for an increased counter
        try:
            prev_movement = self.movements_list[ruuvitag_mac]
        except KeyError:
            # start with empty movement first
            prev_movement = None
        if prev_movement == movement_cnt or prev_movement is None:
            motion = 0
        else:
            motion = 1
        self.movements_list[ruuvitag_mac] = movement_cnt
        result["motion"] = motion
        result["motion timer"] = motion

    result.update({
        "rssi": rssi,
        "mac": ''.join('{:02X}'.format(x) for x in ruuvitag_mac[:]),
        "type": device_type,
        "packet": packet_id,
        "firmware": firmware,
        "data": True
    })
    return result


def to_mac(addr: int):
    return ':'.join('{:02x}'.format(x) for x in addr).upper()
