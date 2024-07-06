---
manufacturer: Linptech
name: Smart Wireless Switch KS1 Pro
model: KS1BP
image: Linptech_KS1BP.png
physical_description:
broadcasted_properties:
  - temperature
  - humidity
  - four btn switch 1
  - four btn switch 2
  - four btn switch 3
  - four btn switch 4
  - battery
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
encryption_key: Probably (not confirmed yet)
custom_firmware:
notes:
  - There are two different versions of this switch, without temperature/humidity (KS1) and with temperature/humidity (KS1BP).
  - The switch sensor state will return to `no press` after the time set with the [reset_timer](configuration_params#reset_timer) option. It is advised to change the reset time to 1 second (default = 35 seconds).
---
