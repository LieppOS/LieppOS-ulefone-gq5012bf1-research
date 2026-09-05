# Ulefone GQ5012BF1 `tcpc_mt6375.ko` reconstruction

## Final classification

**Byte-exact code reconstruction.**

Every code-bearing and data-bearing section of the reconstructed module is byte-identical to the
Ulefone stock binary, every relocation resolves identically, and every import MODVERSION CRC matches
the stock module exactly.

```text
.text            18 428 B   sha256 3b4ffd9eb7347423443a699b3a4ec9f26d650e4ad2138d113c0026285bbd7c28
stock .text      18 428 B   sha256 3b4ffd9eb7347423443a699b3a4ec9f26d650e4ad2138d113c0026285bbd7c28
                 IDENTICAL
```

| Property | Stock | Reconstruction | Status |
|---|---|---|---|
| `.text` | 18 428 B | 18 428 B | **byte-identical** |
| Functions | 66 | 66 | **66/66 byte-identical** |
| `.init.text`, `.exit.text` | 48 / 40 B | 48 / 40 B | identical |
| `.rodata`, `.rodata.str1.1`, `.data` | 872 / 1720 / 560 B | same | identical |
| `.altinstructions`, `.plt`, `.hyp.*`, `.note.Linux`, `.gnu.linkonce.this_module` | — | — | identical |
| Relocations (all 10 `.rela.*` sections, 711 entries) | — | — | **identical when resolved by symbol** |
| Imports | 62 | 62 | identical set |
| Import MODVERSION CRCs | 63 | 63 | **0 mismatches vs stock** |
| Provider coherence (reconstructed `tcpc_class` + `pd_dbg_info`) | — | 22 covered | 0 incoherent |
| `MODULE_VERSION` / `LICENSE` / `AUTHOR` / `DESCRIPTION` / `depends` / `name` | — | — | identical |

Only two module-level fields differ, both being build-environment artifacts rather than code:

```text
stock  vermagic=6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64
built  vermagic=6.1.115-android14-11-maybe-dirty  SMP preempt mod_unload modversions aarch64

stock  srcversion=D27BCF95DDC8F09B632224B
built  srcversion=EA7DA9D08253B7F0F495FB1
```

`srcversion` is the MD5 of the source text and therefore reflects comment/whitespace differences
between the Ulefone source file and this reconstruction; it was deliberately not manufactured.
`.note.gnu.build-id`, `.symtab`/`.strtab` ordering and `.llvm_addrsig` differ for the same reason.

## Inputs

| Item | Value |
|---|---|
| Stock `tcpc_mt6375.ko` | `30abac643ebc7428a5ff350741d22b0f4bdcf65a5a071f55ec7ba78d862ca750` |
| Public donor | MiCode/MTK_kernel_device_modules `bsp-chagall-w-oss` @ `2d6f27aa19d521409f443c8d821e2d475bdc72b6` |
| Donor `tcpc_mt6375.c` | `b982ea838fbfdf341f4d2fbf93a1338f68accc3998c337ae23e06e2254d17cac` |
| Framework | reconstructed Ulefone `tcpc_class` 2.0.31_MTK (`//lieppos/tcpc-class-recon`) |
| Debug provider | reconstructed `pd_dbg_info` (`//lieppos/pd-dbg-info-recon`) |
| Kernel | exact GKI 12901745, `android14-6.1-2024-12_r4`, `6b18f0b574ab` |

## RED baseline (preserved)

```text
build succeeds, version 1.0.3, depends tcpc_class,pd_dbg_info
.text = 18 436 B  sha256 18ad4a5ced37e1dd95c5e806c327f90828efbbcc3ae87012c8fb6ba7d2a83fc2
only missing stock import: tcpc_typec_handle_fod
five size mismatches: fod_irq_handler -84, pd_evt_handler +12,
                      set_low_power_mode +60, tcpc_init +12, tcpc_probe +8
```

Preserved in `baseline/`: `tcpc_mt6375.c`, `tcpc_mt6375.ko`, `Module.symvers`, `Makefile`,
`BUILD.bazel`, `imports.txt`, `import-modversions.txt`, `function-sizes.txt`, `text.sha256`,
`validation.txt`.

## Priority 1 — FOD reconstruction (`mt6375_fod_irq_handler`)

Stock's handler is 0x114 bytes and calls `mod_delayed_work_on` + `tcpc_typec_handle_fod`. The
public 2.0.31 handler instead forwarded to `mt6375_floating_ground_evt_process`, and the real
implementation was present but fully commented out.

Recovered from stock disassembly:

```text
read  MT6375_REG_MTST4 (0xA2), 1 byte           → status
mask  status &= MT6375_MSK_FOD_ALL (0xE3)       → and x9, x8, #0xffffffffffffffe3
bit5 (FOD_LR)      → fod = 3 (TCPC_FOD_LR)      highest priority
bit6 (FOD_HR)      → fod = 4 (TCPC_FOD_HR)
bit7 (FOD_DISCHGF) → fod = 2 (TCPC_FOD_DISCHG_FAIL)
bit1 (FOD_OV)      → fod = 1 (TCPC_FOD_OV)      via ubfx w21, w8, #1, #1
else               → fod = 0 (TCPC_FOD_NONE)
read+write MT6375_REG_FODCTRL (0xCF) &= ~0x80   → mt6375_clr_bits(FOD_FW_EN)
if (fod == TCPC_FOD_LR)
        mod_delayed_work_on(WORK_CPU_UNBOUND=0x20, system_wq,
                            ddata+0x150 (fod_polling_dwork), 0x4e2 = 1250 jiffies)
return tcpc_typec_handle_fod(ddata->tcpc, fod)
```

Restored source (the previously commented `mt6375_get_fod_status` / `mt6375_fod_evt_process`,
with `system_freezable_wq` corrected to `system_wq` per the stock relocation):

```c
static int mt6375_fod_evt_process(struct mt6375_tcpc_data *ddata)
{
	int ret = 0;
	enum tcpc_fod_status fod = TCPC_FOD_NONE;
	struct tcpc_device *tcpc = ddata->tcpc;

	ret = mt6375_get_fod_status(ddata, &fod);
	if (ret < 0)
		return ret;
	ret = mt6375_clr_bits(ddata, MT6375_REG_FODCTRL, MT6375_MSK_FOD_FW_EN);
	if (ret < 0)
		return ret;
	if (fod == TCPC_FOD_LR)
		mod_delayed_work(system_wq, &ddata->fod_polling_dwork,
				 msecs_to_jiffies(5000));
	return tcpc_typec_handle_fod(tcpc, fod);
}

static int mt6375_fod_irq_handler(struct mt6375_tcpc_data *ddata)
{
	return mt6375_fod_evt_process(ddata);
}
```

Result: size 0x114 exact, `tcpc_typec_handle_fod` import restored (imports became an exact match),
`.rodata.str1.1` became byte-identical, and the instruction stream matched stock exactly.
`system_wq` (not `system_freezable_wq`) is proven by the stock `R_AARCH64_ADR_PREL_PG_HI21 system_wq`
relocation; delay `0x4e2` = `msecs_to_jiffies(5000)` at HZ=250.

## Priority 2 — `mt6375_pd_evt_handler`

Stock is 0x54 bytes with a single `tcpci_alert(tcpc, true)` and no retry loop:

```c
static irqreturn_t mt6375_pd_evt_handler(int irq, void *data)
{
	struct mt6375_tcpc_data *ddata = data;

	MT6375_DBGINFO("++\n");
	pm_stay_awake(ddata->dev);
	tcpci_lock_typec(ddata->tcpc);
	tcpci_alert(ddata->tcpc, true);
	tcpci_unlock_typec(ddata->tcpc);
	pm_relax(ddata->dev);
	MT6375_DBGINFO("--\n");

	return IRQ_HANDLED;
}
```

The donor's `do { … } while (ret != -ENODATA);` loop was removed. This finding later proved
self-consistent with `tcpc_class`: stock `tcpci_alert()` has no `-ENODATA` early return at all
(see the framework report), so no consumer could loop on it.

Result: size 0x54, normalized instruction stream identical to stock.

## Priority 3 — `mt6375_set_low_power_mode`

Stock ends immediately after the `MT6375_REG_SYSCTRL2` write. The donor appended a
"let CC pins re-toggle" tail that stock does not contain:

```c
-	ret = mt6375_write8(ddata, MT6375_REG_SYSCTRL2, data);
-	/* Let CC pins re-toggle */
-	if (en && ret >= 0 && (tcpc->typec_local_cc & TYPEC_CC_DRP)) {
-		udelay(32);
-		ret = mt6375_write8(ddata, TCPC_V10_REG_COMMAND,
-				    TCPM_CMD_LOOK_CONNECTION);
-	}
-	return ret;
+	return mt6375_write8(ddata, MT6375_REG_SYSCTRL2, data);
```

Binary evidence: stock's final register write is `mov w1, #0x90` (SYSCTRL2); the donor's was
`mov w1, #0x23` (`TCPC_V10_REG_COMMAND`) with `mov w8, #0x99` (`TCPM_CMD_LOOK_CONNECTION`),
preceded by `__const_udelay` and a `tcpc + 0x2c75` bit-2 test (`typec_local_cc & TYPEC_CC_DRP`).

Result: size 0x1b4 exact, register-write sequence exact.

## Priority 4 — `mt6375_tcpc_init`

Two concrete deltas:

1. **PHY register value.** Stock writes `MT6375_REG_PHYCTRL7 (0x86) <- 0x1E`; the donor writes
   `0x36`. Applied as `mt6375_write8(ddata, MT6375_REG_PHYCTRL7, 0x1E);` (BMC decoder idle time).
2. **Water-detect polling start.** After `mt6375_init_wd()`, the donor schedules
   `schedule_delayed_work(&ddata->wd_polling_dwork, msecs_to_jiffies(5000))`
   (`queue_delayed_work_on(WORK_CPU_UNBOUND, system_wq, ddata+0x40, 1250)`), whereas stock calls
   `mt6375_enable_wd_polling(ddata, true)` directly:

```c
		mt6375_init_wd(ddata);
-		schedule_delayed_work(&ddata->wd_polling_dwork,
-				      msecs_to_jiffies(5000));
+		mt6375_enable_wd_polling(ddata, true);
```

The other delayed works that stock does use (`vbus_to_cc_dwork`, `wd12_strise_irq_dwork`,
`fod_polling_dwork`) were left untouched.

Result: size 0x4e8 exact, all register constants and external calls matching.

## Priority 5 — `mt6375_tcpc_probe`

The genuine delta was the severity of one log call. Stock funnels the `mt6375_check_revision`
failure into the same `dev_err(dev, fmt, ret)` tail used by the `mt6375_sw_reset` failure
(`b @+0x88c` into `mov w2, w20; bl _dev_err`), while the donor emitted a separate
`_dev_notice` call:

```c
	ret = mt6375_check_revision(ddata);
	if (ret < 0) {
-		dev_notice(ddata->dev, "failed to check revision(%d)\n", ret);
+		dev_err(ddata->dev, "failed to check revision(%d)\n", ret);
		goto err;
	}
```

All error paths already performed `tcpc_device_unregister()`; only the block ordering differed,
which is compiler layout, not semantics.

Result: size 0x954 exact; normalized instruction stream identical to stock.

## Framework-side finding that completed the match (`tcpc_class` struct layout)

After the five function deltas were closed, `.text` size matched exactly (18 428 B) but six
instructions still differed. They were **not** code differences — they were `struct tcpc_device`
member offsets:

| Site | Stock | Reconstruction (before) | Field |
|---|---|---|---|
| `mt6375_transmit`, `mt6375_retransmit` | `#0x2ffb` | `#0x2ffc` | `pd_retry_count` |
| `mt6375_register_tcpcdev` | `#0x2ffc` | `#0x2ffd` | `disable_pe` |
| `mt6375_get_power_status`, `mt6375_vbus_irq_handler` | `#0x3541` | `#0x3542` | `vbus_safe0v` / `vbus_present` |
| `mt6375_is_water_detected` | `#0x355c` | `#0x3560` | `typec_cable_type` |

Bracketing against the offsets that already matched (`suspend_pending` `0x22e0`, `is_suspended`
`0x22e4`, `resume_wait_que` `0x2320`, `tcpc_flags` `0x2c8c`) localised two 1-byte excesses in the
reconstructed struct, both of which turned out to be MiCode-fork additions absent from both the
2.0.27 donor and the Ulefone stock module:

```c
	bool pd_ping_event_pending;   /* declared but never used in the fork  */
	bool ps_changed;              /* MiCode-only VBUS "ps_changed" flow   */
```

Removing both (and the `ps_changed` uses in `tcpci_alert()`) made all six instructions match and
`.text` byte-identical — and, as a side effect, made the reconstructed `tcpc_class` export CRCs
match the stock oracle 21/21, which in turn made every `tcpc_mt6375` import MODVERSION CRC match
stock exactly.

## Function-size comparison

```text
66 functions in stock, 66 in the reconstruction, identical name set,
66/66 identical sizes, 66/66 identical bytes, 0 mismatches.
```

## Import comparison

```text
imports stock=62 built=62 exact=True   stock_only=[] built_only=[]
```

`tcpc_typec_handle_fod` — the single stock-only import in the RED baseline — was restored by the
FOD reconstruction.

## MODVERSION comparison

```text
IMPORT_MODVERSIONS stock=63 built=63 common=63 mismatched_vs_stock=0
provider_coherence covered=22 incoherent=0
```

All 63 import CRCs match stock, including the 21 symbols provided by the reconstructed
`tcpc_class` (`tcpci_alert`, `tcpc_typec_handle_fod`, `tcpm_suspend`, …) and `pd_dbg_info`
(`0x48fb7437`). No `__versions`, `Module.symvers` or CRC table was edited at any point — the match
is the natural consequence of the framework's type definitions now being correct.

## `.text` comparison

```text
stock  18 428 B  3b4ffd9eb7347423443a699b3a4ec9f26d650e4ad2138d113c0026285bbd7c28
final  18 428 B  3b4ffd9eb7347423443a699b3a4ec9f26d650e4ad2138d113c0026285bbd7c28
cmp: identical
```

Progression: baseline 18 436 B (+8) → FOD 18 520 → PD IRQ 18 508 → low-power 18 448 →
init 18 436 → probe 18 428 (size match) → framework struct fix (byte match).

## Remaining differences

| Item | Explanation |
|---|---|
| `vermagic` | build environment string (`-maybe-dirty` vs stock's `-g945dff7bc1bf`); not code |
| `srcversion` | MD5 of the source text; differs because comments/whitespace of the original Ulefone file are unknown. Deliberately not manufactured |
| `.note.gnu.build-id` | hash over the whole object including the two fields above |
| `.symtab` / `.strtab` / `.shstrtab` / `.llvm_addrsig` | symbol ordering and name-table layout; relocations resolve identically |
| `.rela.*` raw bytes | encode symbol-table indices; all entries identical once resolved to `(offset, type, symbol, addend)` |

No unexplained functional delta remains.

## Artifacts

```text
/home/armol/kernel-work/gki-12901745-workspace/lieppos/tcpc-mt6375-recon/
  baseline/    RED baseline module + metadata
  iterations/  iter1-fod, iter2-pd-evt, iter3-lpm, iter4-init, iter5-probe, iter6-struct-fix
  final/       tcpc_mt6375.c, tcpc_mt6375.ko, Module.symvers, Makefile, BUILD.bazel, inc/,
               imports.txt, import-modversions.txt, function-sizes.txt, text.bin, text.sha256,
               validation.txt, reference-2.0.31-to-final.patch
  check.py     stock-vs-reconstruction validator
  fdiff.py     normalized per-function disassembly diff (relocation-resolved)
```

Analysis copy (with `SHA256SUMS`):

```text
.../ulefone-gq5012bf1-research/workspace/phase4-tcpc-mt6375-reconstruction/
  baseline/  analysis/  iterations/  final/
```

Build:

```bash
cd ~/kernel-work/gki-12901745-workspace
./tools/bazel build //lieppos/tcpc-mt6375-recon:tcpc_mt6375_gki
```

with

```python
deps = [
    "//lieppos/tcpc-class-recon:tcpc_class_gki",
    "//lieppos/pd-dbg-info-recon:pd_dbg_info_gki",
]
```

and `KBUILD_EXTRA_SYMBOLS="$(TCPC_SYMVERS) $(PD_SYMVERS)"`.

## Scope compliance

Nothing was flashed, no slot switched, no partition/boot/vendor_boot/dtbo/vbmeta touched, the clean
Android device tree was not modified, `pd_dbg_info` was not modified, and the two `tcpc_class`
changes were made only on direct binary evidence from this task (the four struct-offset immediates
listed above), as the task permits. The other six TCPC consumers were not touched.
