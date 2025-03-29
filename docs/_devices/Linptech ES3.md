---
manufacturer: Linptech
name: Linptech Human Presence Sensor
model: ES3
image: Linptech_ES3.png
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
broadcast_rate: See Notes
active_scan:
encryption_key: Yes
custom_firmware:
notes: >
  - You can use the [reset_timer](configuration_params#reset_timer) option if you want to use a different time to set the sensor to `motion clear`.
---
