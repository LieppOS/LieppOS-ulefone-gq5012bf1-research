# Slot B insecure-ADB controlled boot

## Candidate

System SHA256:

68b4639959dd189fcc6e6603742a4b4ef57f6106d444da48ef884031a69d1a99

vbmeta_system first-4096 SHA256:

9adb5fb2d3b2375d08884bdb1721097fa26b96f6cbb708408cec47b7862ddfc9

system root digest:

aa57361b018f99c0985c15b2e29934192849adeb

## Diagnostic delta

ro.adb.secure=1 -> ro.adb.secure=0

## Runtime

Authorized ADB was acquired on real Slot B.

sys.boot_completed after the additional observation interval:



## Shared metadata key

Before:
1eac61edfe777d0c6fa2f2d4f62ec892b6a031b90cb7064e4d6581c0a944fbca

After:
1eac61edfe777d0c6fa2f2d4f62ec892b6a031b90cb7064e4d6581c0a944fbca

Expected:
1eac61edfe777d0c6fa2f2d4f62ec892b6a031b90cb7064e4d6581c0a944fbca

Unchanged:
YES

## Persistent Slot-B candidate

system_b:
68b4639959dd189fcc6e6603742a4b4ef57f6106d444da48ef884031a69d1a99

vbmeta_system_b first 4096:
9adb5fb2d3b2375d08884bdb1721097fa26b96f6cbb708408cec47b7862ddfc9

## Safety

- Slot A partitions were not flashed.
- system_b and vbmeta_system_b were the only intended persistent test writes.
- userdata was not formatted.
- metadata was not formatted.
- super metadata was not resized.
- no factory reset was performed.
- phone was returned to fully booted Slot A.
