# Android 17 database generations

Source constants were checked in the exact Lineage 24 checkout and compared
with the previously captured official Lineage 23.2 Android 16 reference and the
local Lineage 22.2 Android 15 source. No device database was opened or changed.

| Provider/state | Android 15 / SDK35 source | Proven bootable B behavior | Healthy A / Android 16 | Built Android 17 source | Direction |
|---|---:|---:|---:|---:|---|
| LineageSettings | 21 | diagnostic constant shim reports 24 | 24 | 24 | native A16/A17 parity; remove old shim |
| Contacts | 1701 | API35 provider generation | 1800 | 1800 | A16→A17 unchanged |
| CallLog | 12 | API35 provider generation | 14 | 14 | A16→A17 unchanged |
| MMS/SMS | 69 | API35 provider generation | 70 | 73 | forward migration; unsafe return |
| Telephony/APN | `73 << 16` | API35 provider generation | `74 << 16` | `78 << 16` | forward migration; downgrade may rebuild/delete DB |
| Settings state | 226 | API35 provider generation | 231 | 236 | A16 downgrade has destructive recreation path |
| MediaProvider | 1506 | API35 provider generation | 1602 | 1700 | forward migration; reverse safety unproven |

Android 17 exact source locations:

```text
lineage-sdk/.../LineageDatabaseHelper.java: DATABASE_VERSION = 24
ContactsDatabaseHelper.java: DATABASE_VERSION = 1800
CallLogDatabaseHelper.java: DATABASE_VERSION = 14
MmsSmsDatabaseHelper.java: DATABASE_VERSION = 73
TelephonyProvider.java: DATABASE_VERSION = 78 << 16
SettingsProvider.java: SETTINGS_VERSION = 236
MediaProvider DatabaseHelper.java: VERSION_C = 1700; VERSION_LATEST = VERSION_C
```

The built image includes the native LineageSettingsProvider under
`/system/system_ext/priv-app/LineageSettingsProvider`; its measured bundle is
79,853 bytes. The Android-15 DB24 constant shim must not be ported.

## Safety conclusion

`SHARED_USERDATA_DIRECT_TEST_SAFE=0` remains unchanged. Contacts and
LineageSettings happen to match A16, but Settings, telephony/SMS and Media move
forward. A direct Android17 boot could update shared state before
`sys.boot_completed`, and Android16 does not provide a safe general reverse
migration. Future GSI testing must use validated DSU with separate guest
userdata or stop.
