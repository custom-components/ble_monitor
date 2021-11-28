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
broadcast_rate:
active_scan:
encryption_key: true
custom_firmware:
notes:
  - After each button press, the sensor state shows the type of press. It will return to `no press` after the time set with the [reset_timer](configuration_params#reset_timer) option.
  - It is advised to change the reset time to 1 second (default = 35 seconds).
  - The sensor has an attribute which shows the `last button press`. You can use the state change event to trigger an automation in Home Assistant.
---
