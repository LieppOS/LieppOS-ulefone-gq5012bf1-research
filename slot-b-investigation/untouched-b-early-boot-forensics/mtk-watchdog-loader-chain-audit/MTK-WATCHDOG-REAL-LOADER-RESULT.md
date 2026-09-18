# MTK watchdog real module-loader chain audit

## Why this audit was needed

The preceding module-handoff audit established that `mtk_wdt`, `mrdump`,
`aee_hangdet`, and `monitor_hang` are loadable modules.

However its reported module-load order was `NONE` because it searched generic
`modules.load` files and direct init `insmod` commands.

The actual MediaTek vendor init path is:

`service insmod_sh /vendor/bin/init.insmod.sh /vendor/etc/init.insmod.${ro.hardware}.cfg`

This audit therefore follows the actual MTK loader implementation and its
tables.

## Slot parity

vendor_boot A/B byte-identical:

`False`

Important live-A vs static-B loader files byte-identical:

`True`

Detected hardware:

`mt6878`

insmod_sh trigger:

`on early-init`

Early-init trigger:

`True`

## Loader membership

mtk_wdt resolved in loader evidence:

`True`

mrdump resolved:

`True`

aee_hangdet resolved:

`True`

monitor_hang resolved:

`True`

## Watchdog handoff classification

MTK_WDT_EARLY_LOADER_PATH_PROVEN: exact A/B loader equivalence remains incomplete.

The important distinction remains:

- after `mtk_wdt` has registered, generic watchdog-core feeding already closes
  normal userspace takeover starvation;
- before registration, a bootloader-enabled watchdog was previously a
  theoretical reset path;
- if A/B vendor_boot and actual MTK early loader chain are identical, that
  pre-registration differential becomes substantially less plausible.

## Immediate panic path

IMMEDIATE_OOPS_REBOOT_POLICY_PROVEN: identical A/B kernel has CONFIG_PANIC_ON_OOPS=y and CONFIG_PANIC_TIMEOUT=-1; B also explicitly writes panic_on_oops=1.

This is a real kernel-level reset authority from very early boot.

It does not require the Android critical-service crash counter.

## Next priority

If the MTK early loader path is now proven equivalent across A/B, prioritize
finding evidence for:

1. kernel oops/die before reset;
2. `aee_hangdet` invoking its reset path;
3. `monitor_hang` invoking `watchdog_reboot_check`;
4. MRDUMP/AEE persistent breadcrumbs that survive B -> A fallback.

## Safety

Read-only phone investigation only.

No watchdog device opened.

No module loaded/unloaded.

No sysctl changed.

No slot change.

No partition write.
