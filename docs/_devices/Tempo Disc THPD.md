---
manufacturer: BlueMaestro
name: Tempo Disc Bluetooth Temperature, Humidity, Dew Point and Pressure Sensor Beacon and Data Logger
model: Tempo Disc THPD
image: BlueMaestro-tempo-disc-THPD.jpg
physical_description: Round sensor, no screen
broadcasted_properties:
  - temperature
  - humidity
  - pressure
  - rssi
broadcasted_property_notes:
  - property: rssi
    note: >
      The RSSI sensor is disabled by default. You can enable the RSSI sensor by going to `configuration`, `integrations`, select `devices` on the BLE monitor integration tile and select your device. Click on the `+1 disabled entity` to show the disabled sensor and select the disabled entity. Finally, click on `Enable entity` to enable it. 
broadcast_rate: Variable, at least once a minute.
active_scan:
encryption_key:
custom_firmware:
notes:>
      The sensor does not send the Dew Point in its BLE advertisements
---
