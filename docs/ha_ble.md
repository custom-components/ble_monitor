---
layout: default
title: DIY sensors
has_children: false
has_toc: false
permalink: ha_ble
nav_order: 6
---


## DIY sensors (HA BLE)


### Introduction

BLE monitor has created support for your own DIY sensors, by introducing our own BLE format that can be read by BLE monitor, called `HA BLE`. This format tries to provide an energy efective, but still flexible BLE format that can be customized to your own needs. A proof of concept is the latest [ATC firmware](https://github.com/pvvx/ATC_MiThermometer), which is supporting our new HA BLE format (firmware version 3.7 and up).

The data format has changed from earlier versions, starting with BLE monitor version 8.1.0 HA BLE is using a new, more efficient, format. Note that The old format will be deprecated soon. 

### The HA BLE format

The `HA BLE` format can best be explained with an example. A BLE advertisement is a long message with bytes (bytestring).  

```
043E1B02010000A5808FE648540F0201060B161C182302C4090303BF13CC
```

This message is split up in three parts, the **header**, the **advertising payload** and an **RSSI value**

- Header: `043E1B02010000A5808FE648540F`
- Adverting payload `0201060B161C182302C4090303BF13`
- RSSI value `CC`

### Header

The first part `043E1B02010000A5808FE648540F` is the header of the message and contains, amongst others

- the length of the message in the 3rd byte (`0x1B` in hex is 27 in decimals, meaning 27 bytes after the third byte = 30 bytes in total)
- the MAC address in reversed order in byte 8-13 (`A5808FE64854`, in reversed order, this corresponds to a MAC address `54:48:E6:8F:80:A5`)
- the length of the advertising payload in byte 14 (`0x0F` = 15)

### Advertising payload

The second part `0201060B161C182302C4090303BF13` contains the advertising payload, and can consist of one or more **Advertising Data (AD) elements**. Each element contains the following:

- 1st byte: length of the element (excluding the length byte itself)
- 2nd byte: AD type – specifies what data is included in the element
- AD data – one or more bytes - the meaning is defined by the AD type

In the `HA BLE` format, the advertsing payload should contain the following two AD elements:

- Flags (`0x01`)
- UUID16 (`0x16`)

In the example, we have:

- First AD element: `020106`
  - `0x02` = length (2 bytes)
    `0x01` = Flags
    `0x06` = in bits, this is `00000110`. Bit 1 and bit 2 are 1, meaning: 
      Bit 1: “LE General Discoverable Mode”
      Bit 2: “BR/EDR Not Supported”
  - This part always has to be added, and is always the same (`0x020106`)

- Second AD element: `0B161C182302C4090303BF13` (HA BLE data) 
  - `0x0B` = length (11 bytes)
    `0x16` = Service Data - 16-bit UUID
    `0x1C182302C4090303BF13` = HA BLE data

#### HA BLE data format (non-encrypted)

The HA BLE data is the part that contains the data. The data can contain multiple measurements. We continue with the example from above.

- HA BLE data = `0x1C182302C4090303BF13`
  - `0x1C18` = The first two byte are the UUID16, which are assigned numbers that can be found in [this official document]https://btprodspecificationrefs.blob.core.windows.net/assigned-values/16-bit%20UUID%20Numbers%20Document.pdf by the Bluetooth organization. For HA BLE we use the so called `GATT Service` = `User Data` (`0x1C18`) for non-encrypted messages. For encrypted messages, we use `GATT Service` = `Bond Management` (`0x1E18`). More information about encryption can be found further down this page. This part should always be `0x1C18` (non-encrypted) or `0x1E18` (encrypted), as it is used to recognize a HA BLE message.
  - `0x2302C409` = Temperature packet
  - `0x0303BF13` = Humidity packet

Lets explain how the last two data packets work. The temperature packet is used as example.

- The first byte `0x23` (in bits `00100011`) is giving information about: 
  - The object length (bit 0-4): `00011` = 3 bytes (excluding the length byte itself)
  - The object format (bit 5-7) `001` = 1 = Signed Integer (see table below)

| type | bit 5-7 | format | Data type              |
| -----| ------- | -------| ---------------------- |
| `0`  | `000`   | uint   | unsingned integer      |
| `1`  | `001`   | int    | signed integer         |
| `2`  | `010`   | float  | float                  |
| `3`  | `011`   | string | string                 |
| `4`  | `100`   | MAC    | MAC address (reversed) |

- The second byte `0x02` is defining the type of measurement (temperature, see table below)
- The remaining bytes `0xC409` is the object value (little endian), which will be multiplied with the factor in the table below to get a sufficient number of digits.
  - The object length is telling us that the value is 2 bytes long (object length = 3 bytes minus the second byte) and the object format is telling us that the value is an Signed Integer (possitive or negative integer).
  - `0xC409` as unsigned integer in little endian is equal to 2500.
  - The factor for a temperature measurement is 0.01, resulting in a temperature of 25.00°C

At the moment, the following sensors are supported. A preferred data type is given for your convienience, which should give you a short data message and at the same time a sufficient number of digits to display your data with high accuracy in Home Assistant. But you are free to use a different data type. If you want another sensor, let us know by creating a new issue on Github. 

| Object id | Property    | Preferred data type | Factor | example          | result       | Unit in HA | Notes |
| --------- | ----------- | --------------------| -------| ---------------- | -------------| -----------| ----- |
| `0x00`    | packet id   | uint8 (1 byte)      | 1      | `020009`         | 9            |            | [1]   |
| `0x01`    | battery     | uint8 (1 byte)      | 1      | `020161`         | 97           | `%`        |       |
| `0x02`    | temperature | sint16 (2 bytes)    | 0.01   | `2302CA09`       | 25.06        | `°C`       |       |
| `0x03`    | humidity    | uint16 (2 bytes)    | 0.01   | `0303BF13`       | 50.55        | `%`        |       |
| `0x04`    | pressure    | uint24 (3 bytes)    | 0.01   | `0404138A01`     | 1008.83      | `hPa`      |       |
| `0x05`    | illuminance | uint24 (3 bytes)    | 0.01   | `0405138A14`     | 13460.67     | `lux`      |       |
| `0x06`    | weight      | uint16 (2 byte)     | 0.01   | `03065E1F`       | 80.3         | `kg`       | [2]   |
| `0x07`    | weight unit | string (2 bytes)    | None   | `63076B67`       | "kg"         |            | [2]   |
| `0x08`    | dewpoint    | sint16 (2 bytes)    | 0.01   | `2308CA06`       | 17.386       | `°C`       |       |
| `0x09`    | count       | uint                | 1      | `020960`         | 96           |            |       |
| `0X0A`    | energy      | uint24 (3 bytes)    | 0.001  | `040A138A14`     | 1346.067     | `kWh`      |       |
| `0x0B`    | power       | uint24 (3 bytes)    | 0.01   | `040B021B00`     | 69.14        | `W`        |       |
| `0x0C`    | voltage     | uint16 (2 bytes)    | 0.001  | `030C020C`       | 3.074        | `V`        |       |
| `0x0D`    | pm2.5       | uint16 (2 bytes)    | 1      | `030D120C`       | 3090         | `kg/m3`    |       |
| `0x0E`    | pm10        | uint16 (2 bytes)    | 1      | `030E021C`       | 7170         | `kg/m3`    |       |
| `0x0F`    | boolean     | uint8 (1 byte)      | 1      | `020F01`         | 1 (True)     | `True`     |       |
| `0x10`    | switch      | uint8 (1 byte)      | 1      | `021001`         | 1 (True)     | `on`       |       |
| `0x11`    | opening     | uint8 (1 byte)      | 1      | `021100`         | 0 (false)    | `closed`   |       |
| `0x12`    | co2         | uint16 (2 bytes)    | 1      | `0312E204`       | 1250         | `ppm`      |       |
| `0x13`    | tvoc        | uint16 (2 bytes)    | 1      | `03133301`       | 307          | `ug/m3`    |       |
|           | mac         | 6 bytes (reversed)  |        | `86A6808FE64854` | 5448E68F80A6 |            | [3]   |


**Notes**

Full example payloads are given in the [test_ha_ble.py](https://github.com/custom-components/ble_monitor/blob/master/custom_components/ble_monitor/test/test_ha_ble.py) file. 

***1. packet id***

The `packet id` is optional and is used to filter duplicate data. This allows you to send multiple advertisements that are exactly the same, to improve the chance that the advertisement arrives. BLE monitor will only process the advertisement if the `packet id` is different compared to the previous one. The `packet id` is a value between 0 (`0x00`) and 255 (`0xFF`), and should be increased on every change in data.

***2. weight (unit)***

The `weight unit` is in `kg` by default, but can be set with the weight unit property. Examples of `weight unit` packets are:
- kg (`63076B67`)
- lbs (`64076C6273`)
- jin (`64076A696E`)

***3. mac***

You don't have to specify the `mac` address in the advertising payload, as it is already included in the [header](#header). However, you can overwrite the `mac` by specifying it in the advertising payload. To do this, set the first byte to `0x86` (meaning: object type = 4 (`mac`) and object length = 6), followed by the MAC in reversed order. No Object id is needed.

***Restore state with restart***

Currently, the state of a sensor is not restored when restarting HA, even when this is enabled in the BLE monitor settings. This will be fixed in a future update. 


#### HA BLE data format (encrypted)

You can also choose to send the data in an encrypted way, which gives you extra security. Unencrypted BLE advertisements can be read by everyone, even your neighbour with Home Assistant and BLE Monitor should in theory be able to receive your BLE data. However, when you use encryption, it will be useless for anyone else, as long as he or she doesn't have the encryption key. The encryption key should be a 16 bytes long key (32 characters). More information on how to encrypt your messages is demonstrated in [this script](https://github.com/custom-components/ble_monitor/blob/master/custom_components/ble_monitor/ble_parser/ha_ble_encryption.py). HA BLE monitor is using an AES encryption (CCM mode). Don't forget to set the encryption key in your BLE monitor device settings.
