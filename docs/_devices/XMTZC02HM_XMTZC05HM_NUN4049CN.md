---
manufacturer: Xiaomi
name: Mi Body Composition Scale 2 / Mi Body Fat Scale
model: XMTZC02HM, XMTZC05HM, NUN4049CN
image: XMTZC05HM.png
physical_description:
broadcasted_properties:
  - weight
  - non-stabilized weight
  - weight removed
  - impedance
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
---
