---
manufacturer: Xiaomi
name: Motion Activated Night Light
model: MJYD02YL
image: MJYD02YL.jpg
physical_description:
broadcasted_properties:
  - battery
  - motion
  - light
  - rssi
broadcasted_property_notes:
broadcast_rate: See Notes
active_scan:
encryption_key: true
custom_firmware:
notes:
  - Light state is broadcasted once every 5 minutes when no motion is detected, when motion is detected the sensor also broadcasts the light state. Motion state is broadcasted when motion is detected, but is also broadcasted once per 5 minutes. If this message is within 30 seconds after motion, it's broadcasting `motion detected`, if it's after 30 seconds, it's broadcasting `motion clear`. Additionally, `motion clear` messages are broadcasted at 2, 5, 10, 20 and 30 minutes after the last motion.
  - You can use the [reset_timer](configuration_params#reset_timer) option if you want to use a different time to set the sensor to `motion clear`.
  - Battery is broadcasted once every 5 minutes.
---
