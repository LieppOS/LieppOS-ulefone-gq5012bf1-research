# Boot-hang / pstore / rescue evidence — 2026-08-29

Primary artifacts behind
[`../../reports/ulefone-debug-pstore-rescue-report.md`](../../reports/ulefone-debug-pstore-rescue-report.md).

Extracted from ~90 scratch directories (12.3 GB) under `~/ulefone-*`; only the
irreplaceable 22 MB is kept here. Everything omitted is either a rebuildable
build product (LZ4 matrices, 64 MiB `vendor_boot` images, ramdisk cpio/lz4) or a
133 MB raw partition dump whose readable payload is already carved out below.

```text
capture-harness/   freestanding PID-1 wrapper + capture payload sources (v1…v11b)
                   *.c, *.S, disassembly.txt, linked init.watchdog binaries
captures/          readable on-device records: ULEFONE_DIAG_V3/V4/V6/V8,
                   recovery mounts, runtime prop dumps
policy/            ROOT CAUSE: exact-policy-inputs/*.sha256 show the GSI
                   plat_sepolicy hash != the hash vendor precompiled_sepolicy
                   was built against; full CIL input set, init binaries, and the
                   kmsg/syslog injection diffs + sepolicy-inject source
pstore/            validated baseline (256 KiB real console log + pmsg
                   persistence marker), failed-boot and recovery-denied results
vendor_boot/       stock AVB footer parameters (Algorithm NONE, salt, digest,
                   67108864 bytes) and the mtkclient/BROM logs showing
                   SBC/SLA/DAA/SWJTAG all disabled
misc/              early USB-ACM console attempt (READY marker only, dead end)
```

Not preserved, deliberately: `expdb.img` (128 MB), `pstore.img` (133 MB),
`metadata.img` (74 MB) and the `vendor_boot` readbacks. They are device-state
snapshots, re-dumpable over BROM, and too large to publish. Copy them out of
`~/ulefone-mtk-dump/` before deleting that directory if the failing-boot state
still matters.
