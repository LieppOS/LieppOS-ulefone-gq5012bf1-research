# pd_dbg_info — Ulefone GQ5012BF1

Status: exact-GKI build environment investigation

## Stock

SHA256:

`3b3553cfee8269a075ac30646301f45b7ee923820676bb286b561b31dc9d217c`

Stock metadata:

- name: `pd_dbg_info`
- license: `GPL`
- description: `PD Debug Info Module`
- author: Lucas Tsai <lucas_tsai@richtek.com>
- dependencies: none
- exported symbol: `pd_dbg_info`
- export CRC: `0x48fb7437`

The stock binary embeds the source path:

`../kernel_device_modules-6.1/drivers/misc/mediatek/typec/tcpc/pd_dbg_info.c`

NothingOSS donor:

`device_modules/drivers/misc/mediatek/typec/tcpc/pd_dbg_info.c`

Donor source SHA256:

`477df9d180e18d3a19e3d2edb96c1d635e01eb5f0b85cbc72a2ae71fe172370a`

Donor header SHA256:

`88f4fb71ef1316c98cc7514bb520f4cf4e5896133bf49674722379dd0c0540fe`

## First exact-GKI build blocker

The unchanged donor source compiled successfully, but modpost failed with:

`missing MODULE_LICENSE() in pd_dbg_info.o`

This is currently treated as a Kconfig/object-composition/build-environment
issue, not source divergence.

The stock module clearly contains GPL module metadata, so no metadata will be
manually added until the original NothingOSS Kbuild/Kconfig composition is
identified.

## Build blocker resolved: CONFIG_PD_DBG_INFO

The donor source itself contains the complete module metadata and implementation.

`pd_dbg_info.c` is wrapped by:

`#if IS_ENABLED(CONFIG_PD_DBG_INFO)`

including:

- implementation of `pd_dbg_info`
- `EXPORT_SYMBOL(pd_dbg_info)`
- init/exit routines
- `MODULE_DESCRIPTION`
- `MODULE_AUTHOR`
- `MODULE_LICENSE`

The standalone exact Google GKI configuration does not define
`CONFIG_PD_DBG_INFO`, so the first validation build compiled an effectively
empty translation unit. Modpost therefore reported:

`missing MODULE_LICENSE() in pd_dbg_info.o`

This was not missing source or missing metadata.

The original MediaTek Makefile builds `pd_dbg_info.o` alongside the TCPC
framework under `CONFIG_TCPC_CLASS`, while the contents of `pd_dbg_info.c`
remain gated by `CONFIG_PD_DBG_INFO`.

For standalone exact-GKI validation, the vendor feature state is reproduced
via the build wrapper without modifying `pd_dbg_info.c`.

Stock export CRC for `pd_dbg_info`:

`0x48fb7437`

This is exactly the CRC imported by both:

- `tcpc_class.ko`
- `tcpc_mt6375.ko`

No reverse engineering is indicated.

## Exact-GKI comparison result

After reproducing `CONFIG_PD_DBG_INFO=y`, the unchanged current NothingOSS
source builds successfully against exact GKI 12901745.

ABI validation:

- imported symbols: exact
- imported MODVERSION contract: exact
- exported `pd_dbg_info` CRC: exact (`0x48fb7437`)
- `init_module` size: exact

However, the implementation is not byte-identical.

Function sizes:

| Function | Stock | Current Nothing donor |
|---|---:|---:|
| `pd_dbg_info` | 756 | 716 |
| `print_out_dwork_fn` | 528 | 448 |
| `cleanup_module` | 188 | 180 |
| `init_module` | 48 | 48 |

Stock `.text` SHA256:

`0da6c26de5c4ee71ba88492a8ad8e42b1181bdb5fbaced3cb3d3013ded3cf642`

Current donor build `.text` SHA256:

`dc29919968f20783e3b077506253ba914f8256d183585f5c7f6865d306c1bc33`

`PD_TEXT_CMP_RC=1`

### Strong source-revision clue

Stock module metadata contains two parameters:

- `mn_limit:uint`
- `dbg_log_limit:uint`

The current NothingOSS donor build exposes only:

- `dbg_log_limit:uint`

Therefore the current NothingOSS `pd_dbg_info.c` revision cannot yet be
classified as an exact direct source match.

The exact ABI together with the missing `mn_limit` parameter strongly suggests
a closely related MediaTek/Richtek source revision rather than an unrelated
implementation.

Current classification:

`LIKELY_PLATFORM_MATCH / DIFFERENT_SOURCE_REVISION`

Next step is to search NothingOSS/MediaTek source history for a revision
containing `mn_limit` before considering binary reconstruction.

## Final reconstruction result

`pd_dbg_info.ko` is now classified as:

**RECONSTRUCTED_EXACT_MATCH**

The stock-only delta from the public NothingOSS donor was recovered and rebuilt
against exact Google GKI 12901745.

Recovered stock additions:

- `mn_limit` module parameter
- default `mn_limit = 10000`
- `size_t mn_cnt` queue counter
- queue-counter increment/decrement/reset semantics
- backlog-drain threshold behavior
- generalized `%zu` / `__func__` WARN strings

Important behavior:

`mn_limit` does not reject allocations or drop new log messages.

When the per-second `dbg_log_limit` has been reached, the worker normally waits
for the next rate window. If the queued message count exceeds `mn_limit`, that
delay is bypassed and queued messages are drained until the backlog falls back
to the configured threshold.

Final validation:

- `pd_dbg_info` size: 756 / exact
- `print_out_dwork_fn` size: 528 / exact
- `cleanup_module` size: 188 / exact
- `init_module` size: 48 / exact
- `.text`: byte-identical
- `.init.text`: byte-identical
- `.exit.text`: byte-identical
- `.data`: exact
- `.bss` layout: exact
- `__param`: exact
- imports: exact
- MODVERSION imports: exact
- export CRC: `0x48fb7437`
- relocations: exact
- `PD_TEXT_CMP_RC=0`

Only full-module differences are build provenance:

- embedded source path
- vermagic
- GNU build ID

Primary reconstruction report:

`kernel/phase4-pd-dbg-info-reconstruction.md`

Final reconstruction workspace:

`$GKI_WS/lieppos/pd-dbg-info-recon/final/`

## Superseded by final reconstruction report

This file is the historical discovery/build/debugging log for `pd_dbg_info.ko`.

Authoritative final report:

    kernel/phase4-pd-dbg-info-reconstruction.md

Final classification:

    RECONSTRUCTED_EXACT_MATCH

The final reconstructed implementation matches stock code-bearing sections,
imports, MODVERSIONs, export CRC, data layout, parameters and relocations.
Remaining full-module differences are build-provenance metadata only.

Keep this file as provenance for the original CONFIG/build-environment
investigation and discovery of the `mn_limit` source revision delta.
