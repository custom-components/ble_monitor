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
  - switch
  - opening
  - rssi
broadcasted_property_notes:
  - property: voltage
    note: battery voltage is only available with custom firmware
  - property: switch
    note: >
      The `switch` sensor is only available with custom firmware (pvvx) and is disabled by default. It represents the state of the Reed Switch. You can enable the `switch` sensor by going to `configuration`, `integrations`, select `devices` on the BLE monitor integration tile and select your device. Click on the `+1 disabled entity` to show the disabled sensor and select the disabled entity. Finally, click on `Enable entity` to enable it. This switch sensor can be used for a temperature or humidity trigger, for use as hygrostat or termostat (depending on settings). More information can be found [here on the pvvx website](https://github.com/pvvx/ATC_MiThermometer#temperature-or-humidity-trigger-on-gpio-pa5-label-on-the-reset-pin)
  - property: opening
    note: >
      The `opening` sensor is only available with custom firmware and is disabled by default. You can enable the `opening` sensor by going to `configuration`, `integrations`, select `devices` on the BLE monitor integration tile and select your device. Click on the `+1 disabled entity` to show the disabled sensor and select the disabled entity. Finally, click on `Enable entity` to enable it. More information about the use of this opening sensor can be found on [here on the pvvx website](https://github.com/pvvx/ATC_MiThermometer#reed-switch-on-gpio-pa6-label-on-the-p8-pin)
broadcast_rate: 1/10min. (battery level ~1/hr.)*
active_scan:
encryption_key: Yes (original firmware), optional with pvvx firmware
custom_firmware:
  - name: pvvx
    url: https://github.com/pvvx/ATC_MiThermometer
  - name: ATC1441
    url: https://github.com/atc1441/ATC_MiThermometer
notes:
  - Both custom firmwares broadcast temperature, humidity, battery voltage and battery level in percent. Broadcast interval can be set by the user and encryption can be used as an option. BLE monitor supports all possible broadcast types that can be selected in the TelinkMiFlasher tool.
---
