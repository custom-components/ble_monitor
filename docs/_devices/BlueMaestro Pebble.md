---
manufacturer: BlueMaestro
name: BM-PEBBLE-MONITOR Pebble™ Environment Monitor & Data Logger
model: Pebble
image: bluemaestro-pebble.jpg
physical_description: Rriangular rounded sensor, no screen
broadcasted_properties:
  - temperature
  - humidity
  - pressure
  - dewpoint
  - rssi
broadcasted_property_notes:
  - property: pressure
    note: Pressure measurement needs confirmation that it is correct. Please open an issue if you think pressure is correct/not correct.
  - property: dewpoint
    note: Dewpoint measurement needs confirmation that it is correct. Please open an issue if you think dewpoint is correct/not correct.
broadcast_rate: 
active_scan:
encryption_key:
custom_firmware:
notes:
  - The sensor sends three temperatures, only one is used as temperature. 
---
