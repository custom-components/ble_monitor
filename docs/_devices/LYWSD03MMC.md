---
manufacturer: Xiaomi
name: Hygro thermometer
model: LYWSD03MMC
image: LYWSD03MMC.jpg
physical_description: Small square body, segment LCD
broadcasted_properties:
  - temperature
  - humidity
  - battery
  - voltage
broadcasted_property_notes:
  - property: voltage
    note: battery voltage is only available with custom firmware
broadcast_rate: 1/10min. (battery level ~1/hr.)*
active_scan:
encryption_key: Yes (original firmware)
custom_firmware:
  - name: pvvx
    url: https://github.com/pvvx/ATC_MiThermometer
  - name: ATC1441
    url: https://github.com/atc1441/ATC_MiThermometer
notes:
  - Both custom firmware's broadcast temperature, humidity, battery voltage and battery level in percent. Broadcast interval can be set by the user and encryption can be used as an option. BLE monitor will automatically use the advertisement type with the highest accuracy, when setting the firmware to broadcast all advertisement types.
---
