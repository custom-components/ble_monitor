---
manufacturer: Sonoff
name: S-MATE Extreme Switch Mate | S-MATE2
model: S-MATE / S-MATE2
image: Sonoff_S-MATE.png
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
encryption_key: Yes
custom_firmware:
notes:
  - There are two revisions of this switch - with and without power pass-through.
  - The switch sensor state will return to `no press` after the time set with the [reset_timer](configuration_params#reset_timer) option. It is advised to change the reset time to 1 second (default = 35 seconds).
---
