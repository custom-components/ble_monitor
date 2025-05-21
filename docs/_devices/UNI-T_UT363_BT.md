---
title: UNI-T UT363-BT
manufacturer: UNI-T
model: UT363-BT
image: UNI-T_UT363_BT.png # Placeholder image name, can be updated later
physical_description: Handheld Bluetooth Anemometer
broadcasted_properties:
  - wind_speed
  - temperature
  - rssi
broadcast_rate: "Approximately 1-2 seconds ( अनुमानित )" # Or a common default if unknown
active_scan: False # Assumed, can be verified later
encryption_key: False # Assumed, can be verified later
custom_firmware: False # Assumed
notes: |
  - Measures wind speed and temperature.
  - Data is broadcast via Bluetooth Low Energy.
  - The `wind_speed` is reported in m/s.
  - The `temperature` is reported in °C.
---

The UNI-T UT363-BT is a digital anemometer that can measure wind speed and temperature, and broadcast these values over BLE.

**Properties:**

*   **Wind Speed**: Speed of the wind (m/s)
*   **Temperature**: Ambient temperature (°C)
*   **RSSI**: Signal strength (dBm)

**Notes:**

*   Ensure your Bluetooth adapter is enabled and within range of the device.
*   The device identifier used in `MEASUREMENT_DICT` is 'UT363BT'.
