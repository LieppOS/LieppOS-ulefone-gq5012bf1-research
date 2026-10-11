# SCP-CONNECTIVITY-BATCH-01: SCP, sensor hub and connectivity kernel source reconstruction (Codex)

**Result: 20 selected identities, all processed: 17 newly A, 0 B, 3 C (cfg80211, mac80211, bluetooth).**
Both families pass independent, bwrap-isolated clean-clone B1/B2 checks with identical outputs and stock acceptance.
This is a delta only. The live canonical audit was **not** modified (see `MERGE-INSTRUCTIONS.md`).

| | |
|---|---|
| Branch / worktree | `codex/scp-connectivity-batch-01` in `ulefone-gq5012bf1-research-codex-connectivity` (base `bb370374`, canonical master, committed state only) |
| Frozen baseline | audit `548526fc` (identical at `bb370374`): 458 identities, A219/B1/C9/D98/G131, 220 certified |
| Scope rule | every uncertified identity in `PRESERVE:SENSOR-HUB` (3) or `PRESERVE:CONNECTIVITY` (17) = **20**; disjoint from AUDIO-BATCH-01 (21) and PLATFORM-BATCH-04 (30); no modem/charging/USB module was added |
| Maintained source | `android_kernel_modules_scp_sensorhub_ulefone_gq5012bf1` @ `26507aa6`; `android_kernel_modules_connectivity_ulefone_gq5012bf1` @ `d0b9e10f` (not pushed; git bundles verified) |
| Provisional totals | this delta alone: **237 certified / 221 uncertified** (A236 B1 C12 D98 G111); with the unmerged AUDIO-BATCH-01 as well: 257 / 201. Claude's Batch04 is excluded |

## Per-module result

| Module | Initial | Final | Functions | Data | CRC/KCFI | Relocations | Source repo/commit | Residual |
|---|---|---|---|---|---|---|---|---|
| hf_manager | G | **A** | 41/41 | 34 | imp 68, exp 15, KCFI 3 | 929 identical | scp-sensorhub `26507aa6` | – |
| scp | G | **A** | 208/208 | 179 | imp 138, exp 27, KCFI 8 | 9309 identical | scp-sensorhub `26507aa6` | – |
| sensorhub | G | **A** | 102/102 | 95 | imp 87, exp 0, KCFI 1 | 1750 identical | scp-sensorhub `26507aa6` | – |
| connadp | G | **A** | 76/76 | 55 | imp 50, exp 44, KCFI 0 | 1252 identical | connectivity `d0b9e10f` | – |
| connscp | G | **A** | 104/104 | 76 | imp 73, exp 5, KCFI 0 | 2437 identical | connectivity `d0b9e10f` | – |
| mtk-btcvsd | G | **A** | 32/32 | 30 | imp 50, exp 0, KCFI 4 | 582 identical | connectivity `d0b9e10f` | – |
| uarthub_drv | G | **A** | 278/278 | 153 | imp 49, exp 61, KCFI 0 | 6987 identical | connectivity `d0b9e10f` | – |
| wifi_cooling | G | **A** | 8/8 | 19 | imp 13, exp 0, KCFI 0 | 58 identical | connectivity `d0b9e10f` | – |
| bt_drv_6878 | G | **A** | 294/294 | 136 | imp 187, exp 1, KCFI 9 | 10868 identical | connectivity `d0b9e10f` | – |
| connfem | G | **A** | 94/94 | 61 | imp 65, exp 8, KCFI 6 | 3121 identical | connectivity `d0b9e10f` | – |
| conninfra | G | **A** | 1356/1356 | 533 | imp 194, exp 81, KCFI 287 | 24964 identical | connectivity `d0b9e10f` | – |
| fmradio_drv_connac2x | G | **A** | 365/365 | 90 | imp 115, exp 1, KCFI 8 | 11660 identical | connectivity `d0b9e10f` | – |
| gps_drv_dl_v051 | G | **A** | 550/550 | 138 | imp 124, exp 0, KCFI 1 | 9612 identical | connectivity `d0b9e10f` | – |
| gps_pwr | G | **A** | 12/12 | 20 | imp 24, exp 0, KCFI 0 | 203 identical | connectivity `d0b9e10f` | – |
| gps_scp | G | **A** | 15/15 | 23 | imp 31, exp 0, KCFI 0 | 349 identical | connectivity `d0b9e10f` | – |
| wlan_drv_gen4m_6878 | G | **A** | 5682/5682 | 981 | imp 390, exp 0, KCFI 941 | 123295 identical | connectivity `d0b9e10f` | – |
| wmt_chrdev_wifi_connac2 | G | **A** | 28/28 | 48 | imp 40, exp 18, KCFI 0 | 1145 identical | connectivity `d0b9e10f` | – |
| bluetooth | G | **C** | 1257/1257 | 176 | imp 219, exp 72, KCFI 26 identical | 15797 identical | connectivity `d0b9e10f` | `.BTF` 14551/215660 B: base refs only |
| cfg80211 | G | **C** | 1435/1435 | 1998 | imp 195, exp 147, KCFI 13 identical | 21249 identical | connectivity `d0b9e10f` | `.BTF` 25249/398337 B: base refs only |
| mac80211 | G | **C** | 1420/1420 | 1408 | imp 319, exp 131, KCFI 34 identical | 20008 identical | connectivity `d0b9e10f` | `.BTF` 26027/363011 B: base refs only |

C rows: every byte outside `.BTF` and the GNU build ID is identical. That covers all code, data, relocations, symbol tables,
import/export CRCs, KCFI IDs, `intree=Y`, `scmversion` and `vermagic`, so the stock counts listed are fully matched.
Exact per-axis values are in `BATCH-PARITY.tsv`; full ledgers are under `evidence/*/cleancheck/acceptance-B1/`.
A modules match the whole file after zeroing only the 20-byte GNU build-ID descriptor. Totals for the 17 A:
9 245 functions, 2 671 objects, 1 698 import CRCs, 261 export CRCs, 1 268 KCFI IDs and 208 521 relocations.

## Recovered rather than redone

- **Sensors.** The historical reconstruction (`reverse-engineering/sensors`, KDM 7d3c303 on 957dac1) was re-expressed on ALPS.
  Its `scp/rv` half turned out to be **byte-identical to pristine ALPS 5e41**, so scp.ko needs no patch at all.
  Only the four sensor-2.0 YFT files remain, as scp-sensorhub patch 0002.
- **Connectivity.**
  - The historical kernel_modules trees equal NothingOSS `2115d27` (V9.9) except the 13-hunk V11.24 wlan backport, which is kept verbatim as patch nkm/0003.
  - The historical KDM tree ids for connectivity, conn_scp, uarthub, wifi_cooling, power_throttling and btcvsd are identical to the ALPS 5e41 trees.
- **Recipe facts carried over.** The `../vendor/...` location, empty `TARGET_BUILD_VARIANT` and `DRIVER_BUILD_DATE` were recovered from the historical recipe and are now pinned and checked.

## New findings

1. **scp.ko is pristine ALPS.** The "Ulefone deltas" previously attributed to the SCP host (DT `awake-timeout`, WFI wait,
   CHRE check, freq re-request) are the ALPS 5e41 revision of public source (`SCP-HOST-INTERFACES.md`).
2. **uarthub platform selection.** The absolute-M build lost `mt6985`/`mt6989` platform objects. The cause is
   `PATH_TO_UARTHUB_DRV := $(srctree)/$(src)`, which resolves only in the vendor's relative-M layout. It was fixed by a
   Kbuild path spelling (`patches/kdm/0009`), not by any code change (`evidence/uarthub-scope/`).
3. **The in-tree modules are now built genuinely in-tree.** A `KBUILD_MIXED_TREE` build lets the authentic modpost emit `intree=Y`.
   This replaces the historical `intree_relink.sh`, which edited `.mod.c` after the build. All non-BTF bytes are identical.
4. **One OEM BTF base explains every vendor in-tree BTF module.** For cfg80211, mac80211 and bluetooth, the `.BTF` header,
   string table, record count and reference positions are identical. The differing words are only type-ID and name-offset
   references, with bijective mappings shifted by +15 types and +389 string bytes. A census of all 11 stock vendor in-tree
   modules with BTF (including Batch03's thermal-generic-adc) shows the same OEM base of exactly 130 366 types; the public base has 130 351.
   The OEM vmlinux `g945dff7bc1bf` is not public, and the device boots the public 12901745 kernel. These modules therefore stay **C**.
   The single next experiment is in `BLOCKERS.tsv`.
5. **Provider ABI.** There are 57 external slots:
   - 47 are reproduced by genuine compiled witnesses (ALPS and public common), each matching CRC, licence, namespace, type and KCFI prefix.
   - 10 `yft_devinfo` slots for hf_manager are `STOCK_PROVIDER_EXPORT`. The provider is ODM-private; one vendor enum tag is
     unrecoverable (about 1.4e13 spellings already excluded). This follows the canonical CAMERA-ISP-KERNEL precedent.

   No provider classification changed (`PROVIDER-BOUNDARIES.tsv`).

## Validation

- Development: SCP 3/3 and connectivity 17/17 built, and all external boundaries were witnessed.
- Clean clone:
  - SCP: 3+3 ko, 54 .o, 42 exports identical.
  - Connectivity: 17+17 ko, 577 .o, 725 symbol records identical.
  - Witnesses, configs and source trees are identical, and both builds accept.
- Mutation tests: 23/23 and 29/29, including C-gate rejection of code, data, CRC, modinfo, BTF-string and BTF-encoding mutations.
- Audit delta: applied to a scratch clone, 20 rows, 8 mapped fields, 458 identities. Wrong-class, unknown-identity and double-apply cases are rejected (`evidence/audit-delta-test.json`).
- `scripts/validate-batch.py` passes.
- Safety:
  - Offline only: no ADB, flashing, module loading, SCP/radio commands or register access.
  - Claude's checkout, branch and builds were untouched, and so was the audio branch and repository.
  - Nothing was pushed.
