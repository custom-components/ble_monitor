---
manufacturer: Sensirion
name: Sensirion SHT4x gadget
model: SHT4x gadget
image: sensirion_SHT4x.png
physical_description:
broadcasted_properties:
  - temperature
  - humidity
  - rssi
broadcasted_property_notes:
broadcast_rate:
active_scan:
encryption_key:
custom_firmware:
notes:
  - BLE monitor doesn't support any of the other Bluetooth features (LED control, download of past data etc.), due to the passive way of getting the data. 
  - The protocol is publically available at Sensirion/arduino-ble-gadget and used to feed data into the Sensirion MyAmbience App (Android + iOS)
  - The same protocol is used by other Sensirion BLE devices as well, but these have not been implemented yet. If you want support for other Sensirion devices, create a new issue.
---
