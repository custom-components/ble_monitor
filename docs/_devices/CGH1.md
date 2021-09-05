---
manufacturer: Qingping
name: Window Door/Sensor
model: CGH1
image: CGH1.png
physical_description:
broadcasted_properties:
  - opening
  - battery
  - status
  - rssi
broadcasted_property_notes:
  - property: battery
    note: For battery level, we do not have accurate periodicity information yet.
  - property: status
    note: >
      The opening entity has an extra attribute "status", which can have the following values:
        * opened
        * closed
        * closing timeout
        * device reset
  - property: rssi
    note: >
      The RSSI sensor is disabled by default. You can enable the RSSI sensor by going to `configuration`, `integrations`, select `devices` on the BLE monitor integration tile and select your device. Click on the `+1 disabled entity` to show the disabled sensor and select the disabled entity. Finally, click on `Enable entity` to enable it. 
broadcast_rate:
active_scan:
encryption_key: true
custom_firmware:
notes:
---
