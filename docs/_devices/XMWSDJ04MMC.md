---
manufacturer: Xiaomi
name: Electronic Thermometer and Hygrometer
model: XMWSDJ04MMC
image: XMWSDJ04MMC.jpg
physical_description: Small square body, EInk version
broadcasted_properties:
  - temperature
  - humidity
  - battery
  - rssi
broadcasted_property_notes:
  - property: rssi
    note: >
      The RSSI sensor is disabled by default. You can enable the RSSI sensor by going to `configuration`, `integrations`, select `devices` on the BLE monitor integration tile and select your device. Click on the `+1 disabled entity` to show the disabled sensor and select the disabled entity. Finally, click on `Enable entity` to enable it. 
broadcast_rate: Once in 5 minutes.
active_scan:
encryption_key: true
custom_firmware:
notes:
---
