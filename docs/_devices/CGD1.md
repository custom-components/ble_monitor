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
  - property: rssi
    note: >
      The RSSI sensor is disabled by default. You can enable the RSSI sensor by going to `configuration`, `integrations`, select `devices` on the BLE monitor integration tile and select your device. Click on the `+1 disabled entity` to show the disabled sensor and select the disabled entity. Finally, click on `Enable entity` to enable it. 
broadcast_rate: ~1/10min.
active_scan:
encryption_key: Yes (Xiaomi MiBeacon advertisement)
custom_firmware:
notes:
  - The sensor sends BLE advertisements in Xiaomi MiBeacon format and Qingping format.
  - Xiaomi MiBeacon advertisements are most likely encrypted.
  - Qingping advertisements are not encrypted.
---
