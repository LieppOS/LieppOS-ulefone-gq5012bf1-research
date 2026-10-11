# MT6375 counter/module metadata investigation

## Measured origin

`__UNIQUE_ID_*` module/addressable names come from the pinned kernel's macro expansion using the translation unit's `__COUNTER__`, not from a stock symbol-table template. The final `.mod.c` metadata names separately consume the common/header counter prefix: vermagic/name/depends/srcversion are generated through the unchanged modpost source and ordinary kernel headers.

The full preprocessed MT6375 translation unit and tracked source/header locations were examined. `evidence/metadata/counter-expansions.json` records 48 expansion sites with source file, source line, expanded declaration and unique identifiers. Direct C-file module metadata appears at the driver footer; prior expansions arise in the actual included common headers. `evidence/metadata/final-inputs/` preserves the real object `.cmd`, Kbuild composition, generated `.mod.c`, include prerequisite hashes, read trace and naturally regenerated fingerprints. No private/dummy counter declaration, `__COUNTER__` override, symbol rename or stock table copy was used.

## Proven declaration-order correction

The pinned ALPS 2.0.27 MT6375 predecessor at `5e415e059253ce0d2e61c97108e5f5785d71f06f` declares author, description, **license, version**. The imported 2.0.31-derived reconstruction had author, description, **version**, class `#endif`, **license**. Stock's ordered `.modinfo` follows license before version. Patch `0003` restores that ordinary source declaration order. This is a real public predecessor plus stock-order observation, not a compiled metadata transplant.

| Declaration | Stock suffix | Baseline suffix | Corrected source suffix |
|---|---:|---:|---:|
| addressable init | 454 | 455 | 455 |
| addressable cleanup | 455 | 456 | 456 |
| author | 456 | 457 | 457 |
| description | 457 | 458 | 458 |
| license | 458 | 460 | 459 |
| version | 459 | 459 | 460 |

The baseline version's accidental numeric agreement was not proof of correct lineage. Restoring the license/version order makes the **remaining +1 prefix displacement consistent**, rather than pretending a coincidentally named symbol fixed it. Order is resolved; prefix origin against unavailable OEM inputs is not.

## Fingerprint and full acceptance

- Baseline natural srcversion: `EA7DA9D08253B7F0F495FB1`.
- Corrected natural srcversion: `86B9C4E19D9B7E5A9933F96`.
- Stock: `D27BCF95DDC8F09B632224B`.
- Actual sumversion input: `tcpc_mt6375.c` only; TCPC `inc/` headers are excluded by the measured same-directory dependency test. They can affect macro counters/ABI/code, but their bytes do not directly enter this fingerprint.
- All **66/66** compiled functions, CRCs, licenses, KCFI and raw/semantic relocation records remain exact. Source versions, counter names/raw symbol table and string table prevent complete acceptance.

The stock suffix alone does not identify which OEM header/declaration consumed one fewer counter. Public/historical candidates preserve genuine input lineage, but no authentic original GQ5012BF1 include/config trace was found. Config flags or unused declaration removal cannot be invented merely to hit 454. Require original OEM C/header/dependency inputs, trace counter consumption and rebuild normally. Keep C; no acceptance rule changed.
