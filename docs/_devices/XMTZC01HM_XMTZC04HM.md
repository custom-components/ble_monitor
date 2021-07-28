---
manufacturer: Xiaomi
name: Mi Smart Scale 1 / Mi Smart Scale 2
model: XMTZC01HM, XMTZC04HM
image: XMTZC04HM.png
physical_description:
broadcasted_properties:
  - weight
  - non-stabilized weight
  - weight removed
broadcasted_property_notes:
  - property: weight
    note: is only reported after the scale is stabilized
  - property: non-stabilized weight
    note: reporting all weight measurements
broadcast_rate:
active_scan:
encryption_key:
custom_firmware:
notes:
  - For additional data like BMI, viscaral fat, etc. you can use e.g. the [bodymiscale](https://github.com/dckiller51/bodymiscale) custom integration.
  - If you want to split your measurements into different persons, you can use [this template sensor](https://community.home-assistant.io/t/integrating-xiaomi-mi-scale/9972/533)
  - https://community.home-assistant.io/t/integrating-xiaomi-mi-scale/9972/533?u=ernst
---
