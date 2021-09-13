---
manufacturer: Moat
name: "Moat S2"
model: "S2 Smart Temperature & Humidity Sensor"
image: "Moat_S2.png"
physical_description: "Square rounded body."
broadcasted_properties:
  - temperature
  - humidity
  - battery
  - rssi
broadcasted_property_notes:
  - property: rssi
    note: >
      The RSSI sensor is disabled by default. You can enable the RSSI sensor by going to `configuration`, `integrations`, select `devices` on the BLE monitor integration tile and select your device. Click on the `+1 disabled entity` to show the disabled sensor and select the disabled entity. Finally, click on `Enable entity` to enable it. 
broadcast_rate:
active_scan: true
encryption_key:
custom_firmware:
notes:
  - Sensor has been added based on information from https://github.com/SteveOnorato/moat_temp_hum_ble. It has not been confirmed that the sensor is working correct. Please leave an message in an new issue to confirm if it is working. 
---
