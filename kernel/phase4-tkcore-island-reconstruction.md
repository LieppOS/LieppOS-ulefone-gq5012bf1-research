# TrustKernel ABI island — reconstruction status

**Classification: `TRUSTKERNEL_ABI_ISLAND_PARTIAL`**
**Runtime validation: NOT PERFORMED (and not attempted).**

GQ5012BF1 (Ulefone Armor 29 Pro Thermal, MT6878/MT6878T), LieppOS.
Static/offline only. No module was loaded, no device node opened, no TEEC
command issued, no secure world contacted.

This report states plainly what is finished and what is not. The stock tkcore
runtime dependency is **not yet eliminated**.

---

## 1. What is COMPLETE and machine-verified

### 1.1 Stock oracle frozen and independently re-derived

`workspace/phase4-tkcore-island/oracle/tkcore.stock.ko`
SHA256 `03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226`,
221352 bytes, Build ID `6b6663820488959123f26a85dded547e305c56d6`.

Full inventory re-derived from scratch: **122 functions, 54 objects, 100
imports, 101 MODVERSION records, 25 exports, 3098 relocations, 176 strings**,
zero intermodule imports.

One correction to the historical record: **srcversion is
`604D4583E310DBFAC768366`, not empty.**

Also clarified: the "101 kernel imports" figure is 100 undefined symbols plus
`module_layout`. Both prior numbers were right; they counted different things.

### 1.2 Donor coverage measured

**67 of 122 stock functions (55%) have a direct OP-TEE `optee_linuxdriver`
analogue.** The remaining 55 are TrustKernel-specific subsystems: log daemon,
procfs, clock manager, secure SPI proxy, compat conversion, dma-buf shared
memory, big-core affinity and platform init. This is a measured name-set
intersection, not an estimate.

### 1.3 Complete 122-function closure matrix

`kernel/phase4-tkcore-function-closure.tsv` — every stock function classified
by subsystem, size, export status, donor analogue, semantic class and
validation oracle. 20 `EXACT_SEMANTICS`, 55 `HIGH_CONFIDENCE_SEMANTICS`,
47 `STRUCTURAL_ONLY`. No function is unaccounted for.

### 1.4 The common TrustKernel type graph — authored and MACHINE-CHECKED

This is the keystone of the island and it is genuinely done.

`lieppos/trustkernel/include/trustkernel/` defines the single shared type
graph (client API, core, wait queue, shm, supplicant, clkmgr, spi).

`layout-assert.h` encodes **every recovered stock anchor** as a
`static_assert`, and the analysis-only target
`//lieppos/trustkernel-layout:tk_layout_probe` **builds successfully** against
exact GKI, so the following are compiler-verified rather than asserted:

* `TEEC_Context` 0x108, `TEEC_Session` 8, `TEEC_SharedMemory` 0x28
  (`size@8`, `flags@0x10`), `TEEC_Operation` 0x118 (`paramTypes@4`,
  `params@8`), `TEEC_UUID` 16
* `struct tee` 0x138 with all 12 proven offset anchors
* `struct tee_context` 0xd0 with all 7 proven offset anchors
* `struct tee_wait_queue_private` 0x40 with `db@0x30`

### 1.5 A real corroboration discovered while doing this

Kernel type sizes were **measured** against exact GKI by emitting them as
symbol sizes, not assumed. `struct mutex` is **48 bytes** on this kernel, not
the 32 a generic arm64 configuration would give.

That single measured fact independently explains two separate proven anchors:
`tee_wait_queue_private` fits 0x40 as exactly `mutex + list_head` with zero
padding, and `struct tee`'s proven `lock@0xf8` lands precisely on the proven
`state@0x128`. Two unrelated anchors falling out of one measurement is strong
evidence the recovered layouts are correct.

---

## 2. What is NOT complete

### 2.1 tkcore implementation — IN PROGRESS, does not build

The 3375-line OP-TEE donor has been imported to
`lieppos/tkcore-island/tkcore/` and rewired onto the common headers, and the
build target `//lieppos/tkcore-island:tkcore` exists. **It does not compile
yet.**

The donor targets a 3.x/4.x-era kernel. The remaining gap is systematic and
mechanical rather than structural, and was measured, not guessed:

| gap | nature |
|---|---|
| `_DEV(tee)` macro | donor resolved it through the inline `struct miscdevice`; TrustKernel uses a misc-device **list**, so the accessor must be redefined for the island type graph |
| `kref` / `refcount_t` | donor reads the refcount directly; 6.1 requires `kref_read()` |
| `miscdev` member references | must be reworked onto `list_misc` |
| `context->devname` truth test | `-Werror,-Wpointer-bool-conversion` on an array |

None of these is a blocker in principle. All of them are unfinished work.

### 2.2 Not started

* The 55 TrustKernel-specific functions (log, procfs, clkmgr, SPI, compat,
  dma-buf shm, platform).
* The three consumer acceptance builds (`tkcore_drv`, `tmem_ffa`,
  `microarray_fp_tee`) against source-built tkcore.
* The historical-vs-island CRC report, secure-protocol contract, runtime ABI
  contract, Android security dependency map, and the fail-closed verifier.

### 2.3 Therefore

**No acceptance claim is made.** Specifically:

* tkcore does **not** build yet, so there is no island export table.
* No consumer has been rebuilt against a source-built tkcore.
* **The stock tkcore runtime dependency is NOT eliminated.**
* `tkcore_drv` still uses its 5 stock tkcore witnesses; `tmem_ffa` still uses
  its 7; `microarray_fp_tee` still uses 1. None of those frozen modules was
  touched.

---

## 3. Strategy confirmation

The task's core strategic premise is confirmed by this work: the 11
historically blocked exports are blocked **only** on unrecoverable private
member spellings, and an internally consistent island type graph resolves
them. The header set is in place and verified; what remains is implementation
labour, not a missing-evidence problem.

The one genuinely irreducible fact remains: island CRCs for those 11 exports
will differ from the historical Ulefone CRCs. That is by design and is never
to be reported as a stock ABI match.

## 4. Forbidden-technique audit (for the work done so far)

| technique | status |
|---|---|
| CRC injection | not used |
| `__versions` editing | not used |
| ELF patching | not used |
| `KBUILD_MODPOST_WARN` | not used |
| fake stock headers to force a hash | not used |
| private-member brute forcing | not attempted (proven futile) |
| claiming historical source identity | not claimed anywhere |

## 5. Honest next step

Finish the 6.1 port of the imported donor (the four mechanical gaps above),
implement the 55 TrustKernel-specific functions, then run the three consumer
acceptance builds. Only after all three resolve their tkcore edges naturally
may the classification move to `TRUSTKERNEL_ABI_ISLAND_RECONSTRUCTED`.

**TRUSTKERNEL ABI ISLAND: PARTIAL — stock tkcore dependency NOT yet
eliminated.**
