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

BLE monitor has created support for your own DIY sensors, by introducing our own BLE format that can be read by BLE monitor, called `HA BLE`. The format is following the official Bluetooth GATT Characteristic and Object Type, which can be found on page 13 and further in this document: [16-bit UUID Numbers
Document](https://btprodspecificationrefs.blob.core.windows.net/assigned-values/16-bit%20UUID%20Numbers%20Document.pdf)

The data format of each property is defined in the [GATT specification supplement](https://www.bluetooth.org/DocMan/handlers/DownloadDoc.ashx?doc_id=524815). At the moment, the following sensors are supported. If you want another sensor, let us know by creating a new issue on Github. 

| Object id | Property    | Data type        | Factor | example | result | Unit in HA |
| --------- | ----------- | ---------------- | ------------- | ------------- | ------------- | ------------- |
| `0x2A19`  | battery     | uint8 (1 byte)   | 1    | `0416192A59` | 89 | `%` |
| `0x2A6D`  | pressure    | uint32 (4 bytes) | 0.001| `07166D2A78091000` | 1051.0 | `hPa` |
| `0x2A6E`  | temperature | sint16 (2 bytes) | 0.01 | `05166E2A3409` | 23.56 | `°C`  | 
| `0x2A6F`  | humidity    | uint16 (2 bytes) | 0.01 | `05166F2A5419` | 64.84 | `%` | 
| `0x2A7B`  | dewpoint    | sint8 (1 byte)   | 1    | `04167b2a18` | 24 | `°C` | 
| `0x2A98`  | weight      | struct (1 byte, flag)) +| bit 0 of flag = 0 => 0.005 | `0616982A00AA33` | 66.13 | `kg` (bit 0 of flag = 0) | 
|           |             | uint16 (2 bytes, weight)| bit 0 of flag = 1 => 0.01 | `0616982A01AA33` | 132.26 | `lbs` (bit 0 of flag = 1) | 
| `0X2AF2`  | energy      | uint32 (4 bytes) | 0.001| `0716F22A81121000` | 1053.313 | `kWh` | 
| `0X2AFB`  | illuminance | uint24 (3 bytes) | 0.01 | `0616FB2A34AA00` | 435.72 | `lux`  | 
| `0x2B05`  | power       | uint24 (3 bytes) | 0.1  | `052B510A00` | 264.1 | `W` | 
| `0x2B18`  | voltage     | uint16 (2 bytes) | 1/64 | `0516182BB400` | 2.8125 | `V` | 
| `0x2BD6`  | pm2.5       | SFLOAT (2 bytes) | 1    | `0516D62BD204` | 1234 | `kg/m3` |
| `0x2BD7`  | pm10        | SFLOAT (2 bytes) | 1    | `0516D72BAB01`| 427 | `kg/m3` |
|           |             |  |  |  | |  |
| `0x2A4D`  | packet id   | uint8 (1 byte)   | 1    | `04164D2A09` | 9 |  |

**Notes**

The pressure sensor unit of measurement is `hPa` in Home Assistant. It was therefore decided to use this unit in stead of `Pa`, which is the GATT specification unit of measurement. 

### Payload format

BLE advertisements must contain `070848415f424c45`, which means `shortened local name` = `HA_BLE`. This will make sure BLE monitor recognizes the packet. The packet id is optional (see below). The payload has to contain at least one of the above measurements. It is allowed to have multiple measurements (e.g. temperature and humidity) in one BLE advertisment. However, the data must follow the above format. 

Full example payloads are given in the [test_ha_ble.py](https://github.com/custom-components/ble_monitor/blob/master/custom_components/ble_monitor/test/test_ha_ble.py) file. 

### packet id

The `packet id` is optional and is used to filter duplicate data. This allows you to send multiple advertisements that are exactly the same, to improve the chance that the advertisement arrives. BLE monitor will only process the advertisement if the `packet id` is different compared to the previous one. The `packet id` is a value between 0 (`0x00`) and 255 (`0xFF`), and should be increased on every change in data. 

### Instructions to create a sensor in HA (temporary workaround)

At the moment, a temperature sensor is added in [const.py](https://github.com/custom-components/ble_monitor/blob/master/custom_components/ble_monitor/const.py#L860) manually. You can change it to your needs by changing this line in const.py to the sensor you want (all sensors from the above table should work). 

**This has to be done manually at the moment and will be lost during each update of BLE monitor.** In a future update, we will change this such that it will automatically add the correct sensor(s), based on the data received. 
