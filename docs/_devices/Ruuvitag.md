---
manufacturer: Ruuvitag
name: Ruuvitag
model: Ruuvitag
image: ruuvitag.jpg
physical_description: Round body
broadcasted_properties:
  - temperature
  - humidity
  - pressure
  - motion
  - acceleration
  - voltage
  - battery
  - rssi
broadcasted_property_notes:
  - property: motion
    note: is reported in HA when the motion counter is increased between two advertisements.
broadcast_rate:
active_scan:
encryption_key:
custom_firmware:
notes:
  - If some of these sensors are not updating, make sure you use the latest firmware (v5).
  - You can use the [reset_timer](configuration_params#reset_timer) option to set the time after which the motion sensor will return to `motion clear`, but it might be overruled by the advertisements from the sensor.
---
