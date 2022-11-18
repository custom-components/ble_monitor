---
manufacturer: Amazfit 
name: Smart Scale
model: Smart Scale
image: amazfit_smart_scale.png
physical_description:
broadcasted_properties:
  - weight
  - non-stabilized weight
  - pulse
  - rssi
broadcasted_property_notes:
  - property: weight
    note: is only reported after person is identified
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
