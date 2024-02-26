---
manufacturer: Xiaomi
name: Mijia wireless switch
model: XMWXKG01LM
image: XMWXKG01LM.png
physical_description: round switch
broadcasted_properties:
  - one btn switch
  - battery
  - rssi
broadcasted_property_notes:
  - property: one btn switch
    note: returns 'single press', 'double press' or 'long press'
broadcast_rate:
active_scan: false
encryption_key: Yes
custom_firmware: false
notes:
  - The switch sensor state will return to `no press` after the time set with the [reset_timer](configuration_params#reset_timer) option. It is advised to change the reset time to 1 second (default = 35 seconds).
---
