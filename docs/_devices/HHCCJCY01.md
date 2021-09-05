---
manufacturer: MiFlora
name: Plant sensor
model: HHCCJCY01
image: HHCCJCY01.jpg
physical_description:
broadcasted_properties:
  - temperature
  - moisture
  - conductivity
  - illuminance
  - battery
  - rssi
broadcasted_property_notes:
  - property: battery
    note: No battery info with firmware v3.2.1.
  - property: rssi
    note: >
      The RSSI sensor is disabled by default. You can enable the RSSI sensor by going to `configuration`, `integrations`, select `devices` on the BLE monitor integration tile and select your device. Click on the `+1 disabled entity` to show the disabled sensor and select the disabled entity. Finally, click on `Enable entity` to enable it. 
broadcast_rate: ~1/min.
active_scan:
encryption_key:
custom_firmware:
notes:
---
