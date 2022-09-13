---
manufacturer: Xiaomi
name: Smart Door Lock 1S
model: XMZNMS08LM
image: XMZNMS08LM.png
physical_description:
broadcasted_properties:
  - battery
  - door
  - lock
  - key id
  - action
  - door action
  - method
  - error
  - timestamp
  - rssi
broadcasted_property_notes:
  - property: lock
    note: The state of the lock depends on the last `action`. The lock entity has five extra attributes, `action`, `method`, `error` and `key id` and `timestamp`
  - property: action
    note: >
      `action` shows the last change of the lock (displayed as an attribute of the lock sensor) and can have the followng values:
        * unlock outside the door
        * lock
        * turn on anti-lock
        * turn off anti-lock
        * unlock inside the door
        * lock inside the door
        * turn on child lock
        * turn off child lock
        * lock outside the door
  - property: method
    note: >
      `method` shows the last used locking mechanism (displayed as an attribute of the lock sensor) and can have the following values:
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
    note: The error state of the lock (displayed as an attribute of the lock sensor)
  - property: key id
    note: >
      `key id` is an id number, displayed as an attribute of the lock sensor).
  - property: timestamp
    note: The timestamp of the latest lock change (displayed as an attribute of the lock sensor)
  - property: door
    note: The door entity has one extra attributes `door action`.
  - property: door action
    note: >
      `door action` shows the last change in of the door state (displayed as an attribute of the door sensor) and can have the followng values:
        * open the door
        * close the door
        * timeout, not closed
        * knock on the door
        * pry the door
        * door stuck
broadcast_rate: Battery state can take up to several hours before it is updated.
active_scan:
encryption_key: true
custom_firmware:
notes:
---
