---
manufacturer: Xiaomi
name: Mi Motion Sensor 2
model: RTCGQ02LM
image: RTCGQ02LM.png
physical_description:
broadcasted_properties:
  - light
  - motion
  - button
  - battery
broadcasted_property_notes:
  - property: motion
    note:  Light state is broadcasted upon a change in light in the room and is also broadcasted at the same time as motion is detected. The sensor does not broadcast `motion clear` advertisements. It is therefore required to use the [reset_timer](configuration_params#reset_timer) option with a value that is not 0).
  - property: button
    note:  The sensor also broadcasts `single press` if you press the button. After each button press, the sensor state shortly shows `single press` and will return to `no press` after 1 second. The sensor has an attribute which shows the `last button press`. You can use the state change event to trigger an automation in Home Assistant. Battery is broadcasted once every few hours.
broadcast_rate: See notes
active_scan:
encryption_key: true
custom_firmware:
notes:
---
