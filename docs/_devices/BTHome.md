---
manufacturer: BTHome
name: BTHome sensors
model: DIY-sensors
image: BTHome.png
physical_description:
broadcasted_properties:
  - battery
  - temperature
  - humidity
  - pressure
  - illuminance
  - mass
  - dew point
  - count
  - energy
  - PM2.5
  - PM10
  - CO2
  - TVOC
  - moisture
  - rssi
broadcasted_property_notes:
broadcast_rate:
active_scan:
encryption_key: Optional (16 byte bindkey)
custom_firmware:
notes:
  - BTHome is a format for DIY sensors and was previously called HA BLE. More information about the format can be found on [BTHome website](https://bthome.io)
  - BTHome is supported on some Xiaomi and Qingping sensors with [custom ATC pvvx firmware](https://github.com/pvvx/ATC_MiThermometer) (select HA BLE as advertising format) and on [b-parasite sensors](https://github.com/rbaron/b-parasite).
---
