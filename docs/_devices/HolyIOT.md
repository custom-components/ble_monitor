---
manufacturer: HolyIOT
name: BLE sensors
model: HolyIOT BLE sensors
image: HolyIOT.png
physical_description:
broadcasted_properties:
  - battery
  - rssi
  - temperature
  - humidity
  - pressure
  - button
  - vibration
broadcasted_property_notes:
  - property: button
    note: press types are 'toggle' or 'no press'
broadcast_rate:
active_scan:
encryption_key: true
custom_firmware:
notes:
  - Supported measurement types depend on the model.
  - New-generation HolyIOT beacons (e.g. B1-B, B1-S; managed by the NexBeacon pro app) broadcast their battery level. Button events (single, double, triple, long press) are only sent over a BLE connection (Nordic UART service) and cannot be captured from advertisements.
  - After each button press, the sensor state shows 'Toggle'. It will return to `no press` after the time set with the [reset_timer](configuration_params#reset_timer) option.
---
