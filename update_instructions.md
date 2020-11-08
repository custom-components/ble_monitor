# Update instructions for 0.8.0

## Why is the configuration input changed?
The configuration options have been restructured in 0.8.0. This will allow us to furher develop the component in the future and add more options at the level of the sensor device.
To make this possible, it was needed to restructure the configuration input. Part of the options have been moved to a new `devices` option, which has sub-options at device level. 

## Do I need to modify my configuration?
If you use one of the following options, you will have to update your configuration after updating to 0.8.0. 

- `encryptors`
- `sensor_names`
- `sensor_fahrenheit`
- `whitelist`

## Instructions how to update
To prevent Home Assistant from not restarting (due to incorrect configuration), use the following procedure: 
1. First update the component in HACS 
2. Restart Home Assistant (component will not load correctly)
3. Update your configuration 
4. Restart Home Assistant

## Conversion
The new configuration should be defined as follows. 

```yaml
sensor:
  - platform: mitemp_bt
    discovery: True
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

For each of the old options, the old and new format is given below. You can combine the options, as shown above. 

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
sensor:
  - platform: mitemp_bt
    devices:
      - mac: 'A4:C1:38:2F:86:6C'
        encryption_key: '217C568CF5D22808DA20181502D84C1B'
      - mac: 'C4:3C:4D:6B:4F:F3'
        encryption_key: 'C99D2313182473B38001086FEBF781BD'
```

Note that if you use secrets to hide your encryption keys, you will have to modify your 'secrets.yaml' file as well and create an entry of each 'encryption key'. 

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
sensor:
  - platform: mitemp_bt
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
sensor:
  - platform: mitemp_bt
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
sensor:
  - platform: mitemp_bt
    discovery: False
    devices:
      - mac: '58:C1:38:2F:86:6C'
      - mac: 'C4:FA:64:D1:61:7D'
```

The `discovery: False` will prevent new sensors being discoverd. Only sensors under devices will be monitored. 
