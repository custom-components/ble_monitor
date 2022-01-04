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
  - switch*
  - opening*
  - rssi
broadcasted_property_notes:
  - property: voltage
    note: battery voltage is only available with custom firmware
  - property: switch
    note: >
      The `switch` sensor is only available with custom firmware and is disabled by default. It represents the state of the Reed Switch. You can enable the `switch` sensor by going to `configuration`, `integrations`, select `devices` on the BLE monitor integration tile and select your device. Click on the `+1 disabled entity` to show the disabled sensor and select the disabled entity. Finally, click on `Enable entity` to enable it.
  - property: opening
    note: >
      The `opening` sensor is only available with custom firmware and is disabled by default. You can enable the `opening` sensor by going to `configuration`, `integrations`, select `devices` on the BLE monitor integration tile and select your device. Click on the `+1 disabled entity` to show the disabled sensor and select the disabled entity. Finally, click on `Enable entity` to enable it.
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
