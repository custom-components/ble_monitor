---
manufacturer: Qingping
name: Temp & RH Monitor Lite
model: CGDK2
image: CGDK2.png
physical_description: Round body, E-Ink
broadcasted_properties:
  - temperature
  - humidity
  - battery
  - voltage
  - rssi
broadcasted_property_notes:
broadcast_rate: ~1/10min.
active_scan:
encryption_key: true
custom_firmware:
  - name: pvvx
    url: https://github.com/pvvx/ATC_MiThermometer
notes:
  - Custom firmware's broadcast temperature, humidity, battery voltage and battery level in percent. Broadcast interval can be set by the user and encryption can be used as an option. BLE monitor will automatically use the advertisement type with the highest accuracy, when setting the firmware to broadcast all advertisement types.
---
