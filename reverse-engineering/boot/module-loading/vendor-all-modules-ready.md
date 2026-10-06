# `vendor.all.modules.ready` — exact semantics (stock GQ5012BF1)

## One line

`vendor.all.modules.ready` is set to `1` by the `insmod_sh` service (`/vendor/bin/init.insmod.sh`,
SELinux domain `init_insmod_sh`) **after both `modprobe` passes of
`/vendor/etc/init.insmod.mt6878.cfg` have returned** (system_dlkm 60 then vendor_dlkm 195
names). Its only consumer is `wait_for_prop vendor.all.modules.ready 1` at the start of
`init.mt6878.rc`'s `on post-fs-data` action, which blocks init's action queue with no timeout.

## Writers (all stock)

| order | where | value | domain | when |
|---|---|---|---|---|
| 1 | `/vendor/etc/init/hw/init.mt6878.rc:25` (`on early-init`) | `1` | vendor_init (setprop from a /vendor rc) | first early-init vendor action; comment: "initialize … to 1 here to prevent NOT GKI project blocked" |
| 2 | `/vendor/etc/init/hw/init.mtkgki.rc:9` (`on early-init`, imported by `init.project.rc`, itself imported by `init.mt6878.rc`) | `0` | vendor_init | immediately after (imports parse after the importing file) |
| 3 | `/vendor/bin/init.insmod.sh` executing cfg line `setprop|vendor.all.modules.ready` | `1` | init_insmod_sh | after `modprobe -a -d /system_dlkm/lib/modules …` and `modprobe -a -d /vendor/lib/modules …` both return; `setprop` retried while it exits non-zero, at most 129 attempts |
| alt | `meta_init.rc:74` / `factory_init.rc:82` | `1` | vendor_init | META / factory init trees; both also import `init.mtkgki.rc` (via `*_init.project.rc`), so the same 1→0→1 sequence applies |

SELinux: property context `vendor.all.modules.ready u:object_r:vendor_mtk_device_prop:s0`
(exact-name entry); `set` allowed only to `init_insmod_sh` and `vendor_init`. No native
binary or library in vendor/system/system_ext contains the property name.

## Readers

| consumer | trigger | effect |
|---|---|---|
| `init.mt6878.rc:180` | `on post-fs-data` | `wait_for_prop vendor.all.modules.ready 1` then bootprof `modprobe: Load_Module_DONE` |
| `meta_init.rc:206`, `factory_init.rc:447` | `on post-fs-data` in those trees | same |

No `on property:vendor.all.modules.ready=…` trigger, service, HAL, or binary reads it.

## What it covers — and what it does not

Covered (insmod_sh, sequential, completes before `1`):
- 60 `system_dlkm` GKI modules; 195 `vendor_dlkm` `modules.load` names (191 new insertions,
  plus their hard/soft dependencies).

Not covered:
- first-stage `vendor_boot` modules (already loaded before second stage starts);
- `init.touch.rc` `exec_background` modprobe (touch: `tui-common`, `focaltech_touch_spi_ft3680`,
  `hynitron`) — parallel, unwaited; it can still be running when the property flips;
- property-triggered `gps_pwr`, `gps_scp`, `bt_drv_6878` (EEXIST), `on boot` `msync2_*`, pstore_blk.

The property means "loader finished", **not** "every module succeeded": `init.insmod.sh`
ignores modprobe exit codes. It cares about no specific filenames — only that the script
reaches its second cfg line.

## Timing (stock, `live-loader-state.txt` bootprof)

| t (ms since boot) | event |
|---|---|
| ≈1780 | last first-stage initcall bookmarked (`microarray_fp_tee`) — first stage ends ≈1.9 s (`ro.boottime.init.modules`=1389 ms) |
| 3745 | `insmod_sh` started (`ro.boottime.insmod_sh=3745163769` ns) |
| 3749 | bootprof `modprobe: Load_Module_START` |
| 4101–6117 | vendor-pass initcalls (pid 493), touch modprobe (pid 495) interleaved at 4279/4641 |
| (>6117) | `setprop vendor.all.modules.ready 1`; `init.svc.insmod_sh=stopped` |
| 11245 | `post-fs-data` reaches the wait → already 1 → `modprobe: Load_Module_DONE` |

So on stock the barrier is ~5 s slack: loading finishes long before `/data` is mounted.

## Failure modes that leave it at 0 (boot stalls at post-fs-data, no timeout)

- `/vendor/etc/init.insmod.${ro.hardware}.cfg` missing → script `exit 2` (historical slot-B blocker);
- script missing / not labeled `init_insmod_sh_exec` → service cannot exec;
- a `modprobe` that never returns (module init hang);
- `setprop` denied 129 times (policy lacking `set_prop(init_insmod_sh, vendor_mtk_device_prop)`);
- `ro.hardware` ≠ `mt6878` (cfg name derives from it).
