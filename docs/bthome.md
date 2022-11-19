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

If you want to create your own DIY sensors, we have introduced the 
BLE format `BTHome`. This format tries to provide an energy effective, 
but still flexible BLE format that can be customized to your own needs. 
A proof of concept is the latest [ATC firmware](https://github.com/pvvx/ATC_MiThermometer), 
which is supporting the BTHome (V1) format (firmware version 3.7 and up). 
V2 has been released in november 2022, and is supported by BLE monitor as well. 
It is advised to use the V2 format. 

The BTHome format is also available as official Home Assistant integration. 
More information about the format of BTHome BLE data is provided on the [project website](https://bthome.io).

#### Encryption

BTHome can use AES encryption (CCM mode) to encrypt your data. 
Don't forget to set the encryption key in your BLE monitor device 
settings. More information on how to encrypt your messages is 
demonstrated in [this script (V2)](https://github.com/Bluetooth-Devices/bthome-ble/blob/v2.3.0/src/bthome_ble/bthome_v2_encryption.py). 
