---
manufacturer: SensorPush
name: Temperature, Humidity, and Barometric Pressure Sensor
model: SensorPush HTP.xw
image: SensorPush-HTPxw.jpg
physical_description:
broadcasted_properties:
  - temperature
  - humidity
  - pressure
  - rssi
broadcasted_property_notes:
  - property: humidity
    note: Typical RH accuracy of the sensor is +/-1.5%RH from 20%-80%
  - property: pressure
    note: Provided barometric pressure readings by this library are the raw "station" pressure. They would need corrected for altitude to match the readings typically provided by meteorolgists. This correction is available in the SensorPush app and may be added in future versions here.
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
