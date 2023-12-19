---
layout: default
title: Configuration parameters
has_children: false
has_toc: false
permalink: configuration_params
nav_order: 3
---


## Configuration parameters at component level


### bt_interface

   **MAC address of the Bluetooth interface/adapter**
   (MAC address or list of multiple MAC addresses or "disable")(Optional) This parameter is used to select the Bluetooth-interface of your Home Assistant host. When using YAML, a list of available Bluetooth-interfaces available on your system is given in the Home Assistant log during startup of the Integration, when you enable the Home Assistant [logger at info-level](https://www.home-assistant.io/integrations/logger/). In the UI, both the MAC address and the hci number will be shown. If you don't specify a MAC address, by default the first interface of the list will be used. If you want to use multiple interfaces in YAML, you can use the following configuration:

```yaml
ble_monitor:
  bt_interface:
    - '04:B1:38:2C:84:2B'
    - '34:DE:36:4F:23:2C'
```

   If you don't want to use the Bluetooth adapter at all, e.g. when you are using ESPHome [BLE Gateway](https://github.com/myhomeiot/esphome-components#ble-gateway) to forward your BLE advertisements to Home Assistant and you do not want to use the Bluetooth on the Home Assistant machine, you can select "Don't use Bluetooth adapter" in the UI or, when working with YAML, use the following configuration:


```yaml
ble_monitor:
  bt_interface: "disable"
```

   Default value: First available MAC address

### hci_interface (YAML only)

   **hci number of the Bluetooth interface/adapter**
   (positive integer or list of positive integers or "disable")(Optional) Like the previous option `bt_interface`, this parameter can also be used to select the bt-interface of your Home Assistant host. It is however strongly advised to use the `bt_interface` option and not this `hci_interface` option, as the hci number can change, e.g. when plugging in a dongle. However, due to backwards compatibility, this option is still available. Use 0 for hci0, 1 for hci1 and so on. On most systems, the interface is hci0. In addition, if you need to collect data from several interfaces, you can specify a list of interfaces:

```yaml
ble_monitor:
  hci_interface:
    - 0
    - 1
```

   If you don't want to use the Bluetooth adapter at all, e.g. when you are using ESPHome [BLE Gateway](https://github.com/myhomeiot/esphome-components#ble-gateway) to forward your BLE advertisements to Home Assistant and you do not want to use the Bluetooth on the Home Assistant machine, you can use the following configuration:


```yaml
ble_monitor:
  hci_interface: "disable"
```

   Default value: No default value, `bt_interface` is used as default.

### bt_auto_restart

  **Automatically restart Bluetooth adapter on failure**
  (boolean)(Optional)
  This option allows the Bluetooth adapter to automatically restart on failures. The Bluez bluetooth management API will be used to power cycle Bluetooth adapter. This can help if your Bluetooth adapter fails periodically.

```yaml
ble_monitor:
  bt_auto_restart: True
```

### active_scan

   **Use active scan instead of passive scan (affects battery)**
   (boolean)(Optional) In active mode scan requests will be sent, which is most often not required, but slightly increases the sensor battery consumption. 'Passive mode' means that you are not sending any request to the sensor but you are just receiving the advertisements sent by the BLE devices. This parameter is a subject for experiment. Default value: False

```yaml
ble_monitor:
  active_scan: True
```

### discovery

   **Discover devices and sensors automatically**
   (boolean)(Optional) By default, the component creates entities for all discovered, supported sensors. However, situations may arise where you need to limit the list of sensors. For example, when you receive data from neighboring sensors, or when data from part of your sensors are received using other equipment, and you don't want to see entities you do not need. To resolve this issue, simply add an entry of each MAC-address of the sensors you need under `devices`, by using the `mac` option, and set the `discovery` option to False:

```yaml
ble_monitor:
  discovery: False
  devices:
    - mac: '58:C1:38:2F:86:6C'
    - mac: 'C4:FA:64:D1:61:7D'
    - uuid: 'e2c56db5-dffb-48d2-b060-d0f5a71096e0'
```

Data from sensors with other addresses will be ignored. Default value: True

### period

   **Peiod to use for averaging**
   (positive integer)(Optional) The period in seconds during which the sensor readings are collected and transmitted to Home Assistant after averaging. Default value: 60.

   *To clarify the difference between the sensor broadcast interval and the component measurement period: The LYWSDCGQ transmits 20-25 valuable BT LE messages (RSSI -75..-70 dBm). During the period = 60 (seconds), the component accumulates all these 20-25 messages, and after the 60 seconds expires, averages them and updates the sensor status in Home Assistant. The period does not affect the consumption of the sensor. It only affects the Home Assistant sensor update rate and the number of averaged values. We cannot change the frequency with which sensor sends data.*

### use_median

   **Use median instead of mean**
   (boolean)(Optional) Use median as sensor output instead of mean (helps with "spiky" sensors). Please note that both the median and the mean values in any case are present as the sensor state attributes. This setting can be overruled with for specific devices with settings [at device level](#configuration-parameters-at-device-level). Default value: False

   *The difference between the mean and the median is that the median is **selected** from the sensor readings, and not calculated as the average. That is, the median resolution is equal to the resolution of the sensor (one tenth of a degree or percent), while the mean allows you to slightly increase the resolution (the longer the measurement period, the larger the number of values will be averaged, and the higher the resolution can be achieved, if necessary with disabled rounding).*

### log_spikes

   **Log spikes**
   (boolean)(Optional) Puts information about each erroneous spike in the Home Assistant log. Default value: False

   *There are reports (pretty rare) that some sensors tend to sometimes produce erroneous values that differ markedly from the actual ones. Therefore, if you see inexplicable sharp peaks or dips on the temperature or humidity graph, I recommend that you enable this option so that you can see in the log which values were qualified as erroneous. The component discards values that exceeds the sensor’s measurement capabilities. These discarded values are given in the log records when this option is enabled. If erroneous values are within the measurement capabilities (-40..60°C and 0..100%H), there are no messages in the log. If your sensor is showing this, there is no other choice but to calculate the average as the median (next option).*

### restore_state

   **Restore state after a restart**
   (boolean)(Optional) This option will, when set to `True`, restore the state of the sensors after a restart of Home Assistant. If your [devices](#devices) are configured with a [mac](#mac) address, they will restore immediately after a restart to the state right before the restart. If you didn't configure your [devices](#devices), the state of all entities of a specific device will be either updated or restored upon the first BLE advertisement being received.
   With `restore_state` set to `False`, Home Assistant will show "Unavailable" as the state of your sensors, until it receives the first BLE advertisements. Setting it to `True` will prevent this, as it restores the old state, but could result in sensors having the wrong state, e.g. if the state has changed during the restart. By default, this option is disabled, as especially the binary sensors would rely on the correct state. For measuring sensors like temperature sensors, this option can be safely set to `True`. It is also possible to overrule this setting for specific devices with settings [at device level](#configuration-parameters-at-device-level). Default value: False

### report_unknown

   **Report unknown sensors**

   (`Off`, `Acconeer`, `Air Mentor`, `Amazfit`, `ATC`, `BlueMaestro`, `Blustream`, `Brifit`, `BTHome`, `Govee`, `Grundfos`, `HolyIOT`, `Hormann`, `HHCC`, `iNode`, `iBeacon`, `Jinou`, `Kegtron`, `Mi Scale`, `Mi Band`,`Mikrotik`, `Oras`, `Qingping`, `Relsib`, `rbaron`, `Ruuvitag`, `Sensirion`, `SensorPush`, `SmartDry`, `Switchbot`, `Teltonika`, `Thermoplus`, `Xiaogui`, `Xiaomi`, `Other` or `False`)(Optional) This option is needed primarily for those who want to request an implementation of device support that is not in the list of [supported sensors](devices). If you set this parameter to one of the sensor brands, then the component will log all messages from unknown devices of the specified brand to the Home Assistant log (`logger` component must be enabled at info level, see for instructions the [FAQ](faq#my-sensor-from-the-xiaomi-ecosystem-is-not-in-the-list-of-supported-ones-how-to-request-implementation)). Using a sensor brand might not catch all BLE advertisements.

   If you can't find the advertisements in this way, you can set this option to `Other`, which will result is all BLE advertisements being logged. You can also enable this option at device level. **Attention!** Enabling this option can lead to huge output to the Home Assistant log, especially when set to `Other`, do not enable it if you do not need it! If you know the MAC address of the sensor, its advised to set this option at device level. Details in the [FAQ](faq#my-sensor-from-the-xiaomi-ecosystem-is-not-in-the-list-of-supported-ones-how-to-request-implementation). Default value: `Off`


## Configuration parameters at device level

### devices

   (Optional) The devices option is used for setting options at the level of the device and/or if you want to whitelist certain sensors with the `discovery` option. For tracking devices, it is mandatory to specify your devices to be tracked. Note that if you use the `devices` option, the `mac` option is also required.

#### Configuration in the User Interface

   To add a device, open the options menu of the integration and look for the `mac` of your device in the devices drop down menu. Most sensors are automatically added to the drop down menu. If it isn't shown or if you want to add a device to be tracked, select **Add Device** in the device drop down menu and click on Submit. You can modify existing configured devices in a similar way, by selecting your device in the same drop down menu and clicking on Submit. Both will show the following form.

  ![device setup]({{site.baseurl}}/assets/images/device_screen.png)

#### Configuration in YAML

   To add a device, add the following to your `configuration.yaml`

```yaml
ble_monitor:
  devices:
    # sensors
    - mac: 'A4:C1:38:2F:86:6C'
      name: 'Livingroom'
      encryption_key: '217C568CF5D22808DA20181502D84C1B'
      temperature_unit: C
      use_median: False
      restore_state: default
    - mac: 'C4:3C:4D:6B:4F:F3'
      reset_timer: 35
    # device trackers
    - mac: 'D4:3C:2D:4A:3C:D5'
      track_device: True
      tracker_scan_interval: 20
      consider_home: 180
    # ibeacon
    - uuid: 'e2c56db5-dffb-48d2-b060-d0f5a71096e0'
      track_device: True
      tracker_scan_interval: 20
      consider_home: 180
```

### mac

   (string)(Required if none uuid) The `mac` option (`MAC address` in the UI) is used to identify your device based on its mac-address. This allows you to define other additional options for this specific device, to track it and/or to whitelist it with the `discovery` option. You can find the MAC address in the attributes of your sensor (`Developers Tools` --> `States`). For deleting devices see the instructions [in the FAQ](faq#how-to-remove-devices-and-sensors).

### uuid

   (string)(Required if none mac)(Priority higher than mac if both are specified.) The `uuid` option (`Beacon UUID` in the UI) is used to identify your device based on its beacon uuid. This allows you to define other additional options for this specific device, to track it and/or to whitelist it with the `discovery` option. You can find the Beacon UUID and MAC address(may be dynamic) in the attributes of your sensor (`Developers Tools` --> `States`). For deleting devices see the instructions [in the FAQ](faq#how-to-remove-devices-and-sensors).

### name

   When using configuration in the User Interface, you can modify the device name by opening your device, via configuration, integrations and clicking on devices on the BLE monitor tile. Select the device you want to change the name of and click on the cogwheel in the topright corner, where you can change the name. You will get a question whether you want to rename the individual entities of this device as well (normally, it is advised to do this).

   (string)(Optional) When using YAML, you can use the `name` option to link a device name and sensor name to the mac-address of the device. Using this option (or changing a name) will create new sensor/tracker entities. The old data won't be transferred to the new sensor/tracker. The old sensor/tracker entities can be safely deleted afterwards, but this has to be done manually at the moment, see the instructions [in the FAQ](faq#how-to-remove-devices-and-sensors). The sensors/trackers are named with the following convention: `sensor.ble_sensortype_device_name` (e.g. `sensor.ble_temperature_livingroom`) in stead of the default `ble_sensortype_mac` (e.g. `sensor.ble_temperature_A4C1382F86C`). You will have to update your lovelace cards, automation and scripts after each change. Note that you can still override the entity_id from the UI. Default value: Empty

```yaml
ble_monitor:
  devices:
    - mac: 'A4:C1:38:2F:86:6C'
      name: 'Livingroom'
```

### encryption_key

   (string, 24 or 32 characters)(Optional) This option is used for sensors broadcasting encrypted advertisements. The encryption key should be 32 characters (= 16 bytes) for most devices (LYWSD03MMC, CGD1, MCCGQ02HL, and MHO-C401 (original firmware only). Only Yeelight YLYK01YL (all types), YLYB01YL-BHFRC, YLKG07YL and YLKG08YL require a 24 character (= 12 bytes) long key. The case of the characters does not matter. The keys below are an example, you need your own key(s)! Information on how to get your key(s) can be found [here](faq#my-sensors-ble-advertisements-are-encrypted-how-can-i-get-the-key). Default value: Empty

```yaml
ble_monitor:
  devices:
    - mac: 'A4:C1:38:2F:86:6C'
      encryption_key: '217C568CF5D22808DA20181502D84C1B'
```

### temperature_unit

   (C or F)(Optional) Most sensors are sending BLE advertisements with temperature data in Celsius (C), even when set to Fahrenheit (F) in the MiHome app. However, sensors with custom ATC firmware will start sending temperature data in Fahrenheit (F) after changing the display from Celsius to Fahrenheit. This means that you will have to tell `ble_monitor` that it should expect Fahrenheit data for these specific sensors, by setting this option to Fahrenheit (F). Note that Home Assistant is always converting measurements to C or F based on your Unit System setting in Configuration - General. Default value: C

```yaml
ble_monitor:
  devices:
    - mac: 'A4:C1:38:2F:86:6C'
      temperature_unit: F
```

### use_median (device level)

   (boolean or `default`)(Optional) Use median as sensor output instead of mean (helps with "spiky" sensors). Overrules the setting at integration level. Please note that both the median and the mean values in any case are present as the sensor state attributes. Default value: default (which means: use setting at integration level)

```yaml
ble_monitor:
  devices:
    - mac: 'A4:C1:38:2F:86:6C'
      use_median: True
    - mac: 'A4:C1:38:2F:86:6B'
      use_median: default
```

### restore_state (device level)

   (boolean or `default`)(Optional) This option will, when set to `True`, restore the state of the sensors immediately after a restart of Home Assistant to the state right before the restart. Overrules the setting at integration level. See for a more detailed explanation the setting at integration level. Default value: default (which means: use setting at integration level)

```yaml
ble_monitor:
  devices:
    - mac: 'A4:C1:38:2F:86:6C'
      restore_state: True
    - mac: 'A4:C1:38:2F:86:6B'
      restore_state: default
```

### reset_timer

   (positive integer)(Optional) This option sets the time (in seconds) after which a sensor is reset to `motion clear` (motion sensors) or `no press` (button and dimmer sensors). After each `motion detected` advertisement or `button/dimmer press`, the timer starts counting down again. Setting this option to 0 seconds will turn this resetting behavior off.

   Note that motion sensors also sends advertisements themselves that can overrule this setting. To our current knowledge, advertisements after 30 seconds of no motion send by the sensor are `motion clear` messages, advertisements within 30 seconds are `motion detected` messages. For button and dimmer sensors, it is advised to set the `reset_timer` to 1 second. Default value: 35

```yaml
ble_monitor:
  devices:
    - mac: 'A4:C1:38:2F:86:6C'
      reset_timer: 35
```

### report_unknown (device level)

   (boolean)(Optional) This option is needed primarily for those who want to request an implementation of device support that is not in the list of [supported sensors](devices). If you enable this parameter, then the component will log all messages from the MAC address or UUID in the Home Assistant log (`logger` component must be enabled at info level, see for instructions the [FAQ](faq#my-sensor-from-the-xiaomi-ecosystem-is-not-in-the-list-of-supported-ones-how-to-request-implementation)). Default value: False


```yaml
ble_monitor:
  devices:
    - mac: 'A4:C1:38:2F:86:6C'
      report_unknown: True
    - uuid: 'e2c56db5-dffb-48d2-b060-d0f5a71096e0'
      report_unknown: True
```

### track_device

   (boolean)(Optional) Enabling this option will create a device tracker in Home Assistant. The device tracker will be `Home` as long as it receives data and will move to `Away` after no data is received anymore for more that the set period with [consider_home](#consider_home). Note that your device should have a fixed MAC address to be able to track. Default value: False


```yaml
ble_monitor:
  devices:
    - mac: 'A4:C1:38:2F:86:6C'
      track_device: True
      tracker_scan_interval: 20
      consider_home: 180
    - uuid: 'e2c56db5-dffb-48d2-b060-d0f5a71096e0'
      track_device: True
      tracker_scan_interval: 20
      consider_home: 180
```

### tracker_scan_interval

   (positive integer)(Optional) To reduce the state updates in Home Assistant and not spam your Home Assistant, it is advised to set a scan interval. After a BLE advertisement is received and the state has been updated, Home Assistant Scan will not update the state during the set interval to safe resources. The setting is in seconds. Default value: 20

### consider_home

   (positive integer)(Optional) This option sets the period with no data after which the device tracker is considered to be away. The setting is in seconds. Default value: 180

### delete_device

   (boolean)(Optional) This option is only available in the UI. Selecting this option will delete your device from your configuration and will delete your device from the Home Assistant device registry. Note that the device will automatically be rediscoverd if you have [discover](#discovery) enabled. Default value: False
