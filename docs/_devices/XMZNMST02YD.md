---
manufacturer: Xiaomi
name: Xiaomi Mijia Mi Smart Door Lock Push Pull
model: XMZNMST02YD
image: XMZNMST02YD.png
physical_description:
broadcasted_properties:
  - fingerprint
  - door
  - lock
  - battery
  - result
  - key id
  - action
  - door action
  - method
  - error
  - timestamp
  - rssi
broadcasted_property_notes:
  - property: fingerprint
    note: The fingerprint sensor is `On` if the fingerprint scan was successful, otherwise it is `Off` The fingerprint entity has two extra attributes, `result` and `key id`.
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
  - property: lock
    note: The state of the lock depends on the last `action`. The lock entity has five extra attributes, `action`, `method`, `error` and `key id` and `timestamp`
  - property: action
    note: >
      `action` shows the last change in of the lock (displayed as an attribute of the lock sensor) and can have the following values:
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
  - property: timestamp
    note: The timestamp of the latest lock change (displayed as an attribute of the lock sensor)
  - property: door
    note: The door entity has one extra attributes `door action`.
    - property: door action
    note: >
      `door action` shows the last change in of the door state (displayed as an attribute of the door sensor) and can have the following values:
        * open the door
        * close the door
        * timeout, not closed
        * knock on the door
        * pry the door
        * door stuck
broadcast_rate:
active_scan:
encryption_key: Unknown
custom_firmware:
notes: Not confirmed working yet. If you have this device, let us know if it works and if it uses encryption
---
