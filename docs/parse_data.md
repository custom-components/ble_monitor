---
layout: default
title: Extend range with ESPHome
has_children: false
has_toc: false
permalink: parse_data
nav_order: 5
---


## Extend Bluetooth range with ESPHome BLE Gateway

### ESPHome BLE Gateway

It is possible to extend the Bluetooth range of your Home Assistant device / BLE monitor, by using an ESPHome device with ESPHome [BLE Gateway](https://github.com/myhomeiot/esphome-components#ble-gateway). An ESPHome [BLE Gateway](https://github.com/myhomeiot/esphome-components#ble-gateway) device is able to receive BLE advertisements and will forward the messages over Wifi to your Home Assistant device with BLE monitor. BLE monitor has a built in service to parse the incoming BLE advertisements from your ESPHome device, just like the BLE advertisemetns that are received with a Bluetooth dongle.

### Why isn't BLE monitor working with ESPHome Bluetooth Proxies?

A commonly asked question, why isn't BLE monitor working with ESPHome Bluetooth Proxies? This is because an ESPHome Bluetooth Proxy is forwarding its data to the official Bluetooth integration in Home Assistant. The Bluetooth integration is forwarding the data to a brand specific integration.

BLE monitor is using its own Bluetooth collecting mechanism based on `aioblescan` which is working at a lower level (HCI). BLE monitor is not using the Bluetooth integration to receive its data, and is therefore not able to receive data from ESPHome Bluetooth Proxies. You can use ESPHome [BLE Gateway](https://github.com/myhomeiot/esphome-components#ble-gateway) instead, which is able to forward data to BLE monitor in a similar way.

### Using the parse_data service for debugging

You can also use this service to debug for you own home-brew sensor, as long as you make sure you follow the format of one of the existing sensors. An open format that is free to use and that supports many sensor types is [BTHome](https://bthome.io).

In this example you can see the BLE data packet from a device with MAC address `A4:C1:38:B4:94:4C`, in the packet it's in reversed order `4C94B438C1A4`. The BLE packet should be in HCI format, with packet type HCI Event (0x04). The gateway id is optional and can e.g. be used to identify which ESPHome device did receive the message, which can be useful for room localization.

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
