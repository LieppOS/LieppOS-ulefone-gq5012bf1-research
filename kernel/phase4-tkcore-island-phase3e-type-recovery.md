# GQ5012BF1 tkcore Phase 3E — KCFI type recovery

The proven Phase-3C method was reused:

```text
type_id = low32(xxHash64("_ZTSF" + Itanium-mangled-function-type + "E"))
```

Tool: `workspace/phase4-tkcore-island/phase3c/kcfi-recovery/kcfi_type_recover.py`.

## Independent validation

- `int(void)` → `_ZTSFivE` → `0x36b1c5a6` (`plat_tee_init`, also known Phase-3D APIs)
- `bool(int)` → `_ZTSFbiE` → `0xbd7efeae` (`plat_cpu_is_big`)
- `void(void)` → `_ZTSFvvE` → `0xa540670c` (stock `cleanup_module`)
- `int(unsigned)` → `_ZTSFijE` → `0xab53c5c9` (proven `tee_spi_cfg_padsel`)

## Affinity callback search

Stock call/body evidence fixed the shapes: ignored pointer context; match additionally consumes `w1` as an `int`; candidate returns an `int`; predicates return one-bit boolean. The search tested 4,258 candidates comprising primitive-only forms, `void *`, const/non-const pointers, and 250 plausible domain struct tags across the compatible one/two-argument shapes.

Unique matches:

| Function | Stock ID | Unique mangled type | Prototype |
|---|---|---|---|
| `need_bind_cpu` | `0x98d3ad02` | `_ZTSFbPvE` | `bool (void *)` |
| `match_cpu` | `0x7850c00b` | `_ZTSFbPviE` | `bool (void *, int)` |
| `get_candidate_cpu` | `0x89fb613d` | `_ZTSFiPvE` | `int (void *)` |

No private struct spelling is involved: the ABI intentionally uses `void *`. Expected random-collision count over 4,258 32-bit hashes is about `9.9e-7`. Compiler confirmation is the exact-GKI rebuild: all three emitted IDs equal stock, and all three function bodies are raw-byte identical.

No genksyms member-name brute force was performed.
