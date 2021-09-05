---
manufacturer: SensorPush
name: Temperature and Humidity Sensor
model: SensorPush HT.w
image: SensorPush-HTw.jpg
physical_description:
broadcasted_properties:
  - temperature
  - humidity
  - rssi
broadcasted_property_notes:
  - property: humidity
    note: Typical RH accuracy of the sensor is +/-1.5%RH from 20%-80%
  - property: rssi
    note: >
      The RSSI sensor is disabled by default. You can enable the RSSI sensor by going to `configuration`, `integrations`, select `devices` on the BLE monitor integration tile and select your device. Click on the `+1 disabled entity` to show the disabled sensor and select the disabled entity. Finally, click on `Enable entity` to enable it. 
broadcast_rate: One reading per minute.
active_scan:
encryption_key:
custom_firmware:
notes:
  - Sensor must be first paired to the SensorPush app to activate it. Following this activation, it can be used with Home Assistant with or without further interaction with the SensorPush app.
---
