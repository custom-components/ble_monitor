---
manufacturer: Teltonika
name: Eye Beacon
model: Eye Beacon
image: Teltonika_eye.png
physical_description: Rounded beacon, no screen
broadcasted_properties:
  - temperature
  - humidity
  - roll
  - pitch
  - magnetic field detected
  - moving
  - movement counter
  - battery low
  - rssi
broadcasted_property_notes:
broadcast_rate:
active_scan: see notes
encryption_key:
custom_firmware:
notes:
  - Teltonika EYE sensors can send BLE data in 3 formats
1. iBeacon + EYE Sensors
2. Eddystone + EYE Sensors
3. EYE Sensors

For iBeacon + EYE Sensors and Eddystone + EYE Sensors protocols only iBeacon/Eddystone packet is broadcasted and will be seen by both active and passive scans, to see the EYE Sensors packet you need to use active scan. In other words in an environment where no BLE devices are scanning with an active scan or in case when there are no scanning devices at all, only the iBeacon/Eddystone packet will be sent by the BTS device to conserve energy.

This means that if you use the iBeacon (1) or Eddystone format (2), you will need to enable active scan. If you are only using EYE sensors format (3), you can use passive scanning in BLE monitor.
---
