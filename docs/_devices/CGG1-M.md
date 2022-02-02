---
manufacturer: Qingping
name: Hygro thermometer
model: CGG1-M
image: CGG1.png
physical_description: Round body, E-Ink
broadcasted_properties:
  - temperature
  - humidity
  - battery
  - voltage
  - rssi
broadcasted_property_notes:
  - property: voltage
    note: Battery voltage is only available with custom firmware.
broadcast_rate: ~20/min.
active_scan:
encryption_key: True
custom_firmware:
  - name: pvvx
    url: https://github.com/pvvx/ATC_MiThermometer
notes:
  - There are three versions of the CGG1.  The CGG1-M has a `qingping` logo at the back (left picture) ![CGG1]({{site.baseurl}}/assets/images/CGG1-back.png)
  - broadcasts about 20 readings per minute, although exceptions have been reported with 1 reading per 10 minutes.
  - Custom firmware's broadcast temperature, humidity, battery voltage and battery level in percent. Broadcast interval can be set by the user and encryption can be used as an option. BLE monitor will automatically use the advertisement type with the highest accuracy, when setting the firmware to broadcast all advertisement types.
---
