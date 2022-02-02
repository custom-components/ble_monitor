---
manufacturer: Qingping
name: Cleargrass CGD1 alarm clock
model: CGD1
image: CGD1.jpg
physical_description: Segment LCD
broadcasted_properties:
  - temperature
  - humidity
  - battery
  - rssi
broadcasted_property_notes:
  - property: battery
    note: For battery level, we do not have accurate periodicity information yet.
broadcast_rate: ~1/10min.
active_scan:
encryption_key: Yes (Xiaomi MiBeacon advertisement)
custom_firmware:
notes:
  - The sensor sends BLE advertisements in Xiaomi MiBeacon format and Qingping format.
  - Xiaomi MiBeacon advertisements are most likely encrypted.
  - Qingping advertisements are not encrypted.
---
