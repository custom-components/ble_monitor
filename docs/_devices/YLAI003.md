---
manufacturer: Yeelight
name: Smart Wireless Switch
model: YLAI003
image: YLAI003.jpg
physical_description:
broadcasted_properties:
  - button
  - battery
  - rssi
broadcasted_property_notes:
  - property: button
    note: press types are 'single press', 'double press' or 'long press'
  - property: rssi
    note: >
      The RSSI sensor is disabled by default. You can enable the RSSI sensor by going to `configuration`, `integrations`, select `devices` on the BLE monitor integration tile and select your device. Click on the `+1 disabled entity` to show the disabled sensor and select the disabled entity. Finally, click on `Enable entity` to enable it. 
broadcast_rate:
active_scan:
encryption_key: true
custom_firmware:
notes:
  - After each button press, the sensor state shows the type of press. It will return to `no press` after the time set with the [reset_timer](configuration_params#reset_timer) option.
  - It is advised to change the reset time to 1 second (default = 35 seconds).
  - The sensor has an attribute which shows the `last button press`. You can use the state change event to trigger an automation in Home Assistant.
---
