# Current proven B versus Lineage 24 candidate

| Property | Proven booting B reference | Lineage 24 source candidate |
|---|---|---|
| Android / SDK | Android 15 / 35 | Android 17 / 37 |
| framework release family | BP1A-generation with diagnostic edits | CP2A, native Lineage 24 |
| system | 665391104 bytes | not built; GSI folds product/system_ext into system |
| system_ext | 366891008 bytes | no separate GSI image |
| product | 337686528 bytes | no separate GSI image |
| filesystem | EROFS parity image | ext4 default; EROFS supported/configurable |
| APEX generation | API-35 modules, mixed shared-data state | API-37/C modules |
| LineageSettings expected DB | diagnostic shim declares 24 (native SDK35 was 21) | native 24; shim disappears |
| Contacts expected DB | 1701 in SDK35 source | 1800; same as A16, so no A16→17 change |
| CallLog expected DB | 12 | 14; A16 is already 14 |
| MMS/SMS expected DB | 69 | 73 (A16 is 70) |
| Telephony/APN expected DB | `73<<16` | `78<<16` (A16 is `74<<16`) |
| Settings state | 226 | 236 (A16 is 231) |
| MediaProvider | 1506 | 1700 (A16 is 1602) |
| Launcher schema | old API-35 generation | 32 or 34 by flag; same as A16 source |
| accounts CE/DE | 10 / 3 | 10 / 3 |
| permission model | Android 15 generation | API-37 local-network/location-button upgrades; access state latest 19/20 by flags |
| PackageManager state | packages last reconciled by mixed A16/B15 systems | API-37 scan and permission generation; rollback behavior unproven |
| vendor expectation | FCM 8 / VNDK 34 works after old fixes | FCM 8 / VNDK 34 explicitly retained |
| SELinux generation | platform API35 plus vendor 34 mapping | platform 202604 plus retained vendor 34 mapping |
| VINTF framework level | Android 15 generation | level 202604 current, retains level 8 |
| ART/runtime | API35 ART | API37 ART; dalvik-cache/APEX data may be regenerated/migrated |

## Old hacks that disappear

- DB24 LineageSettings constant shim: native version is already 24.
- Android-15→16 property parity edit: Android 17 emits its own coherent identity.
- selective Google config removal: official target is vanilla/no-GApps.
- `ro.adb.secure=0`: not a production setting; any bring-up debug variant must
  be explicit and temporary.

## New incompatibilities

**PROVEN:** Android17 telephony, settings and media state versions exceed A16.
**INFERRED:** API37 permission/APEX/package state and ART caches add rollback
risk. **UNKNOWN:** exact vendor extension failures and image sizes.
