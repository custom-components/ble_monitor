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
broadcasted_property_notes:
  - property: remote
    note: button pressed options are 'on', 'off', 'color temperature', '+', 'M', '-'
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
