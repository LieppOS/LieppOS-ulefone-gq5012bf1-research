# GQ5012BF1 tkcore island Phase 3D — RED

Immutable. Recorded before any Phase-3D source edit.

Baseline: Phase-3C-R `7d9d7979521853c8d5a4412bb08c534870cd977a2f1efebe363f172ef067aeee`,
113/122 functions, 21/25 exports, 97 imports.
Stock oracle: `03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226`.

## RED status — all four targets ABSENT

| Target | Stock off | Stock size | Bind | Sec | Stock KCFI | Island (3C-R) |
|---|---|---:|---|---|---|---|
| `tee_clkmgr_handle` | `0x08d88` | 308 | GLOBAL FUNC | 14 | `0x06da45e1` | **ABSENT** |
| `tee_spi_cfg_padsel` | `0x090c8` | 332 | GLOBAL FUNC | 14 | `0xab53c5c9` | **ABSENT** |
| `tee_spi_transfer` | `0x09218` | 452 | GLOBAL FUNC | 14 | `0xffeb18b3` | **ABSENT** |
| `tee_spi_transfer_disable` | `0x093e0` | 300 | GLOBAL FUNC | 14 | `0x36b1c5a6` | **ABSENT** |

All four `__ksymtab_*` / `__kstrtab_*` records exist in stock and are **ABSENT** in the island.

Every stock KCFI id above matches the value independently recorded in
`phase4-tkcore-provider-abi.md`, which also fixes the historical export CRCs:

| Symbol | Historical stock CRC | Proven prototype |
|---|---|---|
| `tee_clkmgr_handle` | `0x6913f6b2` | `int tee_clkmgr_handle(uint32_t, uint32_t)` |
| `tee_spi_cfg_padsel` | `0x56729869` | `int tee_spi_cfg_padsel(uint32_t)` |
| `tee_spi_transfer` | `0x184ce7da` | `int tee_spi_transfer(void *, uint32_t, void *, void *, uint32_t)` |
| `tee_spi_transfer_disable` | `0xadb9b21c` | `int tee_spi_transfer_disable(void)` |

## Per-target stock facts

### tee_clkmgr_handle
- callees: `mutex_lock`, `mutex_unlock`, `_printk`
- objects: `.data+0x1b8` (mutex), `.data+0x1e8` (list head), `.rodata+0x69f` (4-entry jump table), `.rodata.str1.1+0x10c4`
- strings: `"\x013tkcore: unsupported token %u argnum %zu\n"`
- indirect `blr` sites: **4** (one per argnum 0..3)
- intra-module callers: none — exported API only
- locking: one `mutex_lock` / `mutex_unlock` pair; unlock happens **before** any callback
- no allocation, no list mutation, no DT/SPI/provider interaction

### tee_spi_cfg_padsel
- callees: `memset`, `_printk`, `TEEC_InitializeContext`, `TEEC_OpenSession`, `TEEC_InvokeCommand`, `TEEC_CloseSession`, `TEEC_FinalizeContext`, `__stack_chk_fail`
- objects: `.data+0x1f8` (TA UUID), 4 strings
- strings: `"\x016tkcore: padsel=0x%x\n"` + 3 shared TEEC failure strings
- indirect calls: **0**; no locks; no global mutable state

### tee_spi_transfer
- callees: as above **plus `memcpy`**
- objects: `.data+0x1f8`, 6 strings
- strings: `"\x016tkcore: conf=%p conf_size=%u inbuf=%p outbuf=%p size=%u\n"`,
  `"\x013tkcore: Bad parameters NULL buf\n"`, `"\x013tkcore: zero buf size\n"` + 3 shared
- indirect calls: 0; no locks; no global mutable state

### tee_spi_transfer_disable
- callees: `memset`, `_printk`, the five `TEEC_*`, `__stack_chk_fail`
- objects: `.data+0x1f8`, 3 shared strings
- no entry log, no validation, no locks, no global mutable state

## Shared secure-SPI state — the decisive structural finding

All three SPI functions are **secure-world RPC wrappers**, not hardware SPI drivers.
`.data+0x1f8` holds one 16-byte `TEEC_UUID`:

```text
raw: 7c3f6d96 ef04 eb1b 08b7 57f37a6d87f9
UUID: 966d3f7c-04ef-1beb-08b7-57f37a6d87f9
```

This is exactly the TrustKernel SPI proxy TA recorded in the MicroArray
reconstruction. All three open their own context and session to it:

| Function | commandID | paramTypes |
|---|---:|---|
| `tee_spi_transfer` | **0** | `0x75` |
| `tee_spi_transfer_disable` | **1** | `0x0` |
| `tee_spi_cfg_padsel` | **2** | `0x1` |

`paramTypes = 0x75` and `commandID = 0` match the MicroArray consumer evidence exactly.

None of the three touches pinctrl, a SPI controller, `spi_sync`, a `spi_message`,
a `spi_transfer`, a clock, a device reference, a lock, or any mutable global.
There is no persistent secure-SPI state at all beyond the constant UUID.

## Frozen evidence

Relocation-aware stock disassembly for all four is frozen under
`workspace/phase4-tkcore-island/phase3d/oracle/`.

## Header defects found during RED (not yet corrected at RED time)

1. `tee_spi.h` declares `int tee_spi_transfer_disable(bool disable)`. The proven
   provider-ABI table says `(void)`. Stock never reads `x0`, which is consistent
   with either spelling, so KCFI (a type-derived id) is the decisive test.
2. `tee_clkmgr.h` defines `TEE_CLKMGR_OP_ENABLE 0` / `TEE_CLKMGR_OP_DISABLE 1`.
   Stock selects `record->enable` when `(val & 1) != 0`. These constants are
   **inverted** and have zero uses anywhere in the tree.
