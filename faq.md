# Frequently asked questions

## Table of contents

<!-- TOC -->
  - [Why is this component called “passive” and what does this mean](#why-is-this-component-called-passive-and-what-does-this-mean)
  - [INSTALLATION ISSUES](#installation-issues)
      - [I get a PermissionError in Home Assistant after the installation](#i-get-a-permissionerror-in-home-assistant-after-the-installation-or-python-upgrade)
      - [How do I find the number of the HCI interface?](#how-do-i-find-the-number-of-the-hci-interface)
      - [How can I create a battery sensor?](#how-can-i-create-a-battery-sensor)
  - [RECEPTION ISSUES](#reception-issues)
      - [My sensor doesn't receive any readings from my sensors anymore or only occasionally](#my-sensor-doesnt-receive-any-readings-from-my-sensors-anymore-or-only-occasionally)
      - [How to increase coverage](#how-to-increase-coverage)
      - [My sensor's BLE advertisements are encrypted, how can I get the key?](#my-sensors-ble-advertisements-are-encrypted-how-can-i-get-the-key)
  - [OTHER ISSUES](#other-issues)
      - [Conflicts with other components using the same BT interface](#conflicts-with-other-components-using-the-same-bt-interface)
      - [My sensor stops receiving updates some time after the system restart](#my-sensor-stops-receiving-updates-some-time-after-the-system-restart)
      - [My sensor from the Xiaomi ecosystem is not in the list of supported ones. How to request implementation?](#my-sensor-from-the-xiaomi-ecosystem-is-not-in-the-list-of-supported-ones-how-to-request-implementation)
  - [DEBUG](#debug)
  - [FORUM](#forum)
<!-- /TOC -->

## Why is this component called passive and what does this mean

Unlike the original component (and most other solutions), this custom component does not use connections (polling) to collect data. The fact is that many sensors from the Xiaomi ecosystem transmit information themselves about their condition to the air with some frequency. We need only to "passively" receive these messages and update the status of the corresponding entities in the Home Assistant. What does this give us?

- firstly, it reduces the power consumption of the sensors (the battery lasts longer), since the sensor does not transmit anything other than that provided by its developers.
- secondly, since the range of bluetooth is rather limited, passive reception can solve some problems that arise when using "polling" components. In the case of connecting to a sensor, a two-way exchange takes place, which means we not only should “hear” the sensor well, but the sensor, in its turn, must also “hear” us well, and this could be problematic. To increase the radius of reception, you can, for example, install an external bt-dongle with a large antenna on your host, to make it "hear" better, but you can’t do anything with the sensor itself. A passive data collection method solves this problem, because in this case the sensor does not know about our existence, and should not "hear" us at all. The main thing is that we "hear" it well.
- another important point is the fact that the frequency of sending data for many sensors is quite high. For example, the LYWSDCGQ sensor sends about 20-25 measurements per minute. If your sensor is far away, or you have poor reception conditions, you only need to receive one out of twenty messages to update your Home Assistant entity... Not a bad chance, is it? And if you increase the `period` option, then the chances increase even more. In addition, receiving a stream of 20-25 measurements per minute gives you the opportunity to increase the resolution of measurements by averaging (which is implemented in our component) and this gives more smooth (beautiful, if you want) graphs and a faster reaction of corresponding automations.
- passive method allows without problems collecting data from several interfaces simultaneously, which expands your ability to increase the reception area. For example, you can use several external BT-dongles connected by cheap [USB-RJ45 extenders](https://sc01.alicdn.com/kf/HTB1q0VKodcnBKNjSZR0q6AFqFXae.jpg) and high-quality cat5/6 ethernet cables.

I’m not sure that I have listed all the advantages resulting from the passivity of this component. But I hope that I was able to explain the essence.

## INSTALLATION ISSUES

### I get a PermissionError in Home Assistant after the installation or python upgrade

Python needs root access to access the HCI interface. If Python doesn't have root access, you will get an error message in Home Assistant which ends with:

```shell
PermissionError: [Errno 1] Operation not permitted
```

First, try to set root access with

```shell
sudo setcap 'cap_net_raw,cap_net_admin+eip' `readlink -f \`which python3\``
```

Next, check that it is set correctly with the following command

```shell
sudo getcap `readlink -f \`which python3\``
```

The command will return the path to python and looks like (can vary based on your python version):

```shell
/usr/bin/python3.7 = cap_net_admin,cap_net_raw+eip
```

Make sure you first stop homeassistant and then start homeassistant again. Restarting Home Assistant is not enough, as the python process does not exit upon restart.

If you have multiple python versions, make sure it refers to the same version which is used by Home Assistant. If Home Assistant is using a different version, e.g. python3.6, run the following command to set the correct version (adjust it to your own version if needed).

```shell
sudo setcap 'cap_net_raw,cap_net_admin+eip' /usr/bin/python3.6
```

### How do I find the number of the HCI interface?

To find the correct number, run the following command:

```shell
hcitool dev
```

The command will return the HCI interface number and mac address.

```shell
Devices:
        hci0    B8:27:EB:77:75:50
```

### How can I create a battery sensor?

You can create a battery sensor by using a template sensor. Add the following to your `configuration.yaml`. Make sure you adjust the name of the sensor with your own sensor.

```yaml
sensor:
  - platform: template
    sensors:
      mi_b_582d34339449:
        friendly_name: "Battery"
        unit_of_measurement: "%"
        value_template: "{{ state_attr('sensor.mi_t_582d34339449', 'battery_level') }}"
        device_class: "battery"
```

Or (since v0.5.4) you can set option `batt_entities` to `True` - the battery sensor entity will be created automatically for each device reporting battery status.

## RECEPTION ISSUES

### My sensor doesn't receive any readings from my sensors anymore or only occasionally

The custom component uses Bluetooth (BLE) to receive messages from your sensor(s). The number of messages per minute that are being send by your sensor depends on the type, but is around 20 messages per minute for LYWSDCGQ, LYWSD02 and CGG1 sensors, around 2 per minute for HHCCPOT002 and around 1 per minute for HHCCJCY01T.

The number of messages that are received by Home Assistant can be less or even zero. Parameters that affect the reception of messages are:

- The distance between the sensor and the Bluetooth device on your Home Assistant device.

Try to keep the distance as limited as possible.

- Interference with other electrical devices.

Especially SSD devices are known to affect the Bluetooth reception, try to place your SSD drive as far as possible from your Bluetooth tranceiver.

- The quality of your Bluetooth transceiver.

The range of the built-in Bluetooth tranceiver of a Raspberry Pi is known to be limited. Try using an external Bluetooth transceiver to increase the range, e.g. with an external antenna.
It is also worth noting that starting from v0.5.5, a component can receive data from multiple interfaces simultaneously (see the `hci_interface` option).

### How to increase coverage

There are several ways to increase coverage:

- use an external BT-dongle (preferably with a full-size antenna).
- use multiple spaced BT-dongles. You can experiment with various extension cords (for example, inexpensive [USB-RJ45 extenders](https://sc01.alicdn.com/kf/HTB1q0VKodcnBKNjSZR0q6AFqFXae.jpg) in combination with a regular ethernet cable).
- use additional devices with their own BT-interface, and connect them to Home Assistant. For example, it could be another raspberrypi with Home Assistant and our component, connected to the main host using the [remote_homeassistant](https://github.com/lukas-hetzenecker/home-assistant-remote) component, which links multiple Home Assistant instances together.

### My sensor's BLE advertisements are encrypted, how can I get the key?

There are several ways:

1. Get the key from the MiHome application traffic (in violation of the Xiaomi user agreement terms):

      - iOS: Two known working options - [using Charles proxy](https://github.com/custom-components/sensor.mitemp_bt/issues/7#issuecomment-595327131), or [Stream - Network Debug Tool](https://github.com/custom-components/sensor.mitemp_bt/issues/7#issuecomment-595885296).
      - Android: I am not aware of successful interceptions on Android, but there are applications for this (Packet Capture, for example).

2. Android only. Get the key with the customized [MiHome mod](https://github.com/custom-components/sensor.mitemp_bt/issues/7#issuecomment-595874419).

## OTHER ISSUES

### Conflicts with other components using the same BT interface

Since our component uses a special operating mode of the HCI interface and works with a continuous data stream, conflicts with other software using the same HCI interface are possible. The conflict is caused by the fact that another component can switch the HCI interface to a different operating mode, thereby stopping the reception of data. Or our component may lead to malfunctioning of another component.
A reliable, but not the only way out of this situation (apart from the refusal to use one component in favor of another) can be the use of two BT-interfaces (one for our component, the second, for example, for the tracker). Work is underway to find other solutions to such situations...

### My sensor stops receiving updates some time after the system restart

Most often, the cause of this is the presence of bugs in the system components responsible for the BT operation (kernel modules, firmwares, etc). As a rule, in such cases, the corresponding entries appear in the system log. Please carefully review the contents of your `syslog`, and try searching the Internet for a solution - with high probability you are not alone in this. For example, here is an issue with a typical Raspberry PI problem - [BT problem, Raspberry PI3 and Hass.io](https://github.com/custom-components/sensor.mitemp_bt/issues/31#issuecomment-595417222)

### My sensor from the Xiaomi ecosystem is not in the list of supported ones. How to request implementation?

- [Install the component](https://github.com/custom-components/sensor.mitemp_bt/blob/master/README.md#how-to-install) if you have not already done so.
- Make sure you have [logger](https://www.home-assistant.io/integrations/logger/) enabled, and logging enabled for `info` level (globally or just for `custom_components.mitemp_bt`). For example:

```yaml
logger:
  default: warn
  logs:
    custom_components.mitemp_bt: info
```

- Place your sensor extremely close to the HA host (BT interface).
- [Enable the option](https://github.com/custom-components/sensor.mitemp_bt/blob/master/README.md#configuration) `report_unknown`.
- Wait until a number of "BLE ADV from UNKNOWN" messages accumulate in the log.
- Create a new [issue](https://github.com/custom-components/sensor.mitemp_bt/issues), write everything you know about your sensor and attach the obtained log.
- Do not forget to disable the `report_unknown` option (delete it or set it to `False` and restart HA)! Since the potentially large output of this option will spam the log and can mask really important messages.
- Wait for a response from the developers.

## DEBUG

To enable debug logging, add the following lines to `configuration.yaml`:

```yaml
logger:
  default: warn
  logs:
    custom_components.mitemp_bt: debug
```

In addition, the `btmon` utility can provide a lot of useful information.
For example, using the command

```shell
btmon -t -w problem.log
```

You can write to the problem.log file the moment the problem occurs and attach this file to your issue.

## FORUM

You can more freely discuss the operation of the component, ask for support, leave feedback and share your experience in [our topic](https://community.home-assistant.io/t/xiaomi-passive-ble-monitor-sensor-platform/) on the Home Assistant forum.
