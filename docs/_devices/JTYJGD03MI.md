---
manufacturer: Xiaomi/Honeywell
name: Smoke Detector (Bluetooth)
model: JTYJGD03MI
image: JTYJGD03MI.png
physical_description: Smoke detector
broadcasted_properties:
  - smoke detector
  - button
  - battery
  - rssi
broadcasted_property_notes:
  - property: rssi
    note: >
      The RSSI sensor is disabled by default. You can enable the RSSI sensor by going to `configuration`, `integrations`, select `devices` on the BLE monitor integration tile and select your device. Click on the `+1 disabled entity` to show the disabled sensor and select the disabled entity. Finally, click on `Enable entity` to enable it. 
broadcast_rate:
active_scan:
encryption_key:
custom_firmware:
notes:
  - Only the Bluetooth model is supported
---
