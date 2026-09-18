# Slot-B missing init.insmod.mt6878.cfg boot-blocker closure

## Classification

`SLOT_B_INSMOD_CFG_BOOT_BLOCKER_PROVEN_STATICALLY`

## Proven B-specific difference

Current B does not contain:

`/vendor/etc/init.insmod.mt6878.cfg`

Working A does contain the file.

## Effective property sequence

The normal B init chain contains:

1. `init.mt6878.rc` early-init -> `vendor.all.modules.ready=1`
2. imported `init.mtkgki.rc` early-init -> `vendor.all.modules.ready=0`
3. `start insmod_sh`
4. `init.insmod.sh` expects `/vendor/etc/init.insmod.${ro.hardware}.cfg`
5. with `ro.hardware=mt6878`, current B lacks that cfg
6. the script exits through its missing-config failure path
7. `init.mt6878.rc` later waits for `vendor.all.modules.ready=1` during post-fs-data.

## Ordering

Local Lineage init documentation was inspected for import parsing and action execution order.

Imports deferred after parent parse: `True`

Actions execute in parse order: `True`

## Packaging search

Source-tree search hit count: `20`

Device/proprietary manifest hit count: `6`

See the generated evidence files for exact paths.

## Investigation consequence

This defect must be repaired before another Slot-B boot is useful.

The already-completed vendor_boot/watchdog comparison is not repeated here.

## Safety

- Slot A remained active
- no partition writes
- no slot changes
- no module load/unload
- no sysctl writes
