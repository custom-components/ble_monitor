---
manufacturer: Xiaomi
name: Xiaomi Human Body Sensor 2S
model: XMPIRO2SXS
image: XMPIRO2SXS.png
physical_description:
broadcasted_properties:
  - illuminance
  - motion
  - battery
  - rssi
broadcasted_property_notes:
  - property: illuminance
    note: is measured in lux.
  - property: motion
    note: Motion state is ‘motion detected’ or ‘clear’.
broadcast_rate:
active_scan:
encryption_key: True
custom_firmware:
notes: >
  - You can use the [reset_timer](configuration_params#reset_timer) option if you want to use a different time to set the sensor to `motion clear`.
---
