# Passive BLE Monitor integration

### Xiaomi Mijia BLE MiBeacon Monitor

<!-- TOC -->

- [INTRODUCTION](#introduction)
- [SUPPORTED SENSORS](#supported-sensors)
- [HOW TO INSTALL](#how-to-install)
  - [1. Grant permissions for Python to have rootless access to the HCI interface](#1-grant-permissions-for-python-to-have-rootless-access-to-the-hci-interface)
  - [2. Install the custom integration](#2-install-the-custom-integration)
  - [3. Add your sensors to the MiHome app if you haven’t already](#3-add-your-sensors-to-the-mihome-app-if-you-havent-already)
  - [4. Configure the integration](#4-configure-the-integration)
    - [4a. Configuration in the User Interface](#4a-configuration-in-the-user-interface)
    - [4b. Configuration in YAML](#4b-configuration-in-yaml)
- [CONFIGURATION PARAMETERS](#configuration-parameters)
  - [Configuration parameters at component level](#configuration-parameters-at-component-level)
  - [Configuration parameters at device level](#configuration-parameters-at-device-level)
  - [Configuration in the User Interface](#configuration-in-the-user-interface)
  - [Configuraton in YAML](#configuraton-in-yaml)
  - [Deleting devices and sensors](#deleting-devices-and-sensors)
- [FREQUENTLY ASKED QUESTIONS](#frequently-asked-questions)
- [CREDITS](#credits)
- [FORUM](#forum)

<!-- /TOC -->

## INTRODUCTION

This custom component is an alternative for the standard build in [mitemp_bt](https://www.home-assistant.io/integrations/mitemp_bt/) integration that is available in Home Assistant and supports much more sensors than the build in integration. Unlike the original `mitemp_bt` integration, which is getting its data by polling the device with a default five-minute interval, this custom component is parsing the Bluetooth Low Energy packets payload that is constantly emitted by the sensor. The packets payload may contain temperature/humidity/battery and other data. Advantage of this integration is that it doesn't affect the battery as much as the built-in integration. It also solves connection issues some people have with the standard integration (due to passivity and the ability to collect data from multiple bt-interfaces simultaneously). Read more in the [FAQ](https://github.com/custom-components/ble_monitor/blob/master/faq.md#why-is-this-component-called-passive-and-what-does-it-mean).

## SUPPORTED SENSORS

|Name|Description|Picture|
|---|---|---|
|**LYWSDCGQ** <img width=100/>|**Xiaomi Hygro thermometer**<br /><br />Round body, segment LCD, broadcasts temperature, humidity and battery level, about 20 readings per minute. <img width=100/>|![LYWSDCGQ](/pictures/LYWSDCGQ.jpg) <img width=1500/>|
|**CGG1**|**Qingping Hygro thermometer**<br /><br />Round body, E-Ink, broadcasts temperature, humidity and battery level, about 20 readings per minute. Note that there are (at least) three versions, CGG1, CGG1-M (MiHome version) and CGG1-H (Homekit version). The CGG1-H (Homekit version) is not supported. The CGG1-M (MiHome version) works with encryption and has a `qingping` logo at the back (left picture), while the old CGG1 works without encryption and doesn't have a logo at the back (right picture).<br /><br />![CGG1](/pictures/CGG1-back.png)<br /><br />For sensors with encryption, you will need to set the encryption key in your configuration, see for instructions the [encryption_key](#encryption_key) option.<br /><br />CGG1-M (MiHome version) also supports custom ATC firmware available [here](https://github.com/pvvx/ATC_MiThermometer). The old CGG1 does not support custom firmware. |![CGG1](/pictures/CGG1.png)|
|**CGDK2**|**Qingping Temp & RH Monitor Lite**<br /><br />Round body, E-Ink, broadcasts temperature, humidity and battery level, about 1 readings per 10 minutes, advertisements are encrypted, therefore you need to set the key in your configuration, see for instructions the [encryption_key](#encryption_key) option.|![CGDK2](/pictures/CGDK2.png)|
|**LYWSD02**|**Xiaomi Temperature and Humidity sensor**<br /><br />Rectangular body, E-Ink, broadcasts temperature, humidity and battery level (battery level is available for firmware version 1.1.2_00085 and later), about 20 readings per minute.|![LYWSD02](/pictures/LYWSD02.jpeg)|
|**LYWSD03MMC**|**Xiaomi Hygro thermometer**<br /><br />Small square body, segment LCD, broadcasts temperature and humidity once in about 10 minutes and battery level once in an hour (original firmware). With the original firmware, advertisements are encrypted, therefore you need to set an encryption key in your configuration, see for instructions the [encryption_key](#encryption_key) option (not needed for sensors with custom firmware).<br /><br />`ble_monitor` also supports custom ATC firmware (both the firmware by `ATC1441`, available [here](https://github.com/atc1441/ATC_MiThermometer), and the improved firmware by `pvvx` available [here](https://github.com/pvvx/ATC_MiThermometer)). Both custom firmware's broadcast temperature, humidity, battery voltage and battery level in percent (note that both battery sensors are only visible as sensor with `batt_entities: True`). Reloading the integration is needed to receive the voltage sensor after switching the firmware. For the `pvvx` firmware, it is advised to change the `advertisement type` from `all` to `custom`. Sending multiple advertisment types at the same time might cause the voltage sensor from not showing up, depending on which advertisement comes first. The advertisement type `custom` will also result in a higher accuracy.|![LYWSD03MMC](/pictures/LYWSD03MMC.jpg)|
|**CGD1**|**Qingping Cleargrass CGD1 alarm clock**<br /><br />Segment LCD, broadcasts temperature and humidity (once in about 10 minutes), and battery level (we do not have accurate periodicity information yet). The sensor sends BLE advertisements in Xiaomi MiBeacon format and Qingping format. Qingping advertisements are not encrypted. Xiaomi MiBeacon advertisements are encrypted, if you want to receive both advertisements, you need to set the key in your configuration, see for instructions the [encryption_key](#encryption_key) option.|![CGD1](/pictures/CGD1.jpg)|
|**CGP1W**|**Qingping Cleargrass indoor weather station with Atmospheric pressure measurement**<br /><br />Broadcasts temperature, humidity, air pressure and and battery level (we do not have accurate periodicity information yet).|![CGP1W](/pictures/CGP1W.jpg)|
|**MHO-C303**|**Alarm clock**<br /><br />Rectangular body, E-Ink, broadcasts temperature, humidity and battery level, about 20 readings per minute.|![MHO-C303](/pictures/MHO-C303.png)|
|**MHO-C401**|**Alarm clock**<br /><br />Small square body, E-Ink display, broadcasts temperature and humidity once in about 10 minutes and battery level once in an hour, advertisements are encrypted, therefore you need to set the key in your configuration, see for instructions the [encryption_key](#encryption_key) option.<br /><br />`ble_monitor` also supports custom ATC firmware available [here](https://github.com/pvvx/ATC_MiThermometer). It has not been tested yet, but will most likely work (please confirm if working for MHO-C401 by creating an issue)|![MHO-C401](/pictures/MHO-C401.jpg)|
|**JQJCY01YM**|**Xiaomi Honeywell Formaldehyde Sensor**<br /><br />OLED display, broadcasts temperature, humidity, formaldehyde (mg/m³) and battery level, about 50 messages per minute.|![supported sensors](/pictures/JQJCY01YM.jpg)|
|**HHCCJCY01**|**MiFlora plant sensor**<br /><br />Broadcasts temperature, moisture, illuminance, conductivity, 1 reading per minute, no battery info with firmware v3.2.1.|![HHCCJCY01](/pictures/HHCCJCY01.jpg)|
|**GCLS002**|**VegTrug Grow Care Garden**<br /><br />Similar to MiFlora HHCCJCY01.|![GCLS002](/pictures/GCLS002.png)|
|**HHCCPOT002**|**FlowerPot, RoPot**<br /><br />Broadcasts moisture and conductivity, 2 readings per minute, no battery info with firmware v1.2.6.|![HHCCPOT002](/pictures/HHCCPOT002.jpg)|
|**WX08ZM**|**Xiaomi Mija Mosquito Repellent**<br /><br />Smart version, broadcasts switch state, tablet resource, battery level, about 50 messages per minute.|![WX08ZM](/pictures/WX08ZM.jpg)
|**MCCGQ02HL**|**Xiaomi Mijia Window/Door Sensor 2**<br /><br />Broadcasts opening state, light state and battery level. Advertisements are encrypted, therefore you need to set an encryption key in your configuration, see for instructions the [encryption_key](#encryption_key) option. Battery level is only send once in approximately 24 hours.|![MCCGQ02HL](/pictures/MCCGQ02HL.png)|
|**CGH1**|**Qingping Window Door/Sensor**<br /><br />Broadcasts opening state and battery level. Advertisements are encrypted, therefore you need to set an encryption key in your configuration, see for instructions the [encryption_key](#encryption_key) option. Battery level is broadcasted, but interval is currently not known.|![CGH1](/pictures/CGH1.png)|
|**YM-K1501**|**Xiaomi Mijia Smart kettle**<br /><br />Broadcasts temperature. The switch entity has an extra `ext_state` attribute, with the following values: `0` - kettle is idle, `1` - kettle is heating water, `2` - warming function is active with boiling, `3` - warming function is active without boiling.|![YM-K1501](/pictures/YM-K1501.png)|
|**V-SK152**|**Viomi Smart Kettle**<br /><br />Broadcasts temperature and `ext_state` attribute as in YM-K1501, data broadcasted every 30 seconds.|![V-SK152](/pictures/V-SK152.png)|
|**SJWS01LM**|**Xiaomi Smart Water Leak Sensor**<br /><br />Broadcasts moisture state (wet/dry), advertisements are encrypted, therefore you need to set the key in your configuration, see for instructions the [encryption_key](#encryption_key) option.|![SJWS01LM](/pictures/SJWS01LM.png)|
|**MJYD02YL**|**Xiaomi Motion Activated Night Light**<br /><br />Broadcasts light state (`light detected/no light`), motion (`motion detected/clear`) and battery state, advertisements are encrypted, therefore you need to set the key in your configuration, see for instructions the [encryption_key](#encryption_key) option.<br /><br />Light state is broadcasted once every 5 minutes when no motion is detected, when motion is detected the sensor also broadcasts the light state. Motion state is broadcasted when motion is detected, but is also broadcasted once per 5 minutes. If this message is within 30 seconds after motion, it's broadcasting `motion detected`, if it's after 30 seconds, it's broadcasting `motion clear`. Additonally, `motion clear` messages are broadcasted at 2, 5, 10, 20 and 30 minutes after the last motion. You can use the [reset_timer](#reset_timer) option if you want to use a different time to set the sensor to `motion clear`. Battery is broadcasted once every 5 minutes.|![MJYD02YL](/pictures/MJYD02YL.jpg)|
|**MUE4094RT**|**Xiaomi Philips Bluetooth Night Light**<br /><br />Broadcasts motion detection (only `motion detected`, no light or battery state). The sensor does not broadcast `motion clear` advertisements. It is therefore required to use the [reset_timer](#reset_timer) option with a value that is not 0.|![MUE4094RT](/pictures/MUE4094RT.jpg)|
|**RTCGQ02LM**|**Xiaomi Mi Motion Sensor 2**<br /><br />Broadcasts light state (`light detected/no light`), motion (`motion detected/clear`), button press and battery state, advertisements are encrypted, therefore you need to set the key in your configuration, see for instructions the [encryption_key](#encryption_key) option.<br /><br />Light state is broadcasted upon a change in light in the room and is also broadcasted at the same time as motion is detected. The sensor does not broadcast `motion clear` advertisements. It is therefore required to use the [reset_timer](#reset_timer) option with a value that is not 0). The sensor also broadcasts `single press` if you press the button. After each button press, the sensor state shortly shows `single press` and will return to `no press` after 1 second. The sensor has an attribute which shows the `last button press`. You can use the state change event to trigger an automation in Home Assistant. Battery is broadcasted once every few hours.|![RTCGQ02LM](/pictures/RTCGQ02LM.png)|
|**CGPR1**|**Qingping Motion and ambient light sensor**<br /><br />Broadcasts illuminance (in lux), motion (`motion detected/clear`) and battery state, advertisements are encrypted, therefore you need to set the key in your configuration, see for instructions the [encryption_key](#encryption_key) option.<br /><br />Illumination is broadcasted upon every 10 minutes and when motion is detected. Motion state is broadcasted when motion is detected. Additonally, `motion clear` messages are broadcasted at 1, 2, 5, 10, 20 and 30 minutes after the last motion. You can use the [reset_timer](#reset_timer) option if you want to use a different time to set the sensor to `motion clear`. Battery level is broadcasted, but interval is currently not known.|![CGPR1](/pictures/CGPR1.png)|
|**MMC-T201-1**|**Xiaomi Miaomiaoce Digital Baby Thermometer**<br /><br />Broadcasts temperature and battery state. The calculated body temperature is displayed in BLE Monitor, please note the disclaimer below. About 15-20 messages per minute.<br /><br />**DISCLAIMER**<br />The sensor sends two temperatures in the BLE advertisements, that are converted to a body temperature with a certain algorithm in the original app. We tried to reverse engineering this relation, but we were only able to approximate the relation in the range of 36.5°C - 37.9°C at this moment. It has not been calibrated at elevated body temperature (e.g. if someone has a fever), so measurements displayed in Home Assistant might be different (wrong) compared to those reported in the app. It is therefore advised NOT to rely on the measurements in BLE monitor if you want to monitor your or other peoples body temperature / health). If you have additional measurements, especially outside the investigated range, please report them in this [issue](https://github.com/custom-components/ble_monitor/issues/264).|![MMC-T201-1](/pictures/MMC-T201-1.jpg)|
|**YLAI003**|**Yeelight Smart Wireless Switch**<br /><br />Broadcasts `single press`, `double press` and `long press`. After each button press, the sensor state shortly shows the type of press and will return to `no press` after 1 second. The sensor has an attribute which shows the `last button press`. You can use the state change event to trigger an automation in Home Assistant. Advertisements are encrypted, you need to set the encryption key in your configuration, see for instructions the [encryption_key](#encryption_key) option.|![YLAI003](/pictures/YLAI003.jpg)|
|**XMTZC01HM, XMTZC04HM**|**Mi Smart Scale 1 / Mi Smart Scale 2**<br /><br />Broadcasts `weight`, `non-stabilized weight` and `weight removed`. The `weight` is only reported after the scale is stabilized, while the `non-stabilized weight` is reporting all weight measurements.|![XMTZC05HM](/pictures/XMTZC04HM.png)|
|**XMTZC02HM, XMTZC05HM, NUN4049CN**|**Mi Body Composition Scale 2 / Mi Body Fat Scale**<br /><br />Broadcasts `weight`, `non-stabilized weight`, `impedance` and `weight removed`. The `weight` is only reported after the scale is stabilized, while the `non-stabilized weight` is reporting all weight measurements.|![XMTZC05HM](/pictures/XMTZC05HM.png)|
  
*The amount of actually received data is highly dependent on the reception conditions (like distance and electromagnetic ambiance), readings numbers are indicated for good RSSI (Received Signal Strength Indicator) of about -75 till -70dBm.*

**Do you want to request support for a new sensor? In the [FAQ](https://github.com/custom-components/ble_monitor/blob/master/faq.md#my-sensor-from-the-xiaomi-ecosystem-is-not-in-the-list-of-supported-ones-how-to-request-implementation) you can read instructions how to request support for other sensors.**

## HOW TO INSTALL

### 1. Grant permissions for Python to have rootless access to the HCI interface

This is usually only needed for alternative installations of Home Assistant that only install Home Assistant core.

- to grant access:

     ```shell
     sudo setcap 'cap_net_raw,cap_net_admin+eip' `readlink -f \`which python3\``
     ```

- to verify:

     ```shell
     sudo getcap `readlink -f \`which python3\``
     ```

*In case you get a PermissionError, check the [Frequently Asked Questions (FAQ) page](faq.md).

### 2. Install the custom integration

The easiest way to install the BLE Monitor integration is with [HACS](https://hacs.xyz/). First install [HACS](https://hacs.xyz/) if you don't have it yet. After installation you can find this integration in the HACS store under integrations.

Alternatively, you can install it manually. Just copy paste the content of the `ble_monitor/custom_components` folder in your `config/custom_components` directory. As example, you will get the `sensor.py` file in the following path: `/config/custom_components/ble_monitor/sensor.py`. The disadvantage of a manual installation is that you won't be notified about updates.

### 3. Add your sensors to the MiHome app if you haven’t already

Many Xiaomi ecosystem sensors (maybe all) do not broadcast BLE advertisements containing useful data until they have gone through the "pairing" process in the MiHome app. The encryption key is also (re)set when adding the sensor to the MiHome app, so do this first. Some sensors also support alternative firmware, which doesn't need to be paired to MiHome.

### 4. Configure the integration

There are two ways to configure the integration and your devices (sensors), in the User Interface (UI) or in your YAML configuration file. Choose one method, you can't use both ways at the same time. You are able to switch from one to the other, at any time.

#### 4a. Configuration in the User Interface

Make sure you restart Home Assistant after the installation in HACS. After the restart, go to **Configuration** in the side menu in Home Assistant and select **Integrations**. Click on **Add Integrations** in the bottom right corner and search for **Passive BLE Monitor** to install. This will open the configuration menu with the default settings. The options are explained in the [configuration parameters](#configuration-parameters) section below and can also be changed later in the options menu. After a few seconds, the sensors should be added to your Home Assistant automatically. Note that the actual measurements require at least one [period](#period) to become visible.

  ![Integration setup](/pictures/configuration_screen.png)

#### 4b. Configuration in YAML

Alternatively, you can add the configuration in `configuration.yaml` as explained below. The options are the same as in the UI and are explained in the [configuration parameters](#configuration-parameters) section below. After adding your initial configuration to your YAML file, or applying a configuration change in YAML, a restart is required to load the new configuration. After a few minutes, the sensors should be changed/added to your Home Assistant automatically (at least one [period](#period) required).

An example of `configuration.yaml` with the minimum configuration is:

```yaml
ble_monitor:
```

An example of `configuration.yaml` with all optional parameters is:

```yaml
ble_monitor:
  bt_interface: '04:B1:38:2C:84:2B'
  discovery: True
  active_scan: False
  report_unknown: False
  batt_entities: False
  decimals: 1
  period: 60
  log_spikes: False
  use_median: False
  restore_state: False
  devices:
    - mac: 'A4:C1:38:2F:86:6C'
      name: 'Livingroom'
      encryption_key: '217C568CF5D22808DA20181502D84C1B'
      temperature_unit: C
      decimals: 2
      use_median: False
      restore_state: default
    - mac: 'C4:3C:4D:6B:4F:F3'
      name: 'Bedroom'
      temperature_unit: F
    - mac: 'B4:7C:8D:6D:4C:D3'
      reset_timer: 35
```

Note: The encryption_key parameter is only needed for sensors, for which it is [pointed](#supported-sensors) that their messages are encrypted.

## CONFIGURATION PARAMETERS

### Configuration parameters at component level


#### bt_interface

   (MAC address or list of multiple MAC addresses)(Optional) This parameter is used to select the Bluetooth-interface of your Home Assistant host. When using YAML, a list of available Bluetooth-interfaces available on your system is given in the Home Assistant log during startup of the Integration. If you don't specify a MAC address, by default the first interface of the list will be used. If you want to use multiple interfaces, you can use the following configuration:

```yaml
ble_monitor:
  bt_interface:
    - '04:B1:38:2C:84:2B'
    - '34:DE:36:4F:23:2C'
```

   Default value: First available MAC address

#### hci_interface

   (positive integer or list of positive integers)(Optional) Like the previous option `bt_interface`, this parameter is also used to select the bt-interface of your Home Assistant host. It is however strongly advised to use the `bt_interface` option and not this `hci_interface` option, as the hci number can change, e.g. when plugging in a dongle. However, due to backwards compatibility, this option is still available. Use 0 for hci0, 1 for hci1 and so on. On most systems, the interface is hci0. In addition, if you need to collect data from several interfaces, you can specify a list of interfaces:

```yaml
ble_monitor:
  hci_interface:
    - 0
    - 1
```

   Default value: No default value, `bt_interface` is used as default.

#### discovery

   (boolean)(Optional) By default, the component creates entities for all discovered, supported sensors. However, situations may arise where you need to limit the list of sensors. For example, when you receive data from neighboring sensors, or when data from part of your sensors are received using other equipment, and you don't want to see entities you do not need. To resolve this issue, simply add an entry of each MAC-address of the sensors you need under `devices`, by using the `mac` option, and set the `discovery` option to False:

```yaml
ble_monitor:
  discovery: False
  devices:
    - mac: '58:C1:38:2F:86:6C'
    - mac: 'C4:FA:64:D1:61:7D'
```

Data from sensors with other addresses will be ignored. Default value: True

#### active_scan

   (boolean)(Optional) In active mode scan requests will be sent, which is most often not required, but slightly increases the sensor battery consumption. 'Passive mode' means that you are not sending any request to the sensor but you are just receiving the advertisements sent by the BLE devices. This parameter is a subject for experiment. Default value: False

#### report_unknown

   (boolean)(Optional) This option is needed primarily for those who want to request an implementation of device support that is not in the list of [supported sensors](#supported-sensors). If you set this parameter to `True`, then the component will log all messages from unknown Xiaomi ecosystem devices to the Home Assitant log (`logger` component must be enabled). **Attention!** Enabling this option can lead to huge output to the Home Assistant log, do not enable it if you do not need it! Details in the [FAQ](https://github.com/custom-components/ble_monitor/blob/master/faq.md#my-sensor-from-the-xiaomi-ecosystem-is-not-in-the-list-of-supported-ones-how-to-request-implementation). Default value: False

#### batt_entities

   (boolean)(Optional) By default, the battery information will be presented only as a sensor attribute called `battery level`. If you set this parameter to `True`, then the battery sensor entity will be additionally created - `sensor.ble_battery_ <sensor_mac_address>`. Default value: False

#### rounding [DEPRECATED]

   (boolean)(Optional) This option has been deprecated from `ble_monitor` 1.0.0. Enable/disable rounding of the average of all measurements taken within the number seconds specified with 'period'. This option is designed to disable rounding and thus keep the full average accuracy. When disabled, the `decimals` option is ignored. Default value: True

#### decimals

   (positive integer)(Optional) Number of decimal places to round. This setting can be overruled with for specific devices with settings [at device level](#configuration-parameters-at-device-level). Default value: 1

#### period

   (positive integer)(Optional) The period in seconds during which the sensor readings are collected and transmitted to Home Assistant after averaging. Default value: 60.

   *To clarify the difference between the sensor broadcast interval and the component measurement period: The LYWSDCGQ transmits 20-25 valuable BT LE messages (RSSI -75..-70 dBm). During the period = 60 (seconds), the component accumulates all these 20-25 messages, and after the 60 seconds expires, averages them and updates the sensor status in Home Assistant. The period does not affect the consumption of the sensor. It only affects the Home Assistant sensor update rate and the number of averaged values. We cannot change the frequency with which sensor sends data.*

#### log_spikes

   (boolean)(Optional) Puts information about each erroneous spike in the Home Assistant log. Default value: False
  
   *There are reports (pretty rare) that some sensors tend to sometimes produce erroneous values that differ markedly from the actual ones. Therefore, if you see inexplicable sharp peaks or dips on the temperature or humidity graph, I recommend that you enable this option so that you can see in the log which values were qualified as erroneous. The component discards values that exceeds the sensor’s measurement capabilities. These discarded values are given in the log records when this option is enabled. If erroneous values are within the measurement capabilities (-40..60°C and 0..100%H), there are no messages in the log. If your sensor is showing this, there is no other choice but to calculate the average as the median (next option).*

#### use_median

   (boolean)(Optional) Use median as sensor output instead of mean (helps with "spiky" sensors). Please note that both the median and the mean values in any case are present as the sensor state attributes. This setting can be overruled with for specific devices with settings [at device level](#configuration-parameters-at-device-level). Default value: False
  
   *The difference between the mean and the median is that the median is **selected** from the sensor readings, and not calculated as the average. That is, the median resolution is equal to the resolution of the sensor (one tenth of a degree or percent), while the mean allows you to slightly increase the resolution (the longer the measurement period, the larger the number of values will be averaged, and the higher the resolution can be achieved, if necessary with disabled rounding).*

#### restore_state

   (boolean)(Optional) This option will, when set to `True`, restore the state of the sensors immediately after a restart of Home Assistant to the state right before the restart. The integration needs some time (see [period](#period) option) after a restart before it shows the actual data in Home Assistant. During this time, the integration receives data from your sensors and calculates the mean or median values of these measurements. During this period, the entity will have a state "unknown" or "unavailable" when `restore_state` is set to `False`. Setting it to `True` will prevent this, as it restores the old state, but could result in sensors having the wrong state, e.g. if the state has changed during the restart. By default, this option is disabled, as especially the binary sensors would rely on the correct state. If you only use measuring sensors like temperature sensors, this option can be safely set to `True`. It is also possible to overrule this setting for specific devices with settings [at device level](#configuration-parameters-at-device-level). Default value: False

### Configuration parameters at device level

#### devices

   (Optional) The devices option is used for setting options at the level of the device and/or if you want to whitelist certain sensors with the `discovery` option. Note that if you use the `devices` option, the `mac` option is also required.

### Configuration in the User Interface

   To add a device, open the options menu of the integration and select **Add Device** in the device drop down menu and click on Submit. You can modify existing configured devices in a similar way, by selecting your device in the same drop down menu and clicking on Submit. Both will show the following form.

  ![device setup](/pictures/device_screen.png)

### Configuraton in YAML

   To add a device, add the following to your `configuration.yaml`

```yaml
ble_monitor:
  devices:
    - mac: 'A4:C1:38:2F:86:6C'
      name: 'Livingroom'
      encryption_key: '217C568CF5D22808DA20181502D84C1B'
      temperature_unit: C
      decimals: 2
      use_median: False
      restore_state: default
    - mac: 'C4:3C:4D:6B:4F:F3'
      reset_timer: 35
```

#### mac

   (string)(Required) The `mac` option (`MAC address` in the UI) is used to identify your sensor device based on its mac-address. This allows you to define other additional options for this specific sensor device and/or to whitelist it with the `discovery` option. You can find the MAC address in the attributes of your sensor (`Developers Tools` --> `States`). For deleting devices see the instructions [below](#deleting-devices-and-sensors).

#### name

   When using configuration in the User Interface, you can modify the device name by opening your device, via configuration, integrations and clicking on devices on the BLE monitor tile. Select the device you want to change the name of and click on the cogwheel in the topright corner, where you can change the name. You will get a question wether you want to rename the individual sensor entities of this device as well (normally, it is advised to do this).

   (string)(Optional) When using YAML, you can use the `name` option to link a device name and sensor name to the mac-address of the sensor device. Using this option (or changing a name) will create new sensor entities. The old data won't be transfered to the new sensor. The old sensor entities can be safely deleted afterwards, but this has to be done manually at the moment, see the instructions [below](#deleting-devices-and-sensors). The sensors are named with the following convention: `sensor.ble_sensortype_device_name` (e.g. `sensor.ble_temperature_livingroom`) in stead of the default `ble_sensortype_mac` (e.g. `sensor.ble_temperature_A4C1382F86C`). You will have to update your lovelace cards, automation and scripts after each change. Note that you can still override the entity_id from the UI. Default value: Empty

```yaml
ble_monitor:
  devices:
    - mac: 'A4:C1:38:2F:86:6C'
      name: 'Livingroom'
```

#### encryption_key

   (string, 32 characters)(Optional) This option is used for sensors broadcasting encrypted advertisements. The encryption key should be 32 characters (= 16 bytes). This is only needed for LYWSD03MMC, CGD1, MCCGQ02HL and MHO-C401 sensors (original firmware only). The case of the characters does not matter. The keys below are an example, you need your own key(s)! Information on how to get your key(s) can be found [here](https://github.com/custom-components/ble_monitor/blob/master/faq.md#my-sensors-ble-advertisements-are-encrypted-how-can-i-get-the-key). Default value: Empty

```yaml
ble_monitor:
  devices:
    - mac: 'A4:C1:38:2F:86:6C'
      encryption_key: '217C568CF5D22808DA20181502D84C1B'
```

#### temperature_unit

   (C or F)(Optional) Most sensors are sending BLE advertisements with temperature data in Celsius (C), even when set to Fahrenheit (F) in the MiHome app. However, sensors with custom ATC firmware will start sending temperature data in Fahrenheit (F) after changing the display from Celsius to Fahrenheit. This means that you will have to tell `ble_monitor` that it should expect Fahrenheit data for these specific sensors, by setting this option to Fahrenheit (F). Note that Home Assistant is always converting measurements to C or F based on your Unit System setting in Configuration - General. Default value: C

```yaml
ble_monitor:
  devices:
    - mac: 'A4:C1:38:2F:86:6C'
      temperature_unit: F
```

#### decimals (device level)

   (positive integer or `default`)(Optional) Number of decimal places to round. Overrules the setting at integration level. Default value: default (which means: use setting at integration level)

```yaml
ble_monitor:
  devices:
    - mac: 'A4:C1:38:2F:86:6C'
      decimals: 2
    - mac: 'A4:C1:38:2F:86:6B'
      decimals: default
```

#### use_median (device level)

   (boolean or `default`)(Optional) Use median as sensor output instead of mean (helps with "spiky" sensors). Overrules the setting at integration level. Please note that both the median and the mean values in any case are present as the sensor state attributes. Default value: default (which means: use setting at integration level)

```yaml
ble_monitor:
  devices:
    - mac: 'A4:C1:38:2F:86:6C'
      use_median: True
    - mac: 'A4:C1:38:2F:86:6B'
      use_median: default
```

#### restore_state (device level)

   (boolean or `default`)(Optional) This option will, when set to `True`, restore the state of the sensors immediately after a restart of Home Assistant to the state right before the restart. Overrules the setting at integration level. See for a more detailed explanation the setting at integration level. Default value: default (which means: use setting at integration level)

```yaml
ble_monitor:
  devices:
    - mac: 'A4:C1:38:2F:86:6C'
      restore_state: True
    - mac: 'A4:C1:38:2F:86:6B'
      restore_state: default
```

#### reset_timer

   (possitive integer)(Optional) This option sets the time (in seconds) after which a motion sensor is reset to `motion clear`. After each `motion detected` advertisement, the timer starts counting down again. Note that the sensor also sends advertisements itself that can overrule this setting. To our current knowledge, advertisements after 30 seconds of no motion send by the sensor are `motion clear` messages, advertisements within 30 seconds are `motion detected` messages. In a future release we will filter out messages, if they do not correspond to the setting in `ble_monitor`. Default value: 35

```yaml
ble_monitor:
  devices:
    - mac: 'A4:C1:38:2F:86:6C'
      reset_timer: 35
```

### Deleting devices and sensors

Removing devices can be done by removing the corresponding lines in your `configuration.yaml`. In the UI, you can delete devices by typing `-` in the `MAC address` field. Note that if the [discovery](#discovery) option is set to `True` they will be discovered automatically again.

Unfortunately, old devices and sensor entities are not entirely deleted by this, they will still be visible, but will be `unavailable` after a restart. The same applies for changing a name of an existing device in YAML, the sensor entities with the old name will still remain visible, but with an `unavailable` state after a restart. To completely remove these left overs, follow the following steps.

#### 1. Remove old entities

First, delete the old entities, by going to **configuration**, **integrations** and selecting **devices** in the BLE monitor tile. Select the device with old entities and select each unavailable sensor, to delete it manually. If the delete button isn't visible, you will have to restart Home Assistant to unload the entities. Make sure all old sensor entities are deleted before going to the next step.

#### 2. Remove old devices

If the sensor doesn't have any sensor entities anymore, you can delete the device as well. Unfortunately, Home Assistant doesn't have an delete option to remove the old device. To overcome this problem, we have created a `service` to help you solve this. Go to **developer tools**, **services** and select the `ble_monitor.cleanup_entries` service. Click on **Call service** and the device should be gone. If not, you probably haven't deleted all sensor entities (go to step 1).

## FREQUENTLY ASKED QUESTIONS

Still having questions or issues? Please first have a look on our [Frequently Asked Questions (FAQ) page](faq.md) to see if your question is already answered. There are some useful tips also.
If your question or issue isn't answered in the FAQ, please open an [issue](https://github.com/custom-components/ble_monitor/issues).

## CREDITS

Credits and big thanks should be given to:

- [@Magalex](https://community.home-assistant.io/u/Magalex) and [@Ernst](https://community.home-assistant.io/u/Ernst) for the component creation, development, and support.
- [@koying](https://github.com/koying) for implementing the configuration in the user interface.
- [@tsymbaliuk](https://community.home-assistant.io/u/tsymbaliuk) for the idea and the first code.

## FORUM

You can more freely discuss the operation of the component, ask for support, leave feedback and share your experience in [our topic](https://community.home-assistant.io/t/passive-ble-monitor-integration-xiaomi-mijia-ble-mibeacon-monitor/) on the Home Assistant forum.
