# `custom_ldo.ko` source candidates

## Classification

`NO_USEFUL_SOURCE`

No public or local source containing the two stock export identifiers, the two
provider identifiers together, the stock description, or an identifiable
`custom_ldo.c` shim was found. There is therefore no candidate that can be
classified `EXACT_SOURCE`, `STRONG_SOURCE_MATCH`, or `SOURCE_DELTA`.

## Exact identifiers searched

* `custom_ldo_en`
* `custom_ldo_vout`
* `will_ldo_en`
* `will_ldo_vout`
* `Custom Ldo Driver`
* `custom_ldo.c`
* `camera custom ldo`
* `wl2864 custom_ldo`
* `wl2868 custom_ldo`

## Local trees and history

Searched working trees and every available local git branch/tag/history:

* Nothing MT6878 `kernel`, `device_modules`, and `kernel_modules`
* MiCode `bsp-klee-w-oss`
* MiCode `bsp-dash-w-oss`
* MiCode MTK device modules `chagall-2.0.31`
* the complete local `vendor-reference` collection
* exact GKI workspace
* this research repository

The Nothing and vendor-reference source trees had zero occurrences of every
exact identifier and of the stock description. Six nested local git
repositories were searched with `git log --all -G`; no historical hit was
found. Project hits are generated inventories/reports from this analysis, and
the only GKI-workspace hits are the already reconstructed WL2868 provider.

Nothing's MT6878 camera adaptor source is a useful **consumer-structure
reference**, not a donor for `custom_ldo.ko`. Its generic power loop and
`subdrv_pw_seq_entry { int id; int val; int delay; }` agree with stock
`imgsensor` disassembly, but it does not contain the Ulefone custom callbacks
or either export.

## Public search

Exact-symbol and filename/description searches covered GitHub/web indexes and
explicitly scoped queries for:

* NothingOSS
* MotorolaMobilityLLC
* MiCode/Xiaomi MTK
* OnePlusOSS
* OPPO source
* realme kernel source
* Sony
* Gitee mirrors

No result contained `custom_ldo_en`, `custom_ldo_vout`, `will_ldo_en`, or
`will_ldo_vout`. Generic LDO/regulator files and older MediaTek camera custom
power tables were rejected because they do not implement the stock shim ABI.
The Sony WL2864/WL2868 material used during the provider task is likewise not
a source for this two-function consumer shim.

## Source provenance used for reconstruction

The reconstruction is source-from-binary: exact stock function boundaries,
bytes, relocations, KCFI IDs, import/export CRCs, and `imgsensor` call sites.
No donor source text was modified or represented as stock provenance.
