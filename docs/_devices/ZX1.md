---
manufacturer: 8H Sleep
name: 8H Intelligent Sleep Aid Natural Latex PillowX
model: ZX1
image: 8H_Sleep_ZX1.png
physical_description:
broadcasted_properties:
  - snoring
  - sleeping
  - bed occupancy
  - button
  - rssi
broadcasted_property_notes:
  - property: sleeping
    note: >
    True means sleeping, False means Awake
  - property: bed occupancy
    note: >
    True means in bed, False means out of bed
  - property: button
    note: >
    The button sensor will report report "double click" when double clicking on the controller.
broadcast_rate: See Notes
active_scan:
encryption_key: true
custom_firmware:
notes:
  - The button sensor state will return to `no press` after the time set with the [reset_timer](configuration_params#reset_timer) option.
---
