---
manufacturer: Linptech
name: Switch (three button version)
model: K9B
image: Linptech_K9B.png
physical_description:
broadcasted_properties:
  - three btn switch left
  - three btn switch middle
  - three btn switch right
  - button switch
  - rssi
broadcasted_property_notes:
  - property: three btn switch left
    note: returns 'short press', 'double press' or 'long press'
  - property: three btn switch middle
    note: returns 'short press', 'double press' or 'long press'
  - property: three btn switch right
    note: returns 'short press', 'double press' or 'long press'
broadcast_rate:
active_scan:
encryption_key: Probably (not confirmed yet)
custom_firmware:
notes:
  - There are three different versions of this switch, with one, two or three buttons.
  - The switch sensor state will return to `no press` after the time set with the [reset_timer](configuration_params#reset_timer) option. It is advised to change the reset time to 1 second (default = 35 seconds).
---
