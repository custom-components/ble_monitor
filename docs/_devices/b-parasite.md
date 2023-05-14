---
manufacturer: rbaron
name: BLE soil moisture sensor
model:  b-parasite
image: bparasite.jpg
physical_description: Plant sensor
broadcasted_properties:
  - temperature
  - moisture
  - humidity
  - illuminance
  - voltage
  - rssi
broadcasted_property_notes:
  - property: voltage
    note: Voltage of the battery
  - property: illuminance
    note: Only available for v1.1.0 and upwards devices
broadcast_rate: configurable, ~5-10/min
active_scan:
encryption_key: false
custom_firmware:
notes:
    - This device is [Open Source Hardware](https://github.com/rbaron/b-parasite)
---
