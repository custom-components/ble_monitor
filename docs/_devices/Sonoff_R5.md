---
manufacturer: Sonoff
name: SwitchMan R5 Scene Controller
model: R5 / R5W
image: Sonoff_R5.png
physical_description:
broadcasted_properties:
  - six btn switch top left
  - six btn switch top middle
  - six btn switch top right
  - six btn switch bottom left
  - six btn switch bottom middle
  - six btn switch bottom right
  - button switch
  - rssi
broadcasted_property_notes:
  - property: six btn switch top left
    note: returns 'short press', 'double press' or 'long press'
  - property: six btn switch top middle
    note: returns 'short press', 'double press' or 'long press'
  - property: six btn switch top right
    note: returns 'short press', 'double press' or 'long press'
  - property: six btn switch bottom left
    note: returns 'short press', 'double press' or 'long press'
  - property: six btn switch bottom middle
    note: returns 'short press', 'double press' or 'long press'
  - property: six btn switch bottom right
    note: returns 'short press', 'double press' or 'long press'
broadcast_rate:
active_scan:
encryption_key: Yes
custom_firmware:
notes:
  - There are two versions of this switch - black and white.
  - The switch sensor state will return to `no press` after the time set with the [reset_timer](configuration_params#reset_timer) option. It is advised to change the reset time to 1 second (default = 35 seconds).
---
