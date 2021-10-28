---
manufacturer: Xiaogui
name: Smart Bluetooth Body Fat Scale
model: TZC4
image: XMTZC05HM.png
physical_description:
broadcasted_properties:
  - weight
  - non-stabilized weight
  - impedance
  - rssi
broadcasted_property_notes:
  - property: weight
    note: is only reported after the scale is stabilized
  - property: impedance
    note: is only reported after the scale is stabilized
  - property: non-stabilized weight
    note: reporting all weight measurements
  - property: rssi
    note: >
      The RSSI sensor is disabled by default. You can enable the RSSI sensor by going to `configuration`, `integrations`, select `devices` on the BLE monitor integration tile and select your device. Click on the `+1 disabled entity` to show the disabled sensor and select the disabled entity. Finally, click on `Enable entity` to enable it. 
broadcast_rate:
active_scan:
encryption_key:
custom_firmware:
notes:
  - This scale is a clone of the Xiaomi Mi Scale (V2), but is using a different BLE advertisement format. 
  - For additional data like BMI, viscaral fat, etc. you can use e.g. the [bodymiscale](https://github.com/dckiller51/bodymiscale) custom integration.
  - If you want to split your measurements into different persons, you can use [this template sensor](https://community.home-assistant.io/t/integrating-xiaomi-mi-scale/9972/533)
---
