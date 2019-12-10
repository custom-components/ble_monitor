# Xiaomi BLE Monitor sensor platform
This custom component is an alternative for the standard build in [mitemp_bt](https://www.home-assistant.io/integrations/mitemp_bt/) integration that is available in Home Assistant. Unlike the original `mitemp_bt` integration, which is getting its data by polling the device with a default five-minute interval, this custom component is parsing the Bluetooth Low Energy packets payload that is constantly emitted by the sensor. The packets payload may contain temperature/humidity/battery and other data. Advantage of this integration is that it doesn't affect the battery as much as the built-in integration. It also solves connection issues some people have with the standard integration.

Supported sensors:

![supported sensors](/sensors.jpg)

 - LYWSDCGQ 
 (round body, segment LCD, broadcasts temperature, humidity and battery, about 20 readings per minute)
 
 - LYWSD02 
 (rectangular body, E-Ink, broadcasts temperature and humidity, about 20 readings per minute, no battery info)
 
 - CGG1 
 (round body, E-Ink, broadcasts temperature, humidity and battery, about 20 readings per minute)
 
 - HHCCJCY01 
 (MiFlora, broadcasts temperature, moisture, illuminance, conductivity, 1 reading per minute, no battery info with firmware v3.2.1)
 
 *The amount of actually received data is highly dependent on the reception conditions (like distance and electromagnetic ambiance), readings numbers are indicated for good RSSI (Received Signal Strength Indicator) of about -75 till -70dBm.*

## HOW TO INSTALL
**1. Install bluez-hcidump (not needed on HASSio):**
   - The package `bluez-hcidump` needs to be installed first. `bluez-hcidump` reads raw the data coming from and going to your Bluetooth device. You can install it with the following command
     ```shell
     sudo apt-get install bluez-hcidump
     ```
     
**2. Allow hcitool and hcidump to run without root access (not needed on HASSio):**
   - This custom component uses hcitool and hcidump commands to receive the data. Run the following commands to allow hcitool and hcidump to run without root access:
     ```shell
     sudo setcap 'cap_net_raw+ep' `readlink -f \`which hcidump\``
     sudo setcap 'cap_net_raw+ep' `readlink -f \`which hcitool\``
     ```
**3. Install the custom component:**
   - The easiest way is to install it with [HACS](https://hacs.netlify.com/). First install [HACS](https://hacs.netlify.com/) if you don't have it yet. After installation you can find this custom component in the HACS store under integrations.
   
     Alternatively, you can install it manually. Just copy paste the content of the `sensor.mitemp_bt/custom_components` folder in your `config/custom_components` directory.
     
     As example, you will get the `sensor.py` file in the following path: `/config/custom_components/mitemp_bt/sensor.py`.


**4. Restart Home Assistant:**
   - A restart is required to unload the build in component and load the custom component. Do this before step 5, as Home Assistant will otherwise complain that your configuration is not ok (as it still uses the build in `mitemp_bt` integration), and won't restart when hitting restart in the server management menu.
   
     
**5. Add the platform to your configuration.yaml file (see [below](#configuration))**


**6. Restart Home Assistant again:**
   - A second restart is required to load the component. After a few minutes, the sensors should be added to your home-assistant automatically (at least one [period](#configuration-variables) required). 


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
    decimals: 2
    period: 60
    log_spikes: False
    use_median: False
    hcitool_active: False
```

IMPORTANT. This component uses temporary file to accumulate sensor data between sensor updates. Therefore, to reduce the number of write operations and extend the life of the physical medium (especially if it is an SD card, as is the case with Raspberry PI), we recommend moving `/tmp` mount point to RAM (tmpfs). To do this, add the following line to the end of your `/etc/fstab` and restart the host:
```
tmpfs		/tmp		tmpfs	rw,nosuid,nodev 0	0
```
You can check the `/tmp` mount point with the command `mount | grep /tmp`. If as a result you see something like `tmpfs on /tmp type tmpfs (rw, nosuid, nodev, relatime)`, then everything is fine.


### Configuration Variables

**rounding**

  (boolean)(Optional) Enable/disable rounding of the average of all measurements taken within the number seconds specified with 'period'. Default value: True

**decimals**

  (positive integer)(Optional) Number of decimal places to round if rounding is enabled. Default value: 2

**period**

  (positive integer)(Optional) The period in seconds during which the sensor readings are collected and transmitted to Home Assistant after averaging. Default value: 60. 

  *To clarify the difference between the sensor broadcast interval and the component measurement period: The LYWSDCGQ transmits 20-25 valuable BT LE messages (RSSI -75..-70 dBm). During the period = 60 (seconds), the component accumulates all these 20-25 messages, and after the 60 seconds expires, averages them and updates the sensor status in Home Assistant. The period does not affect the consumption of the sensor. It only affects the Home Assistant sensor update rate and the number of averaged values. We cannot change the frequency with which sensor sends data.*

**log_spikes**

  (boolean)(Optional) Puts information about each erroneous spike in the Home Assistant log. Default value: False
  
  *There are reports (pretty rare) that some sensors tend to sometimes produce erroneous values that differ markedly from the actual ones. Therefore, if you see inexplicable sharp peaks or dips on the temperature or humidity graph, I recommend that you enable this option so that you can see in the log which values were qualified as erroneous. The component discards values that exceeds the sensor’s measurement capabilities. These discarded values are given in the log records when this option is enabled. If erroneous values are within the measurement capabilities (-40..60°C and 0..100%H), there are no messages in the log. If your sensor is showing this, there is no other choice but to calculate the average as the median (next option).*

**use_median**

  (boolean)(Optional) Use median as sensor output instead of mean (helps with "spiky" sensors). Please note that both the median and the mean values in any case are present as the sensor state attributes. Default value: False
  
  *The difference between the mean and the median is that the median is **selected** from the sensor readings, and not calculated as the average. That is, the median resolution is equal to the resolution of the sensor (one tenth of a degree or percent), while the mean allows you to slightly increase the resolution (the longer the measurement period, the larger the number of values will be averaged, and the higher the resolution can be achieved, if necessary with disabled rounding).*

**hcitool_active**

  (boolean)(Optional) In active mode hcitool sends scan requests, which is most often not required, but slightly increases the sensor battery consumption. 'Passive mode' means that you are not sending any request to the sensor but you are just reciving the advertisements sent by the BLE devices. This parameter is a subject for experiment. See the hcitool docs, --passive switch. Default value: False



## Credits
Credits and a big thanks should be given to [@tsymbaliuk](https://community.home-assistant.io/u/tsymbaliuk) and [@Magalex](https://community.home-assistant.io/u/Magalex). The main python code for this component was originally developed by [@tsymbaliuk](https://community.home-assistant.io/u/tsymbaliuk) and later modified by [@Magalex](https://community.home-assistant.io/u/Magalex).
