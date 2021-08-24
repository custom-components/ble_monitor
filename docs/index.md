---
layout: default
title: About
has_children: false
has_toc: false
permalink: /
nav_order: 1
---


## Introduction

This [Home Assistant](https://www.home-assistant.io) custom component is an alternative for
 the standard build in
 [mitemp_bt](https://www.home-assistant.io/integrations/mitemp_bt/) integration
 and the
 [Bluetooth LE Tracker](https://www.home-assistant.io/integrations/bluetooth_le_tracker/)
 integration that are available in Home Assistant. BLE monitor supports
 [many more sensors](devices) than the build in integration from manufactures like
 [Qingping, Govee, Kegtron, Thermoplus, Brifit, Ruuvitag, iNode, SensorPush and more](by_brand)
 . Unlike the original `mitemp_bt` integration, which is getting its data by
 polling the device with a default five-minute interval, this custom component
 is parsing the Bluetooth Low Energy packets payload that is constantly emitted
 by the sensor. The packets payload may contain temperature/humidity/battery
 and other data. Advantage of this integration is that it doesn't affect the
 battery as much as the built-in integration. It also solves connection issues
 some people have with the standard integration (due to passivity and the
 ability to collect data from multiple bt-interfaces simultaneously). Read more
 in the  [FAQ](faq#why-is-this-component-called-passive-and-what-does-this-mean)
 . BLE monitor also has the possibility to track BLE devices based on its (static)
 MAC address. It will listen to incoming BLE advertisements for the devices that
 you have chosen to track.

## Credits

Credits and big thanks should be given to:

- [@Magalex](https://community.home-assistant.io/u/Magalex) and [@Ernst](https://community.home-assistant.io/u/Ernst) for the component creation, development, and support.
- [@koying](https://github.com/koying) for implementing the configuration in the user interface.
- [@Thrilleratplay](https://github.com/Thrilleratplay) for the Govee sensor support and Jekyll documentation
- [@tsymbaliuk](https://community.home-assistant.io/u/tsymbaliuk) for the idea and the first code.
