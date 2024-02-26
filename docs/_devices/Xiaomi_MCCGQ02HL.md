---
manufacturer: Xiaomi
name: Mijia Window/Door Sensor 2
model: MCCGQ02HL
image: MCCGQ02HL.png
physical_description:
broadcasted_properties:
  - battery
  - opening
  - light
  - status
  - rssi
broadcasted_property_notes:
  - property: status
    note: >
      The opening entity has an extra attribute "status", which can have the following values:
        * opened
        * closed
        * closing timeout
        * device reset
broadcast_rate: battery level ~1/day
active_scan:
encryption_key: true
custom_firmware:
notes:
---
