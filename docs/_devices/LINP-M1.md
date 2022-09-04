---
manufacturer: Linptech
name: Linptech Door and Window Sensor
model: LINP-M1
image: 
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
broadcast_rate:
active_scan:
encryption_key: true
custom_firmware:
notes:
---
