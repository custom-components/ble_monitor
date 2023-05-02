---
layout: default
title: New sensor request
permalink: sensor_request
nav_order: 8
has_children: true
---

## Request support for new sensor

To be able to add support for a new sensor, we need some info from the device you want us to add. The most important info we need are some examples of the BLE advertisement data that the sensor is sending. There are multiple ways to get this data, we explain two possibilities, one posibility is with the logger in Home Assistant and another option is creating a HCIdump.

### Getting BLE advertisements with the Home Assistant logger

- Add the [logger](https://www.home-assistant.io/integrations/logger/) integration in your Home Assistant configuration and enable logging at `info` level (globally or just for `custom_components.ble_monitor`). You can do this by adding the following to your `configuration.yaml`:

```yaml
logger:
  default: warn
  logs:
    custom_components.ble_monitor: info
```

- Place your sensor extremely close to the HA host (BT interface).
- If you know the MAC address (or UUID) of your sensor, it is preferred to use the `report_unknown` option at device level, by going to the BLE monitor options, and adding a device in the `devices` pull down menu. After clicking submit, a new window will open where you can add the MAC address (or UUID) and [enable the option](configuration_params#report_unknown_(device_level)) `report_unknown`. This will filter the data only for the specified MAC or UUID.
- If you don't know the MAC address, [enable the option](configuration_params#report_unknown) `report_unknown` at global level. First try it by specifying the sensor brand you want to get info from. If you don't know the sensor brand or you can't find data you want, use `report_unkown: Other` to get all BLE advertisements. Especially in the last case, be prepared for a huge number of log lines.
- Wait until a number of "BLE ADV from UNKNOWN" messages accumulate in the log.
- Create a new [issue](https://github.com/custom-components/ble_monitor/issues), write everything you know about your sensor and attach the obtained log.
- Do not forget to disable the `report_unknown` option (delete it or set it to `Off` and restart HA)! Since the potentially large output of this option will spam the log and can mask really important messages.

### Getting BLE advertisements with a HCIdump

The BLE advertisements can also be collected with a `hcidump` with the following command on a linux system (leave it running for a couple of minutes). If you are using a full Home Assistant installation including Home Assistant OS, you will have to follow [this procedure](https://developers.home-assistant.io/docs/operating-system/debugging/) first to get access to these commands.

```shell
sudo hcidump --raw hci > dump.txt
```

In case you get `Disable scan failed: Input/output error`, reset hciconfig with one of the following

```shell
sudo hciconfig hci0 down
sudo hciconfig hci0 up
```

or

```shell
sudo hciconfig hci0 reset
```

And than run the first command again.

Attach the created `dump.txt` to a new [issue](https://github.com/custom-components/ble_monitor/issues) as described above.

### Getting BLE advertisements with an android app

If you don't have access to `hcidump`, you could also use the android app [Bluetooth LE Scanner](https://play.google.com/store/apps/details?id=uk.co.alt236.btlescan) to collect data.
