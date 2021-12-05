---
layout: default
title: Parse data from ESPHome
has_children: false
has_toc: false
permalink: parse_data
nav_order: 5
---


## Parse_data service


### Introduction

BLE monitor has a service to parse BLE advertisements. This service can e.g. be used with ESPHome [BLE Gateway](https://github.com/myhomeiot/esphome-components#ble-gateway) (at the moment requires some manual adjustments to ESPHome).

You can also use this service to create support for you own home-brew sensor, as long as you make sure you follow the format of one of the existing sensors.

In this example you can see the BLE data packet from device with MAC address `BC:9A:78:56:34:12`, in the packet it's in reverse order `123456789ABC`. The BLE packet should be in HCI format, with packet type HCI Event (0x04).

![parse_data_service]({{site.baseurl}}/assets/images/parse_data_service_screen.png)

### Example of an automation

The example below is parsing BLE advertisements that are received by ESPHome [BLE Gateway](https://github.com/myhomeiot/esphome-components#ble-gateway) and converts it to a BLE monitor sensor, if it is in the correct format of a supported sensor. 

```yaml
automation:
  - alias: ESPHome BLE Advertise
    mode: queued
    trigger:
      - platform: event
        event_type: esphome.on_ble_advertise
    action:
      - service: ble_monitor.parse_data
        data:
          packet: "{{ trigger.event.data.packet }}"
```
