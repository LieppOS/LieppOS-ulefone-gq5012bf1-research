# Slot Control Analysis

Date: 2026-09-24

## Summary

The device contains A/B-style partition infrastructure, but standard fastboot A/B slot management is unavailable.

## Verified Results

### Fastboot

Command:

fastboot getvar current-slot

Result:

Device does not report slot.

Command:

fastboot set_active b

Result:

fastboot: error: Device does not support slots

### Android Runtime

Command:

getprop ro.boot.slot_suffix

Result:

_a

The phone booted successfully into slot A.

### Boot State

Verified:

- sys.boot_completed = 1
- system_server running
- Android framework operational

### Conclusion

The device uses A/B-like partition structures but does not expose standard fastboot slot switching.

Slot selection is likely controlled through MediaTek-specific mechanisms.

Possible locations:

- boot_control HAL
- misc partition metadata
- MediaTek LK bootloader logic
- vendor boot configuration
- bootloader environment

## Status

PARTIAL

## Completed

- Confirmed runtime slot
- Confirmed fastboot slot commands unavailable
- Confirmed safe return to Android
- Confirmed AVB/dm-verity mappings active

## TODO

- Dump misc partition
- Analyze boot_control HAL
- Search LK binaries for slot handling
- Inspect boot/vendor_boot/init_boot selection
- Determine safe B slot activation method

