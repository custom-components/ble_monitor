---
manufacturer: iNode
name: Energy Meter
model: Energy Meter
image: iNode_Energy_Meter.png
physical_description:
broadcasted_properties:
  - battery
  - voltage
  - energy
  - power
  - rssi
broadcasted_property_notes:
broadcast_rate: ~30/min. (See Notes)
active_scan:
encryption_key:
custom_firmware:
notes:
  - Energy meter based on pulse measuring.
  - Energy and power are calculated based on the formula's as given in the [documentation](https://docs.google.com/document/d/1hcBpZ1RSgHRL6wu4SlTq2bvtKSL5_sFjXMu_HRyWZiQ/edit#heading=h.l38j4be9ejx7).
  - The `constant` factor that is used for these calculations as well as the light level are given in the energy sensor attributes.
  - Advertisements are broadcasted every 1 a 2 seconds, but the measurement data is only changed once a minute.
---
