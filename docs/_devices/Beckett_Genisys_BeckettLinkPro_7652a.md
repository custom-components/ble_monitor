---
manufacturer: Beckett Corp.
name: Genisys oil burner control
model: BeckettLink 7652a
image: Beckett_BeckettLinkPro-7652a_Genisys-7505.jpg
physical_description: Rectangular box which plugs in to a Beckett HVAC control module .
broadcasted_properties:
  - TODO
  - rssi
broadcasted_property_notes:
  - property: TODO TODO fingerprint
    note: The fingerprint sensor is `On` if the fingerprint scan was succesaful, otherwise it is `Off` The fingerprint entity has two extra attributes, `result` and `key id`.
  - property: result
    note: >
      `result` shows the result of the last fingerprint reading and can have the following values:
        * match successful
        * match failed
        * timeout
        * low quality (too light, fuzzy)
        * insufficient area
        * skin is too dry
        * skin is too wet
  - property: key id
    note: >
      `key id` is an id number. For the fingerprint sensor, it can also be `administrator` or `unknown operator`
broadcast_rate:
active_scan: true
encryption_key:
custom_firmware:
notes:
  - The device is a BLE interface module to a modular HVAC burner system. The exact nomenclature is fuzzy. It was tested on a `BeckettLink Pro 7652a` BLE interface, coupled to a `Genisys 7505` burner control.
  - In principle this integration supports all Beckett systems which compatible with the `BeckettLink Pro 7652a` BLE interface. However, only the `Genisys 7505` burner control host module has been tested. The possible modules are listed below, but may not match the physical device *(e.g., a 7505 device via a BeckettLinkPro presents as a `LegacyGenisys`)*:
    - Genisys75xx
    - GenisysOil
    - Iot7653
    - Genisys7505
    - LegacyGenisys
    - Iot7652
    - BeckettLinkPro
    - GenisysGas
  - **active scan is not required.** It *might* give higher resolution data, allowing closer tracking of burner ignition cycles.
  - These `7652a` modules are expensive on EBay, but cheap -- With overnight shipping -- From arbitrary online parts houses.
  - The `7652a` is discontinued. However, its protocol may be substantially or entirely similar to other Beckett BLE interfaces.
  - This integration was developed by inspecting a React Native bundle inside the `MyTechnician` android app.
  - The wire protocol between the `7652a` BLE interface and the `7505` (or any other) burner control module is plain old RS232, with a very similar structure to the un-XORed BLE ADV packet.
  - Much more interesting and complete diagnostic data is available via actively read characteristics *(i.e. outside the scope of this passive BLE integration)*, but, required to read these characteristics is a physical presence check comprising a press of the "reset" button on the burner control module. It is currently unknown whether this can be overridden on stock firmware. Also, exposing the burner control's writeable characteristics -- Config *and firmware update* -- presents unfortunate risk.
---
