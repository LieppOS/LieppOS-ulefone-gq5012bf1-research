# Phase 4 — `yft_devinfo.ko`: KCFI type-id channel

A second, independent prototype oracle was found in the stock module and
applied. It is strictly stronger than the MODVERSION-CRC channel used in
[`phase4-yft-devinfo-reconstruction.md`](phase4-yft-devinfo-reconstruction.md),
it **corrected two stock prototypes outright**, and it shrinks the one
remaining unknown to a single identifier spelling that is now constrained by
*four* independent 32-bit equations instead of one.

---

## 1. The channel

GQ5012BF1 kernel modules are built with clang's kernel CFI (`-fsanitize=kcfi`).
Every function whose address is taken carries a 32-bit constant immediately
before its entry point:

    type_id = xxHash64(itanium_mangled_function_type) & 0xffffffff

The mangled string for a C function type `R f(A, B)` is `_ZTSF<R><A><B>E`.
Parameter *names* do not appear; parameter and return **types** do, including
the spelling of a named `enum` / `struct` / `union` tag (`<len><tag>`).

Oracle implementation + self-test: `reverse-engineering/scripts/ko-kcfi-typeid.py`
(pure-Python xxHash64, no third-party module required).

### Why it beats the CRC channel

genksyms CRCs only exist for *exported* symbols, and for this module the ten
affected exports share one common suffix, so (CRC being affine over GF(2))
they collapse to **one** 32-bit equation on the unknown text — a brute-force
hit is meaningless at ~1 collision per 4·10⁹ candidates.

KCFI type ids exist for *every* address-taken function and each one is a
separate equation. The unknown second parameter type `T` appears in four
different function types here, so a candidate must satisfy four 32-bit
constraints simultaneously (~2⁻¹²⁸ false-positive rate):

| family | stock type id | mangled form |
|---|---|---|
| `yft_camera_device_add` | `0x803f8280` | `_ZTSFiPc<N><T>E` |
| `yft_{touchpanel,fuelgauge}_device_add` | `0x076247bd` | `_ZTSFiP10i2c_driver<N><T>E` |
| `yft_{spitouchpanel,tinylcd,touchpanel_spi}_device_add` | `0x73f54704` | `_ZTSFiP10spi_driver<N><T>E` |
| `yft_{acc,m,alsps,sar,baro}sensor_device_add` | `0x16318e3f` | `_ZTSFiP11sensor_info<N><T>E` |

## 2. What it proved (two corrections, now applied)

Both were previously reconstructed as returning `int`:

| function | stock type id | proven prototype |
|---|---|---|
| `yft_add_display_info` | `0x6a3c623b` = `_ZTSFvPciE` | `void yft_add_display_info(char *info, int len)` |
| `yft_display_info_dump` | `0x9831c2fc` = `_ZTSFvP8seq_fileE` | `void yft_display_info_dump(struct seq_file *m)` |

Independently confirmed by codegen: neither stock function writes `w0` before
`ret`. Both are fixed in `source/yft_devinfo.c` / `source/yft_devinfo.h`.

## 3. What it rules out for the unknown `T`

`T` is **not** a builtin type and **not** a typedef of one: a typedef is
transparent to Itanium mangling, so any `typedef`-of-builtin would have
produced one of the builtin codes, and none match (all of
`b c a h s t i j l m x y w n o f d e` and the common pointer forms tested).
`T` therefore names a real `enum` (or `struct`/`union`) **tag**, consistent
with the genksyms measurement that its expansion is 73 characters long.

Searched and excluded (no candidate satisfying even the single camera
equation, let alone all four):

| space | size | tool |
|---|---|---|
| every identifier ≤ 7 chars over `[a-z0-9_]` | 9.5·10¹⁰ | `ko-kcfi-brute-affix.c` |
| `yft_` / `YFT_` / `yft_dev_` / `yft_device_` / `yft_devinfo_` + ≤ 7 chars | 6.7·10¹¹ | same |
| ≤ 7 chars + `_type _t _e _state _used _flag _info _mode _status _sel _en _id` | 1.1·10¹² | same |
| `yft_` + ≤ 7 chars + `_type _state _t _e _used _flag _status` | 6.6·10¹¹ | same |
| 1–3 dictionary words (2 499-word vocabulary harvested from the stock module and its seven consumers), `_`/no separator, lower/UPPER | 1.2·10¹¹ | `ko-kcfi-brute-dict.c` |
| fixed first word (`yft YFT yft_dev yft_device Yft dev device camera sensor touch hw hwinfo e_yft enum_yft ul ulefone`) + 1–3 dictionary words, lower/UPPER/Capitalised | 1.1·10¹³ | same |
| all 3 076 `enum` tags and `typedef` names reachable from 1 983 `include/linux` headers of exact GKI 12901745 | 3 076 | genksyms harness |

Total ≈ 1.4·10¹³ distinct tag spellings excluded. Every reported hit was a
camera-only collision; none survived the i2c/spi/sensor cross-check, which is
exactly the expected behaviour of the four-equation filter.

**Conclusion unchanged and now much better evidenced:** the spelling is
vendor-private, appears in no shipped artifact, and cannot be recovered
offline. Declaring the parameter `int` remains the honest choice; it costs
exactly the ten `*_device_add` export CRCs and the matching ten KCFI ids.

## 4. Reproducing

```sh
cc -O3 -march=native -o kcfi-brute-affix reverse-engineering/scripts/ko-kcfi-brute-affix.c
seq 0 36 | xargs -P "$(nproc)" -I{} ./kcfi-brute-affix 'yft_' '' 7 37 {}
# prints "VERIFIED <tag>" only when all four family equations hold
```

<!-- component: YFT-DEVINFO -->
