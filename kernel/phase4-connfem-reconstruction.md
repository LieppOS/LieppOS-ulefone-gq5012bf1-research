# Phase 4 — `connfem.ko` targeted reconstruction (Ulefone GQ5012BF1)

## Result

```text
Classification: ABI_EXACT_RECONSTRUCTION
```

The reconstruction builds against exact GKI 12901745 and matches the stock
module on every interface-level property that can be derived from the binary:

| property | stock | reconstruction | verdict |
|---|---|---|---|
| module metadata (name/license/description/authors/depends) | — | — | **exact** |
| module parameters | 5 | 5 | **exact** |
| imports | 64 | 64 | **exact** (0 missing, 0 extra) |
| import MODVERSION CRCs | 65 | 65 | **exact** (0 mismatches) |
| exports | 8 | 8 | **exact** (0 missing, 0 extra) |
| export CRCs | 8 | 7 exact | 1 unmatchable (see below) |
| **consumer-required export ABI** | 4 | 4 | **PRESERVED** |
| function set | 94 | 94 | **exact** (0 missing, 0 extra) |
| function sizes | — | 62 / 94 identical | partial |
| function bytes | — | 52 / 94 identical | partial |
| `cfm_epa_ctx` / `cfm_sku_ctx` / `cfm_ctx` sizes | 1112 / 21472 / 24 | 1112 / 21472 / 24 | **exact** |
| `.text` | 38408 | 33860 | differs |

It is **not** claimed to be byte-exact. The 38 new SKU functions are
behaviourally reconstructed from disassembly, not statement-identical.

Artifacts:

- source + `.ko` + `Module.symvers` + `Makefile` + `BUILD.bazel` + `SHA256SUMS`
  + donor→final patch: `$GKI_WS/lieppos/connfem-recon/final/`
- validation report: `$AN/final/validation.txt`
- structure derivation: `$AN/structure-recovery.md`
- consumer ABI map: `$AN/consumer-boundary.tsv`, `$AN/consumer-boundary.md`
- function classification: `$AN/function-classification.tsv`
- per-iteration evidence: `$GKI_WS/lieppos/connfem-recon/iterations/iter01…08`

Nothing was flashed, no partition, DTBO or device tree was touched, and no
symbol CRC was fabricated — every CRC in this report was read out of a binary.

---

## Required research conclusions

1. **NothingOSS MT6878 provides a valid older MediaTek ConnFem base.** Built
   unchanged against exact GKI 12901745 it already reproduced 36 byte-identical
   functions and 5 of 6 export CRCs, including all four that stock consumers
   actually import.
2. **Stock Ulefone contains a newer SKU/truth-table subsystem.** 38 functions,
   a 21472-byte SKU context, a truth-table/usage model and a config-file header
   dispatcher that have no counterpart in the donor.
3. **NothingOSS lacks** `connfem_sku_data`, `connfem_sku_flag_u8` and the whole
   `cfm_sku_*` family.
4. **Local source/ref searches found no public copy of this stock revision.**
   Re-confirmed; no new tree was discovered during this phase.
5. **The local Nothing repo contains one available commit/ref only**
   (`5f75a3b13e8135d45b4b0b70ec893345144f70df`, branch `mt6878/Tetris/u`,
   shallow/grafted), so no historical revision could be bisected.
6. **Stock `connfem.ko` is self-contained w.r.t. vendor `.ko` dependencies** —
   `depends` is empty and all 64 imports are ordinary kernel/GKI symbols.
7. **MT6878 public DTS exists but is not Ulefone hardware data.** No value from
   `cust_mt6878_connfem.dtsi` was copied into the reconstruction; the driver
   contains no device-specific FEM identity.
8. **Every reconstruction decision is tied to stock binary evidence** —
   recorded in `structure-recovery.md` with the exact instruction, object size
   or relocation each decision rests on.

---

## What the binary proved

### Consumer ABI boundary (task 1)

All 471 stock `.ko` files were scanned. Only **two** modules consume ConnFem,
using only **four** of the eight exports:

```text
bt_drv_6878.ko           get_fem_info, get_flags, get_pin_info
wlan_drv_gen4m_6878.ko   get_fem_info, get_pin_info, laa_get_pin_info
```

All six import CRCs match the stock provider's export CRCs exactly (0
mismatches). The two stock-only SKU exports have **no consumer at all** in this
image, which bounds how much the SKU ABI can matter in practice.

### The architectural change

Stock replaces the donor's single flat `struct connfem_context` (plus nine
per-SoC static instances of 1080 bytes) with a **polymorphic context**: a
56-byte header carrying a type tag and four operations, and two concrete
contexts dispatched through a type-indexed table.

```c
struct connfem_context {          /* 56 bytes */
        unsigned int id;                                          /* +0x00 */
        struct platform_device *pdev;                             /* +0x08 */
        enum connfem_type type;                                   /* +0x10 */
        enum cfm_src src;                                         /* +0x14 */
        void (*context_free)(struct connfem_context *);           /* +0x18 */
        int  (*dt_parse)(struct connfem_context *);               /* +0x20 */
        int  (*flags_config_get)(struct connfem_context *,
                                 struct cfm_epaelna_flags_config **); /* +0x28 */
        int  (*available_get)(struct connfem_context *, bool *);  /* +0x30 */
};

cfm_ctx[] = { NULL, &cfm_epa_ctx, &cfm_sku_ctx };   /* 24 B, .data */
```

This was read directly from the static initialisers of `cfm_epa_ctx` and
`cfm_sku_ctx`, which name all four operations in relocations. `enum
connfem_type` gains `CONNFEM_TYPE_SKU = 2`; adding that enumerator is what
brought `connfem_is_available`'s CRC from `0xf6db78aa` to the stock
`0x6a71e6aa`.

Size arithmetic closed exactly and independently:

```text
cfm_epa_ctx = 56 + 424 (cfm_dt_context) + 632 (cfm_epaelna_config) = 1112  OK
cfm_sku_ctx = 56 + 4 + 1 + pad + 21288 (cfm_sku_data)
                 + 48 (cfm_dt_epaelna_flags_context) + 72 (flags_cfg) = 21472  OK
```

The 48-byte member was identified from two independent facts: it is exactly
`sizeof(struct cfm_dt_epaelna_flags_context)`, and stock
`cfm_sku_context_free()` calls `cfm_dt_epaelna_flags_free()`.

### Flag subsystem (Priority 6)

The donor's `connfem_epaelna_subsys_cb` callback model is **retained
unchanged**; only the flag structs and name maps were extended. Field order and
offsets were read out of the `.data` flag maps with relocations resolved:

```text
bt: +efem_mode ("efem-mode"), +rxmode ("rx-mode")            4 -> 6 bytes
wf: +nv_attr ("nv-attr")                                      4 -> 5 bytes
cm: +fe_conn_dpdt_sp3t, +fe_bt_wf_usage, +fe_conn_spdt_2      6 -> 9 bytes
```

This exactly reproduces the nine `CmFlags.*` names in the task brief, and all
six flag objects/maps now match stock byte-size exactly.

### Config-file dispatch (Priority 3)

`header_table` in `.rodata` gave the four magics, and `cfm_cfg_process`'s
disassembly gave the dispatch:

```text
"CFM:cpy-sku" 1 -> cfm_ctx[SKU],     cfm_cfg_copy_sku_hdl()
"CFM:legacy"  2 -> cfm_ctx[EPAELNA], cfm_cfg_legacy_hdl()
"CFM:hw-name" 3 -> cfm_cfg_parse_hw_name()
"CFM:hwid"    4 -> cfm_cfg_parse_hwid()
none / size<0x20 -> cfm_ctx[EPAELNA], cfm_cfg_legacy_hdl(…, NULL)
```

Critically, stock **never allocates** a context here — it selects one of the two
static contexts. That is why stock imports only `__kmalloc` and no
constant-size `kmalloc` helper. Porting the donor's `kzalloc(sizeof(struct
connfem_context))` onto the new 56-byte header would have been a real heap
overflow; the binary caught it (the build acquired a `__write_overflow_field`
import that stock does not have), and removing the allocation eliminated it.

### SKU data model (Priorities 1, 4, 5)

Recovered from `cfm_sku_data_dump`, `cfm_sku_get_tt_usage_wf/bt`,
`connfem_sku_data`, `cfm_sku_flags_config_get` and `connfem_dev_read`:

```c
struct cfm_sku_fem {                       /* 0x9E4 = 2532, bound 8 */
        unsigned int id; unsigned short vid, pid; unsigned int flag;
        char name[64];
        unsigned int ctrl_pin_cnt; unsigned char ctrl_pin[8];
        unsigned int ttbl_cnt; struct {u32 op, bin;} ttbl[32];
        struct cfm_sku_tt_usage tt_usage[2];   /* wf @0x15C, bt @0x5A0 */
};                                             /* 0x15C + 2*0x444 = 0x9E4 exact */
```

`connfem_dev_read` (a new `.read` fops handler absent from the donor) exposes
the context window `[0x38, 0x5368)` in 0x800-byte chunks, which independently
fixes `sizeof(struct cfm_sku_data) == 21288`.

---

## Remaining differences

1. **`connfem_sku_data` export CRC** (stock `0x65186bbd`, built `0x97327a3b`).
   genksyms hashes the fully expanded parameter type. Stock's parameter is a
   pointer to a concrete struct whose *field names* are not recoverable from a
   stripped binary. Confirmed not to be an opaque pointer — a `void **`
   prototype yields `0xb301c4e5`, also not the stock value. **No module in the
   stock image imports this symbol**, so no load can fail because of it.
2. **`.text` size and content.** The SKU subsystem is behaviourally
   reconstructed; statement-level structure is not recoverable from a binary.
   52/94 functions are byte-identical and 62/94 size-identical.
3. **`vermagic` and `__UNIQUE_ID_*` suffixes.** Build-id/`__COUNTER__` position
   only; all corresponding object sizes are identical.
4. **One unresolved constant.** `cfm_sku_data_dump`'s layout bounds trap is
   `cmp #0x11` (17) while every size constraint (the `connfem_dev_read` window,
   the final pin dump offsets, and the 21472-byte context total) requires a
   16-entry layout array. Recorded rather than papered over.

---

## Ulefone DT/DTBO items still to recover

The driver reconstruction is complete and hardware-agnostic. Configuring it for
this phone is a **separate task** and still needs the following read out of the
stock Ulefone DT/DTBO (the hardware oracle — *not* the NothingOSS DTSI):

- which `connfem` compatible the Ulefone DT uses (stock added a generic
  `mediatek,connfem` alongside `mediatek,mt6878-connfem`);
- whether the ConnFem node carries a `sku` / `sku-mtk` child (SKU mode) or an
  `epa-elna` / `epa-elna-mtk` child (legacy mode) — this alone selects the
  context type at probe;
- FEM `vid`/`pid`/`name`/`flag` entries and per-FEM control-pin ids;
- truth-table entries and per-subsystem truth-table usage categories;
- layout entries: `fem_idx`, `bandpath-wf`, `bandpath-bt`, ANTSEL `pinmap`
  triples;
- pinctrl states, ANTSEL GPIOs, and PMIC/IIO HWID inputs;
- whether a `connfem.cfg` config file is shipped and, if so, which header magic
  it carries.

No DTBO was modified in this phase.

---

## Build

```bash
cd ~/kernel-work/gki-12901745-workspace
tools/bazel build //lieppos/connfem-recon/src:connfem_gki
```

Builds clean with the donor's `-Wall -Werror`, `CONNFEM_DBG=0`,
`CONNFEM_TEST_ENABLED=0`, and without `connfem_internal.o` (no stock evidence
for internal mode was found). The only build-environment change relative to the
donor Kbuild is absolutising `$(src)` for the `-I` path, which is the donor's
own `KO_CODE_PATH` idiom.

## Integration freeze classification

For strict terminology, the reconstruction is frozen as:

`STOCK_CONSUMER_ABI_EXACT_RECONSTRUCTION`

All 471 stock modules were scanned. Only:

- `bt_drv_6878.ko`
- `wlan_drv_gen4m_6878.ko`

consume ConnFem.

Together they consume four ConnFem exports through six imports, and all six
MODVERSION CRCs match the reconstructed provider exactly.

Therefore the complete ConnFem ABI actually exercised by the Ulefone stock
image is preserved.

One exported but unused API, `connfem_sku_data`, has a different genksyms CRC
because the stripped stock binary cannot reveal the original field names of
its concrete parameter struct. No stock module imports this symbol.

This does not block stock BT/WLAN consumers or initial LieppOS custom-kernel
integration.

Further statement-level reconstruction of the SKU subsystem is deferred unless
DT/DTBO recovery or runtime integration testing exposes a concrete behavioral
difference.

## Ulefone ConnFem firmware/config discovery

The stock Ulefone vendor partition contains:

`vendor/firmware/connfem.cfg`

This is significant because the reconstructed stock ConnFem revision contains
explicit config-file dispatch support for:

- `CFM:cpy-sku`
- `CFM:legacy`
- `CFM:hw-name`
- `CFM:hwid`

The file's header/content has not yet been classified. It must be inspected
before deciding whether this device actively uses the reconstructed SKU
subsystem or the legacy ePA/eLNA path.

Hardware/configuration recovery remains separate from the already-frozen
ConnFem driver reconstruction.

## Stock `connfem.cfg` is an empty placeholder

The Ulefone stock image contains:

`vendor/firmware/connfem.cfg`

but the file is exactly zero bytes.

Observed:

- size: `0`
- SHA256:
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `file`: `empty`
- no strings
- no ConnFem config header magic

Therefore the stock image does not provide any of the reconstructed config
payloads through this file:

- `CFM:cpy-sku`
- `CFM:legacy`
- `CFM:hw-name`
- `CFM:hwid`

The earlier note that the config-file header was still unclassified is
superseded.

This strongly shifts hardware/configuration recovery toward the stock Ulefone
DT/DTBO.

ConnFem itself is demonstrably active in the stock userspace integration:

- `connfem.ko` is present in `modules.load`;
- `bt_drv_6878.ko` depends on it;
- `wlan_drv_gen4m_6878.ko` depends on it;
- `/dev/connfem` is created with system access;
- SELinux defines `connfem_device`;
- `nvram_daemon` is permitted to access the ConnFem character device.

Next requirement:

Recover the Ulefone stock ConnFem node from DT/DTBO/vendor_boot and determine
whether the phone selects:

- SKU / SKU-MTK mode, or
- legacy EPA/eLNA mode,

followed by its actual FEM IDs, layouts, truth tables, ANTSEL/pinctrl and HWID
configuration.

## GQ5012BF1 ConnFem runtime mode confirmed

The captured live device-tree topology contains:

`/sys/firmware/devicetree/base/connfem/epa-elna-mtk`

with:

- `bt`
- `wifi`
- `hwid`
- BT `flags-*` nodes
- Wi-Fi `flags-*` nodes

No `connfem/sku` or `connfem/sku-mtk` node was found.

Together with the stock zero-byte `vendor/firmware/connfem.cfg`, this confirms
that GQ5012BF1 uses the legacy MediaTek ePA/eLNA ConnFem configuration path,
not the newer SKU/truth-table context.

Classification:

`GQ5012BF1_CONNFEM_MODE = EPAELNA_MTK_LEGACY`

Integration consequence:

The reconstructed SKU subsystem remains necessary for complete reconstruction
of the stock module, but it is not on the active ConnFem configuration path
for this device.

The runtime-critical configuration to recover is now limited to the stock
`epa-elna-mtk` DT subtree:

- HWID selection
- Wi-Fi flags
- Bluetooth flags
- FEM identities
- pin mappings
- pinctrl states
- ANTSEL configuration

## Live ConnFem DT topology — complete node catalog

The previously captured live device-tree topology provides the complete
GQ5012BF1 ConnFem child-node list.

The root contains FEM definition nodes:

- `nofem`
- `wlan7207h`
- `wlan7207c`
- `qm42195`
- `qm45197`
- `sky85320`
- `sky85720`
- `mxd7751s`
- `rtc7620`
- `sky85732`

and the active configuration subtree:

`connfem/epa-elna-mtk`

with:

- `hwid`
- `bt`
- `wifi`
- BT `flags-3` through selected `flags-11` nodes
- Wi-Fi `flags-3` through selected `flags-11` nodes

The first eight FEM definitions substantially overlap the public MT6878
ConnFem reference DTS, while `rtc7620` and `sky85732` are additional entries
present in the Ulefone runtime tree.

These FEM nodes represent the available hardware-definition catalog and do
not by themselves prove which FEM combination is physically selected.
Selection must be recovered from the `epa-elna-mtk` HWID/config properties.

ADB was unavailable during this pass, but this is not a blocker because exact
backups already exist for:

- `vendor_boot_a.img`
- `dtbo_a.img`

Offline DT extraction is therefore the next hardware-recovery step.

## Offline stock DT/DTBO recovery

Exact offline extraction recovered:

- one base DTB from `vendor_boot_a.img`
- one Android DTBO table entry from `dtbo_a.img`

Base DTB:

- size: `342331`
- contains the stock ConnFem platform node
- compatible: `mediatek,mt6878-connfem`

The DTBO contains a single overlay entry and `fragment@39` explicitly targets
the base `connfem` node.

Fragment 39 adds the GQ5012BF1-specific:

`epa-elna-mtk`

subtree.

Therefore the ConnFem hardware split is now proven:

- `vendor_boot` DTB: MT6878 generic FEM definitions and pinctrl catalog
- `dtbo` fragment 39: GQ5012BF1 FEM selection/configuration

The overlay HWID property uses three GPIOs:

- GPIO 131
- GPIO 132
- GPIO 92

The overlay `parts` property contains 24 FEM references. From `__fixups__`,
their resolved order is:

0. nofem
1. nofem
2. nofem
3. nofem
4. nofem
5. nofem
6. mxd7751s
7. mxd7751s
8. sky85320
9. sky85720
10. sky85320
11. sky85720
12. qm42195
13. qm45197
14. wlan7207h
15. wlan7207c
16. nofem
17. sky85732
18. nofem
19. sky85732
20. nofem
21. qm45197
22. rtc7620
23. nofem

Viewed as consecutive two-FEM entries this yields:

- nofem + nofem
- nofem + nofem
- nofem + nofem
- mxd7751s + mxd7751s
- sky85320 + sky85720
- sky85320 + sky85720
- qm42195 + qm45197
- wlan7207h + wlan7207c
- nofem + sky85732
- nofem + sky85732
- nofem + qm45197
- rtc7620 + nofem

The generic base DTB pinctrl catalog independently contains matching pair
names:

- `wlan7207h-wlan7207c`
- `qm42195-qm45197`
- `sky85320-sky85720`
- `mxd7751s-mxd7751s`
- `nofem-sky85732`
- `nofem-qm45197`
- `rtc7620-nofem`

This proves the Ulefone overlay uses the same base MT6878 ConnFem hardware
catalog while extending it with Ulefone-selected combinations.

The actual runtime-selected HWID/FEM pair has not yet been established and
must not be guessed. It will be recovered from historical ConnFem logs or a
future read-only runtime observation.

Next:

1. apply the stock DTBO to the extracted vendor_boot DTB offline;
2. decompile the merged FDT;
3. validate it against the previously captured live DT topology;
4. recover the runtime HWID and therefore the physically selected FEM pair.

## Offline merged DT validation

The exact stock `vendor_boot_a` base DTB and exact stock `dtbo_a` overlay were
successfully merged offline using `fdtoverlay`.

Result:

- `fdtoverlay` return code: `0`
- merged DTB SHA256:
  `7ce69ab5bb4f9714446a262966d0478409a7e00a70c8f6d781461f9abb301104`

The final merged FDT contains:

`connfem`

with:

- compatible: `mediatek,mt6878-connfem`
- Ulefone overlay subtree: `epa-elna-mtk`
- HWID GPIOs:
  - GPIO 131
  - GPIO 132
  - GPIO 92

The merged FEM catalog is:

| FEM | VID | PID |
|---|---:|---:|
| nofem | 0 | 0 |
| wlan7207h | 2 | 4 |
| wlan7207c | 2 | 7 |
| qm42195 | 3 | 1 |
| qm45197 | 3 | 2 |
| sky85320 | 1 | 1 |
| sky85720 | 1 | 2 |
| mxd7751s | 4 | 1 |
| sky85732 | 1 | 3 |
| rtc7620 | 6 | 1 |

The stock Ulefone overlay configures Bluetooth flags as:

- flags-3: bypass
- flags-4: bypass
- flags-5: bypass
- flags-6: epa-elna
- flags-7: epa-elna
- flags-8: epa-elna
- flags-9: bypass
- flags-10: epa-elna
- flags-11: epa-elna

Wi-Fi contains flags-3 through flags-11 as empty flag nodes.

The standalone-DTBO phandle fixups were resolved successfully by applying the
overlay to the stock base DTB, validating that the extracted images form a
coherent stock device-tree pair.

### Parts-array interpretation correction

An earlier intermediate note interpreted the 24-element `parts` array as 12
consecutive FEM pairs.

That interpretation is now considered provisional and must not be treated as
the final hardware mapping until the MediaTek driver's exact
`cfm_dt_epaelna_parts_parse()` indexing logic is checked.

There are three HWID GPIOs, implying eight possible hardware IDs, and the
24-element parts array may therefore encode a multi-element record for each
HWID rather than twelve independent pairs.

The raw resolved 24-element phandle order remains valid evidence; only its
semantic grouping is pending source-level confirmation.

The actual runtime-selected HWID also remains unknown and must not be guessed.

## ConnFem HWID selection semantics recovered

The public MediaTek parser confirms the exact parts-selection formula:

`start = hwid * CONNFEM_PORT_NUM`

followed by `CONNFEM_PORT_NUM` phandles starting at that index.

Therefore the DT `parts` property is an HWID-indexed table; it is not an
unordered FEM catalog.

The exact value of `CONNFEM_PORT_NUM` is being confirmed from the public
header before final grouping is frozen.

The GPIO HWID calculation is fully recovered.

The GQ5012BF1 DT orders the HWID GPIOs as:

- index 0: GPIO 131
- index 1: GPIO 132
- index 2: GPIO 92

The driver computes:

`hwid |= ((gpio_value & 1) << index)`

Therefore:

`HWID = GPIO131 | (GPIO132 << 1) | (GPIO92 << 2)`

and the three GPIOs naturally encode HWID values 0 through 7.

The parser then uses that same HWID to select:

- the corresponding `parts` group;
- `wifi/flags-<hwid>`;
- `bt/flags-<hwid>`.

The actual GPIO electrical values on this handset remain to be recovered.

## GQ5012BF1 HWID source narrowed

The public ConnFem donor has:

`CFG_HWID_PMIC_SUPPORT = 1`

so the driver is capable of extending the GPIO-derived HWID with PMIC/IIO
bits.

However, the final merged GQ5012BF1 device tree contains only:

`connfem/epa-elna-mtk/hwid/gpio`

with three GPIO entries:

- GPIO 131
- GPIO 132
- GPIO 92

There is no PMIC child under the GQ5012BF1 ConnFem HWID node.

Therefore the normal DT-driven HWID on this device is GPIO-only:

`HWID = GPIO131 | (GPIO132 << 1) | (GPIO92 << 2)`

unless the `epa_elna_hwid` module parameter is explicitly overridden.

A search for such an override is the remaining configuration check.

## ConnFem parts table semantics finalized

`CONNFEM_PORT_NUM` is definitively 2.

Public header defines:

    enum connfem_rf_port {
        CONNFEM_PORT_BT = 0,
        CONNFEM_PORT_WFG = CONNFEM_PORT_BT,
        CONNFEM_PORT_WFA = 1,
        CONNFEM_PORT_NUM
    };

Therefore:

- port 0 = BT / WFG
- port 1 = WFA

The MediaTek parser selects parts using:

    start = hwid * CONNFEM_PORT_NUM

and reads exactly `CONNFEM_PORT_NUM` phandles.

Therefore the Ulefone 24-element `parts` property is definitively:

12 HWID groups x 2 RF ports.

Final table:

| HWID | BT/WFG | WFA |
|---:|---|---|
| 0 | nofem | nofem |
| 1 | nofem | nofem |
| 2 | nofem | nofem |
| 3 | mxd7751s | mxd7751s |
| 4 | sky85320 | sky85720 |
| 5 | sky85320 | sky85720 |
| 6 | qm42195 | qm45197 |
| 7 | wlan7207h | wlan7207c |
| 8 | nofem | sky85732 |
| 9 | nofem | sky85732 |
| 10 | nofem | qm45197 |
| 11 | rtc7620 | nofem |

The GQ5012BF1 HWID node contains three GPIO selectors in this order:

- GPIO 131 -> bit 0
- GPIO 132 -> bit 1
- GPIO 92 -> bit 2

The driver computes:

    HWID = GPIO131 | (GPIO132 << 1) | (GPIO92 << 2)

Therefore normal GPIO-derived HWIDs are limited to 0 through 7.

Although `CFG_HWID_PMIC_SUPPORT = 1` in the driver, the merged GQ5012BF1
ConnFem HWID node contains no PMIC child.

A stock-tree search also found no actual `epa_elna_hwid` module-parameter
override. Matches were limited to research/documentation and the DT HWID node.

Therefore HWID groups 8 through 11 are present in the platform DT catalog but
are not currently known to be reachable during normal GQ5012BF1 operation.

The only remaining hardware-selection unknown is the electrical state of:

- GPIO 131
- GPIO 132
- GPIO 92

Once those three values are observed on the handset, the physically selected
FEM pair is determined exactly.

## Live ConnFem HWID observation attempt

A live stock-runtime observation was attempted with KernelSU root.

Confirmed:

- ADB connected successfully.
- KernelSU root works:
  `uid=0(root) gid=0(root) context=u:r:ksu:s0`.
- root `dmesg` access works.
- the current dmesg ring no longer contains the original ConnFem probe
  messages; only unrelated CMDQ `hwid` messages were found.
- `/sys/kernel/debug/gpio` is not present.
- `/sys/kernel/debug/pinctrl` is not present.
- no GPIO direction, GPIO export, pinctrl state or partition was modified.

`/proc/kmsg` was verified readable as root, but it should not be used for
continued investigation because reading it consumes the live kernel-message
stream.

Therefore direct GPIO debugfs observation is unavailable in this runtime.

Preferred remaining read-only paths are:

1. retained Android `logcat` kernel/all buffers;
2. live ConnFem module parameters;
3. the existing `/dev/connfem` read/ioctl ABI, allowing the running stock
   driver to report its already-selected FEM configuration directly.

No active GPIO manipulation is required.

## Live stock ConnFem parameter state

Read-only observation of the loaded stock ConnFem module showed:

- `epa_elna_hwid = 4294967295` (`0xffffffff`)
- `hwid = 4294967295` (`0xffffffff`)
- `hw_name` empty
- `config_file = connfem.cfg`
- `connfem_major = 478`

Both HWID parameters therefore contain their invalid/default sentinel rather
than a forced hardware ID.

The stock `connfem.cfg` has previously been proven to be exactly zero bytes.

Consequently there is currently no evidence of either:

- a module-parameter HWID override, or
- a config-file-provided FEM selection.

The running stock ConnFem instance therefore uses the device-tree ePA/eLNA
configuration and its hardware-derived HWID.

The public ConnFem ABI also exposes the read-only:

`CFM_IOC_EPA_INFO`

ioctl.

Its handler retrieves the already-selected
`connfem_epaelna_fem_info` and copies it to userspace.

This provides a preferable method for identifying the physically selected
FEM pair: query `/dev/connfem` through the stock driver's existing read-only
ABI rather than manipulating HWID GPIOs.

The exact ioctl structure size must be confirmed before issuing the command,
because Linux `_IOR()` encodes `sizeof(struct cfm_ioc_epa_info)` in the ioctl
number.

## Live ConnFem ioctl ABI confirmed

The public donor and final stock reconstruction agree on the legacy ePA/eLNA
userspace ioctl:

`CFM_IOC_EPA_INFO`

defined as:

`_IOR(0xCF, 0x03, struct cfm_ioc_epa_info)`

For the recovered ABI:

- `CONNFEM_PORT_NUM = 2`
- `CONNFEM_PART_NAME_SIZE = 64`
- `sizeof(struct connfem_part) = 2`
- `sizeof(struct cfm_ioc_epa_info) = 136` (`0x88`)

Therefore the Linux ioctl command is:

`0x8088cf03`

The handler calls `connfem_epaelna_get_fem_info()` and copies the resulting
already-selected FEM information directly to userspace.

The live stock character device is:

`/dev/connfem`

with:

- major: 478
- minor: 0
- SELinux type: `connfem_device`

and the loaded module parameter reports:

`connfem_major = 478`

This establishes a read-only path for determining the handset's selected
physical FEM configuration without GPIO manipulation.

## Live CFM_IOC_EPA_INFO query attempt

A small ARM64 Android userspace helper was built against the recovered legacy
ConnFem ioctl ABI and executed on the stock GQ5012BF1 runtime.

Verified helper ABI:

- `sizeof(struct cfm_ioc_epa_info) = 136`
- `CFM_IOC_EPA_INFO = 0x8088cf03`
- binary target: ARM64 Android
- `/dev/connfem` opened successfully

The ioctl returned:

`errno 95: Operation not supported on transport endpoint`

This proves userspace can reach the live stock ConnFem character device.

At this stage errno 95 has two possible origins:

1. stock `connfem_dev_unlocked_ioctl()` rejected `0x8088cf03`, implying a
   Ulefone-specific userspace ioctl ABI difference; or
2. `CFM_IOC_EPA_INFO` matched and its handler returned `-EOPNOTSUPP` while
   retrieving the runtime FEM information.

Recent ConnFem kernel logs must be inspected immediately after issuing the
ioctl to distinguish those two cases before changing the query helper.

## Live legacy ePA/eLNA availability result

The live `CFM_IOC_EPA_INFO` experiment has now been resolved.

The stock binary directly compares the ioctl command against:

`0x8088cf03`

and on a match calls:

`connfem_epaelna_get_fem_info`

Therefore the recovered userspace ioctl ABI is exact for this operation.

Immediately after issuing the ioctl, stock kernel logs reported:

`connfem_is_available: FEM is not available`

and:

`connfem_epaelna_get_fem_info, Not support`

The returned userspace error was:

`-EOPNOTSUPP` / errno 95.

Therefore the ioctl was not rejected. The stock driver intentionally reports
that its legacy ePA/eLNA FEM state is unavailable.

This invalidates the earlier assumption that the only remaining unknown was
simply the three electrical HWID GPIO levels.

A likely explanation is that the hardware-derived HWID selects one of the
`nofem + nofem` records (HWID 0, 1 or 2), causing a zero FEM ID and an
unavailable legacy FEM state. This must be confirmed against the public DT
population/availability semantics before being frozen.

Alternative explanations such as a DT parse failure or selection of another
ConnFem configuration path remain possible until that source check is done.

## ConnFem availability semantics narrowed

Public MediaTek ConnFem DT parsing sets legacy ePA/eLNA availability only when
the populated FEM ID is non-zero:

    if (result->fem_info.id)
        result->available = true;

The FEM ID is constructed directly from the VID/PID values of both selected
RF-port part nodes.

Therefore a `nofem + nofem` selection, whose VID/PID values are all zero,
produces:

`fem_info.id = 0`

and does not set legacy ePA/eLNA availability.

Live stock runtime observation showed the ePA/eLNA availability query
returning false and `connfem_epaelna_get_fem_info()` returning
`-EOPNOTSUPP`.

Stock disassembly further confirms that `connfem_epaelna_get_fem_info()`:

- requires a valid ConnFem context;
- requires the expected context type;
- calls the context availability callback;
- requires that callback to return a true availability result;
- only then copies the 136-byte FEM-info structure to the caller.

The stock and reconstructed implementations are structurally equivalent at
this boundary.

This makes an HWID selecting `nofem + nofem` (HWID 0, 1 or 2 on the
GQ5012BF1 DT table) the leading explanation for the live unavailable state.

However, this is not yet frozen as the final physical-HWID conclusion because
a DT parsing failure could also leave the availability state false. The
availability callback implementation and initialization path should be
confirmed before eliminating that alternative.

## ConnFem availability callback resolved

The reconstructed stock context dispatch table assigns:

    cfm_epa_ctx.hdr.available_get = cfm_epaelna_available_get;

and the callback implementation is:

    *available = cfm_epa(cfm)->available;

with no additional availability policy.

Stock and reconstructed `connfem_is_available()` have equivalent control
flow:

- validate the global context;
- require the requested type to match the registered context type;
- invoke the context `available_get` callback;
- return true only when that callback succeeds and reports true.

Therefore the live stock result:

`connfem_is_available: FEM is not available`

means the registered EPA/eLNA context's own `available` field is false.

Both recovered configuration paths set that field only when the populated
legacy FEM ID is nonzero:

- DT parsing: `if (result->fem_info.id) result->available = true`
- legacy config parsing: availability is likewise set only for nonzero
  `fem_info.id`

Since the stock config file is empty and live HWID override parameters remain
at their invalid sentinel values, `nofem + nofem` / FEM ID zero is now the
leading explanation.

The final remaining check is whether any DT parse error path can subsequently
clear an already-populated nonzero FEM ID or availability flag. If later-error
cleanup preserves these fields, the live false result proves FEM ID zero and
therefore narrows the GQ5012BF1 runtime to HWID 0, 1 or 2, all of which select
`nofem + nofem`.

## DT error cleanup semantics proven against stock

`cfm_epaelna_config_free(cfg, false)` has now been confirmed in both the
reconstructed source and the actual stock `connfem.ko`.

The recovered source explicitly states that when `free_all == false`, FEM
information and flags are retained and only PIN-related configuration is
cleared:

    if (!free_all) {
        memset(&cfg->pin_cfg, 0, sizeof(cfg->pin_cfg));
        return;
    }

With `free_all == true`, flags are released and the full configuration
structure is zeroed.

Stock and reconstructed machine code for `cfm_epaelna_config_free()` are
structurally/instruction-wise equivalent at this behavior boundary:

- `free_all=true` frees the flags container and clears the full 0x278-byte
  configuration;
- `free_all=false` clears only the pin-config region and returns.

The DT parser error path calls:

    cfm_dt_epaelna_free(dt, false);
    cfm_epaelna_config_free(result, false);

Therefore any error occurring after FEM population and availability selection
does not erase `fem_info` or reset `available`.

Consequently a nonzero FEM selected successfully by
`cfm_epaelna_feminfo_populate()` would remain visible as available even if a
later flags/pinctrl stage failed.

The only remaining alternative to the runtime `nofem + nofem` interpretation
is an early DT parse failure before FEM population. Platform-probe error
handling is the final check needed to eliminate that possibility.

## Platform-probe error behavior clarified

Stock and reconstructed `connfem_plat_probe()` preserve partially parsed
ConnFem information when device-tree parsing fails.

After:

    err = cfm->dt_parse(cfm);

a negative result is handled specially only for `-EAGAIN`, which is converted
to `-EPROBE_DEFER` and returned immediately.

For other DT parse errors, probe deliberately continues. The source comments
state that partially recovered information such as:

- HWID
- EPA/eLNA availability
- FEM info
- flags
- parts

is intentionally retained.

The context is subsequently assigned to:

    connfem_ctx
    connfem_cdev_ctx.cfm

even though the original DT parser error remains the probe return value.

Stock disassembly confirms this control flow.

Therefore the mere existence of a live `connfem_ctx` does not prove that DT
parsing completed successfully.

The final read-only discriminator is Linux platform-driver binding state:
if the ConnFem platform device is currently bound to `mtk_connfem`, probe must
have returned success. A retained nonzero DT parser error would prevent a
successful driver binding.

## Live platform binding result

Live sysfs inspection found:

- `/sys/bus/platform/devices/connfem` exists;
- `/sys/bus/platform/drivers/mtk_connfem` exists;
- the driver directory contains no bound `connfem` device symlink;
- `/sys/bus/platform/devices/connfem/driver` does not resolve.

Therefore the ConnFem platform device is currently unbound.

This invalidates the previous proposal that successful live driver binding
could be used to prove a zero-error DT parse.

Recovered stock probe behavior explains how this state can coexist with a
working `/dev/connfem` character device and registered `connfem_ctx`:

- a non-`EAGAIN` DT parse error is retained as the platform probe return value;
- partially parsed state is intentionally preserved;
- `connfem_ctx` and `connfem_cdev_ctx.cfm` are still assigned before returning;
- the platform core therefore sees a failed probe while the ConnFem module's
  character-device API can still access the preserved context.

Current runtime conclusion is therefore:

    EPA/eLNA context selected
    available == false
    platform device unbound

The remaining ambiguity is:

1. successful FEM selection produced `fem_info.id == 0`, corresponding to the
   GQ5012BF1 `nofem + nofem` rows HWID 0/1/2; or
2. DT parsing failed before FEM population.

No driver rebind or GPIO mutation has been performed.

## GQ5012BF1 live ConnFem root cause resolved

The previous hypothesis that live `available == false` proved selection of
HWID 0/1/2 (`nofem + nofem`) is withdrawn.

Direct stock disassembly and live firmware-state inspection now explain the
runtime behavior without requiring any HWID inference.

### connfem_is_internal

Stock and reconstructed `connfem_is_internal()` are both 0x7c bytes and have
equivalent machine-code behavior.

They call:

    request_firmware_direct(..., "connfem_internal", NULL)

and return true only when that firmware request succeeds.

The live firmware-class search path is:

    /vendor/firmware

No `connfem_internal` file exists in the extracted stock vendor firmware or
the searched live firmware locations.

Therefore on the stock GQ5012BF1 runtime:

    connfem_is_internal() == false

### Stock cfm_dt_epa_parse behavior

The merged GQ5012BF1 DT contains:

    /connfem/epa-elna-mtk

but no generic:

    /connfem/epa-elna

Stock `cfm_dt_epa_parse()` searches the `epa-elna-mtk` candidate list only
when `connfem_is_internal()` returns true.

Since the live result is false, stock skips the MTK-specific node and searches
only the generic EPA/eLNA candidate names.

No generic node exists.

Stock machine code then logs the missing-node condition and explicitly
returns:

    -EINVAL

This was a confirmed difference from the reconstruction, which logged the
missing node but returned success. It has since been repaired — see
*`cfm_dt_epa_parse()` corrected against the stock oracle* below.

### Why the live platform device is unbound

`connfem_plat_probe()` preserves partially initialized ConnFem state after
non-EAGAIN DT errors. It registers the EPA context into `connfem_ctx` and the
character-device context, but returns the original DT parser error.

Therefore stock runtime naturally reaches:

    connfem_ctx exists
    /dev/connfem exists
    EPA context selected
    EPA availability == false
    CFM_IOC_EPA_INFO returns -EOPNOTSUPP
    platform device remains unbound from mtk_connfem

This exactly matches live observations.

### Hardware conclusion

The live runtime does NOT provide evidence that HWID is 0, 1 or 2.

The physical GPIO HWID and external-FEM table row are not selected through
the active stock DT parser path because parsing fails before the
`epa-elna-mtk` child is entered.

For stock-compatible integration, the significant device behavior is:

    connfem_internal marker: absent
    EPA-MTK DT node: present but inactive
    generic EPA DT node: absent
    platform probe result: -EINVAL
    platform binding: none
    ConnFem character device: present
    legacy FEM availability: false

Exact physical HWID is therefore currently unknown and not required to
reproduce stock runtime behavior.

---

## `cfm_dt_epa_parse()` corrected against the stock oracle

Oracle: `$RESEARCH/workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/connfem.ko`
(sha256 `6373afa19d09289400c8a1ae3ab8bf1edb1ba354fa92d16003285e4b79771710`,
re-verified for this pass).

RED report (written before any source change):
`$RESEARCH/workspace/phase4-connfem-hardware/cfm-dt-epa-parse-RED.md`.
Raw evidence: `$RESEARCH/workspace/phase4-connfem-hardware/red/`.

### Stock missing-node behaviour is `-EINVAL`

Stock `cfm_dt_epa_parse` (`.text+0x2f38`, size `0x450`) ends its candidate
search with:

```text
2fec: adrp/add x0, .rodata.str1.1+0x1303  => "[connfem][DT]Missing epa elna node"
2ff4: bl    _printk
2ff8: mov   w0, #-0x16                    ; -EINVAL
2ffc: <stack-canary check> ... ret
```

The reconstruction (`size 0x3e0`) emitted `mov w0, wzr` at the same point, i.e.
it reported **success** when no ePA/eLNA child node exists. That single
instruction was the difference between "driver binds" and "driver does not
bind" on this phone.

### Why stock GQ5012BF1 remains unbound

The chain is now fully mechanical, with no inference left in it:

1. `/vendor/firmware/connfem_internal` does not exist, so
   `connfem_is_internal()` (0x7c bytes, byte-identical in both binaries)
   returns false.
2. `cfm_dt_epa_parse()` therefore never walks `cfm_epaelna_mtk_nodenames[]`
   (`"epa-elna-mtk"`, `"epa_elna_mtk"`), which is the only list that could
   match this device's DT.
3. It walks `cfm_epaelna_nodenames[]` (`"epa-elna"`, `"epa_elna"`); the
   GQ5012BF1 DT has no such child under `/connfem`.
4. Missing-node path → `pr_info("Missing epa elna node")` → `return -EINVAL`.
5. `connfem_plat_probe()` propagates the non-`-EAGAIN` error, so the platform
   core leaves `/sys/bus/platform/devices/connfem` **unbound** from
   `mtk_connfem`, while `connfem_ctx`, `/dev/connfem` and the partially
   initialised EPA context still exist — hence `CFM_IOC_EPA_INFO`
   (`0x8088cf03`) reaching `connfem_epaelna_get_fem_info()` and returning
   `-EOPNOTSUPP`, and the kernel log lines
   `connfem_is_available: FEM is not available` /
   `connfem_epaelna_get_fem_info, Not support`.

This is reproducible from source with **no device-tree change and no
`connfem_internal` firmware**, which was the required outcome.

### Why the earlier HWID 0/1/2 inference was withdrawn

The earlier reading was: live `available == false` ⇒ the parser selected a
`nofem + nofem` parts row ⇒ HWID ∈ {0,1,2}. That inference assumed the parser
*ran*. The disassembly shows it does not: parsing aborts at the node-candidate
stage, before `cfm_dt_epaelna_hwid_parse()` and before
`cfm_dt_epaelna_parts_parse()` are ever reached. `available` is false because
the whole EPA context was never populated, not because a particular parts row
was chosen. Both `epa_elna_hwid` and `hwid` module parameters also read
`0xffffffff` (default/invalid), so no override forces a row either. The
physical HWID is therefore still unknown — and is not needed to reproduce
stock behaviour.

### Source changes made

All in `$GKI_WS/lieppos/connfem-recon/src` (mirrored to `final/source`):

`include/connfem_dt.h`

* added `CFM_DT_FLAGS_NODE_NAME_SIZE` (= `sizeof("flags-") + 10 + 1` = 18,
  the `0x12` immediate stock passes to `snprintf`) and used it for
  `struct cfm_dt_epaelna_flags_context::node_name`. No layout change: the
  context stays 48 bytes and `dt->flags.node_name` stays at `cfm+0x1c8`.

`connfem_dt_parser.c`

1. `cfm_dt_epa_parse()`: added the stock NULL-input guard
   `if (!cfm) { pr_info("%s: Missing input", __func__); return -EINVAL; }`
   (stock strings `.rodata.str1.1+0x12e2` + `+0x249d`).
2. `cfm_dt_epa_parse()`: missing-node path now `return -EINVAL` instead of
   `return err /* 0 */`, and the "found" path emits
   `pr_info("Find node '%s'", np->name)` before descending.
3. `cfm_dt_child_find()`: candidate traversal changed from an indexed
   `for (i = 0; names[i]; i++)` to the stock pointer walk
   `for (; *names; names++)`, and the `"Find node '%s'"` diagnostic was moved
   out of the helper into its callers (stock's helper is `0x58` bytes and
   calls no `_printk` at all). Traversal order is unchanged.
4. `cfm_dt_epaelna_parse()`: `Force HWID: %d` → `Force HWID: %u`.
5. `cfm_dt_epaelna_parse()`: the flags node-name composition was hoisted out of
   the callee into the caller, exactly as stock does — 18-byte local, zeroed,
   `snprintf(node_name, sizeof(node_name), "%s%u", CFM_DT_PROP_FLAGS_PREFIX,
   flags_hwid)`, unsigned truncation test, truncation diagnostic
   `"flag node name error %d, sz %u, '%s%u'"` falling into the existing error
   cleanup, then `memcpy(dt->flags.node_name, node_name, sizeof(node_name))`.
6. `cfm_dt_epaelna_flags_parse()` signature changed to
   `static noinline void cfm_dt_epaelna_flags_parse(struct device_node *np,
   const char *node_name, struct cfm_dt_epaelna_flags_context *flags_out)`,
   using `strncpy(flags.node_name, node_name, sizeof(flags.node_name) - 1)`
   (stock's `strncpy` with `w2 = 0x11`). Stock leaves `x0` undefined on return
   and the caller does not test it, so the callee is `void`.
7. The negative-return branch after `cfm_dt_epaelna_flags_parse()` was removed;
   stock only checks `cfm_epaelna_flags_populate()`.

`connfem_sku.c`

8. `cfm_dt_sku_parse()`: emits the `"Find node '%s'"` diagnostic after a
   successful `cfm_dt_child_find()`, compensating for (3). Stock references
   that string from `cfm_dt_epa_parse` and `cfm_dt_sku_parse` only. Stock
   compiles `cfm_dt_sku_parse()` in the `"[connfem][DT]"` pr_fmt translation
   unit; the reconstruction still keeps it in `connfem_sku.c` (`"[connfem]"`),
   so the `[DT]` marker is spelled out in the format string to emit the
   *identical* stock literal rather than introducing a second, non-stock one.
   The SKU translation-unit split remains a separate open gap (stock
   `cfm_dt_sku_parse` `0x6fc` vs `0x2e8` here).

String-table effect: the five stock strings the reconstruction was missing
(`'%s%u'`, `"[connfem][DT]%s: Missing input"`, `"cfm_dt_epa_parse"`,
`"[connfem][DT]Force HWID: %u"`,
`"[connfem][DT]flag node name error %d, sz %u, '%s%u'"`) are now present, two
non-stock strings were removed, and no new non-stock string was added.

Not changed: `connfem_is_internal()`, `cfm_epaelna_config_free()` semantics,
any export/import/CRC, any device tree, any partition.

### Post-fix structural comparison

| metric | before | after | stock |
|---|---|---|---|
| `cfm_dt_epa_parse` size | `0x3e0` | `0x44c` | `0x450` |
| `cfm_dt_epaelna_flags_parse` size | `0x1dc` | `0x190` **byte-identical** | `0x190` |
| `cfm_dt_child_find` size | `0x80` | `0x58` **byte-identical** | `0x58` |
| `connfem_is_internal` | `0x7c` byte-identical | `0x7c` byte-identical | `0x7c` |
| module functions size-identical | 60 / 94 | **62 / 94** | — |
| module functions byte-identical | 50 / 94 | **52 / 94** | — |
| imports / import CRCs | 64 / 65 exact | 64 / 65 exact | 64 / 65 |
| exports / export CRCs | 8 / 7 exact | 8 / 7 exact | 8 |
| consumer-required export ABI | PRESERVED | **PRESERVED** | — |

`cfm_dt_epa_parse` external-call and rodata-string sequence is now **identical**
to stock (`red/postfix-callseq-diff.txt` differs only in the size header).

The normalised instruction-stream diff
(`red/postfix-epa-parse-normalised-diff.txt`) is down to two items, both pure
codegen:

* the two stores that zero the 18-byte stack buffer are emitted in the opposite
  order (`stp`/`strh` vs `strh`/`stp`) — same instructions, same address, same
  effect;
* stock tail-*duplicates* `mov w0, wzr` into the
  "Skip applying GPIO PINMUX for BT dedicate FEM" block while LLVM here
  tail-*merges* it into the shared success block — one instruction, `-4` bytes,
  identical behaviour.

Every branch, every immediate, every relocation target, both `memset` sizes
(`0x1a8`, `0x278`), the `-EAGAIN` pass-through, the `-ENOENT → hwid = 0` case,
the `snprintf` size `0x12`, the unsigned `b.hs` truncation test, and the whole
error-cleanup block (`kfree` of `dt->pctl.state.np`, zeroing `cfm+0x60..0x100`,
`cfm_epaelna_config_free(result, false)`) match.

### Verification performed

```bash
cd ~/kernel-work/gki-12901745-workspace
tools/bazel build //lieppos/connfem-recon/src:connfem_gki   # -Wall -Werror, clean
cd lieppos/connfem-recon
python3 check.py "$STOCK_KO" final/connfem.ko --out final/validation.txt
python3 disfn.py  final/connfem.ko cfm_dt_epa_parse ...
python3 callseq.py final/connfem.ko cfm_dt_epa_parse ...
```

Results: build clean with `-Wall -Werror`; imports 64/64; import MODVERSION
CRCs 65/65; exports 8/8; export CRCs 7/8 exact (the same stock-only
`connfem_sku_data` CRC as before, which no stock consumer imports); all four
consumer-required export CRCs exact; function set 94/94; no function regressed
in size or bytes. New tooling added for this pass:
`lieppos/connfem-recon/disfn.py` (single-function disassembly with resolved
relocations) and `lieppos/connfem-recon/callseq.py` (call/string sequence
extraction). Iteration snapshot:
`lieppos/connfem-recon/iterations/iter09-epa-parse-stock-parity/`.

Nothing was flashed, no partition/DTBO/device tree was modified, and no CRC was
fabricated.

## Current final GQ5012BF1 integration verdict

**Classification:** `STOCK_CONSUMER_ABI_EXACT_RECONSTRUCTION`

The GQ5012BF1 DT contains an `epa-elna-mtk` configuration subtree, but the
stock runtime does not enter that subtree.

`connfem_is_internal()` requires the firmware marker `connfem_internal`.
The stock GQ5012BF1 firmware does not contain that marker, so the stock
`cfm_dt_epa_parse()` skips `epa-elna-mtk`, fails to find a generic
`epa-elna` node, and returns `-EINVAL`.

Consequences on the stock handset:

- `mtk_connfem` platform device: unbound
- `/dev/connfem`: present
- EPA context: retained but unavailable
- `CFM_IOC_EPA_INFO`: returns `-EOPNOTSUPP`
- physical HWID: unknown and not evaluated by the stock active path
- physical FEM pair: unknown and not required for reproducing stock behavior

The reconstructed driver now reproduces this missing-node `-EINVAL` behavior.

For initial LieppOS custom-kernel integration, ConnFem is frozen at the
stock-consumer ABI boundary. Do not add `connfem_internal` or alter the DT
merely to make the platform device bind; doing so would be a deliberate
behavioral change from stock.

## Superseded intermediate ConnFem conclusions

Several earlier sections in this research log record intermediate hypotheses
that were useful during investigation but are no longer the current
GQ5012BF1 integration conclusion.

The following earlier statements are superseded:

- `GQ5012BF1_CONNFEM_MODE = EPAELNA_MTK_LEGACY`
- the claim that the running stock driver reaches the `epa-elna-mtk` parser
  and therefore selects a hardware-derived HWID
- the claim that observing GPIO 131 / 132 / 92 is required to determine the
  stock runtime FEM configuration
- the intermediate hypothesis that `available == false` implied
  `nofem + nofem` and therefore HWID 0, 1 or 2

The final stock-runtime evidence instead proves:

    DT topology contains epa-elna-mtk
    connfem_internal firmware marker is absent
    connfem_is_internal() returns false
    stock cfm_dt_epa_parse() skips epa-elna-mtk
    generic epa-elna node is absent
    cfm_dt_epa_parse() returns -EINVAL
    platform device remains unbound
    partial EPA context remains registered
    EPA availability remains false
    CFM_IOC_EPA_INFO returns -EOPNOTSUPP

Therefore the physical HWID and FEM pair are not evaluated by the active stock
parser path and are not required to reproduce stock GQ5012BF1 behaviour.

The authoritative current classification is:

    STOCK_CONSUMER_ABI_EXACT_RECONSTRUCTION

and the authoritative device verdict is the section:

    Current final GQ5012BF1 integration verdict

ConnFem is frozen for initial LieppOS custom-kernel integration unless later
runtime testing exposes a concrete consumer-visible behavioral defect.
