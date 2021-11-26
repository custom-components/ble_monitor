---
manufacturer: Xiaomi
name: Smart Mijia Magic Cube
model: XMMF01JQD
image: XMMF01JQD.png
physical_description:
broadcasted_properties:
  - button
  - rssi
broadcasted_property_notes:
  - property: button
    note: Possible states are 'left' and 'right', corresponding to the directon you rotate the cube. No edge information is available, only the direction, as this edge info is only available after connecting to the cube. This is not supported in BLE monitor.
broadcast_rate:
active_scan:
encryption_key: true
custom_firmware:
notes:
  - After each rotation, the sensor state shows the direction. It will return to `no press` after the time set with the [reset_timer](configuration_params#reset_timer) option (default = 35 seconds).
  - The sensor has an attribute which shows the `last button press`. You can use the state change event to trigger an automation in Home Assistant.
---
