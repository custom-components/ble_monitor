---
manufacturer: Xiaomi/Philips
name: Bluetooth Night Light
model: MUE4094RT
image: MUE4094RT.jpg
physical_description:
broadcasted_properties:
  - motion
  - rssi
broadcasted_property_notes:
  - property: motion
    note: Motion detection (only `motion detected`, no light or battery state). The sensor does not broadcast `motion clear` advertisements. It is therefore required to use the [reset_timer](configuration_params#reset_timer) option with a value that is not 0.
  - property: rssi
    note: >
      The RSSI sensor is disabled by default. You can enable the RSSI sensor by going to `configuration`, `integrations`, select `devices` on the BLE monitor integration tile and select your device. Click on the `+1 disabled entity` to show the disabled sensor and select the disabled entity. Finally, click on `Enable entity` to enable it. 
broadcast_rate:
active_scan:
encryption_key:
custom_firmware:
notes:
---
