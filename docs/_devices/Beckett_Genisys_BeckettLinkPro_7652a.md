---
manufacturer: Beckett Corp.
name: Genisys oil burner interface
model: BeckettLink 7652a
image: Beckett_BeckettLinkPro-7652a_Genisys-7505.jpg
physical_description: Rectangular box which plugs in to a Beckett HVAC control module .
broadcasted_properties:
  - rssi
  - burner_state
  - burner_last_end_cause
  - burner_cycle_count
  - burner_product
  - burner_device
  - burner_serial
  - burner_is_bootloader
  - burner_connectable
  - burner_advertisement_version

broadcasted_property_notes:
  - property: burner_state
    note: >
      indicates the current operational state of the burner. Possible values might include states such as:
      * `Standby`
      * `MotorRelayTest`
      * `Prepurge`
      * `TFI`
      * `CarryOver`
      * `Run`
      * `PostPurge`
      * `Recycle`
      * `Lockout`
      * `PumpPrime`
      * `MotorRelayFeedbackTest`
      * `NoIgnitionPrePurge`
  - property: burner_last_end_cause
    note: >
      can have the following values:
        * `NoEndCauseReported`
        * `CFHEnded`
        * `FlameLoss`
        * `PumpPrime`
        * `ManualShutdown`
        * `LowVoltage`
        * `DidNotLight`
        * `FlameEndOfPretime`
        * `RelayFailure`
  - property: burner_cycle_count
    note: >
      indicates how many times the burner has ignited. `It persists through power loss.
  - property: burner_product
    note: >
      can have the following values:
        * `Genisys75xx`
        * `GenisysOil`
        * `Iot7653`
        * `Genisys7505`
        * `LegacyGenisys`
        * `Iot7652`
        * `BeckettLinkPro`
        * `GenisysGas`
  - property: burner_device
    note: >
      identifies the specific hardware model of the burner within its `burner_product` family. Possible examples include:
        * `DeviceNameKey7505_7575`
        * `DeviceNameKey7556`
        * `DeviceNameKey7559`
        * `DeviceNameKey7580`
  - property: burner_serial
    note: >
      belongs to the burner control module.
  - property: burner_is_bootloader
    note: >
      indicates whether the burner is currently running in bootloader/firmware-update mode (as the device supports OTA DFU)
  - property: burner_connectable
    note: >
      specifies whether the burner is advertising itself as connectable over BLE.
broadcast_rate:
active_scan: true
encryption_key:
custom_firmware:
notes:
  - Active scan is not required. It *might* give higher resolution data, allowing closer tracking of burner ignition cycles. Battery life is irrelevant since the system is mains powered.
  - The device is a BLE interface module to a modular HVAC burner system. The exact nomenclature is fuzzy. It was tested on a `BeckettLink Pro 7652a` BLE interface, coupled to a `Genisys 7505` burner control.
  - In principle this integration supports all Beckett systems which compatible with the `BeckettLink Pro 7652a` BLE interface. However, only the `Genisys 7505` burner control host module has been tested. In other words `burner_product` may not match the physical device, e.g. a 7505 device via a BeckettLinkPro presents as a `LegacyGenisys`
  - These `7652a` modules are expensive on EBay, but cheap -- With overnight shipping -- From arbitrary online parts houses. The `7652a` is discontinued. However, its protocol may be substantially or entirely similar to other Beckett BLE interfaces.
  - This integration was developed by inspecting a React Native bundle inside the `MyTechnician` android app.
  - The wire protocol between the `7652a` BLE interface and the `7505` (or any other) burner control module is plain old RS232, with a very similar structure to the un-XORed BLE ADV packet.
  - Much more interesting and complete diagnostic data is available via actively read characteristics *(i.e. outside the scope of this passive BLE integration)*, but, required to read these characteristics is a physical presence check comprising a press of the "reset" button on the burner control module. It is currently unknown whether this can be overridden on stock firmware. Also, exposing the burner control's writeable characteristics -- Config *and firmware update* -- presents additional risk.
---
