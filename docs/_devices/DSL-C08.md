---
manufacturer: Xiaomi Lockin
name: Lockin Q2
model: DSL-C08
image: DSL-C08.jpg
physical_description:
broadcasted_properties:
  - lock
  - key id
  - action
  - method
  - error
  - armed away
  - timestamp
  - battery
  - rssi
broadcasted_property_notes:
  - property: lock
    note: The state of the lock depends on the last `action`. The lock entity has five extra attributes, `action`, `method`, `error` and `key id` and `timestamp`
  - property: key id
    note: >
      `key id` is an id number. For the fingerprint sensor, it can also be `administrator` or `unknown operator`
  - property: action
    note: >
      `action` shows the last change in of the lock and can have the followng values:
        * unlock outside the door
        * lock
        * turn on anti-lock
        * turn off anti-lock
        * unlock inside the door
        * lock inside the door
        * turn on child lock
        * turn off child lock
        * lock outside the door
        * abnormal
  - property: method
    note: >
      `method` shows the last used locking mechanism and can have the following values:
        * unlock outside the door
        * lock
        * bluetooth
        * password
        * biometrics
        * key
        * turntable
        * nfc
        * one-time password
        * two-step verification
        * Homekit
        * coercion
        * manual
        * automatic
        * abnormal
  - property: error
    note: The error state of the lock
  - property: timestamp
    note: The timestamp of the latest lock change
  - property: armed away
    note: >
      `armed away` Inside the locked device, this event is output from the door 'up' handle.
broadcast_rate:
active_scan:
encryption_key: Yes, see notes
custom_firmware:
notes: Only supports the Bluetooth version (MiHome version)
---