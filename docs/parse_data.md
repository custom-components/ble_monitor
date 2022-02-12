---
layout: default
title: Receive data from ESPHome (BLE Gateway)
has_children: false
has_toc: false
permalink: parse_data
nav_order: 5
---


## Parse_data service


### Introduction

BLE monitor has a service to parse BLE advertisements. This service can e.g. be used with ESPHome [BLE Gateway](https://github.com/myhomeiot/esphome-components#ble-gateway).

You can also use this service to create support for you own home-brew sensor, as long as you make sure you follow our own [HA BLE](ha_ble) format (or the format of one of the other sensor brands).

In this example you can see the BLE data packet from device with MAC address `A4:C1:38:B4:94:4C`, in the packet it's in reverse order `4C94B438C1A4`. The BLE packet should be in HCI format, with packet type HCI Event (0x04). The gateway id is optional and can e.g. be used to identify which ESPHome device did receive the message, which can be usefull for room localization.

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
          gateway_id: "{{ trigger.event.data.gateway_id }}" # Optional. If your gateway sends.
```

### Example ESPHome BLE Gateway

Configuration example:

```yaml
substitutions:
  board: esp32doit-devkit-v1 # Replace with your board.
  
  gateway_id: ble_gateway # Replace with your device name.

  wifi_ssid: "esphome" # Replace with your wifi ssid.
  wifi_password: "esphome" # Replace with your wifi password.

  ota_password: "esphome"
  api_password: "esphome"

esphome:
  name: $gateway_id
  platform: ESP32
  board: $board

logger:

api:
  password: $api_password

ota:
  password: $ota_password

wifi:
  ssid: $wifi_ssid
  password: $wifi_password
  fast_connect: on

external_components:
  - source: github://myhomeiot/esphome-components
  # For ESPHome 2021.12
  # - source: github://pr#2854
  #   components: [esp32_ble_tracker]

esp32_ble_tracker:

ble_gateway:
  devices:
    - mac_address: "00:00:00:00:00:00" # mac addresses of devices from which you want to receive packets.
  on_ble_advertise:
    then:
      homeassistant.event:
        event: esphome.on_ble_advertise
        data:
          packet: !lambda return packet;
          gateway_id: $gateway_id
```