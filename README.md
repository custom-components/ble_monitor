# Xiaomi Mi Temperature and Humidity Monitor (BLE) sensor platform
This custom component is an alternative for the standard build in [mitemp_bt](https://www.home-assistant.io/integrations/mitemp_bt/) integration that is available in Home Assistant. Unlike the original `mitemp_bt` integration, which is getting its data by polling the device with a default five-minute interval, this custom component is parsing the Bluetooth Low Energy packets payload that is emitted each second by the sensor. The packets payload contains temperature/humidity and battery data. Advantage of this integration is that it doesn't affect the battery as much as the built-in integration. It also solves connection issues some people have with the standard integration.

![sensor](/sensor.jpg)

## HOW TO INSTALL
**1. Install bluez-hcidump (not needed on HASSio):**
   - The package `bluez-hcidump` needs to be installed first. `bluez-hcidump` reads raw the data coming from and going to your Bluetooth device. You can install it with the following command
     ```shell
     sudo apt-get install bluez-hcidump
     ```
     
**2. Allow hcitool and hcidump to run without root access (not needed on HASSio):**
   - This custom component uses a hcitool and hcidump commands to receive the data. Run the following commands to allow hcitool and hcidump to run without root access:
     ```shell
     sudo setcap 'cap_net_raw+ep' `readlink -f \`which hcidump\``
     sudo setcap 'cap_net_raw+ep' `readlink -f \`which hcitool\``
     ```
**3. Install the custom component:**
   - The easiest way is to install it with [HACS](https://hacs.netlify.com/). First install [HACS](https://hacs.netlify.com/) if you don't have it yet. After installation you can find this custom component in the HACS store under integrations.
   
     Alternatively, you can install it manually. Just copy paste the content of the `sensor.mitemp_bt/custom_components` folder in your `config/custom_components` directory.
     
     As example you will get the `sensor.py` file in the following path: `/config/custom_components/mitemp_bt/sensor.py`.


**4. Restart Home Assistant:**
   - A restart is required to unload the build in component and load the custom component. Do this before step 5, as Home Assistant will otherwise complain that your configuration is not ok (as it still uses the build in `mitemp_bt` integration), and won't restart when hitting restart in the server management menu.
   
     
**5. Add the platform to your configuration.yaml file (see [below](#CONFIGURATION))**


**6. Restart Home Assistant again:**
   - A second restart is required to load the component. After a few minutes, the sensors should be added to your home-assistant automatically. 


## CONFIGURATION
Add the following to your `configuration.yaml` file.

```yaml
sensor:
  - platform: mitemp_bt
```

IMPORTANT. If you used the standard Home Assistant built ['mitemp_bt'](https://www.home-assistant.io/integrations/mitemp_bt/) integration, make sure you delete the additional parameters, like `mac:` and `monitored_conditions:`.

## Credits
Credits and a big thanks should be given to [@tsymbaliuk](https://community.home-assistant.io/u/tsymbaliuk) and [@Magalex](https://community.home-assistant.io/u/Magalex). The main python code for this component was originally developed by [@tsymbaliuk](https://community.home-assistant.io/u/tsymbaliuk) and later modified by [@Magalex](https://community.home-assistant.io/u/Magalex).
