# Ulefone Armor 29 Pro Thermal (GQ5012BF1) — debug, pstore and rescue report

Consolidated findings from **90 artifact sets / 12 GB** left in `~/ulefone-*` by
earlier agent sessions. Everything here was produced on **2026-08-29** (one
continuous session, 02:43 → 00:14) plus a single `vbmeta` artifact on 08-30.

This document is a synthesis of what those artifacts *prove*. Statements are
labelled:

- **[EVIDENCE]** — read directly out of a captured artifact
- **[INFERENCE]** — deduced from artifacts, consistent but not directly observed
- **[UNPROVEN]** — attempted, no confirming evidence found

---

## 1. What was being investigated

A LieppOS/GSI system image was put on the device and it did not complete boot.
The device has **no usable serial console**, so the entire session was an effort
to obtain *any* log from a boot that never reaches ADB, and then to recover a
flashable, verified `vendor_boot`.

Three parallel workstreams are visible in the artifacts:

| # | Workstream | Directories |
|---|---|---|
| 1 | **vendor_boot rescue/repack** — produce a flashable 64 MiB image preserving the stock ramdisk + DTB | `ulefone-rescue-*` (17), `ulefone-hybrid-*` (9), `ulefone-final-preflash-verify` |
| 2 | **Boot-hang instrumentation** — inject a diagnostic payload as PID 1 and persist its output across reboot | `ulefone-initboot-watchdog-*` (19), `ulefone-v*-raw-capture` (9), `ulefone-early-acm-*` (3) |
| 3 | **SELinux policy forensics** — determine the active policy and why the boot stalls | `ulefone-*-policy-test` (6), `ulefone-active-policy-audit`, `ulefone-v7-debug-policy-audit` |

---

## 2. Device facts established

**[EVIDENCE]** `/proc/bootconfig`, captured on-device (`ulefone-v8-raw-capture/v8-readable.txt`):

```text
androidboot.hardware          = mt6878
androidboot.boot_devices      = bootdevice, soc/112b0000.ufshci, 112b0000.ufshci
androidboot.vbmeta.device     = PARTUUID=00000009-39c2-4488-9bb0-00cb43c9ccd4
androidboot.vbmeta.avb_version= 1.2
androidboot.vbmeta.device_state = unlocked
androidboot.veritymode        = disabled       (managed = yes)
androidboot.verifiedbootstate = orange
androidboot.slot_suffix       = _a
androidboot.serialno          = 5012BF3010001335
androidboot.vba_regional      = EEA
androidboot.bootreason        = reboot
androidboot.ddr_size          = 17179869184    (16 GiB)
```

**[EVIDENCE]** `/proc/cmdline` (identical across V3/V4/V8 captures) — the two
lines that governed the whole debugging effort:

```text
console=ttynull  …  mtk_printk_ctrl.disable_uart=1
ramoops.mem_address=0x48090000 ramoops.mem_size=0xe0000
ramoops.pmsg_size=0x80000 ramoops.console_size=0x40000
```

- `console=ttynull` + `mtk_printk_ctrl.disable_uart=1` → **no serial console at
  all**. This is why every diagnostic path had to go through RAM/pstore.
- The ramoops region is only **0xe0000 (896 KiB)** total, of which
  **console = 256 KiB** and **pmsg = 512 KiB**.

Storage/panel/DRAM identifiers from the same cmdline: UFS `MT512GBCAV8U31`,
`flash_type=12`, panel `yft_vtdr6115_fhdp_dsi_cmd_hx_dphy_667_ky_lcm_drv`.

**[EVIDENCE]** BROM/preloader state (`ulefone-mtk-dump/mtk-read.log`):

```text
CPU: MT6878 (Dimensity 7300)   HW code: 0x1375   Target config: 0x0
SBC enabled: False   SLA enabled: False   DAA enabled: False   SWJTAG enabled: False
```

**This device has completely open BROM access** — no secure boot chain, no
serial-link authentication, no download-agent authentication. That is what made
every offline partition dump and restore in this session possible, and it is the
single most valuable recovery capability the device has.

---

## 3. Root cause of the boot stall — SELinux policy hash mismatch

**[EVIDENCE]** `ulefone-active-policy-audit/exact-policy-inputs/`:

```text
gsi-plat_sepolicy_and_mapping.sha256        3617114ed6d5fde858b6161e1bc19f1771e388611da305735a1d0e2e46ef199e
vendor-expected-plat.sha256                 53f5f99e123b79fc249c70188463f03249b0447a847d45d11fcebedae91b056b   ← MISMATCH

stock-system_ext_sepolicy_and_mapping.sha256 80c66fa92aa34a89ea5e6936f842ff5669af5b2fceb35a52344d4b44f5034897
vendor-expected-system_ext.sha256            80c66fa92aa34a89ea5e6936f842ff5669af5b2fceb35a52344d4b44f5034897   ← match
```

The vendor partition ships `precompiled_sepolicy` together with the SHA-256 of
the **platform** policy it was compiled against. The GSI/LieppOS `system`
image carries a *different* `plat_sepolicy.cil`, so that hash no longer matches
while `system_ext` still does.

**[INFERENCE]** Consequence, per standard AOSP `init` behaviour: the precompiled
vendor policy is rejected and `init` must **compile the full policy at runtime**
from CIL. The audit directory contains exactly the input set init would use:

```text
exact-runtime-policy-audit/
  plat_policy.cil            3.1 MB      vendor_policy.cil          1.2 MB
  plat_pub_versioned.cil     972 KB      system_ext_policy.cil      311 KB
  plat_mapping.cil           156 KB      system_ext_mapping.cil     6.8 KB
  plat_compat.cil / system_ext_compat.cil / genfs 202504 + 202604
  init.exact                 2.7 MB      (the exact init binary that must do it)
```

This is the pivot of the whole session: everything after ~16:00 is instrumenting
the window **between kernel handoff and successful policy load**.

**[EVIDENCE]** The diagnostic payload always found itself in that window:

```text
/proc/self/attr/current = u:r:kernel:s0        ← still the kernel domain
/sys/fs/selinux/enforce = 1                    ← enforcing already
```

`u:r:kernel:s0` with enforcing=1 is precisely the "policy loaded, domain
transition not yet done" state.

---

## 4. Instrumentation method (the interesting engineering)

### 4.1 init_boot watchdog wrapper

**[EVIDENCE]** `ulefone-initboot-watchdog-v*/watchdog_v*.S` — a freestanding
AArch64 PID-1 wrapper, no libc, no dynamic linker:

```text
Parent:  clone() a watchdog child, then execve("/init.stock", original argv/envp)
Child:   nanosleep ≥ 80 s
         capture diagnostic state into the reserved pstore partition tail
         fsync
         reboot(RESTART2, "recovery")      (v10+ can also target "bootloader")
```

So the real `init` is renamed `/init.stock` and always still runs — the wrapper
never blocks the boot, it only guarantees that after 80 s the device reboots
**into recovery with a written record**, which is how the data got off a device
that otherwise hangs forever.

### 4.2 Freestanding capture payload

**[EVIDENCE]** `capture_v9.c` / `capture_v10.c` / `capture_v11b.c` headers:

```text
Writes ONLY inside:
  physical partition: /dev/block/by-name/pstore   (later /dev/block/sdc21)
  offset:             0x08100000
  maximum length:     0x00400000 (4 MiB)
Partition total size previously verified: 0x08500000 (133 MiB)
```

Raw syscalls only (`openat/read/write/lseek/fsync/getdents64/getxattr/syslog/
setgroups`). Writing to a **reserved tail of the 133 MiB pstore partition** —
not the 896 KiB ramoops RAM region — is what made the record survive the reboot
without touching anything the bootloader validates.

**[EVIDENCE]** `v11b` reverted `/dev/block/sdc21` back to
`/dev/block/by-name/pstore` — i.e. the by-name symlink was found to be the more
reliable target.

### 4.3 Payload evolution

| Ver | Purpose (from binary `PURPOSE=` string) | Fresh record? |
|---|---|---|
| v1/v2 | bare watchdog: exec `/init.stock`, reboot to recovery after 90 s | n/a |
| **v3** | first full capture: cmdline, mounts, `/proc/1/*`, enforce | **yes** |
| **v4** | `self-context+active-selinux-policy` | **yes** |
| v5 | retry with patched policy | no — stale V4 record |
| **v6** | (capture rewritten) | **yes** |
| v7 | `v7-handoff-test` | no — stale V6 record |
| **v8** | `readproc+pid1+bootconfig+v7-handoff-test` | **yes** |
| v9 | `early-readproc+pid1+debug-ramdisk-handoff`, `setgroups(3009)` before SELinux | no — stale V8 |
| v10 | `minimal-phase-flushed-readproc`, phase markers, writes to `sdc21` | no — stale V8 |
| v11 / v11b | same payload, by-name device, smaller ramdisk | no — stale V8 |

**[EVIDENCE]** Stale-record detection: every `pstore-after-vN.img` was scanned
for its `ULEFONE_DIAG_Vn` marker. v5, v7, v9, v10, v11, v11b all still contain
the *previous* generation's marker — the newer payload never reached its write.

**[INFERENCE]** The failing generations are exactly the ones that tried to gain
privilege *earlier* (`setgroups` before SELinux, `/debug_ramdisk` policy
handoff, phase-flushed minimal writer). The boot died before the child's 80 s
timer, or the child never got to write. The "capture late and simply" design
(v3/v4/v6/v8) is the one that works.

---

## 5. What the successful captures proved

**[EVIDENCE]** Consistent across V3, V4, V8:

| Probe | Result | Meaning |
|---|---|---|
| `/dev/kmsg` | `OPEN_FAILED rc=-13` | EACCES — SELinux denies `kernel` domain |
| `getxattr /dev/kmsg` | `rc=-13` | cannot even read the label |
| `syslog(SIZE_BUFFER/READ_ALL)` | `rc=-13` | classic `syslog_read` denial |
| `/proc/sys/kernel/dmesg_restrict`, `kptr_restrict` | `rc=-13` | |
| `/sys/fs/selinux/policy` | `rc=-13` (label `u:object_r:selinuxfs:s0`) | active policy not dumpable in this domain |
| `/proc/1/*` (status, cmdline, environ, syscall, wchan, stack, mountinfo) | `rc=-2` | ENOENT — `/proc` mounted `hidepid=invisible` |
| `setgroups(AID_READPROC=3009)` | `rc=-1` | cannot buy visibility into PID 1 |
| `/proc` directory listing | `OPEN /proc FAILED` | no process inventory |
| `/sys/fs/selinux/enforce` | `1` | enforcing throughout |
| `/dev/block/sdc21`, `/dev/block/by-name/pstore` | `u:object_r:pstore_block_device:s0` | the write target and its label |

**[EVIDENCE]** The mount table at hang time is a *recovery-like* early
environment: `rootfs /`, `tmpfs /dev /mnt /apex /linkerconfig /tmp`,
`proc(hidepid=invisible)`, `sysfs`, `selinuxfs`, `cgroup2`, `binderfs`,
`pstore`, `configfs`, and **both** `functionfs` gadgets already up
(`/dev/usb-ffs/adb`, `/dev/usb-ffs/fastboot`). No `/system`, `/vendor`,
`/data` — first-stage mount had not happened.

**Net conclusion [INFERENCE]:** the payload could never read a kernel log from
inside the failing boot, because the domain it runs in is denied every kernel-log
interface, and PID 1 is invisible. That is why the effort pivoted to patching
the policy itself.

---

## 6. Policy-patching attempts

**[EVIDENCE]** `ulefone-normal-v3-policy-test/policy.diff` — binary policy
patched to widen the `kernel` domain:

```diff
-allow kernel kmsg_device:chr_file { relabelto write };
+allow kernel kmsg_device:chr_file { getattr open read relabelto write };
```

**[EVIDENCE]** `ulefone-normal-v5-policy-test/v3-to-v5.diff` — adds the syslog
path as well:

```diff
+allow kernel kernel:system syslog_read;
```

Tooling: `ulefone-rescue-v6-policy-test/sepolicy-inject-v6.c` (16 KB source,
351 KB built binary) with `sepolicy.stock` → `sepolicy.1/.2/.v6` variants, and
the same pattern again at v9. `ulefone-v7-debug-policy-audit/` holds
`userdebug_plat_sepolicy.cil` (3 MB) — the userdebug policy intended to be
handed to init via `/debug_ramdisk`, referenced by the v9/v11b binaries.

**[UNPROVEN]** No capture ever shows a *successful* `/dev/kmsg` or `syslog`
read. `kmsg-v5.txt`, `kmsg-v6.txt`, `kmsg-v7.txt` each contain exactly
`[OPEN_FAILED rc=-13]`, and v5/v7 records are stale. **The policy-patching route
was never demonstrated to work on-device.**

---

## 7. Early-USB-console attempt

**[EVIDENCE]** `ulefone-early-acm-v9/v10/v11` build a `vendor_boot` whose
platform ramdisk brings up an early USB CDC-ACM console.
`ulefone-early-acm-v10/early-kmsg-v10.log` contains **only** the handshake:

```text
READYREADYREADY… (117 repetitions, 585 bytes, no kernel text)
```

**[INFERENCE]** The gadget enumerated and the host read the ready-marker loop,
but no kernel log was ever piped into it — consistent with `console=ttynull` and
with the console never being re-pointed at the ACM device. **Dead end as built.**

---

## 8. pstore / ramoops — what actually works

| Attempt | Result | Evidence |
|---|---|---|
| Read `/sys/fs/pstore/*` after a **failed** stock boot | `No such file or directory` | `ulefone-pstore-failed-stock-boot/` |
| Read `/sys/fs/pstore/*` from **recovery** | `Permission denied` | `ulefone-pstore-v10-recovery-test/` |
| `dmesg` in recovery | `klogctl: Permission denied` | `ulefone-pstore-controlled-hang-.../recovery-dmesg.txt` |
| v11/v12 recovery + marker tests | **empty directories** — nothing captured | 5 empty `ulefone-pstore-*` dirs |
| **pmsg persistence marker** | **WORKS** | `pstore-v9-validated-baseline/pmsg-ramoops-0` contains `CHATGPT_V9_PSTORE_PERSIST_20260829_01` |
| **console-ramoops after a normal boot** | **WORKS — 256 KiB of real kernel log** | `pstore-v9-validated-baseline/console-ramoops-0` |
| **Raw pstore partition via BROM/mtkclient** | **WORKS — 133 MiB dump, every time** | `ulefone-mtk-dump/pstore.img`, 9 × `pstore-after-v*.img` |

**[EVIDENCE]** The validated baseline console log (2 845 lines, t=2.5 s → 381 s)
is a *healthy* boot and ends with a deliberate reboot:

```text
[  381.413669][ T350] init: Received sys.powerctl='reboot,recovery' from pid: 431 (/system/bin/reboot)
[  381.426368][   T1] init: Reboot start, reason: reboot,recovery, reboot_target: recovery
[  381.777375][   T1] reboot: Restarting system with command 'recovery'
```

Useful secondary observations in that log:

- `[wdtk] kick watchdog` every ~15 s and periodic `wdt_dump_cntcv` for CPU0–7 →
  the MediaTek watchdog kicker is the boot's liveness heartbeat. Its absence is
  the signature to look for in a hung boot.
- Benign-but-noisy stock behaviour: `SELinux: Multiple same specifications for
  android.hardware.radio.*`, `avc: denied { read } … comm="mtk_plpath_util"`,
  `avc: denied { read } name="type" dev="sysfs"` (the health-HAL power_supply
  denial that the device tree later fixed), `get_charger_zcv failed: -95`.
- `init: [libfs_mgr] Warning: unknown flag: resize` — stock fstab carries a flag
  this init does not know.

**Bottom line [INFERENCE]:** on-device pstore access is useless during the
failure (empty when it matters, denied from recovery), while **offline BROM dumps
of the 133 MiB pstore partition are 100 % reliable** — which is exactly why the
capture payload was redirected to write into that partition's tail.

---

## 9. vendor_boot rescue engineering

**[EVIDENCE]** `ulefone-rescue-v6-final/stock-avb.txt` — the exact contract every
rebuilt image had to satisfy:

```text
Footer version:          1.0
Image size:              67108864 bytes      (exactly 64 MiB)
Original image size:     33828864 bytes
VBMeta offset:           33828864     VBMeta size: 640 bytes
Algorithm:               NONE         Rollback Index: 0
Hash descriptor:
  Partition Name:  vendor_boot
  Hash Algorithm:  sha256
  Salt:            9c02741721a24549180ce75e774265e894e30f7442167b91ef7b06dec913b654
  Digest:          63c2d4b2a2a8c61ed469bbe22734e620be071a566b3759d0d0ec18ada97bd305
  Prop com.android.build.vendor_boot.fingerprint ->
       Ulefone/GQ5012BF1_EEA/GQ5012BF1:15/AP3A.240905.015.A2/1761131274:user/release-keys
```

`Algorithm: NONE` — the descriptor is a **plain hash, unsigned**, so a rebuilt
image can be made verifiable without vendor keys. This is why the rescue path is
viable at all on an unlocked device.

**[EVIDENCE]** The `vendor_boot` v4 layout that had to be preserved (two ramdisk
fragments + DTB), from `ulefone-hybrid-vendorboot-inspect` and
`ulefone-rescue-build/final-check/`:

```text
entry 0  PLATFORM  ~27 MB lz4  (63 MB cpio)   ← stock, must be preserved
entry 1  RECOVERY  ~4 MB lz4   (6 MB cpio)    ← the part being replaced
dtb.raw  334 KB                                ← stock, must be preserved
```

**[EVIDENCE]** A systematic **LZ4 compression-level matrix** was run to make the
rebuilt fragments fit the 64 MiB partition:
`ulefone-rescue-build/lz4-tests/{original,patched}-l{9,10,11,12}.lz4` and
`ulefone-rescue-compression-matrix/{A,B,C,D}-{platform,recovery}.{cpio,lz4}` —
8 + 8 variants. Follow-ups `ulefone-rescue-v5-size-test` and
`-v5-padding-test` (trimmed cpio) show size/padding was the binding constraint.

**[EVIDENCE]** Nine rescue generations were built and, importantly,
**read back from the device and verified**:

```text
ulefone-mtk-dump/vendor_boot_a_rescue_v3_readback.img
ulefone-mtk-dump/vendor_boot_a_rescue_v4_readback.img
ulefone-mtk-dump/vendor_boot_a_rescue_v5_readback.img
ulefone-mtk-dump/vendor_boot_a_after_restore.img
ulefone-rescue-v6-final/vendor_boot_a_v6_readback.img
… plus verify/vendor_boot.img inside v6/v9/hybrid/early-acm builds
```

Flash → read back → compare is the discipline used throughout; every build
directory carries its own `verify/` copy.

**[EVIDENCE]** The **hybrid** line (`ulefone-hybrid-stockplat-v9rec…v12rec`,
`hybrid-v3-kmsg`, `hybrid-v5-kmsg-syslog`) keeps the **stock PLATFORM fragment
byte-identical** and swaps only the RECOVERY fragment, and in the
`hybrid-v*-kmsg*` variants injects the patched `final-sepolicy.bin` into the
platform ramdisk. Round-trip files (`*.roundtrip.cpio`) prove cpio
repack-decompress equivalence was checked, not assumed.

**[EVIDENCE]** Final state artifacts: `ulefone-final-preflash-verify/`
(`init_boot.img` 8 MB + `vendor_boot.img` 64 MB, 20:20),
`ulefone-lieppos-reflash/lieppos-system-fresh.img` (2 GB, 23:57),
`ulefone-metadata-audit/{metadata-fsck-copy,metadata-label-audit}.img` (74 MB
each, 23:34), and `ulefone-vbmeta-disabled.img` (8 KB, next morning) — a vbmeta
with verification disabled, the standard last-resort unblocker.

---

## 10. Chronology (2026-08-29)

```text
02:43  metadata recovery attempt (empty result)
04:14  stock vendor_boot / init_boot unpacked and inspected
04:25  first rescue build; 04:51-05:20  rescue v2 → v5 + LZ4/size/padding matrix
05:22  BROM dumps: expdb, metadata, pstore, vendor_boot readbacks
12:43  policy-injection tooling; 12:56-13:22  rescue v6 → v8 (build + verify)
14:17  first debug init_boot
14:58-15:28  early USB-ACM console attempts v9 → v11  (only "READY" ever seen)
16:33  rescue v9; 16:49  pstore persistence proven (pmsg marker + 256 KiB console)
16:59  pstore after a FAILED stock boot: empty
17:16-17:42  ramoops raw test; init_boot watchdog v1/v2
17:50-19:32  recovery-side pstore reads: all denied/empty (5 empty dirs)
17:58-19:17  hybrid stock-platform recovery builds v9rec → v12rec
19:45-20:12  watchdog v3 + first kmsg policy patch
20:20  FINAL PREFLASH VERIFY (init_boot + vendor_boot)
20:28  ✅ V3 capture — first real on-device record
20:34-20:54  watchdog v4/v5 + syslog_read policy patch;  ✅ V4 capture, v5 stale
21:02-21:11  watchdog v6;  ✅ V6 capture
21:26  ✅ ACTIVE POLICY AUDIT — the plat_sepolicy hash mismatch is nailed
21:29-22:01  userdebug policy prep, watchdog v7/v8;  ✅ V8 capture (bootconfig)
22:20-23:22  watchdog v9/v10/v11/v11b — every record stale, no new data
23:34  metadata audit;  23:57  fresh LieppOS system image staged
00:14  vbmeta-disabled image prepared
```

---

## 11. Consolidated findings

1. **[EVIDENCE] The device has fully open BROM** (SBC/SLA/DAA all False). Any
   partition can be dumped or restored offline. This is the recovery guarantee.
2. **[EVIDENCE] There is no serial console** (`console=ttynull`,
   `mtk_printk_ctrl.disable_uart=1`). Any boot-hang debugging must use RAM,
   pstore, or USB.
3. **[EVIDENCE] The GSI/LieppOS plat_sepolicy hash does not match the hash the
   vendor `precompiled_sepolicy` was built against** (`3617114e…` vs
   `53f5f99e…`), while `system_ext` matches. **[INFERENCE]** This forces
   runtime policy compilation and is the most probable cause of the stall.
4. **[EVIDENCE] At hang time the process context is `u:r:kernel:s0` with
   enforcing=1**, `/proc` is `hidepid=invisible`, and every kernel-log interface
   (`/dev/kmsg`, `syslog`, `/sys/fs/selinux/policy`) returns EACCES. The failing
   window is *before* the init domain transition and is deliberately unobservable.
5. **[EVIDENCE] pstore is useless from the device when it matters** — empty after
   a failed boot, permission-denied from recovery — but **the 133 MiB pstore
   partition dumps perfectly over BROM**, and a reserved tail at `0x08100000`
   (4 MiB) is a safe scratch area that survives reboot.
6. **[EVIDENCE] The working instrumentation pattern** is: rename init to
   `/init.stock`, run a freestanding PID-1 wrapper that clones a child, exec the
   real init, and have the child capture + `fsync` + `reboot("recovery")` after
   80 s. Four generations (V3, V4, V6, V8) produced fresh records this way.
7. **[EVIDENCE] Every "smarter" variant failed** (early `setgroups`,
   `/debug_ramdisk` policy handoff, phase-flushed minimal writer): V5, V7, V9,
   V10, V11, V11b all left the previous generation's record in place.
8. **[UNPROVEN] Policy patching to read kmsg never demonstrably worked.** The
   rules were injected (`kernel kmsg_device:chr_file { getattr open read }`,
   `kernel kernel:system syslog_read`) but no capture shows a successful read.
9. **[UNPROVEN] The early USB-ACM console never carried kernel output** — only
   its own `READY` marker loop.
10. **[EVIDENCE] `vendor_boot` is rebuildable and verifiable without vendor keys**
    (AVB `Algorithm: NONE`, plain sha256 hash descriptor, salt and digest known,
    exact 67108864-byte size). The stock PLATFORM fragment and DTB must be
    preserved byte-for-byte; only the RECOVERY fragment is safely replaceable.
11. **[EVIDENCE] The healthy-boot signature is `[wdtk] kick watchdog` every
    ~15 s** plus periodic `wdt_dump_cntcv` for all 8 CPUs. Its disappearance is
    the marker to search for in any future hung-boot dump.

---

## 12. Recommended next steps

1. **Test the hypothesis directly**: ship a `plat_sepolicy_and_mapping.sha256`
   that matches the GSI policy, or drop `precompiled_sepolicy` from vendor
   entirely so init compiles once, deterministically. This is a two-file change
   and would confirm or kill finding #3 immediately.
2. **Instrument with V8, not V9+**. The late-and-simple capture is the only
   design with a proven success rate. Extend V8's probe list rather than
   restructuring it.
3. **Capture `console-ramoops` from the failing boot via BROM**, not via
   `/sys/fs/pstore` — dump the pstore partition and carve the ramoops region at
   `0x48090000` (console 256 KiB) offline.
4. **If kmsg is still required**, prefer a permissive `kernel` domain in a
   *debug-only* policy over per-rule injection, and prove it with a positive
   read in the capture record before building on it.
5. **Keep the BROM path documented and rehearsed** — it is what makes the device
   unbrickable in practice.

---

## 13. Artifact index

| Family | Dirs | Size | Keep? |
|---|---|---|---|
| `ulefone-rescue-*` | 17 | ~2.7 GB | keep final images + `stock-avb.txt`; the LZ4/size matrices are reproducible, drop after recording levels |
| `ulefone-hybrid-*` | 9 | ~2.3 GB | keep `v12rec` + `hybrid-v5-kmsg-syslog` (last of each line) |
| `ulefone-initboot-watchdog-*` | 19 | ~350 MB | **keep sources**: `capture_v*.c`, `watchdog_v*.S`, `disassembly.txt`; images are rebuildable |
| `ulefone-v*-raw-capture` | 9 | ~1.2 GB | **keep the readable `.txt` records**; the 133 MB `pstore-after-*.img` files are redundant once carved |
| `ulefone-early-acm-*` | 3 | 654 MB | keep `early-kmsg-v10.log` only (dead end) |
| policy audits | 6 | ~2.1 GB | **keep `exact-policy-inputs/*.sha256` and the `.cil` set** — this is the root-cause evidence |
| `ulefone-mtk-dump` | 1 | 665 MB | **keep** `expdb.img`, `pstore.img`, `metadata.img`, readbacks |
| `ulefone-pstore-*` | 9 | 768 KB | **keep** `v9-validated-baseline` (real console log + persistence marker); 5 dirs are empty and can go |
| misc images | — | ~2.3 GB | `lieppos-system-fresh.img`, `vbmeta-disabled.img`, `final-preflash-verify/` |

Total on disk: **12 GB**. The irreplaceable subset — capture sources, readable
records, policy hashes/CIL, the validated console log, and the AVB parameters —
is **under 40 MB**.

---

*Compiled from artifacts only. No device was attached and nothing was re-run;
every quoted value is read out of the files listed above.*
