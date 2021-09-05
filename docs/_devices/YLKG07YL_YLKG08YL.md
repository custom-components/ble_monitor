---
manufacturer: Yeelight
name: Rotating Dimmer
model: YLKG07YL_YLKG08YL
image: YLKG07YL_YLKG08YL.png
physical_description:
broadcasted_properties:
  - dimmer
  - rssi
broadcasted_property_notes:
  - property: dimmer
    note: >-
      types are 'rotate', 'rotate (presses)', 'short press*', 'long press'.
      For rotation, it reports the rotation direction (`left`, `right`) and how far you rotate (number of `steps`).
      For `short press` it reports how many times you pressed the dimmer.
      For `long press` it reports the time (in seconds) you pressed the dimmer.
  - property: rssi
    note: >
      The RSSI sensor is disabled by default. You can enable the RSSI sensor by going to `configuration`, `integrations`, select `devices` on the BLE monitor integration tile and select your device. Click on the `+1 disabled entity` to show the disabled sensor and select the disabled entity. Finally, click on `Enable entity` to enable it. 
broadcast_rate:
active_scan:
encryption_key: true
custom_firmware:
notes:
  - The dimmer sensor state will return to `no press` after the time set with the [reset_timer](configuration_params#reset_timer) option
  - It is advised to change the reset time to 1 second (default = 35 seconds).
---
