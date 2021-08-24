---
manufacturer: SensorPush
name: Temperature and Humidity Sensor
model: SensorPush HT.w
image: SensorPush-HTw.jpg
physical_description:
broadcasted_properties:
  - temperature
  - humidity
broadcasted_property_notes:
  - property: humidity
    note: Typical RH accuracy of the sensor is +/-1.5%RH from 20%-80%
active_scan:
encryption_key:
custom_firmware:
notes:
  - Sensor must be first paired to the SensorPush app to activate it. Following this activation, it can be used with Home Assistant with or without further interaction with the SensorPush app.
---
