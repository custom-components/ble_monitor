---
manufacturer: BTHome
name: BTHome sensors
model: DIY-sensors
image: BTHome.png
physical_description:
broadcasted_properties:
  - binary
  - door
  - light
  - lock
  - motion
  - opening
  - smoke
  - switch
  - battery
  - CO2
  - count
  - dew point
  - energy
  - humidity
  - illuminance
  - weight
  - moisture
  - PM2.5
  - PM10
  - power
  - pressure
  - rssi
  - temperature
  - TVOC
  - voltage
broadcasted_property_notes:
broadcast_rate:
active_scan:
encryption_key: Optional (16 byte bindkey)
custom_firmware:
notes:
  - BTHome is a BLE format for DIY sensors. BLE monitor supports both V1 and V2 and we support most measurement types, but not all yet. If you miss one of the measurement types, please let us know, such that we can add it. More information about the format can be found on [BTHome website](https://bthome.io)
  - BTHome is supported on some Xiaomi and Qingping sensors with [custom ATC pvvx firmware](https://github.com/pvvx/ATC_MiThermometer) (select BTHome as advertising format) and on [b-parasite sensors](https://github.com/rbaron/b-parasite).
  - Multiple measurements of the same type is not supported yet in BLE monitor. Please use the official BTHome integration in HA instead.
---
