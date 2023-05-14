---
manufacturer: Tilt
name: Tilt
model: Tilt Hydrometer and thermometer
image: Tilt.png
physical_description:
broadcasted_properties:
  - temperature
  - gravity
  - rssi
broadcasted_property_notes:
broadcast_rate:
active_scan:
encryption_key:
custom_firmware:
notes:
  - Tilt is using the iBeacon protocol to send its data. It is therefore added in BLE monitor based on its UUID, not on its MAC address. It is unknown whether the MAC address is fixed or dynamic. The UUID is used to determine the color of the Tilt sensor, based on the information on this [page](https://kvurd.com/blog/tilt-hydrometer-ibeacon-data-format/). The color can be found in the `device model` in HA.
---
