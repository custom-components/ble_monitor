---
manufacturer: Chef iQ
name: Wireless Meat Thermometer
model: CQ60
image: Chef_iQ_CQ60.png
physical_description: pen-shaped probe.
broadcasted_properties:
  - temperature probe tip
  - temperature probe
  - ambient temperature
  - meat temperature
  - rssi
broadcasted_property_notes:
  - property: temperature probe tip
    note: >
      The probe has multiple temperature sensors. `temperature probe tip` is the sensor at the ring closest to the tip of the probe.
  - property: temperature probe
    note: >
      `temperature probe 1, 2 and 3` are the sensors at the other rings, where 1 is the ring next to the ring at the tip of the probe and 3 is the ring closest to the black end
      of the probe. Note that all sensors are broadcasting temperature with 1 digit, only temperature probe 3 is broadcasting temperature with 0 digits (before averaging in BLE monitor).
  - property: ambient temperature
    note: >
      `ambient temperature` is the sensor in the black part of the probe. Note that there seems to be an upper limit for the broadcasted ambient temperature.
  - property: meat temperature
    note: >
      `meat temperature` is the minimum of `temperature probe tip`, `temperature probe 1` and `temperature probe 2`.
broadcast_rate:
active_scan: true
encryption_key:
custom_firmware:
notes:
---
