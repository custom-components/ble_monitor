"""Helpers for ble_monitor."""
import logging
import subprocess
import time

_LOGGER = logging.getLogger(__name__)


# Bluetooth interfaces available on the system
def hci_get_mac(interface_list=[0]):
    """Get dict of available bluetooth interfaces, returns hci and mac."""
    btaddress_dict = {}
    output = subprocess.run(
        ["hciconfig"], stdout=subprocess.PIPE, check=True
    ).stdout.decode("utf-8")

    for interface in interface_list:
        hci_id = "hci{}".format(interface)
        try:
            btaddress_dict[interface] = (
                output.split("{}:".format(hci_id))[1]
                .split("BD Address: ")[1]
                .split(" ")[0]
                .strip()
            )
        except IndexError:
            pass
    return btaddress_dict

# rfkill commands


def rfkill_list_bluetooth(hci):
    """Execute the rfkill list bluetooth command."""
    _LOGGER.debug("rfkill list bluetooth.....")
    output = subprocess.run(
        ["rfkill", "list", "bluetooth"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
    )
    stdout = output.stdout.decode("utf-8")
    stderr = output.stderr
    if output.returncode != 0:
        _LOGGER.error("executing rfkill list bluetooth failed: %s", stderr)
        return "Uknown", "Uknown"
    hci_id = "hci{}".format(hci)
    try:
        soft_blocked = (
            stdout.split("{}:".format(hci_id))[1]
            .split("Soft blocked: ")[1]
            .split("\n")[0]
            .strip()
        )
        hard_blocked = (
            stdout.split("{}:".format(hci_id))[1]
            .split("Hard blocked: ")[1]
            .split("\n")[0]
            .strip()
        )
        if soft_blocked == "yes":
            soft_block = True
        else:
            soft_block = False
        if hard_blocked == "yes":
            hard_block = True
        else:
            hard_block = False
    except IndexError:
        pass
    return soft_block, hard_block


def rfkill_block_bluetooth():
    """Execute the rfkill block bluetooth command."""
    _LOGGER.debug("rfkill block bluetooth.....")
    command = subprocess.run(["rfkill", "block", "bluetooth"], stderr=subprocess.PIPE, check=True)
    stderr = command.stderr
    if command.returncode != 0:
        _LOGGER.error("executing rfkill block bluetooth failed: %s", stderr)
        return


def rfkill_unblock_bluetooth():
    """Execute the rfkill unblock bluetooth command."""
    _LOGGER.debug("rfkill unblock bluetooth.....")
    command = subprocess.run(["rfkill", "unblock", "bluetooth"], stderr=subprocess.PIPE, check=True)
    stderr = command.stderr
    if command.returncode != 0:
        _LOGGER.error("executing rfkill unblock bluetooth failed: %s", stderr)
        return


# Bluetoothctl commands
def bluetoothctl_select(mac):
    """Execute the bluetoothctl select command."""
    _LOGGER.debug("bluetoothctl select %s", mac)
    command = subprocess.run(["bluetoothctl", "select", mac], stderr=subprocess.PIPE, check=True)
    stderr = command.stderr
    if command.returncode != 0:
        _LOGGER.error("executing bluetoothctl select failed: %s", stderr)
        return


def bluetoothctl_show():
    """Execute the bluetoothctl show command."""
    _LOGGER.debug("bluetoothctl show.....")
    output = subprocess.run(
        ["bluetoothctl", "show"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
    )
    stdout = output.stdout.decode("utf-8")
    stderr = output.stderr
    if output.returncode != 0:
        _LOGGER.error("executing rfkill list bluetooth failed: %s", stderr)
        power = "Unknown"
    else:
        power_state = (
            stdout.split("Powered: ")[1]
            .split("\n")[0]
            .strip()
        )
        if power_state == "on" or "yes":
            power = True
        else:
            power = False
    return power


def bluetoothctl_power_off():
    """Execute the bluetoothctl power off command."""
    _LOGGER.debug("bluetoothctl power off.....")
    command = subprocess.run(["bluetoothctl", "power", "off"], stderr=subprocess.PIPE, check=True)
    stderr = command.stderr
    if command.returncode != 0:
        _LOGGER.error("eexecuting bluetoothctl power off failed: %s", stderr)
        return


def bluetoothctl_power_on():
    """Execute the bluetoothctl power on command."""
    _LOGGER.debug("bluetoothctl power on.....")
    command = subprocess.run(["bluetoothctl", "power", "on"], stderr=subprocess.PIPE, check=True)
    stderr = command.stderr
    if command.returncode != 0:
        _LOGGER.error("eexecuting bluetoothctl power on failed: s%s", stderr)
        return


def reset_bluetooth(hci):
    """Resetting the Bluetooth adapter."""
    _LOGGER.debug("resetting Bluetooth")

    # Select the Bluetooth adapter and retreive the state of the adapter
    mac = hci_get_mac([hci])[0]
    if not mac:
        _LOGGER.eror(
            "HCI%i seems not to exist (anymore), check BT interface mac address in your settings ",
            hci
        )
        return

    bluetoothctl_select(mac)
    power_state_before = bluetoothctl_show()
    if power_state_before is True:
        _LOGGER.debug("Power state of bluetooth adapter is on before resetting Bluetooth")
    elif power_state_before is False:
        _LOGGER.debug(
            "Power state of bluetooth adapter is off before resetting Bluetooth, trying to turn it back on."
        )
    else:
        _LOGGER.debug(
            "Power state of bluetooth adapter before resetting Bluetooth could not be determined, trying to turn it back on anyways."
        )

    soft_block, hard_block = rfkill_list_bluetooth(hci)
    if soft_block is True:
        _LOGGER.debug("bluetooth adapter is soft blocked before reset")
    elif soft_block is False:
        _LOGGER.debug("bluetooth adapter is not soft blocked before reset")
    else:
        _LOGGER.debug("bluetooth adapter soft blocked state could not be determined before reset")
    if hard_block is True:
        _LOGGER.debug("bluetooth adapter is hard blocked before reset")
    elif hard_block is False:
        _LOGGER.debug("bluetooth adapter is not hard blocked before reset")
    else:
        _LOGGER.debug("bluetooth adapter hard blocked state could not be determined before reset")

    # Turn the power on and unblock bluetooth adapter
    bluetoothctl_power_on()
    rfkill_unblock_bluetooth()
    time.sleep(5)

    # Check the state after the reset
    power_state_after = bluetoothctl_show()
    if power_state_after is True:
        _LOGGER.debug("Power state of bluetooth adapter is on after resetting Bluetooth")
    elif power_state_after is False:
        _LOGGER.debug("Power state of bluetooth adapter is still off after resetting Bluetooth.")
    else:
        _LOGGER.debug(
            "Power state of bluetooth adapter after resetting Bluetooth could not be determined."
        )

    soft_block, hard_block = rfkill_list_bluetooth(hci)
    if soft_block is True:
        _LOGGER.debug("bluetooth adapter is still soft blocked after reset")
    elif soft_block is False:
        _LOGGER.debug("bluetooth adapter is not soft blocked after reset")
    else:
        _LOGGER.debug("bluetooth adapter soft blocked state could not be determined after reset")
    if hard_block is True:
        _LOGGER.debug("bluetooth adapter is still hard blocked after reset")
    elif hard_block is False:
        _LOGGER.debug("bluetooth adapter is not hard blocked after reset")
    else:
        _LOGGER.debug("bluetooth adapter hard blocked state could not be determined after reset")


try:
    BT_INTERFACES = hci_get_mac([0, 1, 2, 3])
    DEFAULT_BT_INTERFACE = list(BT_INTERFACES.items())[0][1]
    DEFAULT_HCI_INTERFACE = list(BT_INTERFACES.items())[0][0]
except (IndexError, OSError, subprocess.CalledProcessError):
    BT_INTERFACES = {}
    DEFAULT_BT_INTERFACE = "disable"
    DEFAULT_HCI_INTERFACE = "disable"
    _LOGGER.debug(
        "No Bluetooth interface found. Make sure Bluetooth is installed on your system"
    )

BT_MULTI_SELECT = dict([(v, v + ' (hci' + str(k) + ')') for k, v in BT_INTERFACES.items()])
BT_MULTI_SELECT["disable"] = "Don't use Bluetooth adapter"
