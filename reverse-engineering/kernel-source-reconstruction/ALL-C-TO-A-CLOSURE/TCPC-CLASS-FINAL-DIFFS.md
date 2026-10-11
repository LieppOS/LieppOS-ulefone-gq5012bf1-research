# TCPC final residuals — preserved, not reclassified

This work starts from USB-TYPEC-CLOSURE, not the older 701/709 Batch04 TCPC source.
Type-C repository: `758f9edc78c7a50d07b8629126438a3674845911`.
Charging repository: `b2a343a9d8664b77a63dc16835b5af0fd0e55cf1`.
The USB closure research branch at `7e196c32` records independent builds and detailed
source/modpost traces. These inputs are not overwritten by ALL-C experiments.

## tcpc_class

Inherited accepted reconstruction: 709/709 raw function bodies, 113/114 named data
objects, 54/54 timers. The last named data discrepancy is source-version metadata,
not an unclosed PD/timer implementation. Natural srcversion and resulting raw
symbol/string/layout/relocation metadata still prevent full stock acceptance.

No new matching token composition was found or manufactured here. The four-module
public-history fingerprint search does not cover tcpc_class's larger multi-object input
set. Its actual traced read list is the required starting point for the next experiment.
Do not infer that because all code matches, its unknown source tokens can be normalized.

## tcpc_mt6375

66/66 function bodies remain exact. The latest prior closure restored real license-before-
version declaration order. Counter prefix remains natural 455 versus stock 454, alongside
srcversion/raw symbol/string metadata. The earlier counter trace recorded 48 genuine
macro-expansion sites. A prior analysis called this an unexplained +1; the direction is
**build greater than stock**. No artificial filler, counter override, fabricated deletion,
or symbol/metadata transplant is permitted.

The new NothingOSS/MiCode scan tested 27 + 36 authentic C blobs and found no stock
fingerprint. This narrows the searched public lineage but does not explain the counter
prefix or prove absence of an unsearched OEM source release.

Next: obtain the original OEM include/declaration stream and compare actual counter
expansion provenance, or identify a new real same-directory modpost input set. Preserve
all 709/709 TCPC functions and all timers while testing it. Both modules remain C.

## Continuation: source-reproduced MTK ACK headers (evidence/usb-mtkack-counter/)

The new OEM BTF lineage (MTK ACK c364c39ae8d) differs from public GKI in two headers that
tcpc_mt6375 actually includes: `include/linux/printk.h` and `dev_printk.h` (MTK printk-debug
wrappers). Preprocessing the exact recorded tcpc_mt6375 command against both common trees gives
**byte-identical** output: the MTK additions are inactive under the pinned vendor config. The
counter prefix (`__UNIQUE_ID_license459` etc.) is unchanged, and srcversion only hashes
same-directory inputs. Rejected; the +1 counter and fingerprints are not a common-lineage effect.
