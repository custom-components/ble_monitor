---
manufacturer: Qingping
name: Hygro thermometer
model: CGG1
image: CGG1.png
physical_description: Round body, E-Ink
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
active_scan: false
encryption_key: false
custom_firmware: false
notes:
  - There are three versions of the CGG1.  The older CGG1 doesn't have a logo on the back (right picture) ![CGG1]({{site.baseurl}}/assets/images/CGG1-back.png).
  - broadcasts about 20 readings per minute, although exceptions have been reported with 1 reading per 10 minutes.
---
