---
manufacturer: Xiaomi/Honeywell
name: Formaldehyde Sensor
model: JQJCY01YM
image: JQJCY01YM.jpg
physical_description: OLED display
broadcasted_properties:
  - temperature
  - humidity
  - battery
  - formaldehyde
  - rssi
broadcasted_property_notes:
  - property: rssi
    note: >
      The RSSI sensor is disabled by default. You can enable the RSSI sensor by going to `configuration`, `integrations`, select `devices` on the BLE monitor integration tile and select your device. Click on the `+1 disabled entity` to show the disabled sensor and select the disabled entity. Finally, click on `Enable entity` to enable it. 
  - property: formaldehyde
    note: measured in (mg/m³)
broadcast_rate: ~50/min.
active_scan:
encryption_key:
custom_firmware:
notes:
---
