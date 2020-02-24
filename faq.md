# Frequently asked questions

## Table of contents

<!-- TOC -->

  - [INSTALLATION ISSUES](#installation-issues)
      - [I get a PermissionError in Home Assistant after the installation](#i-get-a-permissionerror-in-home-assistant-after-the-installation-or-python-upgrade)
      - [How do I find the number of the HCI interface?](#how-do-i-find-the-number-of-the-hci-interface)
      - [How can I create a battery sensor?](#how-can-i-create-a-battery-sensor)
  - [RECEPTION ISSUES](#reception-issues)
      - [My sensor doesn't receive any readings from my sensors anymore or only occasionally](#my-sensor-doesnt-receive-any-readings-from-my-sensors-anymore-or-only-occasionally)
  - [OTHER ISSUES](#other-issues)
      - [Conflicts with other components using the same BT interface](#conflicts-with-other-components-using-the-same-bt-interface)
      - [My sensor stops receiving updates some time after the system restart](my-sensor-stops-receiving-updates-some-time-after-the-system-restart)
  - [DEBUG](#debug)

<!-- /TOC -->

## INSTALLATION ISSUES

### I get a PermissionError in Home Assistant after the installation or python upgrade

Note: This answer is only applicable for version 0.5 and higher.

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

## OTHER ISSUES

### Conflicts with other components using the same BT interface

Since our component uses a special operating mode of the HCI interface and works with a continuous data stream, conflicts with other software using the same HCI interface are possible. The conflict is caused by the fact that another component can switch the HCI interface to a different operating mode, thereby stopping the reception of data. Or our component may lead to malfunctioning of another component.
A reliable, but not the only way out of this situation (apart from the refusal to use one component in favor of another) can be the use of two BT-interfaces (one for our component, the second, for example, for the tracker). Work is underway to find other solutions to such situations...

### My sensor stops receiving updates some time after the system restart

Most often, the cause of this is the presence of the bugs in the system components responsible for the BT operation (kernel modules, firmwares, etc). As a rule, in such cases, the corresponding entries appear in the system log. Please carefully review the contents of your `syslog`, and try searching the Internet for a solution - with high probability you are not alone in this.

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

You can write to the problem.log file the moment the problem occurs, and attach this file to your issue.
