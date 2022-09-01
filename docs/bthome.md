---
layout: default
title: DIY sensors
has_children: false
has_toc: false
permalink: bthome
nav_order: 6
---


## DIY sensors (BTHome)


### Introduction

BLE monitor has created support for your own DIY sensors, by introducing our own BLE format that can be read by BLE monitor, called `BTHome` (previously known as `HA BLE`). This format tries to provide an energy efective, but still flexible BLE format that can be customized to your own needs. A proof of concept is the latest [ATC firmware](https://github.com/pvvx/ATC_MiThermometer), which is supporting our new BTHome format (firmware version 3.7 and up). The BTHome forat is also available as official Home Assistant integration. More information about the format of BTHome BLE data is provided on our [project website](https://bthome.io).

#### Encryption

BTHome can use AES encryption (CCM mode) to encrypt your data. Don't forget to set the encryption key in your BLE monitor device settings. More information on how to encrypt your messages is demonstrated in [this script](https://github.com/custom-components/ble_monitor/blob/master/custom_components/ble_monitor/ble_parser/bthome_encryption.py). 
