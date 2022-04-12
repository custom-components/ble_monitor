---
manufacturer: MaxxMee QJ-J
name: Personal Body Analysis Scale
model: QJ-J
image: MaxxMee_QJ-J.png
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
broadcast_rate:
active_scan:
encryption_key:
custom_firmware:
notes:
  - This scale is a clone of the Xiaomi Mi Scale (V2), but is using a different BLE advertisement format. 
  - For additional data like BMI, viscaral fat, etc. you can use e.g. the [bodymiscale](https://github.com/dckiller51/bodymiscale) custom integration.
  - If you want to split your measurements into different persons, you can use [this template sensor](https://community.home-assistant.io/t/integrating-xiaomi-mi-scale/9972/533)
---
