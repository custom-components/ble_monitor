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
    note: No battery info with firmware v3.2.1. Battery sensor is only supported when using [BLE gateway](https://github.com/myhomeiot/esphome-components) to forward the BLE advertisements with ESPHome to BLE monitor.
broadcast_rate: ~1/min.
active_scan:
encryption_key:
custom_firmware:
notes:
---
