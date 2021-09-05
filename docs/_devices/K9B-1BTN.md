---
manufacturer: Linptech
name: Switch (one button version)
model: K9B
image: Linptech_K9B.png
physical_description:
broadcasted_properties:
  - one btn switch
  - button switch
  - rssi
broadcasted_property_notes:
  - property: one btn switch
    note: returns 'toggle'
  - property: button switch
    note: types are 'short press', 'double press' or 'long press'
  - property: rssi
    note: >
      The RSSI sensor is disabled by default. You can enable the RSSI sensor by going to `configuration`, `integrations`, select `devices` on the BLE monitor integration tile and select your device. Click on the `+1 disabled entity` to show the disabled sensor and select the disabled entity. Finally, click on `Enable entity` to enable it. 
broadcast_rate:
active_scan:
encryption_key: Probably (not confirmed yet)
custom_firmware:
notes:
  - There are three different versions of this switch, with one, two or three buttons.
  - The switch sensor state will return to `no press` after the time set with the [reset_timer](configuration_params#reset_timer) option. It is advised to change the reset time to 1 second (default = 35 seconds).
---
