# Ulefone GQ5012BF1 `pd_dbg_info.ko` targeted reconstruction

## Result

**Classification: reconstructed exact implementation match.**

The stock-only source delta was recovered and rebuilt against `//common:kernel_aarch64` in the exact GKI 12901745 workspace. The reconstructed module has:

- byte-identical `.text`, `.init.text`, and `.exit.text` sections;
- exact function sizes and bytes for all four functions;
- exact code/data/parameter relocations;
- exact imports and exact import MODVERSION table;
- exact exported `pd_dbg_info` CRC, `0x48fb7437`;
- exact initialized data, parameter table, warning strings, and queue-counter storage;
- `PD_TEXT_CMP_RC=0`.

The complete `.ko` files are not byte-identical only because of build-provenance metadata: the embedded source path, vermagic, and resulting GNU build ID.

## Inputs

| Input | SHA256 |
|---|---|
| Ulefone stock `pd_dbg_info.ko` | `3b3553cfee8269a075ac30646301f45b7ee923820676bb286b561b31dc9d217c` |
| NothingOSS donor `pd_dbg_info.c` | `477df9d180e18d3a19e3d2edb96c1d635e01eb5f0b85cbc72a2ae71fe172370a` |
| Unchanged donor `pd_dbg_info.h` | `88f4fb71ef1316c98cc7514bb520f4cf4e5896133bf49674722379dd0c0540fe` |

The standalone module Makefile preserves the vendor condition with:

```make
ccflags-y += -DCONFIG_PD_DBG_INFO=1
```

No device tree, phone partition, boot image, or unrelated Type-C source was modified.

## Required RED baseline

An unchanged donor baseline was preserved and built before reconstruction.

| Function | Stock | Baseline donor |
|---|---:|---:|
| `pd_dbg_info` | 756 | 716 |
| `print_out_dwork_fn` | 528 | 448 |
| `cleanup_module` | 188 | 180 |
| `init_module` | 48 | 48 |

Baseline validation:

```text
stock .text SHA256:    0da6c26de5c4ee71ba88492a8ad8e42b1181bdb5fbaced3cb3d3013ded3cf642
baseline .text SHA256: dc29919968f20783e3b077506253ba914f8256d183585f5c7f6865d306c1bc33
PD_TEXT_CMP_RC=1
imports: exact (19)
import MODVERSION section: byte-identical (1280 bytes)
pd_dbg_info export CRC: 0x48fb7437
```

Baseline artifacts are under:

```text
$RECON/baseline/
$OUT/baseline/
```

## Recovered `mn_limit` state

### Parameter and default

Stock ELF evidence identifies:

```text
mn_limit: OBJECT, local, size 4, .data offset 0x4
__param_mn_limit: OBJECT, size 40
__param_str_mn_limit: "mn_limit"
parmtype=mn_limit:uint
```

The first two little-endian words of stock `.data` are:

```text
c8 00 00 00  10 27 00 00
```

Therefore:

```c
static unsigned int dbg_log_limit = 200;
static unsigned int mn_limit = 10000;
module_param(mn_limit, uint, 0644);
```

The final `__param` section and all `.rela__param` entries are byte/semantically identical to stock, confirming the type, backing storage, and mode.

### Queue counter

Stock has a second stock-only symbol:

```text
mn_cnt: OBJECT, local, size 8, .bss offset 0x0
```

It is reconstructed as:

```c
static size_t mn_cnt;
```

The final `.bss` layout is exact: 20 bytes total, with `mn_cnt` occupying the first 8 bytes.

## Recovered behavior

`mn_limit` is **not an allocation limit** and does not reject new log messages. It is a backlog-drain threshold layered onto the existing per-second print limiter.

### Producer: `pd_dbg_info()`

The stock path still computes sizes and timestamps, allocates exactly one node, formats it, and appends it to `msg_list`. It adds only queue accounting:

```c
mutex_lock(&list_lock);
list_add_tail(&mn->list, &msg_list);
mn_cnt++;
mutex_unlock(&list_lock);
```

Consequences proven by disassembly:

- no `mn_limit` check occurs before or after allocation;
- there is no new drop path;
- there is no list traversal to count nodes;
- allocation failures still return `-ENOMEM`;
- disabled logging still returns `-EPERM`;
- the successful return remains `ts_size + msg_size`.

The additional 40 bytes in stock `pd_dbg_info()` are fully accounted for:

- 8 bytes: reset `mn_cnt` in the inlined disabled-log cleanup path;
- 16 bytes: load/increment/store `mn_cnt` under `list_lock` after insertion;
- 8 bytes: pass `__func__` to the timestamp warning;
- 8 bytes: pass `__func__` to the formatted-message warning.

### Consumer: `print_out_dwork_fn()`

The normal rate-limit gate changed from:

```c
if (dbg_log_limit && printed >= dbg_log_limit)
```

to:

```c
if (dbg_log_limit && printed >= dbg_log_limit && mn_cnt <= mn_limit)
```

Thus, when the one-second print limit has been reached:

- if queued nodes are at or below `mn_limit`, work is delayed until the next rate window;
- if queued nodes exceed `mn_limit`, the worker bypasses that delay and starts draining nodes.

Each dequeue is performed under `list_lock`:

```c
list_del(&mn->list);
empty = list_empty(&msg_list);
--mn_cnt;
exceed = !empty && mn_cnt > mn_limit;
if (empty)
        mn_cnt = 0;
```

After unlocking, stock ordering is:

```text
pr_notice
printed++
kfree
empty check
queue-excess check
schedule_delayed_work, if needed
```

If the remaining queue is still above `mn_limit`, the same worker invocation returns to the locked dequeue path and prints another node immediately. Once the remaining count reaches `mn_limit`, it schedules ordinary immediate work; the next invocation can then apply the per-second rate limiter. This drains an oversized backlog down to the configured threshold without capping producer allocation or dropping messages.

The rate-gate read of `mn_cnt` is outside `list_lock`, matching stock. Counter increment, decrement, empty-list reset, and cleanup reset are protected by `list_lock`.

### Cleanup and exit

`clean_up_list()` frees every node while holding `list_lock`, then performs:

```c
mn_cnt = 0;
```

before unlocking. This accounts for the 8-byte `cleanup_module` increase after inlining. The same helper behavior appears in the `dbg_log_limit == 1` cleanup paths.

## Warning-format revision

Stock disassembly and string relocations prove that the generalized warning form uses `size_t` formatting and `__func__`:

```c
WARN(ts_size != size,
     "different return values (%zu and %zu) from %s()",
     ts_size, size, __func__);

WARN(msg_size != size,
     "different return values (%zu and %zu) from %s(\"%s\", ...)",
     msg_size, size, __func__, fmt);
```

The final `.rodata.str1.1` section is byte-identical to stock, including both warning strings and `pd_dbg_info` used as the `__func__` argument.

## Reconstruction iterations

| Revision | Result |
|---|---|
| Baseline | Required RED mismatch reproduced. |
| Iteration 1 | Counter/parameter/warnings correct; `pd_dbg_info`, cleanup, and init already byte-exact; structured `do/while` caused a 760-byte duplicated worker body. |
| Iteration 2 | Replaced structured loop with the stock-like labeled drain path; worker size became exact at 528 bytes. |
| Iteration 3 | Materialized `!empty && mn_cnt > mn_limit` under the lock; only two register-encoding bytes differed. |
| Iteration 4 | Rejected compiler experiment (`-Wunsequenced`); not used. |
| Iteration 5/final | Reordered decrement/excess/reset to match stock lowering; complete `.text` became byte-identical. |

All iteration sources and successful modules are retained under `iterations/`.

## Final validation

### Function bytes

| Function | Stock | Final | Byte-identical |
|---|---:|---:|---|
| `pd_dbg_info` | 756 | 756 | yes |
| `print_out_dwork_fn` | 528 | 528 | yes |
| `cleanup_module` | 188 | 188 | yes |
| `init_module` | 48 | 48 | yes |

### Key sections

| Section | Stock size | Final size | Result |
|---|---:|---:|---|
| `.text` | 1292 | 1292 | exact |
| `.exit.text` | 192 | 192 | exact |
| `.init.text` | 52 | 52 | exact |
| `.data` | 208 | 208 | exact |
| `.bss` | 20 | 20 | exact layout |
| `.rodata` | 23 | 23 | exact |
| `.rodata.str1.1` | 187 | 187 | exact |
| `__param` | 80 | 80 | exact |
| `__versions` | 1280 | 1280 | exact |
| `__bug_table` | 24 | 24 | exact |
| `__ksymtab` / `__kcrctab` | 12 / 4 | 12 / 4 | exact |

Final text result:

```text
stock .text SHA256: 0da6c26de5c4ee71ba88492a8ad8e42b1181bdb5fbaced3cb3d3013ded3cf642
final .text SHA256: 0da6c26de5c4ee71ba88492a8ad8e42b1181bdb5fbaced3cb3d3013ded3cf642
PD_TEXT_CMP_RC=0
```

All 11 normalized relocation sections are exact, including `.rela.text`, `.rela.exit.text`, `.rela.init.text`, `.rela.data`, and `.rela__param`. This also establishes exact external-call sequence and multiplicity.

### ABI

```text
imports: exact, 19 symbols
import MODVERSION entries: exact, 20 entries including module_layout
import MODVERSION bytes: exact
exported symbol: pd_dbg_info
export CRC: 0x48fb7437
public prototype: unchanged
header: unchanged
```

### Remaining full-module differences

The final module SHA256 is:

```text
a954ae4ff08997b54cbef1b17ef8c1bf91edf44f667ea30018f2061d71d9374c
```

An exhaustive comparison found only three differing allocatable sections out of 29:

1. `.rodata.str`: embedded build source path;
2. `.modinfo`: stock vermagic `6.1.115-android14-11-g945dff7bc1bf ...` versus workspace `6.1.115-android14-11-maybe-dirty ...`;
3. `.note.gnu.build-id`: derived build identity.

These are provenance differences, not implementation, ABI, parameter, or runtime-behavior differences.

## Artifacts

Reconstruction workspace:

```text
/home/armol/kernel-work/gki-12901745-workspace/lieppos/pd-dbg-info-recon
```

Final source and module:

```text
/home/armol/kernel-work/gki-12901745-workspace/lieppos/pd-dbg-info-recon/final/pd_dbg_info.c
/home/armol/kernel-work/gki-12901745-workspace/lieppos/pd-dbg-info-recon/final/pd_dbg_info.ko
```

Analysis and validation artifacts:

```text
/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/workspace/phase4-pd-dbg-info-reconstruction
```

Key final files there include:

```text
final/pd_dbg_info.c
final/pd_dbg_info.ko
final/pd_dbg_info.patch
final/validation.txt
final/build.log
final/SHA256SUMS
final/stock.text.disasm.txt
final/built.text.disasm.txt
```
