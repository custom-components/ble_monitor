---
manufacturer: Qingping
name: Motion and ambient light sensor
model: CGPR1
image: CGPR1.png
physical_description:
broadcasted_properties:
  - illuminance
  - light
  - motion
  - battery
  - rssi
broadcasted_property_notes:
  - property: illuminance
    note: is measured in lux.
  - property: light
    note: Qingping advertisements send a message with light status (dark/light). For Xiaomi MiBeacon advertisements, 100 lux is assumed to be the limit for dark/light.
  - property: motion
    note: Motion state is ‘motion detected’ or ‘clear’.
broadcast_rate: See Notes
active_scan:
encryption_key: See Notes
custom_firmware:
notes: >
  - This sensor sends advertisements in Xiaomi MiBeacon format when connected to MiHome. In this case, communication is encrypted, so it requires an encryption key to be set in the configuration options. If it is not connected to MiHome, it will broadcast advertisements in Qingping format. This advertisement format is not encrypted, so it won't require an encryption key. 
  - Switching to Qingping mode is done by pressing the button for a very long time until the LED stops flashing.
  - In Xiaomi MiBeacon mode, illuminance is broadcasted upon every 10 minutes and when motion is detected. Motion state is broadcasted when motion is detected. Additionally, `motion clear` messages are broadcasted at 1, 2, 5, 10, 20 and 30 minutes after the last motion.
  - In Qingping mode, broadcast rate of illumination and battery is every second.
  - You can use the [reset_timer](configuration_params#reset_timer) option if you want to use a different time to set the sensor to `motion clear`.
---
