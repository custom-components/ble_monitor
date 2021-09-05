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
  - property: rssi
    note: >
      The RSSI sensor is disabled by default. You can enable the RSSI sensor by going to `configuration`, `integrations`, select `devices` on the BLE monitor integration tile and select your device. Click on the `+1 disabled entity` to show the disabled sensor and select the disabled entity. Finally, click on `Enable entity` to enable it. 
broadcast_rate: battery level ~1/day
active_scan:
encryption_key: true
custom_firmware:
notes:
---
