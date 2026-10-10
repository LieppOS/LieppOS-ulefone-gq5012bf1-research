# Batch02 — offline independent reproduction

Source repositories/exact compiled commits are in SOURCE-REPOSITORIES.tsv; bundles under
family/source recover each recipe. Public pins unchanged from Batch01. No private headers,
prepared provider tables, cached target/provider objects or historical/tmp scripts are inputs.

```sh
export LIEPPOS_IOMMU_MIRROR=/home/armol/kernel-work/interconnect-pin-mirror
export JOBS=8
bash /path/to/fresh-recipe/scripts/bootstrap.sh /space-free/new-ws
bash /path/to/fresh-recipe/scripts/bulk-build.sh /space-free/new-ws B1
bash /path/to/fresh-recipe/scripts/bulk-build.sh /space-free/new-ws B2
python3 /path/to/fresh-recipe/scripts/verify.py \
  /space-free/new-ws/out/B1 /path/to/actual-stock-operands /path/to/full-ledgers
```

Default verification covers only that family's owned targets. Joint27 witness compilation
does not transfer ownership or prove every external producer's complete implementation.
Reference hashes permit validation without stock operands; all-axis ledgers require actual
stock. Bootstrap checks immutable Git trees, Clang subtree, official GKI12901745 symvers;
base config8f9d1d2901dfbc77062764b4f9e21bc1000097392a36f8ba1eebd9c47d35f50e.
Clang-r487747c/LLVM IAS/-faddrsig, stock macro-prefix-map and exact release string
6.1.115-android14-11-g945dff7bc1bf reproduce the full stripped stock ELF.

## What actually ran

scripts/cleancheck.sh cloned ALL FOUR committed recipes without hardlinks, hid original
Batch02 dev workspace AND original four recipe paths, verified public inputs once, then
actually executed each family clone's engine as joint27 B1/B2: **eight fresh compilations**.
Every source/provider tree is reassembled from immutable ALPS; no target cache survives.
Compatible base headers/config are hash-verified and reused, not regenerated27 times.

For each family,27 raw/stripped outputs,105 intermediate objects, source/config/ABI/provider
identities and full stock comparisons agree between B1/B2. Those same operands agree across
all four independently cloned engines. All compiler/modpost exits0, no warnings/errors.
44/44 source CRC/licence/namespace/required KCFI-prefix boundaries and19 naturally derived
external slots match. GKI core slots come from the verified official symbol table, not a new
full kernel build. Core provider prefix words remain UNKNOWN in the provider graph; exact
consumer instructions and imports still match stock. No fabricated kernel KCFI witness.

An earlier successful eight-build proof was repeated after removing accidentally tracked
Python bytecode from the memory recipe and adding ignore rules. No C/header/build behavior
changed. Public prepared base inputs were reverified/reused; targets/providers compiled
freshly again. Final recipes contain no tracked .pyc/.o/.ko. Both proof logs are retained.

## Patches

Only0001-joint-kbuild-scope.patch:27 targets plus8 provider-only units, inherited Kconfig
flags/composites unchanged. External absolute-src wildcard/include correction; ICC core
trace -I$(src); power trace resolves genuine public header through include/trace; CCCI
producer gets original upstream include flags even when CONFIG_MTK_ECCCI_DRIVER=m.
No C/H logic or board table patch was needed. All27 are direct ALPS source matches.

Source producer-only units: aee_aed,clk-common,clk-chk-mt6878,mrdump_mini,port_proxy,
gpueb_ipi,gpufreq_v2,tinysys-scmi. The first three include already certified clock provider
code solely for required ABI dependencies; no Batch01 reconstruction or CMDQ work repeated.
Do not install these helper-unit outputs as replacements for actual whole producer modules.

## Proof policy and replay

Parsed GNU20-byte descriptor is the ONLY normalization. Every function,initialized data/BSS
layout,CRC/KCFI/licence/namespace,raw+semantic relocation,section/header/string/symbol table,
modinfo/vermagic/srcversion/signature byte outside that range is unchanged. No added signature
or blanket build-provenance exception.16 actual ELF mutation cases test this acceptance;
canonical audit mutation tests are separate. See per-owned-module full ledgers and final
cleancheck-result.json. Hardware/source roles and firmware boundaries remain separate.

Repeat complete certificate from a NEW check path with
LIEPPOS_BATCH02_CLEANCHECK=/space-free/new-check bash scripts/cleancheck.sh.
Research verifier/report helpers' default check path is the performed canonical location;
use that location or adapt path configuration explicitly. Never hide a workspace in use.
No phone, ADB, register write, IRQ/DMA/mailbox command, firmware operation or push.
