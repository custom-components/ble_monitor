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
    note: Battery sensor is disabled by default. HHCCJCY01 does not send battery info with firmware v3.2.1 and later. Battery sensor is only supported when using [BLE gateway](https://github.com/myhomeiot/esphome-components) to forward the BLE advertisements with ESPHome to BLE monitor. You can enable the `battery` sensor by going to `configuration`, `integrations`, select `devices` on the BLE monitor integration tile and select your device. Click on the `+1 disabled entity` to show the disabled sensor and select the disabled entity. Finally, click on `Enable entity` to enable it.
broadcast_rate: ~1/min.
active_scan:
encryption_key:
custom_firmware:
notes:
---
