# Update instructions for 0.8.1

## Why is the configuration input changed?

Our custom component `mitemp_bt` was designed as a so called `sensor platform`, which is in Home Assistant language a `platform` under the `sensor` integration. Home Assistant however has made an architecture decision in [ADR 0007](https://github.com/home-assistant/architecture/blob/413e3cb248cf8dca766c0280997f3b516e23fb6d/adr/0007-integration-config-yaml-structure.md), which basically says that `mitemp_bt` should be a `integration` on its own.

So, we decided to make this change and, as it will be a breaking change anyways, we also decided to think about the name of the integration. During time we started to add more and more sensors, not only Xiaomi Mi Temperature sensors, what the name `mitemp_bt` suggests. We decided that `ble_monitor` would be a better name to reflect the capablities of our integration. The full name will become Passive BLE Monitor integration.

Note that your sensor names are most likely also renamed. Look for sensors that start for ble_ (e.g. `ble_temperature_livingroom`). We recommend to use the new `name` option to easily rename and find your sensors. 

## Do I need to modify my configuration?

Yes, everybody has to change their config. All users have to change the following lines

```yaml
sensor:
  - platform: mitemp_bt
```

to

```yaml
ble_monitor:
```

If you use one of the following options, you will have to make additional changes, see below.

- `encryptors`
- `sensor_names`
- `sensor_fahrenheit`
- `whitelist`

## Conversion

The new configuration with all optional options should be defined as follows.

```yaml
ble_monitor:
  rounding: True
  decimals: 1
  period: 60
  log_spikes: False
  use_median: False
  active_scan: False
  hci_interface: 0
  batt_entities: False
  discovery: True
  report_unknown: False
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

For each of the depreciated options, the old and new format is given below. You can combine the options, as shown above.

### encryptors

Old configuration.yaml

```yaml
sensor:
  - platform: mitemp_bt
    encryptors:
      'A4:C1:38:2F:86:6C': '217C568CF5D22808DA20181502D84C1B'
      'C4:3C:4D:6B:4F:F3': 'C99D2313182473B38001086FEBF781BD'
```

New configuration.yaml

```yaml
ble_monitor:
  devices:
    - mac: 'A4:C1:38:2F:86:6C'
      encryption_key: '217C568CF5D22808DA20181502D84C1B'
    - mac: 'C4:3C:4D:6B:4F:F3'
      encryption_key: 'C99D2313182473B38001086FEBF781BD'
```

Note that if you use secrets to hide your encryption keys, you will have to modify your `secrets.yaml` file as well and create an entry of each `encryption key`.

### sensor_names

Old configuration

```yaml
sensor:
  - platform: mitemp_bt
    sensor_names:
      'A4:C1:38:2F:86:6C': 'Livingroom'
      'C4:3C:4D:6B:4F:F3': 'Bedroom'
```

New configuration.yaml

```yaml
ble_monitor:
  devices:
    - mac: 'A4:C1:38:2F:86:6C'
      name: 'Livingroom'
    - mac: 'C4:3C:4D:6B:4F:F3'
      name: 'Bedroom'
```

### sensor_fahrenheit

Old configuration.yaml

```yaml
sensor:
  - platform: mitemp_bt
    sensor_fahrenheit:
      - '58:C1:38:2F:86:6C'
      - 'C4:FA:64:D1:61:7D'
```

New configuration.yaml

```yaml
ble_monitor:
  devices:
    - mac: '58:C1:38:2F:86:6C'
      temperature_unit: F
    - mac: 'C4:FA:64:D1:61:7D'
      temperature_unit: F
```

Note, is is not needed to set the temperature_unit to C for sensors that measure in Celsius. C is the default value.

### whitelist

Old configuration.yaml

```yaml
sensor:
  - platform: mitemp_bt
    whitelist:
      - '58:C1:38:2F:86:6C'
      - 'C4:FA:64:D1:61:7D'
```

New configuration.yaml

```yaml
ble_monitor:
  discovery: False
  devices:
    - mac: '58:C1:38:2F:86:6C'
    - mac: 'C4:FA:64:D1:61:7D'
```

The `discovery: False` will prevent new sensors being discoverd. Only sensors under devices will be monitored.
