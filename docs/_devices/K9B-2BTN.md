---
manufacturer: Linptech
name: Switch (two button version)
model: K9B
image: Linptech_K9B.png
physical_description:
broadcasted_properties:
  - two btn switch left
  - two btn switch right
  - button switch
  - rssi
broadcasted_property_notes:
  - property: two btn switch left
    note: returns 'toggle'
  - property: two btn switch right
    note: returns 'toggle'
  - property: button switch
    note: types are 'short press', 'double press' or 'long press' for each button.
broadcast_rate:
active_scan: false
encryption_key: Probably (not confirmed yet)
custom_firmware: false
notes:
  - There are three different versions of this switch, with one, two or three buttons.
  - The switch sensor state will return to `no press` after the time set with the [reset_timer](configuration_params#reset_timer) option. It is advised to change the reset time to 1 second (default = 35 seconds).
---
