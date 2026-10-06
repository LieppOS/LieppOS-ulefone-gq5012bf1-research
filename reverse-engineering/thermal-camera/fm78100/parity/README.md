# yft_tiny2c_usb.ko parity (A = stock, B = rebuild of ../source/yft_tiny2c_usb.c)

- A: `vendor_dlkm/lib/modules/yft_tiny2c_usb.ko`, sha256 `77baeee8…3eed`, 30464 B, build-id `c626fad2…3da`
- B: `../scripts/build.sh F1` (isolated `M=` build against the pinned GKI 6.1.115 tree
  `common@6b18f0b574ab`, clang r487747c, provider symvers `0x398e9c8b yft_usb_flag`),
  stripped sha256 `f6dbce37cf0ac5b692821b99f222ed6d6cc7ac3ac7115036c91271a5fa78e291`;
  **B1 == B2** (two clean builds byte-identical).
- Tool: `reverse-engineering/display-input/rear-display-input/scripts/ko-parity-tsv.py`.

| axis | result |
|---|---|
| functions | 12/12 present, **11/12 byte-identical** with equal relocations; KCFI 12/12 |
| `tiny2c_usb_probe` | 1064 vs 1068 B. `.text` is byte-identical up to probe+0x324; the difference is only the sysfs-creation error-unwind tail: stock keeps a rolled `for (; i >= 0; i--) device_remove_file()` loop (pointer IV + array-bounds check), clang on the rebuild peels/unrolls the ≤2-iteration loop. Every path (success, attr-0 failure, attr-1 failure) calls the same functions with the same arguments and returns the same value. 37 loop/declaration shapes were tried (`../scripts/probe_unwind_loop_trials.py`); none reproduced the rolled form |
| data objects | 27/27 byte-identical, same sections/sizes |
| imports / modversions | 23/23 name+CRC, `__versions` order equal; exports 0/0 |
| modinfo / vermagic | 9/9 positional equal |
| strings | `.rodata.str1.1` 1326/1326 B, same content and order |
| relocations | 378 vs 377 (the one fewer is inside the probe unwind tail) |
| sections | same set; `.text` 3388 vs 3392 |

Corrections vs the earlier phase-4 reconstruction (`kernel/phase4-yft-tiny2c-usb-recon/`,
9/12 byte-identical): plain `printk()` instead of `pr_info/pr_err` for 27 unlevelled stock
strings; probe retry line is `"%s. retry = %d, chip_id = 0x%x. \n"` (not the `zzt_1` string);
`DEVICE_ATTR` objects are global (fixes function and `.data` order); `i2c_msg` fields are
assigned `.addr, .flags, .buf, .len`; the 5-attempt chip-ID loop is
`for (retry = 0; retry < 5; retry++)`.
