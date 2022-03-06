---
manufacturer: Inkbird
name: Inkbird IBS-TH2
model: IBS-TH2
image: Inkbird_IBS-TH2.jpg
physical_description:
broadcasted_properties:
  - temperature
  - humidity
  - battery
  - rssi
broadcasted_property_notes:
broadcast_rate:
active_scan: true
encryption_key:
custom_firmware:
notes:
  - Some IBS-TH2 devices are sending only temperature. Both are sold as IBS-TH2. Sensors that only send temperature will be recognized as IBS-TH2 (T only) in BLE monitor.
  - The BLE advertisements does contain three extra bytes. It is unknown what these bytes represent at the moment, possibly used for an extra probe of the plus versions. If you have such a device, please let us know, such that we can create support for the extra probe.
---
