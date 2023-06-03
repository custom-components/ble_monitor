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
  - side
broadcasted_property_notes:
  - property: button
    note: press types are 'toggle' or 'no press'
broadcast_rate:
active_scan:
encryption_key: true
custom_firmware:
notes:
  - Supported measurement types depend on the model.
  - After each button press, the sensor state shows 'Toggle'. It will return to `no press` after the time set with the [reset_timer](configuration_params#reset_timer) option.
---
