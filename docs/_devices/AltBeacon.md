---
manufacturer: Radius Networks
name: AltBeacon
model: AltBeacon
image: AltBeacon.jpg
physical_description:
broadcasted_properties:
  - rssi
  - measured power
  - uuid
  - mac
  - major
  - minor
broadcasted_property_notes:
broadcast_rate:
active_scan: true
encryption_key:
custom_firmware:
notes:
  - AltBeacon is not a device, but a protocol developed by AltBeacon on which beacons work.
  - It should not be used for tracking `MAC addresses`, they can be dynamic, there is a `Beacon UUID` parameter for this.
---
