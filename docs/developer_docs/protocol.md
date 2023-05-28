---
layout: default
parent: Technical and development documentation
title: Reverse engineering the MiBeacon protocol
permalink: MiBeacon_protocol
nav_order: 2
---

## Reverse engineering the MiBeacon protocol

With the `report_unknown` option, you can collect information about new devices that are not supported yet. An example of the LYWSDCGQ sensor is given below. This sensor supports Temperature, Humidity and battery level and is not encrypted. Enabling this option will generate a lot of output in the logs, which look like this.

`2020-12-23 17:42:12 INFO (Thread-3) [custom_components.ble_monitor] BLE ADV from UNKNOWN: RSSI: -53, MAC: 4C65A8DDB89B, ADV: 043e25020100009bb8dda8654c19020106151695fe5020aa01fe9bb8dda8654c0d1004b2007502cb`

Another option is to use the following command.

`btmon --write hcitrace.snoop | tee hcitrace.txt`

It will display all bluetooth messages, search for the ones that have an `UUID 0xfe95`.

```
> HCI Event: LE Meta Event (0x3e) plen 37                 #292 [hci0] 10.578272
      LE Advertising Report (0x02)
        Num reports: 1
        Event type: Connectable undirected - ADV_IND (0x00)
        Address type: Public (0x00)
        Address: 4C:65:A8:DD:B8:9B (OUI 4C-65-A8)
        Data length: 25
        Flags: 0x06
          LE General Discoverable Mode
          BR/EDR Not Supported
        Service Data (UUID 0xfe95): 5020aa010c9bb8dda8654c0d1004b2004302
        RSSI: -68 dBm (0xbc)
```

In the example below, we will use the data from the `report_unknown` option. When sorting this data, you can find the following pattern for the LYWSDCGQ sensor. The `Service Data` in the HCI Event above corresponds to the part from `Frame ctrl` till the `payload` (without `RSSI`). More info on the Mi Beacon protocol can be found [here](https://cdn.cnbj0.fds.api.mi-img.com/miio.files/commonfile_pdf_f119c8464d43526b48fb453f19f30192.pdf), although most is in Chinese.

```
-----------------------------------------------------------------------------------------------------------------------------------------------------------
HCI  Evt Len Sub Num Evt  Peer -------MAC-------   Len Len Type Val Len  AD  Xiaomi Frame Product Frame ------MAC--------   -----PAYLOAD-------------  RSSI
type code    evt rep type addr                             flag         type  UUID   ctrl   ID    cnt                      Type  Len  Temp   Hum   Batt
 A    B  C    D  E    F    G          H            I   J    K   L   M    N     O      P     Q      R           S            T     U    V      W     X   Y
-----------------------------------------------------------------------------------------------------------------------------------------------------------
 04   3e 25  02  01   00   00  9b b8 dd a8 65 4c   19  02   01  06  15   16  95 fe  50 20  aa 01   fe   9b b8 dd a8 65 4c   0d 10 04  b2 00  75 02      cb
 04   3e 23  02  01   00   00  9b b8 dd a8 65 4c   17  02   01  06  13   16  95 fe  50 20  aa 01   ff   9b b8 dd a8 65 4c   04 10 02  b1 00             d0
 04   3e 25  02  01   00   00  9b b8 dd a8 65 4c   19  02   01  06  15   16  95 fe  50 20  aa 01   00   9b b8 dd a8 65 4c   0d 10 04  b3 00  74 02      d0
 04   3e 25  02  01   00   00  9b b8 dd a8 65 4c   19  02   01  06  15   16  95 fe  50 20  aa 01   01   9b b8 dd a8 65 4c   0d 10 04  b2 00  74 02      c9
 04   3e 25  02  01   00   00  9b b8 dd a8 65 4c   19  02   01  06  15   16  95 fe  50 20  aa 01   02   9b b8 dd a8 65 4c   0d 10 04  b3 00  74 02      c9
 04   3e 25  02  01   00   00  9b b8 dd a8 65 4c   19  02   01  06  15   16  95 fe  50 20  aa 01   03   9b b8 dd a8 65 4c   0d 10 04  b2 00  74 02      c8
 04   3e 23  02  01   00   00  9b b8 dd a8 65 4c   17  02   01  06  13   16  95 fe  50 20  aa 01   04   9b b8 dd a8 65 4c   06 10 02         74 02      cb
 04   3e 25  02  01   00   00  9b b8 dd a8 65 4c   19  02   01  06  15   16  95 fe  50 20  aa 01   05   9b b8 dd a8 65 4c   0d 10 04  b2 00  74 02      cb
 04   3e 25  02  01   00   00  9b b8 dd a8 65 4c   19  02   01  06  15   16  95 fe  50 20  aa 01   06   9b b8 dd a8 65 4c   0d 10 04  b3 00  74 02      c9
 04   3e 23  02  01   00   00  9b b8 dd a8 65 4c   17  02   01  06  13   16  95 fe  50 20  aa 01   07   9b b8 dd a8 65 4c   04 10 02  b2 00             c9
 04   3e 22  02  01   00   00  9b b8 dd a8 65 4c   16  02   01  06  12   16  95 fe  50 20  aa 01   08   9b b8 dd a8 65 4c   0a 10 01                48  cb
-----------------------------------------------------------------------------------------------------------------------------------------------------------
```

### Converting hex to decimals
Next step is to convert some of the hex numbers to decimals. The following parameters are in the table below converted to decimals, to make it human readable:

- Len
- Num rep
- Frame cnt
- Temp
- Hum
- Batt
- RSSI

```
-----------------------------------------------------------------------------------------------------------------------------------------------------------
HCI  Evt Len Sub Num Evt  Peer -------MAC-------   Len Len Type Val Len  AD  Xiaomi Frame Product Frame ------MAC--------   -----PAYLOAD-------------  RSSI
type code    evt rep type addr                             flag         type  UUID   ctrl   ID    cnt                      Type  Len  Temp   Hum   Batt
 A    B  C    D   E   F    G          H            I   J    K   L   M    N     O      P     Q      R           S            T     U    V      W     X   Y
-----------------------------------------------------------------------------------------------------------------------------------------------------------
 04   3e 37  02   1   00  00   9b b8 dd a8 65 4c   25   2   01  06  21   16  95 fe  50 20  aa 01   254  9b b8 dd a8 65 4c   0d 10  4  178    629       -53
 04   3e 35  02   1   00  00   9b b8 dd a8 65 4c   23   2   01  06  19   16  95 fe  50 20  aa 01   255  9b b8 dd a8 65 4c   04 10  2  177              -48
 04   3e 37  02   1   00  00   9b b8 dd a8 65 4c   25   2   01  06  21   16  95 fe  50 20  aa 01     0  9b b8 dd a8 65 4c   0d 10  4  179    628       -48
 04   3e 37  02   1   00  00   9b b8 dd a8 65 4c   25   2   01  06  21   16  95 fe  50 20  aa 01     1  9b b8 dd a8 65 4c   0d 10  4  178    628       -55
 04   3e 37  02   1   00  00   9b b8 dd a8 65 4c   25   2   01  06  21   16  95 fe  50 20  aa 01     2  9b b8 dd a8 65 4c   0d 10  4  179    628       -55
 04   3e 37  02   1   00  00   9b b8 dd a8 65 4c   25   2   01  06  21   16  95 fe  50 20  aa 01     3  9b b8 dd a8 65 4c   0d 10  4  179    628       -56
 04   3e 35  02   1   00  00   9b b8 dd a8 65 4c   23   2   01  06  19   16  95 fe  50 20  aa 01     4  9b b8 dd a8 65 4c   06 10  2         628       -53
 04   3e 37  02   1   00  00   9b b8 dd a8 65 4c   25   2   01  06  21   16  95 fe  50 20  aa 01     5  9b b8 dd a8 65 4c   0d 10  4  178    628       -53
 04   3e 37  02   1   00  00   9b b8 dd a8 65 4c   25   2   01  06  21   16  95 fe  50 20  aa 01     6  9b b8 dd a8 65 4c   0d 10  4  179    628       -55
 04   3e 35  02   1   00  00   9b b8 dd a8 65 4c   23   2   01  06  19   16  95 fe  50 20  aa 01     7  9b b8 dd a8 65 4c   04 10  2  178              -55
 04   3e 34  02   1   00  00   9b b8 dd a8 65 4c   22   2   01  06  18   16  95 fe  50 20  aa 01     8  9b b8 dd a8 65 4c   0a 10  1               72  -53
-----------------------------------------------------------------------------------------------------------------------------------------------------------
```

### Explanation of the data

- A HCI Packet Type: HCI Event (`0x04`)
- B Event Code: LE Data (`0x3e`)
- C Total length of the advertisement (37)
- D Sub Event: LE Advertising report (`0x02`)
- E Num Reports: 1
- F Event Type: Connectable undirected - ADV_IND (`0x00`)
- G Peer Address Type: Public (`0x00`)
- H MAC = MAC address in reversed order (per 2 characters)
- I Data length till the end of advertisement
- J Length
- L Value
- M Length till the end of advertisement
- N AD type (for Xiaomi Mi Beacon `16`)
- O UUID (for the Xiaomi Mi Beacon `95 fe`)
- P Frame control
- Q Product ID = Indicator for the device type, as used in `const.py`
- R Frame cnt = Index number of the message
- S MAC = MAC address in reversed order (per 2 characters)
- T Type = Type of measurement
  - 0d 10 = temperature + humidity
  - 04 10 = temperature
  - 06 10 = humidity
  - 0a 10 = battery
- U Length of measurement data
- V Temperature data in Celsius (divide by 10) (e.g. `b2 00` --> `00 B2` (hex) --> 178 (decimal) --> 17.8 °C)
- W Hum = Humidity in (divide by 10) (e.g. `75 02` --> `02 75` (hex) --> 629 (decimal) --> 62.9 %)
- X Batt = Battery in % (`48` (hex) --> 72 (decimals) --> 72%)
- Y RSSI (`CB` (hex) --> -53 (decimals))

## Encrypted advertisements
Some advertisements are encrypted. The following python script shows the decryption of these messages

```python
from Cryptodome.Cipher import AES

data_string = "043e2b020103000fc4e044ef541f0201061b1695fe58598d0a170fc4e044ef547cc27a5c03a1000000790df258bb"
aeskey = "FDD8CE9C08AE7533A79BDAF0BB755E96"

data = bytes(bytearray.fromhex(data_string))
key = bytes.fromhex(aeskey)

xiaomi_index = data.find(b'\x16\x95\xFE')
xiaomi_mac_reversed = data[xiaomi_index + 8:xiaomi_index + 14]
# xiaomi_mac_reversed: 0fc4e044ef54

device_type = data[xiaomi_index + 5:xiaomi_index + 7]
# device_type: 8d0a

nonce = b"".join([xiaomi_mac_reversed, device_type, data[xiaomi_index + 7:xiaomi_index + 8]])
# nonce: 0fc4e044ef548d0a17

encrypted_payload = data[xiaomi_index + 14:-1]
# encrypted_payload: 7cc27a5c03a1000000790df258

aad = b"\x11"

token = encrypted_payload[-4:]
# token: 790df258

payload_counter = encrypted_payload[-7:-4]
# payload_counter: 000000

nonce = b"".join([nonce, payload_counter])
# nonce: 0fc4e044ef548d0a17000000

cipherpayload = encrypted_payload[:-7]
# cipherpayload: 7cc27a5c03a1

cipher = AES.new(key, AES.MODE_CCM, nonce=nonce, mac_len=4)
cipher.update(aad)

decrypted_payload = cipher.decrypt_and_verify(cipherpayload, token)
# decrypted_payload:  0f0003000000
```
