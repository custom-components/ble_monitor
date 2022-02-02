---
manufacturer: Xiaomi Aqara
name: Lock N100
model: ZNMS16LM
image: ZNMS16LM.png
physical_description:
broadcasted_properties:
  - fingerprint
  - lock
  - battery
  - result
  - key id
  - action
  - method
  - error
  - timestamp
  - rssi
broadcasted_property_notes:
  - property: fingerprint
    note: The fingerprint sensor is `On` if the fingerprint scan was succesful, otherwise it is `Off` The fingerprint entity has two extra attributes, `result` and `key id`.
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
broadcast_rate:
active_scan:
encryption_key:
custom_firmware:
notes: Only supports the Bluetooth version (MiHome version)
---
