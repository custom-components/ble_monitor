---
manufacturer: Otodata
name: Propane Tank Monitor
model: Otodata Tank Monitor
image: otodata_propane_monitor.jpg
physical_description: Propane tank level monitoring sensor
broadcasted_properties:
  - tank level
  - temperature
  - battery
  - rssi
broadcasted_property_notes:
  - property: tank level
    note: Propane tank fill level reported as percentage (0-100%)
  - property: temperature
    note: Ambient or tank temperature in degrees Celsius
broadcast_rate: ~1-5/min (configurable, depends on model)
active_scan: false
encryption_key: false
custom_firmware:
notes:
  - This device monitors propane tank levels via BLE
  - Tank level is typically reported as a percentage
  - Some models may also report temperature and battery status
  - Ensure your specific Otodata model is compatible - different models may have different BLE packet formats
  - If your device is not working, capture BLE advertisements using the report_unknown feature and create an issue on GitHub
---

# Otodata Propane Tank Monitor

This integration supports Otodata propane tank monitoring devices that use Bluetooth Low Energy (BLE) for wireless communication.

## Features

- **Tank Level Monitoring**: Real-time propane tank fill level (0-100%)
- **Temperature Monitoring**: Ambient or tank temperature
- **Battery Monitoring**: Device battery level
- **Signal Strength**: RSSI for connection quality

## Setup

1. Install the forked BLE Monitor integration
2. The sensor should be auto-discovered if the BLE parser is correctly configured
3. Check Home Assistant for new Otodata sensors

## Troubleshooting

If your device is not detected:

1. Enable `report_unknown: "Other"` in your BLE Monitor configuration
2. Check the Home Assistant logs for BLE advertisements from your device
3. Look for the MAC address of your Otodata device
4. Report the captured data to help improve the parser

## Supported Models

- Otodata Propane Tank Monitor (various models)
- Specific model support depends on BLE protocol compatibility

## Notes

- Different Otodata models may use different BLE packet formats
- This integration is community-maintained
- Report issues or improvements on GitHub
