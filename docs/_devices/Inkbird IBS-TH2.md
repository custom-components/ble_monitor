---
manufacturer: Inkbird
name: Inkbird IBS-TH2
model: IBS-TH2
image: Inkbird_IBS-TH2.jpg
physical_description:
broadcasted_properties:
  - temperature
  - temperature probe 1
  - humidity
  - battery
  - rssi
broadcasted_property_notes:
  - property: humidity
    note: Some IBS-TH2 devices are not sending humidity data, only temperature. Both are sold as IBS-TH2. Sensors that only send temperature will be recognized as IBS-TH2/P01R in BLE monitor, the ones with humidity as IBS-TH.
  - property: temperature probe 1
    note: The external temperture probe is only available on the plus version of the Inkbird sensor. When the external probe is connected, the sensor will stop reporting the internal temperature.
broadcast_rate:
active_scan: true
encryption_key:
custom_firmware:
notes:
---
