# Reverse engineering the (non-encrypted) MiBeacon protocol 

With the `report_unknown` option, you can collect information about new devices that are not supported yet. An example of the LYWSDCGQ sensor is given below. This sensor supports Temperature, Humidity and battery level and is not encrypted. Enabling this option will genereate a lot of output in the logs, which look like this.

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

In the example below, we will use the data from the `report_unknown` option. When sorting this data, you can find the following pattern for the LYWSDCGQ sensor. The `Service Data` in the HCI Event above corresponds to the part from `Frame ctrl` till the `payload` (without `RSSI`). 

```
-----------------------------------------------------------------------------------------------------------------------------------------------
      Len             --------MAC-------   Len         Len  AD  Xiaomi Frame Device  Frame ------MAC--------   -----PAYLOAD-------------  RSSI
                                                           type  UUID   ctrl  type    cnt                      Type  Len Temp   Hum   Batt
-----------------------------------------------------------------------------------------------------------------------------------------------
04 3e 25 02 01 00 00   9b b8 dd a8 65 4c   19 02 01 06 15   16  95 fe  50 20  aa 01   fe   9b b8 dd a8 65 4c   0d 10 04  b2 00  75 02      cb
04 3e 23 02 01 00 00   9b b8 dd a8 65 4c   17 02 01 06 13   16  95 fe  50 20  aa 01   ff   9b b8 dd a8 65 4c   04 10 02  b1 00             d0
04 3e 25 02 01 00 00   9b b8 dd a8 65 4c   19 02 01 06 15   16  95 fe  50 20  aa 01   00   9b b8 dd a8 65 4c   0d 10 04  b3 00  74 02      d0
04 3e 25 02 01 00 00   9b b8 dd a8 65 4c   19 02 01 06 15   16  95 fe  50 20  aa 01   01   9b b8 dd a8 65 4c   0d 10 04  b2 00  74 02      c9
04 3e 25 02 01 00 00   9b b8 dd a8 65 4c   19 02 01 06 15   16  95 fe  50 20  aa 01   02   9b b8 dd a8 65 4c   0d 10 04  b3 00  74 02      c9
04 3e 25 02 01 00 00   9b b8 dd a8 65 4c   19 02 01 06 15   16  95 fe  50 20  aa 01   03   9b b8 dd a8 65 4c   0d 10 04  b2 00  74 02      c8
04 3e 23 02 01 00 00   9b b8 dd a8 65 4c   17 02 01 06 13   16  95 fe  50 20  aa 01   04   9b b8 dd a8 65 4c   06 10 02         74 02      cb
04 3e 25 02 01 00 00   9b b8 dd a8 65 4c   19 02 01 06 15   16  95 fe  50 20  aa 01   05   9b b8 dd a8 65 4c   0d 10 04  b2 00  74 02      cb
04 3e 25 02 01 00 00   9b b8 dd a8 65 4c   19 02 01 06 15   16  95 fe  50 20  aa 01   06   9b b8 dd a8 65 4c   0d 10 04  b3 00  74 02      c9
04 3e 23 02 01 00 00   9b b8 dd a8 65 4c   17 02 01 06 13   16  95 fe  50 20  aa 01   07   9b b8 dd a8 65 4c   04 10 02  b2 00             c9
04 3e 22 02 01 00 00   9b b8 dd a8 65 4c   16 02 01 06 12   16  95 fe  50 20  aa 01   08   9b b8 dd a8 65 4c   0a 10 01               48   cb
-----------------------------------------------------------------------------------------------------------------------------------------------
```

## Converting hex to decimals
Next step is to convert some of the hex numbers to decimals. The following parameters are in the table below converted to decimals, to make it human readable:

- Len
- Frame cnt
- Temp
- Hum
- Batt
- RSSI

```
-----------------------------------------------------------------------------------------------------------------------------------------------
      Len             --------MAC-------   Len         Len  AD  Xiaomi Frame Device  Frame ------MAC--------   -----PAYLOAD-------------  RSSI
                                                           type  UUID   ctrl  type    cnt                      Type  Len Temp   Hum   Batt
-----------------------------------------------------------------------------------------------------------------------------------------------
04 3e 37 02 01 00 00   9b b8 dd a8 65 4c   25 02 01 06 21   16  95 fe  50 20  aa 01   254  9b b8 dd a8 65 4c   0d 10  4  178    629       -53
04 3e 35 02 01 00 00   9b b8 dd a8 65 4c   23 02 01 06 19   16  95 fe  50 20  aa 01   255  9b b8 dd a8 65 4c   04 10  2  177              -48
04 3e 37 02 01 00 00   9b b8 dd a8 65 4c   25 02 01 06 21   16  95 fe  50 20  aa 01     0  9b b8 dd a8 65 4c   0d 10  4  179    628       -48
04 3e 37 02 01 00 00   9b b8 dd a8 65 4c   25 02 01 06 21   16  95 fe  50 20  aa 01     1  9b b8 dd a8 65 4c   0d 10  4  178    628       -55
04 3e 37 02 01 00 00   9b b8 dd a8 65 4c   25 02 01 06 21   16  95 fe  50 20  aa 01     2  9b b8 dd a8 65 4c   0d 10  4  179    628       -55
04 3e 37 02 01 00 00   9b b8 dd a8 65 4c   25 02 01 06 21   16  95 fe  50 20  aa 01     3  9b b8 dd a8 65 4c   0d 10  4  179    628       -56
04 3e 35 02 01 00 00   9b b8 dd a8 65 4c   23 02 01 06 19   16  95 fe  50 20  aa 01     4  9b b8 dd a8 65 4c   06 10  2         628       -53
04 3e 37 02 01 00 00   9b b8 dd a8 65 4c   25 02 01 06 21   16  95 fe  50 20  aa 01     5  9b b8 dd a8 65 4c   0d 10  4  178    628       -53
04 3e 37 02 01 00 00   9b b8 dd a8 65 4c   25 02 01 06 21   16  95 fe  50 20  aa 01     6  9b b8 dd a8 65 4c   0d 10  4  179    628       -55
04 3e 35 02 01 00 00   9b b8 dd a8 65 4c   23 02 01 06 19   16  95 fe  50 20  aa 01     7  9b b8 dd a8 65 4c   04 10  2  178              -55
04 3e 34 02 01 00 00   9b b8 dd a8 65 4c   22 02 01 06 18   16  95 fe  50 20  aa 01     8  9b b8 dd a8 65 4c   0a 10  1              72   -53
-----------------------------------------------------------------------------------------------------------------------------------------------
```

## Explanation of the data

- Len = Length of data packet (given at 4 positions, length is from that position till the end of the message)
- MAC = MAC address in reversed order (per 2 characters)
- AD type + Xiaomi UUID = Indicator for the Xiaomi MiBeacon protocol, has to be `16 95 fe`
- Device type = Indicator for the device type, as used in `const.py`
- Frame cnt = Index number of the message
- Type = Type of measurement
  - 0d 10 = temperature + humidity
  - 04 10 = temperature
  - 06 10 = humidity
  - 0a 10 = battery
- Temp = Temperature in Celsius (divide by 10) (e.g. b2 00 --> 00 B2 (hex) --> 178 (decimal) --> 17.8 °C)
- Hum = Humidity in (divide by 10) (e.g. 75 02 --> 0275 (hex) --> 629 (decimal) --> 62.9 %)
- Batt = Battery in %
