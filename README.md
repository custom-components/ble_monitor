# Xiaomi passive BLE Monitor sensor platform

<!-- TOC -->

- [Introduction](#introduction)
- [Supported sensors](#supported-sensors)
- [How to install](#how-to-install)
- [Configuration](#configuration)
  - [Configuration variables](#configuration-variables)
- [Frequently asked questions](#frequently-asked-questions)
- [Credits](#credits)
- [Forum](#forum)

<!-- /TOC -->

## INTRODUCTION

This custom component is an alternative for the standard build in [mitemp_bt](https://www.home-assistant.io/integrations/mitemp_bt/) integration that is available in Home Assistant. Unlike the original `mitemp_bt` integration, which is getting its data by polling the device with a default five-minute interval, this custom component is parsing the Bluetooth Low Energy packets payload that is constantly emitted by the sensor. The packets payload may contain temperature/humidity/battery and other data. Advantage of this integration is that it doesn't affect the battery as much as the built-in integration. It also solves connection issues some people have with the standard integration (due to passivity and the ability to collect data from multiple bt-interfaces simultaneously). Read more in the [FAQ](https://github.com/custom-components/sensor.mitemp_bt/blob/master/faq.md#why-is-this-component-called-passive-and-what-does-it-mean).

## SUPPORTED SENSORS

![supported sensors](/sensors.jpg)

- LYWSDCGQ

  (round body, segment LCD, broadcasts temperature, humidity and battery level, about 20 readings per minute)

- LYWSD02

  (rectangular body, E-Ink, broadcasts temperature and humidity, about 20 readings per minute, no battery info)

- CGG1

  (round body, E-Ink, broadcasts temperature, humidity and battery level, about 20 readings per minute)

- HHCCJCY01

  (MiFlora, broadcasts temperature, moisture, illuminance, conductivity, 1 reading per minute, no battery info with firmware v3.2.1)

- GCLS002

  (VegTrug Grow Care Garden, similar to MiFlora HHCCJCY01)

- HHCCPOT002

  (FlowerPot, RoPot, broadcasts moisture and conductivity, 2 readings per minute, no battery info with firmware v1.2.6)

- LYWSD03MMC

  (small square body, segment LCD, broadcasts temperature and humidity once in about 10 minutes and battery level once in an hour, advertisements are encrypted, therefore you need to set the key in your configuration, see for instructions the [encryptors](#configuration-variables) option)

- CGD1

  (Cleargrass (Qingping) CGD1 alarm clock, segment LCD, broadcasts temperature and humidity (once in about 3 minutes?), and battery level (we do not have accurate periodicity information yet), advertisements are encrypted, therefore you need to set the key in your configuration, the procedure is similar to the LYWSD03MMC sensor)

- JQJCY01YM

  (Xiaomi Honeywell Formaldehyde Sensor, OLED display, broadcasts temperature, humidity, formaldehyde (mg/m³) and battery level, about 50 messages per minute)

- WX08ZM

  (Xiaomi Mija Mosquito Repellent, Smart version, broadcasts switch state, tablet resource, battery level, about 50 messages per minute)
  
- MHO-C401
  
  (small square body, E-Ink display, broadcasts temperature and humidity once in about 10 minutes and battery level once in an hour, advertisements are encrypted, therefore you need to set the key in your configuration, see for instructions the [encryptors](#configuration-variables) option)

*The amount of actually received data is highly dependent on the reception conditions (like distance and electromagnetic ambiance), readings numbers are indicated for good RSSI (Received Signal Strength Indicator) of about -75 till -70dBm.*

**Do you want to request support for a new sensor? In the [FAQ](https://github.com/custom-components/sensor.mitemp_bt/blob/master/faq.md#my-sensor-from-the-xiaomi-ecosystem-is-not-in-the-list-of-supported-ones-how-to-request-implementation) you can read instructions how to request support for other sensors.**

## HOW TO INSTALL

**1. Grant permissions for Python rootless access to HCI interface (usually only needed for alternative installations of home assistant that only install home assistant core):**

- to grant:

     ```shell
     sudo setcap 'cap_net_raw,cap_net_admin+eip' `readlink -f \`which python3\``
     ```

- to check:

     ```shell
     sudo getcap `readlink -f \`which python3\``
     ```

*In case you get a PermissionError, check the [Frequently Asked Questions (FAQ) page](faq.md).

**2. Install the custom component:**

- The easiest way is to install it with [HACS](https://hacs.xyz/). First install [HACS](https://hacs.xyz/) if you don't have it yet. After installation you can find this custom component in the HACS store under integrations.

- Alternatively, you can install it manually. Just copy paste the content of the `sensor.mitemp_bt/custom_components` folder in your `config/custom_components` directory.
     As example, you will get the `sensor.py` file in the following path: `/config/custom_components/mitemp_bt/sensor.py`.

**3. Stop and start Home Assistant:**

- Stop and start Home Assistant. Make sure you first stop Home Assistant and then start Home Assistant again. Restarting Home Assistant is not sufficient, as the python process does not exit upon restart. Stopping and starting Home Assistant is also required to unload the build in component and load the custom component. Do this before step 4, as Home Assistant will otherwise complain that your configuration is not ok (as it still uses the build in `mitemp_bt` integration).

**4. Add the platform to your configuration.yaml file (see [below](#configuration))**

**5. Restart Home Assistant:**

- A second restart is required to load the configuration. After a few minutes, the sensors should be added to your home-assistant automatically (at least one [period](#period) required).

**6. Add your sensors to the MiHome app if you haven’t already.**

Many Xiaomi ecosystem sensors (maybe all) do not brodcasts BLE advertisements containing useful data until they have gone through the "pairing" process in the MiHome app.

## CONFIGURATION

Add the following to your `configuration.yaml` file.

```yaml
sensor:
  - platform: mitemp_bt
```

IMPORTANT. If you used the standard Home Assistant built ['mitemp_bt'](https://www.home-assistant.io/integrations/mitemp_bt/) integration, make sure you delete the additional parameters, like `mac:` and `monitored_conditions:`.

An example of `configuration.yaml` with all optional parameters is:

```yaml
sensor:
  - platform: mitemp_bt
    rounding: True
    decimals: 1
    period: 60
    log_spikes: False
    use_median: False
    active_scan: False
    hci_interface: 0
    batt_entities: False
    encryptors:
               'A4:C1:38:2F:86:6C': '217C568CF5D22808DA20181502D84C1B'
    report_unknown: False
    whitelist: False
```

Note: The encryptors parameter is only needed for sensors, for which it is [pointed](#supported-sensors) that their messages are encrypted.

### Configuration Variables

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

#### active_scan

   (boolean)(Optional) In active mode scan requests will be sent, which is most often not required, but slightly increases the sensor battery consumption. 'Passive mode' means that you are not sending any request to the sensor but you are just receiving the advertisements sent by the BLE devices. This parameter is a subject for experiment. Default value: False

#### hci_interface

   (positive integer or list of positive integers)(Optional) This parameter is used to select the bt-interface used. 0 for hci0, 1 for hci1 and so on. On most systems, the interface is hci0. In addition, if you need to collect data from several interfaces, you can specify a list of interfaces:

   ```yaml
   sensor:
       - platform: mitemp_bt
         hci_interface:
                       - 0
                       - 1
   ```

   Default value: 0

#### batt_entities

   (boolean)(Optional) By default, the battery information will be presented only as a sensor attribute called `battery level`. If you set this parameter to `True`, then the battery sensor entity will be additionally created - `sensor.mi_batt_ <sensor_mac_address>`. Default value: False

#### encryptors

   (dictionary)(Optional) This option is used to link the mac-address of the sensor broadcasting encrypted advertisements to the encryption key (32 characters = 16 bytes). This is only needed for LYWSD03MMC and CGD1 sensors. The case of the characters does not matter. The keys below are an example, you need your own key(s)! Information on how to get your key(s) can be found [here](https://github.com/custom-components/sensor.mitemp_bt/blob/master/faq.md#my-sensors-ble-advertisements-are-encrypted-how-can-i-get-the-key). Default value: Empty

   ```yaml
   sensor:
     - platform: mitemp_bt
       encryptors:
                'A4:C1:38:2F:86:6C': '217C568CF5D22808DA20181502D84C1B'
                'A4:C1:38:D1:61:7D': 'C99D2313182473B38001086FEBF781BD'
   ```

#### report_unknown

   (boolean)(Optional) This option is needed primarily for those who want to request an implementation of device support that is not in the list of [supported sensors](#supported-sensors). If you set this parameter to `True`, then the component will log all messages from unknown Xiaomi ecosystem devices to the Home Assitant log. **Attention!** Enabling this option can lead to huge output to the Home Assistant log, do not enable it if you do not need it! Details in the [FAQ](https://github.com/custom-components/sensor.mitemp_bt/blob/master/faq.md#my-sensor-from-the-xiaomi-ecosystem-is-not-in-the-list-of-supported-ones-how-to-request-implementation). Default value: False

#### whitelist

   (list or boolean)(Optional) By default, the component creates entities for all detected supported sensors. However, situations may arise where you need to limit the list of sensors. For example, when you receive data from neighboring sensors, or when data from part of your sensors are received using other equipment, and you don't want to see entities you do not need. To resolve this issue, simply list the MAC-addresses of the sensors you need in the `whitelist` option:

   ```yaml
   sensor:
     - platform: mitemp_bt
       whitelist:
         - '58:C1:38:2F:86:6C'
         - 'C4:FA:64:D1:61:7D'
   ```

   Data from sensors with other addresses will be ignored.
   In addition, all addresses listed in the `encryptors` option will be automatically whitelisted.
   If you have no sensors other than those listed in `encryptors`, then just set `whitelist` to `True`:

   ```yaml
   sensor:
     - platform: mitemp_bt
       encryptors:
         'A4:C1:38:2F:86:6C': '217C568CF5D22808DA20181502D84C1B'
         'A4:C1:38:D1:61:7D': 'C99D2313182473B38001086FEBF781BD'
       whitelist: True
   ```

   Default value: False

## FREQUENTLY ASKED QUESTIONS

Still having questions or issues? Please first have a look on our [Frequently Asked Questions (FAQ) page](faq.md) to see if your question is already answered. There are some useful tips also.
If your question or issue isn't answered in the FAQ, please open an [issue](https://github.com/custom-components/sensor.mitemp_bt/issues).

## CREDITS

Credits and big thanks should be given to:

- [@tsymbaliuk](https://community.home-assistant.io/u/tsymbaliuk) for the idea and the first code.
- [@Magalex](https://community.home-assistant.io/u/Magalex) and [@Ernst](https://community.home-assistant.io/u/Ernst) for the component creation, development, and support.

## FORUM

You can more freely discuss the operation of the component, ask for support, leave feedback and share your experience in [our topic](https://community.home-assistant.io/t/xiaomi-passive-ble-monitor-sensor-platform/) on the Home Assistant forum.
