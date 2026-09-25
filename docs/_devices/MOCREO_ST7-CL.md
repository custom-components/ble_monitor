---
manufacturer: MOCREO
name: Temperature Controller
model: ST7-CL
image: MOCREO_ST7-CL.png
physical_description: Compact MOCREO temperature controller / sensor with a BLE broadcast packet that follows the same base ST7 frame structure but advertises the ST7-CL model identifier.
broadcasted_properties:
  - temperature
  - rssi
broadcasted_property_notes:
  - AC-powered device; battery is not a relevant advertised entity for ST7-CL.
broadcast_rate:
active_scan: no
encryption_key:
custom_firmware:
notes: >
  This MOCREO device uses the same BLE advertisement family as the earlier ST7 model, but the app identifies the payload as ST7-CL using the model byte 0x85 in the manufacturer payload.

  The packet layout follows the existing MOCREO parsing logic for the ST7 family:
    - company identifier 0x004A
    - local name "ST7-CL"
    - manufacturer payload length 0x11
    - device type byte at offset 1 in the common payload
    - temperature extracted from the signed 16-bit field at byte 5, bit 0, with a scale of 0.01 °C
    - battery is not treated as a valid advertised entity for this AC-powered controller

  Thermostat bounds and relay state are not available in BLE advertisements.
---
