---
manufacturer: Xiaomi
name: Xiaomi Smart Pillow
model: MJZNZ018H
image: MJZNZ018H.png
physical_description:
broadcasted_properties:
  - battery
  - snoring
  - sleeping
  - bed occupancy
  - button switch
  - rssi
broadcasted_property_notes:
  - property: sleeping
    note: >
    True means sleeping, False means Awake
  - property: bed occupancy
    note: >
    True means in bed, False means out of bed
  - property: button switch
    note: >
    The switch sensor will report report "double click" when double clicking on the controller. 
broadcast_rate: See Notes
active_scan:
encryption_key: true
custom_firmware:
notes:
  - The switch sensor state will return to `no press` after the time set with the [reset_timer](configuration_params#reset_timer) option.
---
