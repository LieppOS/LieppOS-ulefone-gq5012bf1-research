# Slot-B missing MTK insmod cfg and vendor_boot watchdog audit

## Correction to previous watchdog loader classification

The previous `mtk-watchdog-loader-chain-audit` reported
`MTK_WDT_LOADER_HIT=1`.

That did not prove that second-stage `/vendor/bin/init.insmod.sh` loads
`mtk_wdt`.

The second-stage module inventory does not contain the four relevant modules
under the inspected `/vendor` / `system_dlkm` paths, while the stock module
database classifies:

- `mtk_wdt.ko`
- `mrdump.ko`
- `aee_hangdet.ko`
- `monitor_hang.ko`

as `vendor_boot_platform`.

The actual first-stage vendor_boot ramdisk/module path is therefore the
relevant path for watchdog handoff analysis.

## Concrete Slot-B second-stage difference

Working A has:

`/vendor/etc/init.insmod.mt6878.cfg`

Current B mounted vendor has it:

`False`

B cfg absent:

`True`

The exact working-A cfg executes:

1. `modprobe|*`
2. `setprop|vendor.all.modules.ready`

B's identical `init.mtkgki.rc` runs in `early-init`, sets
`vendor.all.modules.ready=0`, and starts `insmod_sh`.

The identical `init.insmod.sh` exits with code 2 when its cfg does not exist.

B's `init.mt6878.rc` separately contains:

fallback set ready=1:

`True`

later wait for ready=1:

`True`

Classification:

B_MISSING_INSMOD_CFG_IS_BOOT_CRITICAL: B early-init explicitly sets vendor.all.modules.ready=0, insmod_sh exits 2 because its cfg is absent, and init.mt6878.rc later waits for vendor.all.modules.ready=1. Exact action ordering determines whether the earlier fallback setprop=1 survives or is overwritten by the GKI setprop=0.

The remaining critical point is exact action/parse ordering between the
`init.mt6878.rc` fallback setter and `init.mtkgki.rc` setter/start action.

If the fallback 1 executes first and mtkgki subsequently writes 0, the failed
loader leaves the property stuck at 0 and the later `wait_for_prop` becomes a
hard second-stage init barrier.

## vendor_boot first-stage watchdog comparison

All four relevant module binaries A/B identical:

`True`

Relevant first-stage modules.load ordering A/B identical:

`True`

Classification:

VENDORBOOT_WATCHDOG_PATH_A_B_STATIC_EQUIVALENT: all four first-stage watchdog/AEE module binaries and their relevant modules.load ordering are identical across A/B. The prior second-stage MTK_WDT_LOADER_HIT classification was based on database/search evidence and is corrected here.

## Implication

The missing B `init.insmod.mt6878.cfg` is a much more concrete Slot-B-specific
userspace/package defect than generic watchdog starvation.

No Slot-B boot should be needed until the property-action ordering is fully
resolved statically.

## Safety

- phone remained booted on successful Slot A
- no partition writes
- no slot changes
- vendor_boot_a/b read only
- temporary host copies only
- no module insertion/removal
- no sysctl writes
