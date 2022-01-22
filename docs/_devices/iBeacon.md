---
manufacturer: Apple
name: iBeacon
model: iBeacon
image: iBeacon.jpg
physical_description:
broadcasted_properties:
  - cypress temperature
  - cypress humidity
  - rssi
  - measured power
  - uuid
  - mac
  - major
  - minor
broadcasted_property_notes:
  - property: cypress temperature
    note: Measured in °C. Calculated based on minor `175.72 * ((minor & 0xff) * 256) / 65536 - 46.85`
  - property: cypress humidity
    note: Measured in RH%. Calculated based on minor `125.0 * (minor & 0xff00) / 65536 - 6`
broadcast_rate:
active_scan: true
encryption_key:
custom_firmware:
notes:
  - iBeacon is not a device, but a protocol developed by Apple on which beacons work, for example Apple AirTags.
  - It should not be used for tracking `MAC addresses`, they can be dynamic, there is a `Beacon UUID` parameter for this.
---