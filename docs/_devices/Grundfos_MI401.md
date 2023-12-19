---
manufacturer: Grundfos
name: ALPHA Reader MI401
model: MI401
image: Grundfos_MI401.png
physical_description: Rounded stick
broadcasted_properties:
  - flow
  - water pressure
  - temperature
  - battery state
  - pump mode
  - pump id
  - rssi
broadcasted_property_notes:
  - property: battery state
    note: Battery state is an attribute of the pump mode sensor. The meaning of the state is unknown. If you have more information about the
    meaning of the different states, let us know
  - property: pump id
    note: The pum id is an attribute of the pump mode sensor. The reader can send data of multiple pumps, each with its own id. In the current
    implementation, we have assumed that only one pump is connected, which means that data of multiple pumps gets mixed in the sensor output.
    If you have multipel pumps, modifications to the code will have to be made. Please open a new issue if you want to request multiple pump support.
broadcast_rate:
active_scan: true
encryption_key:
custom_firmware:
notes:
  - actve scan needs to be enabled in the BLE Monitor settings for this sensor to work.
---
