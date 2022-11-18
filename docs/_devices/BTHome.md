---
manufacturer: BTHome
name: BTHome sensors
model: DIY-sensors
image: BTHome.png
physical_description:
broadcasted_properties:
  - battery
  - CO2
  - conductivity
  - count
  - dew point
  - energy
  - humidity
  - illuminance
  - moisture
  - PM2.5
  - PM10
  - power
  - pressure
  - rssi
  - temperature
  - TVOC
  - voltage
  - weight
  - binary
  - opening
  - switch

broadcasted_property_notes:
broadcast_rate:
active_scan:
encryption_key: Optional (16 byte bindkey)
custom_firmware:
notes:
  - Currently only BTHome v1 is supported and only the above mentioned measurement types are supported. If you need a different type, let us know.
  - More information about the format can be found on [BTHome website](https://bthome.io)
  - BTHome is supported on some Xiaomi and Qingping sensors with [custom ATC pvvx firmware](https://github.com/pvvx/ATC_MiThermometer) (select HA BLE as advertising format) and on [b-parasite sensors](https://github.com/rbaron/b-parasite).
---
