
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

{% if prerelease %}

# NB!: This is a Beta version

# Changes in 0.9.8-beta

- Fix for IndexError when using battery sensors for LYWSD03MMC

# Changes in 0.9.7-beta

- Added support for the ATC advertisement type for LYWSD03MMC sensors from both the firmware by `ATC1441`, available [here](https://github.com/atc1441/ATC_MiThermometer), and the improved firmware by `pvvx` available [here](https://github.com/pvvx/ATC_MiThermometer). Both custom firmware's broadcast temperature, humidity, battery voltage and battery level in percent. For the `pvvx` firmware, it is advised to change the setting `advertisement type` from `all` to `custom`. Sending multiple advertisment types at the same time might cause the voltage sensor from not showing up, depending on which advertisement comes first. The advertisement type `custom` will also result in a higher accuracy. Reloading the integration is needed to receive the voltage sensor after switching the firmware.

{% endif %}
{% if installed or pending_update %}

# Changes in 0.9.8

- Added support for the ATC advertisement type for LYWSD03MMC sensors from both the firmware by `ATC1441`, available [here](https://github.com/atc1441/ATC_MiThermometer), and the improved firmware by `pvvx` available [here](https://github.com/pvvx/ATC_MiThermometer). Both custom firmware's broadcast temperature, humidity, battery voltage and battery level in percent. For the `pvvx` firmware, it is advised to change the setting `advertisement type` from `all` to `custom`. Sending multiple advertisment types at the same time might cause the voltage sensor from not showing up, depending on which advertisement comes first. The advertisement type `custom` will also result in a higher accuracy. Reloading the integration is needed to receive the voltage sensor after switching the firmware.

{% endif %}

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

- LYWSDCGQ

  (round body, segment LCD, broadcasts temperature, humidity and battery level, about 20 readings per minute)
  
  ![LYWSDCGQ](https://raw.github.com/custom-components/ble_monitor/master/pictures/LYWSDCGQ.jpg)
  
- CGG1

  (round body, E-Ink, broadcasts temperature, humidity and battery level, about 20 readings per minute. There are two versions, with encryption and without encryption. We expect that you can check which version you have by looking at the back of the sensor. The ones with encryption have a `qingping` logo at the back (left picture), while the ones without encryption don't have any logo (right picture)) 

  ![CGG1](https://raw.github.com/custom-components/ble_monitor/master/pictures/CGG1-back.png)

  For sensors with encryption, you will need to set the encryption key in your configuration, see for instructions the [encryption_key](#encryption_key) option)

  ![CGG1](https://raw.github.com/custom-components/ble_monitor/master/pictures/CGG1.png)

- CGDK2

  (round body, E-Ink, broadcasts temperature, humidity and battery level, about 10 readings per minute, advertisements are encrypted, therefore you need to set the key in your configuration, see for instructions the [encryption_key](#encryption_key) option)

  ![CGDK2](https://raw.github.com/custom-components/ble_monitor/master/pictures/CGDK2.png)

- LYWSD02

  (rectangular body, E-Ink, broadcasts temperature, humidity and battery level (battery level is available for firmware version 1.1.2_00085 and later), about 20 readings per minute)

  ![LYWSD02](https://raw.github.com/custom-components/ble_monitor/master/pictures/LYWSD02.jpeg)
  
- LYWSD03MMC

  (small square body, segment LCD, broadcasts temperature and humidity once in about 10 minutes and battery level once in an hour (original firmware). With the original firmware, advertisements are encrypted, therefore you need to set an encryption key in your configuration, see for instructions the [encryption_key](#encryption_key) option (not needed for sensors with custom firmware).
  
  `ble_monitor` also supports custom ATC firmware (both the firmware by `ATC1441`, available [here](https://github.com/atc1441/ATC_MiThermometer), and the improved firmware by `pvvx` available [here](https://github.com/pvvx/ATC_MiThermometer)). Both custom firmware's broadcast temperature, humidity, battery voltage and battery level in percent (note that both battery sensors are only visible as sensor with `batt_entities: True`). For the `pvvx` firmware, it is advised to change the `advertisement type` from `all` to `custom`. Sending multiple advertisment types at the same time might cause the voltage sensor from not showing up, depending on which advertisement comes first. The advertisement type `custom` will also result in a higher accuracy. Reloading the integration is needed to receive the voltage sensor after switching the firmware)   
  
  ![LYWSD03MMC](https://raw.github.com/custom-components/ble_monitor/master/pictures/LYWSD03MMC.jpg)

- CGD1

  (Cleargrass (Qingping) CGD1 alarm clock, segment LCD, broadcasts temperature and humidity (once in about 3 minutes?), and battery level (we do not have accurate periodicity information yet), advertisements are encrypted, therefore you need to set the key in your configuration, see for instructions the [encryption_key](#encryption_key) option)

  ![CGD1](https://raw.github.com/custom-components/ble_monitor/master/pictures/CGD1.jpg)

- MHO-C303

  (Alarm clock, rectangular body, E-Ink, broadcasts temperature, humidity and battery level, about 20 readings per minute)
  
  ![MHO-C303](https://raw.github.com/custom-components/ble_monitor/master/pictures/MHO-C303.png)

- MHO-C401
  
  (small square body, E-Ink display, broadcasts temperature and humidity once in about 10 minutes and battery level once in an hour, advertisements are encrypted, therefore you need to set the key in your configuration, see for instructions the [encryption_key](#encryption_key) option)
  
  ![MHO-C401](https://raw.github.com/custom-components/ble_monitor/master/pictures/MHO-C401.jpg)

- JQJCY01YM

  (Xiaomi Honeywell Formaldehyde Sensor, OLED display, broadcasts temperature, humidity, formaldehyde (mg/m³) and battery level, about 50 messages per minute)
  
  ![supported sensors](https://raw.github.com/custom-components/ble_monitor/master/pictures/JQJCY01YM.jpg)

- HHCCJCY01

  (MiFlora, broadcasts temperature, moisture, illuminance, conductivity, 1 reading per minute, no battery info with firmware v3.2.1)
  
  ![HHCCJCY01](https://raw.github.com/custom-components/ble_monitor/master/pictures/HHCCJCY01.jpg)

- GCLS002

  (VegTrug Grow Care Garden, similar to MiFlora HHCCJCY01)

  ![GCLS002](https://raw.github.com/custom-components/ble_monitor/master/pictures/GCLS002.png)

- HHCCPOT002

  (FlowerPot, RoPot, broadcasts moisture and conductivity, 2 readings per minute, no battery info with firmware v1.2.6)
  
  ![HHCCPOT002](https://raw.github.com/custom-components/ble_monitor/master/pictures/HHCCPOT002.jpg)

- WX08ZM

  (Xiaomi Mija Mosquito Repellent, Smart version, broadcasts switch state, tablet resource, battery level, about 50 messages per minute)

  ![WX08ZM](https://raw.github.com/custom-components/ble_monitor/master/pictures/WX08ZM.jpg)

- MCCGQ02HL

  (Xiaomi Mijia Window Door Sensor 2, broadcasts opening state, light state and battery level. Advertisements are encrypted, therefore you need to set an encryption key in your configuration, see for instructions the [encryption_key](#encryption_key) option. Battery level is only send once in approximately 24 hours.)
  
  ![MCCGQ02HL](https://raw.github.com/custom-components/ble_monitor/master/pictures/MCCGQ02HL.png)

- YM-K1501

  (Xiaomi Mijia Smart kettle, experimental support, collecting data. The switch entity has an extra `ext_state` attribute, with the following values: `0` - kettle is idle, `1` - kettle is heating water, `2` - warming function is active with boiling, `3` - warming function is active without boiling)
  
  ![YM-K1501](https://raw.github.com/custom-components/ble_monitor/master/pictures/YM-K1501.png)

- V-SK152

  (Viomi Smart Kettle, experimental support, collecting data, `ext_state` attribute as in YM-K1501, data broadcasted every 30 seconds)

  ![V-SK152](https://raw.github.com/custom-components/ble_monitor/master/pictures/V-SK152.png)

- SJWS01LM

  (Xiaomi Smart Water Leak Sensor. Broadcasts moisture state (wet/dry), advertisements are encrypted, therefore you need to set the key in your configuration, see for instructions the [encryption_key](#encryption_key) option)

  ![SJWS01LM](https://github.com/custom-components/ble_monitor/blob/SJWS01LM/pictures/SJWS01LM.png)

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

Many Xiaomi ecosystem sensors (maybe all) do not broadcast BLE advertisements containing useful data until they have gone through the "pairing" process in the MiHome app. The encryption key is also (re)set when adding the sensor to the MiHome app, so do this first.

### 4. Configure the integration

There are two ways to configure the integration and your devices (sensors), in the User Interface (UI) or in your YAML configuration file. Choose one method, you can't use both ways at the same time. You are able to switch from one to the other, at any time.

#### 4a. Configuration in the User Interface

Make sure you restart Home Assistant after the installation in HACS. After the restart, go to **Configuration** in the side menu in Home Assistant and select **Integrations**. Click on **Add Integrations** in the bottom right corner and search for **Passive BLE Monitor** to install. This will open the configuration menu with the default settings. The options are explained in the [configuration parameters](#configuration-parameters) section below and can also be changed later in the options menu. After a few minutes, the sensors should be added to your Home Assistant automatically (at least one [period](#period) required). Note that changes also require at least one [period](#period) to become visible.

  ![Integration setup](https://raw.github.com/custom-components/ble_monitor/master/pictures/configuration_screen.png)

#### 4b. Configuration in YAML

Alternatively, you can add the configuration in `configuration.yaml` as explained below. The options are the same as in the UI and are explained in the [configuration parameters](#configuration-parameters) section below. After adding your initial configuration to your YAML file, or applying a configuration change in YAML, a restart is required to load the new configuration. After a few minutes, the sensors should be changed/added to your Home Assistant automatically (at least one [period](#period) required).

An example of `configuration.yaml` with the minimum configuration is:

```yaml
ble_monitor:
```

An example of `configuration.yaml` with all optional parameters is:

```yaml
ble_monitor:
  hci_interface: 0
  discovery: True
  active_scan: False
  report_unknown: False
  batt_entities: False
  rounding: True
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
    - mac: 'C4:3C:4D:6B:4F:F3'
      name: 'Bedroom'
      temperature_unit: F
    - mac: 'B4:7C:8D:6D:4C:D3'
```

Note: The encryption_key parameter is only needed for sensors, for which it is [pointed](#supported-sensors) that their messages are encrypted.

## CONFIGURATION PARAMETERS

### Configuration parameters at component level

#### hci_interface

   (positive integer or list of positive integers)(Optional) This parameter is used to select the bt-interface used. 0 for hci0, 1 for hci1 and so on. On most systems, the interface is hci0. In addition, if you need to collect data from several interfaces, you can specify a list of interfaces:

```yaml
ble_monitor:
  hci_interface:
    - 0
    - 1
```

   Default value: 0

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

#### rounding

   (boolean)(Optional) Enable/disable rounding of the average of all measurements taken within the number seconds specified with 'period'. This option is designed to disable rounding and thus keep the full average accuracy. When disabled, the `decimals` option is ignored. Default value: True

#### decimals

   (positive integer)(Optional) Number of decimal places to round (will be ignored if rounding is disabled). Default value: 1

#### period

   (positive integer)(Optional) The period in seconds during which the sensor readings are collected and transmitted to Home Assistant after averaging. Default value: 60.

   *To clarify the difference between the sensor broadcast interval and the component measurement period: The LYWSDCGQ transmits 20-25 valuable BT LE messages (RSSI -75..-70 dBm). During the period = 60 (seconds), the component accumulates all these 20-25 messages, and after the 60 seconds expires, averages them and updates the sensor status in Home Assistant. The period does not affect the consumption of the sensor. It only affects the Home Assistant sensor update rate and the number of averaged values. We cannot change the frequency with which sensor sends data.*

#### log_spikes

   (boolean)(Optional) Puts information about each erroneous spike in the Home Assistant log. Default value: False
  
   *There are reports (pretty rare) that some sensors tend to sometimes produce erroneous values that differ markedly from the actual ones. Therefore, if you see inexplicable sharp peaks or dips on the temperature or humidity graph, I recommend that you enable this option so that you can see in the log which values were qualified as erroneous. The component discards values that exceeds the sensor’s measurement capabilities. These discarded values are given in the log records when this option is enabled. If erroneous values are within the measurement capabilities (-40..60°C and 0..100%H), there are no messages in the log. If your sensor is showing this, there is no other choice but to calculate the average as the median (next option).*

#### use_median

   (boolean)(Optional) Use median as sensor output instead of mean (helps with "spiky" sensors). Please note that both the median and the mean values in any case are present as the sensor state attributes. Default value: False
  
   *The difference between the mean and the median is that the median is **selected** from the sensor readings, and not calculated as the average. That is, the median resolution is equal to the resolution of the sensor (one tenth of a degree or percent), while the mean allows you to slightly increase the resolution (the longer the measurement period, the larger the number of values will be averaged, and the higher the resolution can be achieved, if necessary with disabled rounding).*

#### restore_state

   (boolean)(Optional) This option will, when set to `True`, restore the state of the sensors immediately after a restart of Home Assistant to the state right before the restart. The integration needs some time (see [period](#period) option) after a restart before it shows the actual data in Home Assistant. During this time, the integration receives data from your sensors and calculates the mean or median values of these measurements. During this period, the entity will have a state "unknown" or "unavailable" when `restore_state` is set to `False`. Setting it to `True` will prevent this, as it restores the old state, but could result in sensors having the wrong state, e.g. if the state has changed during the restart. By default, this option is disabled, as especially the binary sensors would rely on the correct state. If you only use measuring sensors like temperature sensors, this option can be safely set to `True`. Default value: False

### Configuration parameters at device level

#### devices

   (Optional) The devices option is used for setting options at the level of the device and/or if you want to whitelist certain sensors with the `discovery` option. Note that if you use the `devices` option, the `mac` option is also required.

### Configuration in the User Interface

   To add a device, open the options menu of the integration and select **Add Device** in the device drop down menu and click on Submit. You can modify existing configured devices in a similar way, by selecting your device in the same drop down menu and clicking on Submit. Both will show the following form.

  ![device setup](https://raw.github.com/custom-components/ble_monitor/master/pictures/device_screen.png)

### Configuraton in YAML

   To add a device, add the following to your `configuration.yaml`

```yaml
ble_monitor:
  devices:
    - mac: 'A4:C1:38:2F:86:6C'
      name: 'Livingroom'
      encryption_key: '217C568CF5D22808DA20181502D84C1B'
      temperature_unit: C
    - mac: 'C4:3C:4D:6B:4F:F3'
```

#### mac

   (string)(Required) The `mac` option (`MAC address` in the UI) is used to identify your sensor device based on its mac-address. This allows you to define other additional options for this specific sensor device and/or to whitelist it with the `discovery` option. You can find the MAC address in the attributes of your sensor (`Developers Tools` --> `States`). For deleting devices see the instructions [below](#deleting-devices-and-sensors).

#### name

   When using configuration in the User Interface, you can modify the device name by opening your device, via configuration, integrations and clicking on devices on the BLE monitor tile. Select the device you want to change the name of and click on the cogwheel in the topright corner, where you can change the name. You will get a question wether you want to rename the individual sensor entities of this device as well (normally, it is advised to do this).

   (string)(Optional)
   When using YAML, you can use the `name` option to link a device name and sensor name to the mac-address of the sensor device. Using this option (or changing a name) will create new sensor entities. The old data won't be transfered to the new sensor. The old sensor entities can be safely deleted afterwards, but this has to be done manually at the moment, see the instructions [below](#deleting-devices-and-sensors). The sensors are named with the following convention: `sensor.ble_sensortype_device_name` (e.g. `sensor.ble_temperature_livingroom`) in stead of the default `ble_sensortype_mac` (e.g. `sensor.ble_temperature_A4C1382F86C`). You will have to update your lovelace cards, automation and scripts after each change. Note that you can still override the entity_id from the UI. Default value: Empty

```yaml
ble_monitor:
  devices:
    - mac: 'A4:C1:38:2F:86:6C'
      name: 'Livingroom'
```

#### temperature_unit

   (C or F)(Optional) Most sensors are sending temperature measurements in Celsius (C), which is the default assumption for `ble_monitor`. However, some sensors, like the `LYWSD03MMC` sensor with custom firmware will start sending temperature measurements in Fahrenheit (F) after changing the display from Celsius to Fahrenheit. This means that you will have to tell `ble_monitor` that it should expect Fahrenheit measurements for these specific sensors. Default value: C

```yaml
ble_monitor:
  devices:
    - mac: 'A4:C1:38:2F:86:6C'
      temperature_unit: F
```

#### encryption_key

   (string, 32 characters)(Optional) This option is used for sensors broadcasting encrypted advertisements. The encryption key should be 32 characters (= 16 bytes). This is only needed for LYWSD03MMC, CGD1, MCCGQ02HL and MHO-C401 sensors (original firmware only). The case of the characters does not matter. The keys below are an example, you need your own key(s)! Information on how to get your key(s) can be found [here](https://github.com/custom-components/ble_monitor/blob/master/faq.md#my-sensors-ble-advertisements-are-encrypted-how-can-i-get-the-key). Default value: Empty

```yaml
ble_monitor:
  devices:
    - mac: 'A4:C1:38:2F:86:6C'
      encryption_key: '217C568CF5D22808DA20181502D84C1B'
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
