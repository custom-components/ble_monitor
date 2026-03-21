---
manufacturer: Xiaomi
name: PTX F1 4-Button Wireless Switch (Display Version)
model: F1
image: PTX_F1_Display.webp
physical_description:
broadcasted_properties:
  - temperature
  - humidity
  - four btn switch 1
  - four btn switch 2
  - four btn switch 3
  - four btn switch 4
  - rssi
broadcasted_property_notes:
  - property: four btn switch 1
    note: returns 'short press', 'double press' or 'long press'
  - property: four btn switch 2
    note: returns 'short press', 'double press' or 'long press'
  - property: four btn switch 3
    note: returns 'short press', 'double press' or 'long press'
  - property: four btn switch 4
    note: returns 'short press', 'double press' or 'long press'
broadcast_rate:
active_scan:
encryption_key: true
custom_firmware:
notes:
  - Unable to retrieve the battery percentage right now. (need help!)
  - The switch sensor state will return to `no press` after the time set with the [reset_timer](configuration_params#reset_timer) option. It is advised to change the reset time to 1 second (default = 35 seconds).
---
