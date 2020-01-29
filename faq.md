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
