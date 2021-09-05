---
manufacturer: Yeelight
name: Fan Remote Control
model: YLYK01YL-FANCL
image: YLYK01YL-FAN.jpg
physical_description:
broadcasted_properties:
  - fan remote
  - button
  - rssi
broadcasted_property_notes:
  - property: fan remote
    note: button pressed options are 'fan toggle', 'light toggle', 'wind speed', 'wind mode', 'brightness', 'color temperature'
  - property: button
    note: press types are 'short press' or 'long press'
  - property: rssi
    note: >
      The RSSI sensor is disabled by default. You can enable the RSSI sensor by going to `configuration`, `integrations`, select `devices` on the BLE monitor integration tile and select your device. Click on the `+1 disabled entity` to show the disabled sensor and select the disabled entity. Finally, click on `Enable entity` to enable it. 
broadcast_rate:
active_scan: false
encryption_key: Partly
custom_firmware: false
notes:
  - The state of the remote sensor shows the combination of both, the attributes shows the button being used and the type of press individually.
  - It will return to 'no press' after the time set with the [reset_timer](configuration_params#reset_timer) option.
  - It is advised to change the reset time to 1 second (default = 35 seconds)
---
