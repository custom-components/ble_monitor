---
manufacturer: Google
name: Eddystone-TLM
model: Eddystone-TLM
image:
physical_description:
broadcasted_properties:
  - temperature
  - voltage
  - battery
  - rssi
broadcasted_property_notes:
  - property: temperature
    note: The beacon's chip temperature, not that of a separate sensor. Not reported by beacons that send -128 °C.
  - property: voltage
    note: Not reported by beacons that send 0 mV.
broadcast_rate:
active_scan:
encryption_key:
custom_firmware:
notes:
  - Eddystone-TLM is not a device, but Google's open telemetry frame, sent by beacons from e.g. Minew and BlueUp.
  - Only unencrypted TLM frames (version `0x00`) are supported.
---
