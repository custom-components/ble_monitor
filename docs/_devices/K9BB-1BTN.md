---
manufacturer: Linptech
name: Switch (one button version, battery powered)
model: K9BB
image: Linptech_K9BB.png
physical_description:
broadcasted_properties:
  - one btn switch
  - button switch
  - battery
  - rssi
broadcasted_property_notes:
  - property: one btn switch
    note: returns 'short press', 'double press' or 'long press'
broadcast_rate:
active_scan:
encryption_key: Probably (not confirmed yet)
custom_firmware:
notes:
  - This is the battery powered version of the Linptech K9B.
  - The switch sensor state will return to `no press` after the time set with the [reset_timer](configuration_params#reset_timer) option. It is advised to change the reset time to 1 second (default = 35 seconds).
---
