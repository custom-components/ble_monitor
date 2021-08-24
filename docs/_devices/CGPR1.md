---
manufacturer: Qingping
name: Motion and ambient light sensor
model: CGPR1
image: CGPR1.png
physical_description:
broadcasted_properties:
  - illuminance
  - motion
  - battery
broadcasted_property_notes:
  - property: illuminance
    note: is measured in lux.
  - property: motion
    note: Motion state is ‘motion detected’ or ‘clear’.
  - property: battery
    note: For battery level, we do not have accurate periodicity information yet.
broadcast_rate: See Notes
active_scan:
encryption_key: true
custom_firmware:
notes:
  - Illuminance is broadcasted upon every 10 minutes and when motion is detected. Motion state is broadcasted when motion is detected. Additionally, `motion clear` messages are broadcasted at 1, 2, 5, 10, 20 and 30 minutes after the last motion.
  - You can use the [reset_timer](configuration_params#reset_timer) option if you want to use a different time to set the sensor to `motion clear`.
---
