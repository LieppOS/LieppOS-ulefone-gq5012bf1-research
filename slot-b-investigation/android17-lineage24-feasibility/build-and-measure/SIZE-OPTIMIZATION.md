# Measured size optimization

The fixed B extents are short by 154,591,232 bytes in aggregate. System is
short 137,072,640 bytes, product 18,055,168 bytes, and measured system_ext has
only 536,576 bytes spare. The following classifications apply to a proper
Ulefone device product, not to ad-hoc deletion from `system.img`.

## Largest contributors

| Contributor | Logical bytes | Partition | Classification | Action |
|---|---:|---|---|---|
| WebView bundle | 267391201 | product | MUST_KEEP | Core WebView provider; retain or source a valid release-matched smaller provider |
| system APEX set | 326856704 | system | MUST_KEEP | Do not strip core modular runtime components |
| `com.android.virt.apex` | 65519616 | system | INVESTIGATE | Omit if Ulefone exposes no AVF/pKVM feature and product dependencies permit |
| system framework | 206986890 | system | MUST_KEEP | Core framework/runtime |
| 32-bit `/system/lib` | 105831084 | system | INVESTIGATE | MTK vendor and 32-bit app clients may require it; require full ABI/process audit |
| fonts | 85785836 | system | INVESTIGATE | Preserve fallback, emoji, accessibility and required locales; measured CJK pair is 58628432 bytes |
| VNDK 31/32/33 APEX | 131538944 | system_ext | PROBABLY_REMOVABLE | Device contract is VNDK/FCM 34; prove with VINTF and ELF audit; keep VNDK 34 |
| VNDK 34 APEX | 42340352 | system_ext | MUST_KEEP | Current vendor compatibility payload |
| SystemUI / Settings | 110030941 / 95198516 | system_ext | MUST_KEEP | Core UI and settings |
| ThemePicker | 50396090 | system_ext | PROBABLY_REMOVABLE | Optional customization for first device proof |
| Vim runtime + binary | 22849858 | system_ext | SAFE_TO_REMOVE | Developer shell convenience, not Android boot functionality |
| Seedvault | 24555756 | system_ext | PROBABLY_REMOVABLE | Optional backup application |
| Lineage SetupWizard | 13095924 | system_ext | INVESTIGATE | Provisioning/permission flow must be replaced coherently if omitted |
| Updater | 5917064 | system_ext | SAFE_TO_REMOVE | Safe for non-OTA bring-up product; restore when OTA exists |
| GSI userdebug SELinux policy | 3441656 | system_ext | SAFE_TO_REMOVE | Replace with proper device policy; compliance-GSI debug policy is not production policy |
| product media/audio | 39444027 | product | PROBABLY_REMOVABLE | Keep functional defaults, remove duplicate ringtone/alarm collections |
| LatinIME | 66272606 | product | KEEP | A keyboard is required for usable setup; replacement/relocation needs explicit choice |

## Optional Lineage/application payload

| Package | Payload bytes | Classification |
|---|---:|---|
| Backgrounds | 7915931 | SAFE_TO_REMOVE |
| Camelot | 2516200 | SAFE_TO_REMOVE |
| Etar | 7659682 | PROBABLY_REMOVABLE |
| Twelve | 8013888 | PROBABLY_REMOVABLE |
| Aperture | 8382679 | INVESTIGATE—camera app useful, HAL independent |
| Glimpse | 5899540 | PROBABLY_REMOVABLE |
| Jelly | 3355195 | PROBABLY_REMOVABLE |
| Recorder | 2587814 | PROBABLY_REMOVABLE |
| DeskClock | 6622989 | KEEP for normal product; optional for first framework proof |
| AudioFX | 1307627 | PROBABLY_REMOVABLE |
| Profiles | 104657 | KEEP; negligible and Lineage-integrated |
| LineageParts | 19601086 | KEEP | Core Lineage settings surface |
| LineageSettingsProvider | 79853 | MUST_KEEP | Native DB24 provider required by Lineage framework |

Removing Backgrounds, Camelot and Etar alone has 18,093,813 uncompressed bytes,
approximately the product deficit, but production needs headroom; target at least
35 MiB product reduction through optional apps plus media trimming.

## Debug/test/generic content

- Switch the final target to `user` after bring-up; userdebug tools include
  simpleperf, layer tracing, tcpdump, strace, bpftool and debug policy.
- Remove universal-GSI virtual HAL/test packages that are not selected by the
  Ulefone VINTF contract.
- Retain userdebug for the first split host build only so failures remain
  diagnosable, but use explicit package exclusions rather than file surgery.
- Do not disable dexpreopt merely to move cost to `/data`. Investigate compiler
  filters only after boot and performance requirements are defined.
- Do not delete 32-bit payload as “duplicate”; current MTK closure must prove it
  unused first.

## Coherent fit strategy

1. Remove VNDK 31–33 after host VINTF/ELF proof, creating about 131.5 MB logical
   system_ext capacity and preserving VNDK 34.
2. Reduce system by at least 153 MB to leave 16 MB headroom: first assess AVF,
   generic-GSI packages, userdebug tools and locale/font scope.
3. Reduce product by at least 35 MB to leave 16 MB headroom using optional apps
   and duplicate media—not WebView or core providers.
4. Rebuild all partitions independently with exact metadata and AVB. Do not
   infer final sizes by subtracting APK bytes.
