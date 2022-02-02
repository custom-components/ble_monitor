---
manufacturer: Xiaomi
name: Mijia Smart kettle
model: YM-K1501
image: YM-K1501.png
physical_description:
broadcasted_properties:
  - temperature
  - switch
  - status
  - rssi
broadcasted_property_notes:
  - property: status
    note: >
      The switch entity has an extra `status` attribute, with the following values:
        * kettle is idle
        * kettle is heating
        * warming function active with boiling
        * warming function active without boiling
broadcast_rate:
active_scan:
encryption_key:
custom_firmware:
---
