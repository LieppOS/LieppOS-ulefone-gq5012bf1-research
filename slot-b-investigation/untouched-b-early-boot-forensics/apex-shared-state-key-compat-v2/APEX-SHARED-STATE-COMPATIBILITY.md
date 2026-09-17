# Slot-B shared APEX state compatibility — corrected audit

This is a read-only device investigation.

The audit was run while the phone was booted and boot-complete on Slot A.

## Result

`NO_ACTIVE_DATA_APEX_BUT_SESSION_STATE_PRESENT: there are no active data APEX replacements, but staged/session metadata exists and should be interpreted before fully closing the shared-state branch.`

## Counts

- active shared `/data/apex/active` packages:
  `0`
- current-B preinstalled APEX/CAPEX packages inventoried:
  `0`
- embedded APEX-key matches:
  `0`
- embedded APEX-key mismatches:
  `0`
- active packages lacking a current-B package match:
  `0`
- unreadable embedded-key comparisons:
  `0`
- visible `/data/apex/sessions` or `/metadata/apex` entries:
  `4`

## Method correction

An earlier attempted audit passed `su -c` to `adb shell` as separate adb
arguments. KernelSU therefore received `-c` without its command, producing:

`Argument to option 'c' missing`

That attempt stopped during preflight and made no device changes.

This corrected audit passes the complete quoted `su -c <command>` expression
as one remote adb-shell command and verifies UID 0 before collecting evidence.

## Safety

No partition was written.

No APEX package, APEX session, decompression cache, `/data`, `/metadata`,
boot-control state, slot state, AVB metadata, or filesystem content was
modified.

The only writes performed by the audit are host-side research evidence files
inside this repository.
