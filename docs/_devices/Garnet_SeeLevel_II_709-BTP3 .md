---
manufacturer: Garnet
name: SeeLeveL II 709-BTP3 Tank Monitor
model: SeeLevel II 709-BTP3
image: Garnet_Seelevel_709-BTP3.png
physical_description: Tank Monitor
broadcasted_properties:
  - tank
  - temperature
  - voltage
  - rssi
broadcasted_property_notes:
  - property: tank
    note: Level of the tank in percentage of the total volume
broadcast_rate:
active_scan:
encryption_key: false
custom_firmware:
notes:
    - The sensor also broadcasts volume and a total (per tank). These sensors are currently not implemented, as in tests these values stay 0 all the time. If you want to debug these sensors, you can make them visible by enabling debug logging. The values will be logged in the HA logs. Please report back here if these sensors actually report anything, such that we can implement them.
---
