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

BLE monitor has created support for your own DIY sensors, by introducing our own BLE format that can be read by BLE monitor, called `HA BLE`. This format tries to create a flexible format that can be customized to your own needs. At the moment, it is still Work in Progress, as sensors in HA are not created automatically. This will be added in a future release. For testing purposes, you can create sensors in HA by modifying this line in [const.py](https://github.com/custom-components/ble_monitor/blob/master/custom_components/ble_monitor/const.py#L860). Note that this file is overwritten on each BLE monitor update. 

The data format has changed from earlier versions, in BLE monitor 8.0 HA BLE is using a new, more efficient, format. Note that The old format will be deprecated soon. 

The `HA BLE` format can best be explained with an example. A BLE advertisement is a long message with bytes (bytestring).  

```
043E1B02010000A5808FE648540F0201060B161C182302C4090303BF13CC
```

This message is split up in three parts, the **header**, the **advertising payload** and an **RSSI value**

- Header: `043E1B02010000A5808FE648540F`
- Adverting payload `0201060B161C182302C4090303BF13`
- RSSI value `CC`

#### Header
The first part `043E1B02010000A5808FE648540F` is the header of the message and contains, amongst others

- the length of the message in the 3rd byte (`0x1B` = 27, meaning 27 bytes after the third byte = 30 bytes in total)
- the MAC address in reversed order in byte 8-13 (`A5808FE64854`, in reversed order, this corresponds to a MAC address `54:48:E6:8F:80:A5`)
- the length of the advertising payload in byte 14 (`0x0F` = 15)

#### Advertising payload
The second part `0201060B161C182302C4090303BF13` contains the advertising payload, and can consist of one or more **Advertising Data (AD) elements**. Each element contains the following:

- 1st byte: length of the element (excluding the length byte itself)
- 2nd byte: AD type – specifies what data is included in the element
- AD data – one or more bytes - the meaning is defined by AD type

In the `HA BLE` format, the advertsing payload should contain the following two AD elements:

- Flags (`0x01`)
- UUID16 (`0x16`)

In the example, we have:

- First AD element: `020106` (always the same),
  - `0x02` = length (2 bytes)
    `0x01` = Flags
    `0x06` = in bits, this is `00000110`. Bit 1 and bit 2 are 1, meaning: 
      Bit 1: “LE General Discoverable Mode”
      Bit 2: “BR/EDR Not Supported”

- Second AD element: `0B161C182302C4090303BF13`, 
  - `0x0B` = length (11 bytes)
    `0x16` = UUID16
    `0x1C182302C4090303BF13` = HA BLE data

The HA BLE data is the part that contains the data. The data can contain multiple measurements. The example contains both temperature data and humidity data.

- HA BLE data = `1C182302C4090303BF13`
  - `0x1C18` = The first two byte are the UUID16, which are assinged numbers that can be found in [this official document]https://btprodspecificationrefs.blob.core.windows.net/assigned-values/16-bit%20UUID%20Numbers%20Document.pdf by the Bluetooth organization. For HA BLE we use the so called `GATT Service` = `User Data`. This part should always be `0x1C18`, as it is used to recognize a HA BLE message.
  - `0x2302C409` = Temperature packet
  - `0x0303BF13` = Humidity packet

Lets explain how the last two data packets work. The temperature packet is used as example.

- The first byte `0x23` (in bits `00100011`) is giving information about: 
  - The object length (bit 0-4): `00011` = 3 bytes (excluding the length byte itself)
  - The object format (bit 5-7) `001` = 1 = Signed Integer (see table below)

| type | bit 5-7 | format | Data type           |
| -----| ------- | -------| ------------------- |
| `0`  | `000`   | uint   | unsingned integer   |
| `1`  | `001`   | int    | signed integer      |
| `2`  | `010`   | float  | float               |
| `3`  | `011`   | string | string              |
| `4`  | `100`   | MAC    | not implemented yet |

- The second byte `0x02` is defining the type of measurement (temperature, see table below)
- The remaining bytes `0xC409` is the object value (little endian), which will be multiplied with the factor in the table below to get a sufficient number of digits.
  - The object length is telling us that the value is 2 bytes long (object length = 3 bytes minus the second byte) and the object format is telling us that the value is an Signed Integer.
  - `0xC409` as unsigned integer in little endian is equal to 2500.
  - The factor for a temperature measurement is 0.01, resulting in a temperature of 25.00°C

At the moment, the following sensors are supported. An preferred data type is given for your convienience, which should give you a short data message and at the same time a sufficient number of digits to display your data with high accuracy in Home Assistant. But you are free to use a different data type. If you want another sensor, let us know by creating a new issue on Github. 

| Object id | Property    | Preferred data type | Factor | example      | result    | Unit in HA | Notes |
| --------- | ----------- | --------------------| -------| ------------ | ----------| -----------| ----- |
| `0x00`    | packet id   | uint8 (1 byte)      | 1      | `020009`     | 9         |            | [1]   |
| `0x01`    | battery     | uint8 (1 byte)      | 1      | `020161`     | 97        | `%`        |       |
| `0x02`    | temperature | sint16 (2 bytes)    | 0.01   | `2302CA09`   | 25.06     | `°C`       |       |
| `0x03`    | humidity    | uint16 (2 bytes)    | 0.01   | `0303BF13`   | 50.55     | `%`        |       |
| `0x04`    | pressure    | uint24 (3 bytes)    | 0.01   | `0404138A01` | 1008.83   | `hPa`      |       |
| `0X05`    | illuminance | uint24 (3 bytes)    | 0.01   |              |           | `lux`      |       |
| `0x06`    | weight      | uint8 (2 byte)      | 0.01   |              |           | `kg`       |       |
| `0x07`    | weight unit | string (2 bytes)    | None   |              |           | `kg`       |       |
| `0x08`    | dewpoint    | sint16 (2 bytes)    | 0.01   |              |           | `°C`       |       |
| `0x09`    | count       | uint                | 1      |              |           |            |       |
| `0X0A`    | energy      | uint24 (3 bytes)    | 0.001  |              |           | `kWh`      |       |
| `0x0B`    | power       | uint24 (3 bytes)    | 0.01   |              |           | `W`        |       |
| `0x0C`    | voltage     | uint16 (2 bytes)    | 0.001  |              |           | `V`        |       |
| `0x0D`    | pm2.5       | uint16 (2 bytes)    | 1      |              |           | `kg/m3`    |       |
| `0x0E`    | pm10        | uint16 (2 bytes)    | 1      |              |           | `kg/m3`    |       |
| `0x0F`    | boolean     | uint8 (1 byte)      | None   |              |           |            |       |


**Notes**

Full example payloads are given in the [test_ha_ble.py](https://github.com/custom-components/ble_monitor/blob/master/custom_components/ble_monitor/test/test_ha_ble.py) file. 

### 1. packet id

The `packet id` is optional and is used to filter duplicate data. This allows you to send multiple advertisements that are exactly the same, to improve the chance that the advertisement arrives. BLE monitor will only process the advertisement if the `packet id` is different compared to the previous one. The `packet id` is a value between 0 (`0x00`) and 255 (`0xFF`), and should be increased on every change in data. 
