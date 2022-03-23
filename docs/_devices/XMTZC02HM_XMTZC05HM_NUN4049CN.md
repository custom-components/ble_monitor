---
manufacturer: Xiaomi
name: Mi Body Composition Scale 2 / Mi Body Fat Scale
model: XMTZC02HM, XMTZC05HM, NUN4049CN
image: XMTZC05HM.png
physical_description:
broadcasted_properties:
  - weight
  - non-stabilized weight
  - stabilized weight
  - weight removed
  - impedance
  - rssi
broadcasted_property_notes:
  - property: weight
    note: `weight` is only reported after both the scale is stabilized and the impedance has been send by the scale (wait for the white line on the scale to start flashing). The `weight` sensor and the `impedance` sensor always correspond to the same measurement.
  - property: stabilized weight
    note: The stabilized weight is updated, even if the impedance has not been calculated and send by the scale. This sensor is updated slightly before the weight sensor, even if you step off the scale before the white line starts flashing, but the `weight` measurement does not always correspond to the `impedance` measurement. 
  - property: non-stabilized weight
    note: this sensor is reporting all weight measurements
broadcast_rate:
active_scan:
encryption_key:
custom_firmware:
notes:
  - For additional data like BMI, viscaral fat, etc. you can use e.g. the [bodymiscale](https://github.com/dckiller51/bodymiscale) custom integration.
  - If you want to split your measurements into different persons, you can use [this template sensor](https://community.home-assistant.io/t/integrating-xiaomi-mi-scale/9972/533)
---
