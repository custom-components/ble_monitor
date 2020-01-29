# Frequently asked questions

## INSTALLATION ISSUES


### I get an PermissionError in Home Assistant after the installation
Python needs root access to access the HCI interface. If Python doesn't have root access, you will get an error message in Home Assistant which ends with:

```
PermissionError: [Errno 1] Operation not permitted
```


First, try to set root access with 

```
sudo setcap 'cap_net_raw,cap_net_admin+eip' `readlink -f \`which python3\``
```

Next, check that it is set correctly with the following command

```
sudo getcap `readlink -f \`which python3\``
```

The command will return the path to python and looks like (can vary based on your python version):

```
/usr/bin/python3.7 = cap_net_admin,cap_net_raw+eip
```

Make sure you first stop homeassistant and then start homeassistant again. Restarting Home Assistant is not enough, as the python process does not exit upon restart.

If you have multiple python versions, make sure it refers to the same version which is used by Home Assistant. If Home Assistant is using a different version, e.g. python3.6, run the following command to set the correct version (adjust it to your own version if needed).

```
sudo setcap 'cap_net_raw,cap_net_admin+eip' /usr/bin/python3.6
```

### How do I find the number of the HCI interface?
To find the correct number, run the following command:

```
hcitool dev
```

The command will return the HCI interface number and mac address.

```
Devices:
        hci0    B8:27:EB:77:75:50
```


## RECEPTION ISSUES

### My sensor doesn't receive any readings from my sensors anymore or only occationally
The custom component uses Bluetooth (BLE) to receive messages from your sensor(s). The number of messages per minute that are being send by your sensor depends on the type, but is around 20 messages per minute for LYWSDCGQ, LYWSD02 and CGG1 sensors, around 2 per minute for HHCCPOT002 and around 1 per minute for HHCCJCY01T. 

The number of messages that are received by Home Assistant can be less or even zero. Parameters that affect the reception of messages are:
- The distance between the sensor and the Bluetooth device on your Home Assistant device.

Try to keep the distance as limited as possible

- Interference with other electrical devices. 

Especially SSD devices are known to affect the Bluetooth reception, try to place your SSD drive as far as possible from your Bluetooth tranceiver. 

- The quality of your Bluetooth transceiver. 

The range of the built-in Bluetooth tranceiver of a Raspberry Pi is known to be limited. Try using an external Bluetooth transceiver to increase the range, e.g. with an external antenna.  
