# Phase 4 — `custom_ldo.ko` reconstruction

# Final classification

**STOCK_CONSUMER_ABI_EXACT_RECONSTRUCTION**

The full consumer-visible ABI and behavior are proved exact. Both reconstructed
functions are byte-identical to stock, including size, offsets, PAC/AUT shape,
KCFI IDs, calls, and return behavior. Imports, imported CRCs, exports, export
CRCs, and all relocations also match exactly. No stock source was found, so
this is not classified `DIRECT_SOURCE_MATCH`. Whole-file identity is prevented
only by generated build-provenance metadata (`srcversion` and GKI local
release), documented below.

# Stock oracle

Frozen oracle: `workspace/phase4-custom-ldo/stock-custom-ldo.ko`.

* canonical source: `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/custom-ldo.ko`
* SHA-256: `9d3d4a3786dd71af4fdee07e4bc332526816b62143925f4e5923f286c9d91556`
* size: 10,296 bytes
* Build ID: `c9a495d571f1814a130fb47830ab1c3f72158f90`
* stock compiler: Android clang 17.0.2, r487747c / llvm revision `d9f89f4d16663d5012e5c09495f3b30ece3d2362`
* placement/load: vendor_dlkm; zero-based load index 102 (line 103)
* metadata: `custom_ldo`, version 1.0, `Custom Ldo Driver`, GPL,
  `depends=custom-ldo-wl2868`, srcversion `B1ACADEFB8818C27CA857AF`
* aliases/parameters/author: none

Complete metadata and load/dependency records:
`kernel/phase4-custom-ldo-stock-oracle.txt`.

# Source provenance

No local/public source donor was found. The minimal source was reconstructed
from stock function bytes, relocations, KCFI, CRCs, and consumer call sites.
See `kernel/phase4-custom-ldo-source-candidates.md`.

Workspace source:
`/home/armol/kernel-work/gki-12901745-workspace/lieppos/custom-ldo-recon/`.
A committed source copy is
`kernel/phase4-custom-ldo-reconstructed-source.c`.

# RED baseline

`NO_PUBLIC_DONOR_FOUND`. No false donor build was manufactured. See
`kernel/phase4-custom-ldo-RED.md`.

# Function inventory

| function | section/offset | stock size | recon size | stock/recon KCFI | bytes exact |
|---|---:|---:|---:|---:|---|
| `custom_ldo_vout` | `.text+0x4` | 28 | 28 | `0x56e5b5a5` | YES |
| `custom_ldo_en` | `.text+0x24` | 28 | 28 | `0x56e5b5a5` | YES |

Stock functions 2; reconstructed functions 2; shared 2; stock-only 0;
recon-only 0; size-identical 2; byte-identical 2. There is no init, exit,
functional data, functional rodata, bss, or module state.

# Import ABI

Exactly three MODVERSION imports match stock:

| import | provider | stock CRC | recon CRC | match |
|---|---|---:|---:|---|
| `module_layout` | GKI | `0xea759d7f` | `0xea759d7f` | true |
| `will_ldo_en` | reconstructed `custom-ldo-wl2868` | `0xdd9b9ea1` | `0xdd9b9ea1` | true |
| `will_ldo_vout` | reconstructed `custom-ldo-wl2868` | `0x23ec3223` | `0x23ec3223` | true |

The two provider symbols are the only undefined ELF symbols and each has one
`R_AARCH64_CALL26` relocation.

# Export ABI

| export and exact prototype | stock CRC | recon CRC | KCFI | consumer | match |
|---|---:|---:|---:|---|---|
| `int custom_ldo_en(int ldo_num, int enable)` | `0x239d3df2` | `0x239d3df2` | `0x56e5b5a5` | `imgsensor` | true |
| `int custom_ldo_vout(int ldo_num, int value)` | `0xfda530e0` | `0xfda530e0` | `0x56e5b5a5` | `imgsensor` | true |

Both are plain `EXPORT_SYMBOL`, matching stock. CRCs were generated naturally
by Kbuild/genksyms. Exact type proof is in
`kernel/phase4-custom-ldo-export-contract.md`.

# Forwarding contract

`custom_ldo_en` directly returns `will_ldo_en(ldo_num, enable)`.
`custom_ldo_vout` directly returns `will_ldo_vout(ldo_num, value)`.

Both incoming arguments and the provider return value are unchanged. There is
no transform, validation, clamp, scaling, range test, unit conversion, error
mapping, log, side effect, or state access. See
`kernel/phase4-custom-ldo-forwarding-contract.md`.

# Imgsensor consumer analysis

Stock `imgsensor.ko` contains exactly four call relocations: vout+enable in
`set_custom_ldo`, and vout+disable in `unset_custom_ldo`. The channel is loaded
from each sensor's `custom_*` DT mapping; the 32-bit sequence value is forwarded
unchanged. Set uses enable 1; unset reprograms the same voltage then uses enable
0. Both wrapper return values are ignored by imgsensor's callback and the
callback returns zero.

Nine stock sensor sequences and the active DT maps prove custom channels receive
1,100,000, 1,200,000, 1,800,000, and 2,800,000 setpoints. The same sequence
field is passed unchanged by stock's alternative regulator backend as both
`min_uV` and `max_uV` to `regulator_set_voltage`. The WL2868 public `value`
argument is therefore proven to be microvolts.

Full analysis: `kernel/phase4-custom-ldo-imgsensor-consumer-analysis.md`.
Exact stages: `kernel/phase4-custom-ldo-imgsensor-custom-stages.tsv`.

# Exact-GKI build

* kernel target: `//common:kernel_aarch64`
* common commit: `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`
* module target: `//lieppos/custom-ldo-recon:custom_ldo_recon`
* `BUILD_RC=0`
* compiler warnings: 0
* modpost warnings: 0
* unresolved symbols: 0
* check-no-remaining: present

Kleaf's missing signing-key diagnostics are not compiler/modpost warnings. See
`kernel/phase4-custom-ldo-build-verification.md`.

# Provider linkage

The build depends on a real source build of the reconstructed WL2868 provider,
not fake symbols. A packaging target emits the provider under stock basename
`custom-ldo-wl2868.ko`, preserving the generated `depends` string naturally.
Its unmodified reconstructed source generates
`will_ldo_vout=0x23ec3223` and `will_ldo_en=0xdd9b9ea1`. The resulting provider
`Module.symvers` is consumed through Kleaf `deps` and
`KBUILD_EXTRA_SYMBOLS`; it is neither handwritten nor patched.

# Structural verification

| metric | result |
|---|---|
| functions | stock 2 / recon 2 / shared 2 |
| stock-only / recon-only | 0 / 0 |
| size-identical functions | 2 |
| byte-identical functions | 2 |
| KCFI parity | 2/2 |
| import parity | exact, 3/3 MODVERSION records |
| export parity | exact, 2/2 names/kinds/CRCs |
| relocation parity | exact, 10/10 |
| object count | 19 / 19 |
| section-name parity | exact (including stock `.llvm_addrsig`) |
| `.text` | 64/64 bytes, byte-identical |
| `__ksymtab` / `__kcrctab` / strings | byte-identical |
| `__versions` | 192/192 bytes, byte-identical |
| `.comment` / `.note.Linux` / `__this_module` | byte-identical |
| `.rodata` / `.data` / `.bss` | absent in both |
| string count | 74 / 74; generated provenance strings differ |
| whole file | stock 10,296 / recon 10,288; not byte-identical |

There are **no instruction-level residuals**. Raw comparison:
`workspace/phase4-custom-ldo/verify-recon-vs-stock.txt`.

# Behavioral verification

| function | stock behavior | recon behavior | exact? |
|---|---|---|---|
| `custom_ldo_en` | pass two `int` arguments unchanged to `will_ldo_en`; return provider result unchanged | identical, and function bytes identical | YES |
| `custom_ldo_vout` | pass two `int` arguments unchanged to `will_ldo_vout`; return provider result unchanged | identical, and function bytes identical | YES |

Neither implementation validates, logs, accesses state, nor performs hardware
I/O itself.

# WL2868 residual impact

This task closes the former WL2868 voltage-unit question: `value` is a
microvolt setpoint, proven through stock imgsensor's shared custom/regulator
backend flow. The WL2868 provider's classification is not otherwise promoted:
its separate probe/data-layout and whole-function/source parity residuals remain,
and live hardware validation is prohibited.

# Residual differences

The only stock-vs-rebuild differences relevant to this module comparison are
generated provenance, not executable behavior or consumer ABI:

* stock srcversion `B1ACADEFB8818C27CA857AF` vs rebuilt
  `D53F851D091EB4D339CEEEA` because original source text is unavailable;
* stock vendor local release `-g945dff7bc1bf` vs exact workspace
  `-maybe-dirty`;
* generated `__UNIQUE_ID_*` counter suffixes differ as a consequence of the
  unavailable original translation-unit/include context;
* resulting `.modinfo` is 218 vs 216 bytes, Build ID/hash differ, and the full
  rebuilt ELF is 8 bytes smaller.

Description, license, version, module name, dependency, compiler comment,
section set, all functional/code sections, and all ABI records match.

# Safety

All analysis and verification were offline/read-only with respect to the
device. No I2C/GPIO/regulator operation, camera open, power sequence,
insmod/rmmod, bind/unbind, sysfs write, DT/DTBO change, flash, or slot switch
was performed.

# Runtime-validation status

**NOT PERFORMED BY POLICY.** Static equivalence is sufficient to prove this
state-free shim; hardware behavior remains owned by its provider.

# Evidence index

* `kernel/phase4-custom-ldo-stock-oracle.txt`
* `kernel/phase4-custom-ldo-{functions,objects,imports,exports,modversions,relocations,strings}.tsv`
* `kernel/phase4-custom-ldo-export-contract.md`
* `kernel/phase4-custom-ldo-forwarding-contract.md`
* `kernel/phase4-custom-ldo-imgsensor-consumer-analysis.md`
* `kernel/phase4-custom-ldo-imgsensor-custom-stages.tsv`
* `kernel/phase4-custom-ldo-source-candidates.md`
* `kernel/phase4-custom-ldo-RED.md`
* `kernel/phase4-custom-ldo-build-verification.md`
* `kernel/phase4-custom-ldo-reconstructed-source.c`
* `workspace/phase4-custom-ldo/` raw oracle, disassembly, consumer call sites,
  source/build glue, symvers, build logs, rebuilt module, and verifier output

# Final verdict

**COMPLETE at STOCK_CONSUMER_ABI_EXACT_RECONSTRUCTION.** Both functions are
byte-identical; prototypes, KCFI, imports, exports, CRCs, relocations,
forwarding behavior, and provider linkage are exact. Only nonfunctional,
generated build-provenance metadata differs. Stop here; no `sc851x_charger`
work was started.
