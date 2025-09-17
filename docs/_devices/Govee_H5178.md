---
manufacturer: Govee
name:  Indoor/Outdoor Thermometer Hygrometer
model: H5178
image: Govee_H5178.png
physical_description: Rounded square body, Backlight LCD Touchscreen with additional rounded rectangular remote sensor for outdoor measurements.
broadcasted_properties:
  - temperature
  - humidity
  - battery
  - rssi
broadcasted_property_notes:
broadcast_rate:
active_scan: true
encryption_key:
custom_firmware:
notes:
  - active scan needs to be enabled in the BLE Monitor settings for this sensor to work. Note that two devices will be created in Home Assistant for this sensor, one with the actual MAC address, which is the indoor sensor, and one with the MAC address increased by 1, which is the outdoor sensor. You can also distinguish between the indoor and outdoor sensor by looking at the device type.
---
