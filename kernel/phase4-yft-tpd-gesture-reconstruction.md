# Ulefone GQ5012BF1 `yft_tpd_gesture.ko` reconstruction

## Final classification

**`BYTE_EXACT_CODE_RECONSTRUCTION` — with one unresolved export CRC
(`tpgesture_value`), reported as `BLOCKED_WITH_EXACT_MISSING_EVIDENCE`
scoped to that single symbol.**

Precisely:

* all code and data are **byte-identical** to stock
  (`.text`, `.init.text`, `.exit.text`, `.rodata`, `.rodata.str1.1`, `.data`,
  `.data..read_mostly`, `.bss` layout, `.altinstructions`, `__jump_table`,
  `.init.eh_frame`);
* the function set, bindings, sections, offsets, sizes and KCFI type IDs are
  identical;
* the import set and the entire 1664-byte `__versions` MODVERSION table are
  byte-identical;
* every one of the 283 relocations is identical in content;
* 2 of the 3 exported MODVERSION CRCs are **generated from the reconstructed
  declarations** and match stock exactly;
* 1 exported MODVERSION CRC (`tpgesture_value`) does **not** match, and the
  missing evidence required to reproduce it is stated exactly in §9.

No CRC was fabricated. `Module.symvers` was not edited. No GKI core file was
modified. The phone was not touched.

---

## 1. Stock oracle

| Item | Value |
|---|---|
| Stock path | `$RESEARCH/workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/yft_tpd_gesture.ko` |
| Stock SHA256 | `e7d4e7cfe4defdd69ff0e1be50c7a3de173b5c717e47e969cf0f9dec13baf9bc` |
| SHA re-verified before analysis | yes |
| Size | 29688 bytes |
| Stock build-id | `8a2ce93d8dddf143ff04cd5fcd69e2334f7b5699` |
| Stock vermagic | `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64` |
| Stock toolchain (`.comment`) | Android clang 17.0.2, `r487747c` |

Loaded by both `modules.load` and `modules.load.recovery` in the vendor_boot
platform ramdisk.

## 2. Provenance result

**No source exists, publicly or locally.**

Local trees searched exhaustively (content walk + git history where present):
`$RESEARCH`, `~/kernel-work` (incl. `vendor-reference/MiCode-bsp-klee-w-oss`,
`MiCode-dash-w-oss`, `MiCode-MTK-kernel-device-modules-chagall-2.0.31`),
`~/androido_dalykai/LieppOS custom ROM/kernel-research/*`,
`android_device_ulefone_gq5012bf1`, `vendor_ulefone_gq5012bf1`,
`OrangeFox-Ulefone-GQ5012BF1`. Zero hits for `yft_tpd_gesture`,
`tpgesture_hander`, `tpgesture_value`, `mediatek,yft_tpd`, `mtk_yft_tpd` or
`"YFT touch gesturewake driver"` outside our own analysis artifacts and the
stock binaries.

Public searches: the misspelling `tpgesture_hander` returns **zero** kernel
results worldwide; `mediatek,yft_tpd`, `mtk_yft_tpd` and the module description
return nothing. Ulefone's GitHub org publishes only 3.x/4.x-era kernels for
other devices; there is no GQ5012BF1 source release.

Generic MTK/FocalTech/Goodix gesture drivers were considered and **explicitly
rejected** as substitutes (different modules, different exports, different
ioctl payloads). Full record:
`$RESEARCH/workspace/phase4-yft-providers/yft-tpd-gesture-source-candidates.md`.

Consequently the RED document is the no-public-source variant: a complete
recovered behaviour/function/data map derived from the binary, produced
**before** any source was written
(`$RESEARCH/workspace/phase4-yft-providers/yft-tpd-gesture-RED.md`).

## 3. Reconstruction location

```text
$GKI_WS/lieppos/yft-tpd-gesture-recon/
├── yft_tpd_gesture.c          reconstructed driver (single TU)
├── Makefile                   Kbuild
├── BUILD.bazel                //lieppos/yft-tpd-gesture-recon:yft_tpd_gesture_gki
├── tools/yft-analyze-stock.py ELF inventory extractor
├── tools/yft-compare.sh       stock-vs-rebuild verifier
├── tools/yft-crc-search.py    genksyms CRC model + exact algebraic solver
└── final/                     built .ko, Module.symvers, frozen sources
```

## 4. Build command and result

```bash
cd /home/armol/kernel-work/gki-12901745-workspace
./tools/bazel build //lieppos/yft-tpd-gesture-recon:yft_tpd_gesture_gki
```

```text
BUILD_RC=0
```

Built against **`//common:kernel_aarch64`** in the exact GKI 12901745
workspace (`kernel/common` @ `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`,
Linux 6.1.115-android14-11). Clean build, no warnings from the module TU.
Nothing in `common/` was modified.

Output SHA256: `3af85d022a01fd86c05c580926a47447b6eeaa498a368abb9869ec9bd21fe023`.

Verification driver:

```bash
bash lieppos/yft-tpd-gesture-recon/tools/yft-compare.sh
```

Full log: `$RESEARCH/workspace/phase4-yft-providers/yft-tpd-gesture-verification.txt`.

## 5. Function comparison

`functions: IDENTICAL` — name, binding, section, offset, size and KCFI type-id
prologue word all match for all 12 functions.

| Function | Bind | Section | Off | Size | KCFI id | Match |
|---|---|---|---:|---:|---|---|
| `tpgesture_hander` | GLOBAL | `.text` | 0x004 | 108 | `0xa540670c` | ✔ |
| `gesture_create_attr` | GLOBAL | `.text` | 0x074 | 160 | `0xa5a95c07` | ✔ |
| `gesture_delete_attr` | GLOBAL | `.text` | 0x118 | 80 | `0xa5a95c07` | ✔ |
| `tpgesture_show` | LOCAL | `.text` | 0x16c | 88 | `0xfc83b4bb` | ✔ |
| `tpgesture_status_show` | LOCAL | `.text` | 0x1c8 | 84 | `0xfc83b4bb` | ✔ |
| `tpgesture_status_store` | LOCAL | `.text` | 0x220 | 140 | `0x7b4cf59f` | ✔ |
| `tpd_unlocked_ioctl` | LOCAL | `.text` | 0x2b0 | 1200 | `0xe01408cd` | ✔ |
| `tpd_misc_open` | LOCAL | `.text` | 0x764 | 28 | `0x8f07ca55` | ✔ |
| `tpd_misc_release` | LOCAL | `.text` | 0x784 | 8 | `0x8f07ca55` | ✔ |
| `tpd_probe` | LOCAL | `.text` | 0x790 | 60 | `0x63df1691` | ✔ |
| `init_module` | GLOBAL | `.init.text` | 0x004 | 112 | `0x36b1c5a6` | ✔ |
| `cleanup_module` | GLOBAL | `.exit.text` | 0x004 | 108 | `0xa540670c` | ✔ |

Function **bytes**, not just sizes:

```text
.text        2076 bytes  IDENTICAL
.init.text    116 bytes  IDENTICAL
.exit.text    112 bytes  IDENTICAL
```

## 6. Import comparison and import CRC comparison

`imports: IDENTICAL` — same 26 symbols, and the `__versions` section is
**byte-identical** (1664 bytes), i.e. identical symbols *in identical order*
with identical CRCs:

```text
__arch_copy_from_user 0x2be0c009   __arch_copy_to_user   0x9a85eebb
__platform_driver_register 0x894c433a   __stack_chk_fail  0xc2c193d2
__wake_up 0xe2964344               _printk               0x92997ed8
alt_cb_patch_nops 0x1348649e       cpu_hwcaps            0x79e4c52b
driver_create_file 0x4cafa18c      driver_remove_file    0xb81ba41d
finish_wait 0x92540fbf             fortify_panic         0xcbd4898c
gic_nonsecure_priorities 0x4b0a3f52 init_wait_entry       0xfe487975
memcpy 0x4829a47e                  memset                0xdcb764ad
misc_deregister 0x94a9d12b         misc_register         0x06987aeb
module_layout 0xea759d7f           nonseekable_open      0x33534e04
platform_driver_unregister 0xe1b15563 prepare_to_wait_event 0x8c26d495
schedule 0x01000e51                scnprintf             0x96848186
strncmp 0x5a921311                 strnlen               0xa916b694
```

The stock module depends on **no vendor module** (`depends=` empty); this is
reproduced.

## 7. Export comparison and export CRC comparison

Membership, kinds, ELF types and sizes are identical:

| Symbol | Kind | ELF | Size | Stock CRC | Rebuilt CRC | Result |
|---|---|---|---:|---|---|---|
| `tpgesture_hander` | `EXPORT_SYMBOL` | FUNC | 108 | `0x8386526d` | `0x8386526d` | **EXACT** |
| `tpgesture_status` | `EXPORT_SYMBOL_GPL` | OBJECT | 1 | `0x30ac810a` | `0x30ac810a` | **EXACT** |
| `tpgesture_value` | `EXPORT_SYMBOL_GPL` | OBJECT | 10 | `0x02f3ea4c` | `0xec3d4c19` | **MISMATCH** |

`__ksymtab`, `__ksymtab_gpl`, `__kcrctab` and `__ksymtab_strings` are
byte-identical; only `__kcrctab_gpl` differs, in the `tpgesture_value` word.

Both matching CRCs were produced by genksyms from the reconstructed
declarations — they were **recovered**, not copied:

```c
void tpgesture_hander(void);   /* -> 0x8386526d */
char tpgesture_status;         /* -> 0x30ac810a ; NOT unsigned char (0xb5c3949e),
                                  NOT signed char (0x4c21c552), NOT bool
                                  (0xf00a46fa), NOT int (0xdcb11189)          */
```

## 8. Data / object layout

`.data`, `.data..read_mostly` and `.rodata` are byte-identical; `.bss` is 13
bytes with identical offsets.

| Section | Off | Symbol | Bind | Size | Match |
|---|---:|---|---|---:|---|
| `.bss` | 0x000 | `tpgesture_status` | GLOBAL | 1 | ✔ |
| `.bss` | 0x004 | `flag_irq` | LOCAL | 1 | ✔ |
| `.bss` | 0x008 | `tpgesture_status_value` | LOCAL | 5 | ✔ |
| `.data..read_mostly` | 0x000 | `tpgesture_value` | GLOBAL | 10 | ✔ |
| `.data` | 0x000 | `g_Waitq` | LOCAL | 24 | ✔ |
| `.data` | 0x018 | `tpd_misc_device` | GLOBAL | 80 | ✔ |
| `.data` | 0x068 | `driver_attr_tpgesture` | LOCAL | 32 | ✔ |
| `.data` | 0x088 | `driver_attr_tpgesture_status` | LOCAL | 32 | ✔ |
| `.data` | 0x0a8 | `tpd_driver` | LOCAL | 248 | ✔ |
| `.rodata` | 0x000 | `tpd_fops` | LOCAL | 272 | ✔ |
| `.rodata` | 0x110 | `touch_of_match` | GLOBAL | 400 | ✔ |

Recovered initialisation, all confirmed by identical bytes + relocations:

```c
static DECLARE_WAIT_QUEUE_HEAD(g_Waitq);

struct miscdevice tpd_misc_device = {
        .minor = MISC_DYNAMIC_MINOR, .name = "touch", .fops = &tpd_fops,
};

static DRIVER_ATTR_RO(tpgesture);          /* 0444, show only            */
static DRIVER_ATTR_RW(tpgesture_status);   /* 0644, show + store         */

static const struct file_operations tpd_fops = {
        .unlocked_ioctl = tpd_unlocked_ioctl,
        .open           = tpd_misc_open,
        .release        = tpd_misc_release,   /* .owner deliberately unset */
};

const struct of_device_id touch_of_match[] = {
        { .compatible = "mediatek,yft_tpd", }, {},   /* no MODULE_DEVICE_TABLE */
};

static struct platform_driver tpd_driver = {
        .probe = tpd_probe,
        .driver = { .name = "mtk_yft_tpd", .owner = THIS_MODULE,
                    .of_match_table = touch_of_match },
};
```

Definition **order** inside the single TU is load-bearing: it reproduces the
stock LLVM global/function emission order and therefore the exact `.data`,
`.bss`, `.rodata`, `.text`, `.rodata.str1.1` and `__versions` layouts. This is
documented in the source header comment and in RED.

## 9. Remaining differences

### 9.1 `tpgesture_value` export CRC — unresolved, bounded

Stock `0x02f3ea4c` vs rebuilt `0xec3d4c19`.

genksyms CRCs are `crc32` over the **expanded declaration text**, verified
against this tree's `scripts/genksyms/genksyms` and calibrated against four
sibling `yft_devinfo` exports (`touch_fw_version`, `second_touch_fw_version`,
`tinylcd_fw_version`, `fuelgauge_fw_version` — all `char NAME[30]`, all
reproduced exactly). Since `crc32` is affine over GF(2), candidate declarations
can be **solved**, not guessed. The searches below are exhaustive within their
stated bounds and all negative:

* every filler of length 1–6 over **all 256 byte values** for
  `char|unsigned char|signed char|_Bool|const char|volatile char tpgesture_value [ ? ] `;
* every filler of length ≤10 over `[]0-9 ()+*-`;
* every 7-char identifier filler over `[A-Za-z0-9_]`;
* `N` = 0…1024 across 1815 base-type spellings including `u8`/`__u8`/`s8`/
  `uint8_t` typedef expansions;
* all 1–5 token C type-keyword sequences over a 43-token alphabet;
* 2-D and 3-D array shapes with product 10;
* struct/union wrappers with solved names/members;
* direct genksyms runs over pointer forms, `extern`/`static`, initializers,
  multi-declarator lists, `__attribute__((section/aligned))`, enum/`sizeof`/
  arithmetic array bounds.

Meanwhile every *observable* property of the object is reproduced exactly: ELF
size 10, `.data..read_mostly+0x0`, section alignment 1, both fortified
`__builtin_object_size` values = 10, byte-identical code in every function that
touches it, and the FT3680 consumer's own 10-byte clear.

**Identified mechanism:** `scripts/Makefile.build` runs genksyms with
`-r <obj>.symref` and, when `KBUILD_PRESERVE` is set, `-p`. In that mode
`genksyms.c:__add_symbol()` takes the `sym->is_override && flag_preserve`
branch, prints *"ignoring … modversion change"* and emits the **reference**
CRC instead of the one implied by the source. That is the only mechanism in
this build system that yields identical source, identical object code and
layout, but a different export CRC — and it fits every observation.

**Exact missing evidence:** the vendor's `yft_tpd_gesture.symref` (or
`.symtypes`) reference type string for `tpgesture_value`, or the vendor header
whose earlier textual declaration genksyms parsed first. Neither exists on the
device image, and neither is derivable from a 32-bit one-way hash.

Full record:
`$RESEARCH/workspace/phase4-yft-providers/yft-tpd-gesture-export-crc-analysis.md`.

### 9.2 Build provenance metadata (expected, not a defect)

| Item | Stock | Rebuilt |
|---|---|---|
| `vermagic` | `6.1.115-android14-11-g945dff7bc1bf …` | `6.1.115-android14-11-maybe-dirty …` |
| `.modinfo` size | 187 | 185 |
| GNU build-id | `8a2ce93d…` | differs |
| `__UNIQUE_ID_*` local symbol counters | `…458`–`462` | `…347`–`351` |

`vermagic` is the GKI kernel's own scmversion stamp, not a property of this
module's source; the `__UNIQUE_ID` counter values are `__COUNTER__` positions
that depend on how many header macros the TU expanded. Both are local-symbol /
metadata level only and affect no code, data, relocation or ABI.

### 9.3 Section-header ordering nit

In the stock `.ko` the `.rela___ksymtab_gpl+tpgesture_status` section header
precedes `.rela___ksymtab+tpgesture_hander`; in the rebuild the order is
reversed. **All 283 relocation entries are identical in content** — this is a
section-table ordering artifact with no ABI or runtime effect.

## 10. Userspace / sysfs ABI (reproduced exactly)

```text
/dev/touch                        miscdevice, MISC_DYNAMIC_MINOR, name "touch"
    open    -> nonseekable_open()
    release -> 0
    ioctl   -> tpd_unlocked_ioctl()
    no compat_ioctl  => 32-bit callers get -ENOTTY from the VFS
    no read/write/poll/llseek

_IOW('A', 3, int)     = 0x40044103  gesture enable
        copy_from_user(&ioarg, arg, 4); tpgesture_status = ioarg;
        returns the copy_from_user residue (result deliberately unchecked)

_IOR('A', 4, char *)  = 0x80084104  gesture value
        flag_irq = false;
        wait_event_freezable(g_Waitq, flag_irq);   /* TASK_INTERRUPTIBLE|TASK_FREEZABLE */
        strcpy(buf10, tpgesture_value);
        copy_to_user(arg, buf10, 10);
        returns the copy_to_user residue

default: pr_info("tpd: unknown IOCTL: 0x%08x\n", cmd); return -ENOIOCTLCMD;
access_ok failure: pr_info("tpd: access error: %08X, (%2d, %2d)\n", …); return -EFAULT;
```

Note the stock quirk preserved verbatim: the `_IOR` size field is 8 (a pointer
type) while the payload actually copied out is 10 bytes.

```text
/sys/bus/platform/drivers/mtk_yft_tpd/tpgesture         0444
    scnprintf(buf, PAGE_SIZE, "%s\n", tpgesture_value)
/sys/bus/platform/drivers/mtk_yft_tpd/tpgesture_status  0644
    show : scnprintf(buf, PAGE_SIZE, "%d\n", tpgesture_status)
    store: strncmp(buf, "on", 2)==0 ? (value="on", status=1)
                                    : (value="off", status=0); return count
```

Kernel-facing provider API:

```c
void tpgesture_hander(void);   /* FT3680 IRQ path: flag_irq = true; wake_up() */
extern char tpgesture_status;  /* gesture enable state                        */
extern char tpgesture_value[10];/* "UP" / "DOWN" / "LEFT" / "RIGHT" / …       */
int  gesture_create_attr(struct device_driver *dev);
int  gesture_delete_attr(struct device_driver *dev);
struct miscdevice tpd_misc_device;
extern const struct of_device_id touch_of_match[];
```

Init/teardown ordering preserved exactly, including the stock behaviours that
`init_module` always returns 0 (both failures only log) and that
`tpd_probe` returns literal `-1`.

## 11. Consequence for the FocalTech FT3680 blocker

| Provider symbol | Stock CRC | Rebuilt CRC | Stock FT3680 links? | Rebuilt FT3680 links? |
|---|---|---|---|---|
| `tpgesture_status` | `0x30ac810a` | `0x30ac810a` | **yes** | yes |
| `tpgesture_hander` | `0x8386526d` | `0x8386526d` | **yes** | yes |
| `tpgesture_value` | `0x02f3ea4c` | `0xec3d4c19` | **no** | yes |

So: 2 of the 3 `tpgesture_*` provider blockers are fully resolved against the
*stock* consumer binary; the third resolves only when
`focaltech_touch_spi_ft3680.ko` is rebuilt from the phase-4 FocalTech
reconstruction against this provider (both sides then carry `0xec3d4c19`).

## 12. Safety

Offline analysis and host-side builds only. Nothing was flashed; no module was
inserted or removed on the device; no DT/DTBO, GPIO, slot or partition was
touched; no CRC was fabricated and no CRC table or `Module.symvers` was edited.

## 13. Artifacts

```text
$RESEARCH/workspace/phase4-yft-providers/
  yft-tpd-gesture-stock-inventory.md        full stock inventory
  yft-tpd-gesture-RED.md                    mandatory RED (no-public-source mode)
  yft-tpd-gesture-source-candidates.md      provenance search record
  yft-tpd-gesture-export-crc-analysis.md    CRC derivation + exhaustion proof
  yft-tpd-gesture-verification.txt          stock-vs-rebuild verification log
  yft-tpd-gesture-functions.tsv
  yft-tpd-gesture-objects.tsv
  yft-tpd-gesture-imports.tsv
  yft-tpd-gesture-exports.tsv
  yft-tpd-gesture-sections.tsv
  yft-tpd-gesture-relocs.tsv
  yft-tpd-gesture-strings.txt
  yft-tpd-gesture-modinfo.txt
  yft-tpd-gesture-disasm.txt

$GKI_WS/lieppos/yft-tpd-gesture-recon/      source, build target, tools, final/
```
