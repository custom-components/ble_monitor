---
manufacturer: Qingping
name: Bluetooth alarm clock
model: CGC1
image: CGC1.jpg
physical_description:
broadcasted_properties:
  - temperature
  - humidity
  - battery
  - rssi
broadcasted_property_notes:
  - property: battery
    note: For battery level, we do not have accurate periodicity information yet.
  - property: rssi
    note: >
      The RSSI sensor is disabled by default. You can enable the RSSI sensor by going to `configuration`, `integrations`, select `devices` on the BLE monitor integration tile and select your device. Click on the `+1 disabled entity` to show the disabled sensor and select the disabled entity. Finally, click on `Enable entity` to enable it. 
broadcast_rate:
active_scan:
encryption_key: Yes (Xiaomi MiBeacon advertisement)
custom_firmware:
notes:
  - The sensor sends BLE advertisements in Xiaomi MiBeacon format and Qingping format, but only MiBeacon format is supported currently.
  - Xiaomi MiBeacon advertisements are most likely encrypted.
  - >
    If you have information about update frequency, encryption key requirement, and/or a log with `report_unknown: 'qingping'`, we can improve the documentation and implement qingping format support without encryption. Please open an issue with this information.
---
