---
manufacturer: Xiaomi/MiaoMiaoCe
name: Alarm clock
model: MHO-C303
image: MHO-C303.png
physical_description: Rectangular body, E-Ink
broadcasted_properties:
  - temperature
  - humidity
  - battery
  - rssi
broadcasted_property_notes:
  - property: rssi
    note: >
      The RSSI sensor is disabled by default. You can enable the RSSI sensor by going to `configuration`, `integrations`, select `devices` on the BLE monitor integration tile and select your device. Click on the `+1 disabled entity` to show the disabled sensor and select the disabled entity. Finally, click on `Enable entity` to enable it. 
broadcast_rate: ~20/min.
active_scan:
encryption_key:
custom_firmware:
notes:
---
