# ST21NFC evidence capture commands

These commands are intended for the rooted stock/research device.

## Framework features

```bash
adb shell 'pm list features | grep -i nfc'
```

## NFC framework state and routing

```bash
adb shell 'dumpsys nfc'
```

Save a clean snapshot:

```bash
adb shell 'dumpsys nfc' > nfc-dumpsys.txt
```

## Secure Element services

```bash
adb shell 'service list | grep -iE "secure|nfc|ese"'
```

Try framework/OMAPI state:

```bash
adb shell 'dumpsys secure_element'
```

If that service name is not dumpable:

```bash
adb shell 'dumpsys | grep -iE "secure.?element|omapi"'
```

## Relevant vendor files

```bash
adb shell 'su -c "cat /vendor/etc/libnfc-hal-st.conf"'
adb shell 'su -c "cat /vendor/etc/libnfc-nci.conf"'
adb shell 'su -c "cat /vendor/etc/st21nfc_conf.txt"'
```

## Locate NFC-related files

```bash
adb shell 'su -c "find /vendor/etc /system/etc /product/etc /odm/etc -type f \\( -iname \"*nfc*\" -o -iname \"*libnfc*\" -o -iname \"*st21*\" \\) 2>/dev/null"'
```

## Search routing / SWP / SE configuration

```bash
adb shell 'su -c "grep -RniE \"UICC|ESE|SWP|NFCEE|ROUTE|FELICA|MIFARE|HCE\" /vendor/etc/libnfc* /vendor/etc/st21nfc_conf.txt 2>/dev/null"'
```

## Runtime logs

Clear logs immediately before toggling NFC off/on:

```bash
adb logcat -c
adb shell svc nfc disable
sleep 2
adb shell svc nfc enable
sleep 3
adb logcat -d | grep -iE 'nfc|st21|nfcee|swp|uicc|ese|hci' > nfc-startup-log.txt
```

If `svc nfc` is unavailable, toggle NFC from Settings after `adb logcat -c`.

With root, also inspect kernel logs:

```bash
adb shell 'su -c "dmesg | grep -iE \\\"nfc|st21|nfcee|swp|uicc|ese|hci\\\" | tail -500"'
```

## NFC storage / debug paths

```bash
adb shell 'su -c "find /data/nfc /sys/kernel/debug /proc -iname \"*nfc*\" -o -iname \"*st21*\" 2>/dev/null | head -300"'
```

## Key capture target

The highest-priority missing evidence is the NCI NFCEE discovery sequence. Search startup logs for:

```text
NFCEE_DISCOVER
NFCEE_DISCOVER_RSP
NFCEE_DISCOVER_NTF
EE_DISCOVER
SWP
UICC
HCI
```

Once captured, record for each endpoint:

```text
NFCEE ID
status
supported protocols
interface type
power/link state
associated SIM/eSE/host service
```
