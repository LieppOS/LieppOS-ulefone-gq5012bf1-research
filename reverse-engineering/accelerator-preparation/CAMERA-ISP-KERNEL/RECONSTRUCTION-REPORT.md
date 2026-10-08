# CAMERA-ISP-KERNEL — reconstruction report

**Result: DONE.** All nineteen registered camera/ISP kernel modules of the Ulefone
Armor 29 Pro Thermal (GQ5012BF1 / MT6878T, stock kernel `6.1.115-android14-11`) are
rebuilt from **public MediaTek vendor source** (NothingOSS mt6878 trees) plus the
GQ5012BF1 patches preserved in
`android_kernel_modules_camera_isp_ulefone_gq5012bf1`.

Seventeen modules are identical to the shipped binaries except their 20-byte GNU
build-ID descriptor. Two carry a single declared, proven non-behavioural residue each.
Nothing is unresolved.

## 1. Per-module result

Measured by `scripts/verify.py` on a **fresh clone**, against the stock operands listed in
[stock-modules.tsv](stock-modules.tsv). Function and data counts are every
`STT_FUNC`/`STT_OBJECT` symbol keyed by (section, offset, name, size).

| module | functions exact | data exact | imports / exports | CRC / KCFI | relocations | residue |
|---|---|---|---|---|---|---|
| `mtk_hcp.ko` | 169/169 | 74/74 | 89 / 112 | all CRCs; 1 abs KCFI id | 3 158 | build ID (20 B) |
| `mtk-ipesys-me.ko` | 14/14 | 20/20 | 18 / 4 | all CRCs; no abs KCFI | 156 | build ID |
| `mtk_imgsys_cmdq.ko` | 165/165 | 211/211 | 130 / 14 | all CRCs; 4 abs KCFI ids | 4 726 | build ID **+ `.symtab`/`.strtab`** (COMPILER_ONLY, §4) |
| `mtk_imgsys_v4l2.ko` | 185/185 | 159/159 | 223 / 5 | all CRCs; 50 abs KCFI ids | 4 967 | build ID |
| `mtk_imgsys_isp7sp.ko` | 85/85 | 141/141 | 44 / 0 | all CRCs; 57 abs KCFI ids | 3 646 | build ID |
| `ccd_rpmsg.ko` | 29/29 | 24/24 | 48 / 13 | all CRCs; 2 abs KCFI ids | 609 | build ID |
| `mtk_ccd_remoteproc.ko` | 25/25 | 27/27 | 66 / 8 | all CRCs; 1 abs KCFI id | 553 | build ID |
| `mtk_ccuv.ko` | 45/45 | 40/40 | 97 / 6 | all CRCs; 4 abs KCFI ids | 855 | build ID |
| `mtk-cam-isp7sp.ko` | 1 220/1 220 | 694/694 | 345 / 5 | all CRCs; 51 abs KCFI ids | 22 882 | build ID |
| `mtk_aie.ko` | 135/135 | 149/149 | 190 / 9 | all CRCs; 17 abs KCFI ids | 3 500 | build ID |
| `mtk_aie_debug_7sp_2.ko` | 6/6 | 13/13 | 7 / 1 | all CRCs; no abs KCFI | 74 | build ID |
| `camera_dpe_isp7sp.ko` | 96/96 | 138/138 | 122 / 11 | all CRCs; 2 abs KCFI ids | 6 047 | build ID |
| `pda_drv_mt6878.ko` | 33/33 | 68/68 | 64 / 0 | all CRCs; no abs KCFI | 2 119 | build ID |
| `mtk-vmm-isp71-regulator.ko` | 22/22 | 49/49 | 62 / 2 | all CRCs; 7 abs KCFI ids | 826 | build ID |
| `mtk-vmm-notifier.ko` | 5/5 | 20/20 | 17 / 1 | all CRCs; no abs KCFI | 125 | build ID |
| `imgsensor-glue.ko` | 4/4 | 11/11 | 8 / 2 | all CRCs; no abs KCFI | 49 | build ID |
| `imgsensor.ko` | **620/621** | 416/416 | 132 / 1 | all CRCs; 17 abs KCFI ids | 15 487 | build ID **+ 1 function** (PROVEN_SEMANTIC_EQUIVALENT, §4) |
| `c2ps_perf_ioctl.ko` | 6/6 | 27/27 | 14 / 10 | all CRCs; 3 abs KCFI ids | 120 | build ID |
| `mtk_c2ps.ko` | 106/106 | 193/193 | 116 / 0 | all CRCs; 2 abs KCFI ids | 2 092 | build ID |
| **total** | **2 970 / 2 971** | **2 474 / 2 474** | **1 792 / 204** | 2 530 ABI rows; 218 KCFI ids | **71 991** | — |

All **978 section headers** are identical. Section contents comprise 955 identical rows,
19 build-ID-only rows, two COMPILER_ONLY rows (`.symtab`/`.strtab`) and two
PROVEN_SEMANTIC_EQUIVALENT rows (`imgsensor .text`/`.rela.text`).
`.modinfo` (including `depends=`, `alias=`, `vermagic`, `srcversion`, `license`, `parm*`)
and symbol ordering are identical; string tables differ only in the declared
`mtk_imgsys_cmdq` case. **71 990/71 991 relocations** are raw and semantic identical;
one byte-load relocation moves four bytes within the equivalent `imgsensor` function.

Machine ledgers: [function-parity.tsv](function-parity.tsv) (2 971 rows),
[data-parity.tsv](data-parity.tsv) (2 474), `evidence/reconstruction/acceptance/`
(`abi-parity.tsv` 2 530, `sections-parity.tsv` 978, `relocations-parity.tsv.xz` 71 991,
`acceptance.json`).

## 2. Source lineage

| unit | public pin | tree |
|---|---|---|
| mtkcam package | `NothingOSS/android_kernel_modules_nothing_mt6878` `5f75a3b13e81`, subtree `mtkcam` | `ae4272e46819…` |
| vendor device modules | `NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878` `957dac185efe` | `05f9c65d40ef…` |
| GKI kernel | `android.googlesource.com/kernel/common` `6b18f0b574ab` (build 12901745) | `710eb8595138…` |
| toolchain | `prebuilts/clang/host/linux-x86` `7775eb113f96` → `clang-r487747c` | `8eb8e3afb00a…` |

Three patches reproduce the device source (`0001` mtkcam deltas + build scope, `0002` the
GQ5012BF1 `imgsensor` package, `0003` vendor headers + build scope); the patched trees are
asserted to be `4b75fc209a4b…` (mtkcam) and `ceab41013` (kdm) on every assemble.
`pda_drv_mt6878`, `mtk-vmm-isp71-regulator` and `mtk-vmm-notifier` need **no** source
patch at all — unmodified NothingOSS source already produces byte-identical modules.
See [SOURCE.md](SOURCE.md).

## 3. What the GQ5012BF1 patches actually change

Grouped by the evidence that forced each change (all were measured against the stock
binaries, never guessed):

* **Behavioural deltas vs the NothingOSS donor** — the `cb_param` pool fallback in
  `imgsys_cmdq_sendtask_plat7sp`, the `camsv_handle_err` fifo-full escalation counter
  (`sv_fifo_full_times`), `CmdqDPEHW` polling `CTRL_STATUS0` instead of a GCE event, the
  `ccd_opened` single-opener guard, `init_camsys_settings()` re-apply after engine reset,
  and the removal of NothingOSS's 43 `"kcalloc memory faill"` vmalloc fallbacks (absent
  from every GQ5012BF1 stock module).
* **The `imgsensor` package** — nine sensor sub-drivers (IMX989, IMX989CTS, S5KGM2SP,
  S5KGN1SP, OV32B40, S5KJN1, S5KJN1CTS, S5KJN1MAIN2, OV64B) with stock-derived mode
  tables, the frame-sync subsystem, and the Ulefone YFT hooks (night LED, CTS board
  gating, charger/devinfo notifications).
* **Stock source layout** — line positions proven by the shipped `__bug_table`
  (file,line) records and the `.rodata` module-parameter string order; see
  [stale-claims.md](stale-claims.md) §3.
* **Build scope only** — the opt-in `LIEPPOS_ONLY` selector in both `Kbuild` files, so a
  parity build can descend into the owned packages without building the whole vendor tree.

## 4. The two declared residues

**`mtk_imgsys_cmdq` — COMPILER_ONLY, 2 853 symbol/string-table bytes plus 20 build-ID bytes.**
Ten private (STB_LOCAL) data objects inside `imgsys_cmdq_parser_plat7sp` carry clang's
module-wide name-uniquing suffix one higher in stock
(`…__func___rs.84/.86/.89/.92/.95/.98/.101/.104/.106/.109` versus `.83/.85/…/.108`).
Proven equal: same section, same address, same size, same bytes for each of the ten; all
other section contents identical except the build ID; all 4 726 relocations identical raw
and semantic; all import/export CRCs, KCFI ids and `.modinfo` identical. `.strtab` moves
only because the tail-merged suffix strings shift. The suffix difference is consistent
with an extra clang private-global counter allocation in the original translation unit;
the exact absent source spelling is not established. No construct was invented to fake
the counter.

**`imgsensor` — PROVEN_SEMANTIC_EQUIVALENT, 49 code bytes + 1 relocation byte + 20 build-ID bytes.**
`yft_ctrl_nightled_by_idx` (172 bytes, static, same address, same callees, same stored
value) plus one `R_AARCH64_LDST8_ABS_LO12_NC` (type 278) relocation: stock `.text+0xb148`
→ build `.text+0xb144`, unchanged target `.bss+0x20`. Both call sites pass
a literal (`mov w1,#1` / `mov w1,wzr`, byte-identical to stock), so this clang narrows the
`state` parameter to {0,1} and emits `cmp w8, #1`, where stock keeps the register
(`ccmp w8, w19, #4, ne`). For every value the two call sites can produce the behaviour is
identical: LED on when `state` is non-zero and the flag differs, LED off when `state` is
zero and the flag is set, no action otherwise, then the flag is stored. The flag is a
zero-initialized local bool, with its only references inside this function. The four-case
truth table, exact call offsets and operand hashes are retained in
[evidence/reconstruction/acceptance/imgsensor-residue-proof.md](evidence/reconstruction/acceptance/imgsensor-residue-proof.md).
The verifier pins both residue modules' exact normalized rebuild hashes and checks the
single moved relocation, so the exception is not an open-ended section allowlist.

No `UNRESOLVED` class exists anywhere in this component.

## 5. Build reproduction

Fresh clone → `bootstrap.sh` (every pin verified by git tree id / sha256) →
`b1b2.sh`: two completely clean builds that re-extract both source trees, re-create the
kernel output tree, regenerate the external ABI and rebuild all nineteen modules.
**B1 == B2** for the raw and stripped modules, all **225** target `.o` files, every
package and provider symvers, the kout `.config` and both source tree ids.
See [build-reproduction.md](build-reproduction.md).

## 6. External ABI

The 1 792 import records comprise **1 547 GKI/core**, **78 owned-module**, and **167
external-vendor** occurrences (552, 76 and 105 distinct symbols respectively).
The provider build ledger contains **107 distinct symbols**: 105 external vendors plus
two owned CCU exports included under historical provider identities for package-scoped
modpost. **97/107** CRCs regenerate from public provider source; the remaining ten retain
the stock provider's `__kcrctab` value (including known public-CMDQ ABI divergence and
non-public OEM providers). See [abi-parity.md](abi-parity.md).

## 7. Boundaries that stay closed

CCU firmware (`firmware/ccu.img`, `vendor/firmware/lib3a.ccu`) and the whole MediaTek
camera HAL / 3A / tuning stack remain proprietary, unmodified and unanalysed
([firmware-boundary.md](firmware-boundary.md)). Sensor dies, EEPROMs, VCM/OIS, flash and
camera LDO rails keep their existing DONE owners.

## 8. Not established

Nothing was executed on hardware. No probe, no stream, no capture, no firmware boot, no
IOCTL. The runtime acceptance list is in
[source-to-userspace-contract.md](source-to-userspace-contract.md) §5.
