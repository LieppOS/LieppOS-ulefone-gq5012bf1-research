# TrustKernel ABI island — evidence index

Every fact used by the island reconstruction, with its provenance. Nothing
here is asserted without a named source.

## 1. Prior reports imported

| report | what it supplies |
|---|---|
| `phase4-tkcore-stock-inventory.md` | first stock inventory of tkcore |
| `phase4-tkcore-provider-abi.md` | the 14/25 natural vs 11/25 blocked split; `struct tee` and `struct tee_context` offset anchors; proof the block is unrecoverable, not unfinished |
| `phase4-tkcore-source-candidates.md` | no public TrustKernel source; OP-TEE `optee_linuxdriver` identified as structural donor |
| `phase4-tkcore-drv-reconstruction.md` | backend consumer; struct tags `tee`, `tee_session`, `tee_cmd`, `tee_shm`; 11 tkcore edges |
| `phase4-tkcore-evidence-from-tmem-ffa.md` | client-side TEEC evidence |
| `phase4-tmem-ffa-trustkernel-type-evidence.md` | `TEEC_Context` 264 B, `TEEC_Session` 8 B, `TEEC_SharedMemory` 0x28, `TEEC_Operation` 0x118 |
| `phase4-trustkernel-abi-island-header-plan.md` | the island strategy and first classification pass |
| `phase4-microarray-fp-tee-reconstruction.md` | `tee_spi_transfer` prototype, KCFI `0xffeb18b3`, CRC `0x184ce7da` |
| `phase4-gz-tz-system-reconstruction.md` | five weak GlobalPlatform stubs independently pinning five TEEC prototypes/KCFI ids |

## 2. Facts established or corrected by THIS task

| fact | evidence | confidence | used by |
|---|---|---|---|
| stock SHA256 `03837d13…226`, size 221352 | frozen oracle | PROVEN | oracle, verifier |
| Build ID `6b666382…d6` | `llvm-readelf -n` | PROVEN | oracle |
| **srcversion is `604D4583E310DBFAC768366`, not empty** | `modinfo` | PROVEN | corrects earlier notes |
| tkcore lives in the **vendor ramdisk**, load index 100, with tkcore_drv at 101 | `modules.load` | PROVEN | runtime ABI, load ordering |
| 122 functions / 54 objects / 100 imports / 101 MODVERSIONs / 25 exports / 3098 relocations / 176 strings | re-derived inventory | PROVEN | closure matrix |
| "101 kernel imports" = 100 UND + `module_layout` | inventory | PROVEN | GKI ABI contract |
| zero intermodule imports | `depends=` empty + import scan | PROVEN | build constraint |
| **67 of 122 stock functions have an OP-TEE donor analogue (55%)** | name-set intersection | PROVEN | feasibility, closure matrix |
| the other 55 are TrustKernel-specific subsystems (log, procfs, clkmgr, SPI, compat, dma-buf shm, big-core affinity, platform init) | name-set difference | PROVEN | closure matrix |
| `struct mutex` on exact GKI is **48 bytes** | symbol-size probe | PROVEN (measured) | type graph |
| `tee_wait_queue_private` 0x40 = mutex + list_head with **no padding** | measurement + proven anchors | PROVEN | header contract |
| `struct tee` `lock@0xf8` + 48-byte mutex lands exactly on proven `state@0x128` | measurement + proven anchors | PROVEN | corroborates layout |
| TrustKernel replaced the donor's inline `struct miscdevice` with a **misc-device list** at `0xa0` | provider-abi report + three stock device nodes | PROVEN_SEMANTICS | type graph |

## 3. Machine-checked evidence

`//lieppos/trustkernel-layout:tk_layout_probe` compiles all layout assertions
against the real exact-GKI headers and **builds successfully**, so every
anchor in §2 that is expressed as an offset or size is verified by the
compiler rather than by prose.

## 4. Function closure

`kernel/phase4-tkcore-function-closure.tsv` classifies all 122 stock
functions across 16 subsystems:

| semantic class | count |
|---|---:|
| `EXACT_SEMANTICS` | 20 |
| `HIGH_CONFIDENCE_SEMANTICS` | 55 |
| `STRUCTURAL_ONLY` | 47 |

| subsystem | functions |
|---|---:|
| core | 18 |
| shared_memory | 17 |
| session | 11 |
| platform | 10 |
| sysfs | 10 |
| client | 8 |
| context | 8 |
| supplicant | 7 |
| helper | 6 |
| procfs | 6 |
| log | 5 |
| waitqueue | 5 |
| compat | 4 |
| spi | 3 |
| clkmgr | 2 |
| module | 2 |

The 20 `EXACT_SEMANTICS` functions are exactly the surfaces whose prototypes
are already pinned by a natural historical CRC, a matching KCFI id, or a
frozen consumer: the SPI proxy, the clock manager, the wait queue, the cached
shm mapping pair, and the 8 GlobalPlatform client entry points.

## 5. Provenance rule applied throughout

No fact was promoted in confidence when it moved between reports. Layout
anchors stay PROVEN, inferred gap members stay SYNTHETIC, and unrecoverable
historical member spellings stay UNKNOWN.
