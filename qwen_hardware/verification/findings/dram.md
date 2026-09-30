# U1 - DRAM vendor / part number / speed / channel layout

**Current claim:** "12/16 GB claim; SoC LPDDR5 ceiling only" - vendor, part and size unknown.

**Previous confidence:** UNKNOWN.

**New evidence**
* Live bootloader-generated kernel command line: `lpddr_used_name=MT512GBCAV8U31`, `lpddr_used_index=0`.
  MediaTek's LK writes this string from the EMI/DRAM identification table entry that actually matched at boot (`lk.img` contains the format string `lpddr_used_name=%s`).
* Live `/proc/device-tree/memory@40000000/reg = <0x0 0x40000000 0x4 0x0>` -> a **16 GiB** physical DRAM window.
* Preloader (`preloader_k6878v1_64.bin`) contains a full `LP5_dram_init.c` / `lpddr_cal` calibration suite and prints `dram_tpye: LPDDR5` / `LPDDR4x`; the MT6878 supports LPDDR4X/LPDDR5/LPDDR5X.
* The `MT` prefix is Micron's part-number namespace; Micron's uMCP line packages LPDDR5X together with UFS in one BGA.
* The same string encodes `512GB`, matching the 512 GB storage SKU - i.e. this is a **combined uMCP part number, not a discrete DRAM die**.

**Contradicting evidence:** none found. GSMchoice/Ulefone list 16 GB RAM for this SKU, consistent with the 16 GiB memory node.

**Internet sources:** VI23, VI24 (Micron uMCP/uMCP5 product and catalogue pages); VI6 (16 GB RAM listing). The specific `MT512GBCAV8U31` catalogue entry could not be retrieved (Q4, Q5, Q12).

**Local evidence:** VL1, VL3; `../evidence/live-devicetree-extracts.md`.

**Read-only live evidence:** the bootargs and memory node above, from the frozen snapshot.

**Final conclusion**
The memory subsystem is a **Micron uMCP (UFS-based multi-chip package) marked `MT512GBCAV8U31`**, combining **512 GB UFS storage with 16 GiB LPDDR5-class DRAM** on the MT6878's LPDDR5 controller. This is the part the bootloader itself identified on this handset, so vendor + package + density are established; the LPDDR generation (LPDDR5 vs LPDDR5X), data rate, channel/rank layout and exact Micron SKU decode are **not** established, because the preloader's EMI timing table is compiled binary and Micron's public catalogue entry was not reachable.

**Final confidence:** vendor + part-number string + 16 GiB size + uMCP topology = **PROVEN**; LPDDR5X vs LPDDR5 grade, MHz, channels/ranks = **UNKNOWN**.

**Remaining uncertainty:** to close it, either read `/sys/kernel/debug/mtk_dramc/*` (or `/proc/dramc`) on a rooted stock boot, or obtain the Micron datasheet for this SKU, or read the package marking in a teardown.

**Impact on final inventory:** YES - MASTER-HARDWARE-INVENTORY memory row is rewritten; UNKNOWN-HARDWARE U1 is marked partially resolved.

**Answers to the standard questions:** (1) 16 GiB, Micron uMCP `MT512GBCAV8U31`; (2) LPDDR generation/speed/channel map; (3) partially - yes for identity, no for timings; (4) yes - a rooted DRAM-info debugfs read; (5) partially - Micron catalogue; (6) only for the package marking cross-check; (7) `MT512GBCAV8U31`; (8) PROVEN identity / UNKNOWN timings; (9) yes; (10) yes; (11) no.

## Second-pass update (2026-09-08)

The exact-string search for `MT512GBCAV8U31` was repeated against Micron catalogues and datasheet indexes
(Q19/VI23/VI24) and again produced no orderable SKU. Bootloader binaries contain generic LP4/LP5 transition,
retention and UFS-generation code compiled for the platform, but no safely decodable density/speed/rank
record tied to this part-name string. Compiled capability is not population evidence. Consequently the
conservative pass-1 verdict stands: **Micron identity, 16 GiB and the bootloader name are proven; LPDDR5 vs
LPDDR5X, data rate, channels and ranks remain UNKNOWN.**
