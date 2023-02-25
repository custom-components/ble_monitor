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

BLE monitor has a service to parse BLE advertisements. This service can e.g. be used with ESPHome [BLE Gateway](https://github.com/myhomeiot/esphome-components#ble-gateway). ESPHome [BLE Gateway](https://github.com/myhomeiot/esphome-components#ble-gateway) will forward BLE advertisements that are received on the ESP device to your Home Assistant device with BLE monitor via WiFi. Please note that this is **not** the same as the recently introduced ESPHome Bluetooth Proxy. Although ESPHome Bluetooth Proxy works in a similar way as ESPHome BLE Gateway, the first is meant to be used in combination with the Home Assistant Bluetooth integration and the brand specific official BLE integrations.

You can also use this service to debug for you own home-brew sensor, as long as you make sure you follow the format of one of the existing sensors. An open format that is free to use and that supports many sensor types is [BTHome](https://bthome.io).

In this example you can see the BLE data packet from device with MAC address `A4:C1:38:B4:94:4C`, in the packet it's in reversed order `4C94B438C1A4`. The BLE packet should be in HCI format, with packet type HCI Event (0x04). The gateway id is optional and can e.g. be used to identify which ESPHome device did receive the message, which can be useful for room localization.

![parse_data_service]({{site.baseurl}}/assets/images/parse_data_service_screen.png)

### Example of an automation

The automation example below is parsing BLE advertisements that are received by ESPHome [BLE Gateway](https://github.com/myhomeiot/esphome-components#ble-gateway). At the moment a BLE advertisement arrives (trigger), it is calling the parse_data service (action) with the received data. BLE Monitor will than take care of the rest, and will add and/or update your BLE Monitor sensors, similar as like it has received an BLE advertisement via the Bluetooth adapter.


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
          packet: "{% raw %}{{ trigger.event.data.packet }}{% endraw %}"
          gateway_id: "{% raw %}{{ trigger.event.data.gateway_id }}{% endraw %}" # Optional. If your gateway sends.
```


More information on how to configure ESPHome BLE Gateway can be found on the ESPHome [BLE Gateway](https://github.com/myhomeiot/esphome-components#ble-gateway) GitHub page. 
