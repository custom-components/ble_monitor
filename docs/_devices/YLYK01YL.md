---
manufacturer: Yeelight
name: Remote Control
model: YLYK01YL
image: YLYK01YL.jpg
physical_description:
broadcasted_properties:
  - remote
  - remote single press
  - remote long press
  - rssi
broadcasted_property_notes:
  - property: remote
    note: button pressed options are 'on', 'off', 'color temperature', '+', 'M', '-'
  - property: rssi
    note: >
      The RSSI sensor is disabled by default. You can enable the RSSI sensor by going to `configuration`, `integrations`, select `devices` on the BLE monitor integration tile and select your device. Click on the `+1 disabled entity` to show the disabled sensor and select the disabled entity. Finally, click on `Enable entity` to enable it. 
broadcast_rate:
active_scan:
encryption_key: Partly
custom_firmware:
notes:
  - The state of the remote sensor shows the combination of both, the attributes shows the button being used and the type of press individually.
  - It will return to 'no press' after the time set with the [reset_timer](configuration_params#reset_timer) option.
  - It is advised to change the reset time to 1 second (default = 35 seconds).
  - Additionally, two binary sensors are generated (one for 'short press', one for 'long press'), which is 'True' when pressing 'on', '+' or '-' and 'False' when pressing 'off'.
---
