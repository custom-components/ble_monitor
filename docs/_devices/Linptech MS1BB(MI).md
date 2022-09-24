---
manufacturer: Linptech
name: Linptech Door and Window Sensor
model: MS1BB(MI)
image: Linptech_MS1BB(MI).png
physical_description:
broadcasted_properties:
  - opening
  - battery
  - status
  - button
  - rssi
broadcasted_property_notes:
  - property: status
    note: >
      The opening entity has an extra attribute "status", which can have the following values:
        * window/door broken open
        * door not closed
broadcast_rate: 20-25 advertisements per second
active_scan:
encryption_key: true
custom_firmware:
notes:
---
