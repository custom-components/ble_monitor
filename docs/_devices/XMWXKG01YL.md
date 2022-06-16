---
manufacturer: Xiaomi
name: Smart Switch (two button version)
model: XMWXKG01YL 
image: XMWXKG01YL.png
physical_description:
broadcasted_properties:
  - two btn switch left
  - two btn switch right
  - rssi
broadcasted_property_notes:
  - property: two btn switch left
    note: returns 'short press', 'double press' or 'long press'
  - property: two btn switch right
    note: returns 'short press', 'double press' or 'long press'
broadcast_rate:
active_scan: false
encryption_key: Probably (not confirmed yet)
custom_firmware: false
notes:
  - The switch sensor state will return to `no press` after the time set with the [reset_timer](configuration_params#reset_timer) option. It is advised to change the reset time to 1 second (default = 35 seconds).
---
