---
manufacturer: Mikrotik
name: Mikrotik TG-BT5-IN
model: TG-BT5-IN
image: Mikrotik_TG-BT5-IN.png
physical_description: Rectangular body, no screen
broadcasted_properties:
  - acceleration
  - switch
  - tilt
  - dropping
  - impact
  - battery
  - rssi
broadcasted_property_notes:
  - property: switch
    note: When the switch reports `on`, this means that the reed switch was closed at the moment of advertising.
  - property: tilt
    note: When the tilt sensor reports `on`, this means that someone is tilting the device.
  - property: dropping
    note: When the dropping sensor reports `on`, this means that someone is dropping the device.
  - property: impact
    note: When the impact sensor reports `on`, this means that there was an impact at the moment of advertising. The attributes show in which direction the impact occurred.
broadcast_rate:
active_scan:
encryption_key: No
custom_firmware:
notes:
  - The sensor can send its data with encryption, but this is not supported yet. If you want support for encrypted messages, we need information about how the data is encrypted and the encryption key.
---
