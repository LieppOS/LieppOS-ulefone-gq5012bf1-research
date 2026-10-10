# Independent bulk reproduction

Four immutable recipe commits are in SOURCE-REPOSITORIES.tsv and per-family source/COMMIT;
recovery Git bundles are preserved beside them. All clones share identical verified engine,
public pins, joint35-target scope and9 provider-only object scope. OWNERSHIP.json identifies
which distinct modules each repository owns; joint witnesses do not transfer ownership.

## Offline portable build

Use a space-free workspace, a fresh clone of any family recipe, and the preserved public
input mirror `/home/armol/kernel-work/interconnect-pin-mirror`. Bootstrap verifies every
Git tree, the Clang subtree and official GKI12901745 symvers SHA256. No network is used:
bootstrap requires LIEPPOS_IOMMU_MIRROR. No private ACK/header overlay is permitted.

```sh
export LIEPPOS_IOMMU_MIRROR=/home/armol/kernel-work/interconnect-pin-mirror
export JOBS=8
bash /path/to/fresh-recipe/scripts/bootstrap.sh /space-free/new-ws
bash /path/to/fresh-recipe/scripts/bulk-build.sh /space-free/new-ws B1
bash /path/to/fresh-recipe/scripts/bulk-build.sh /space-free/new-ws B2
```

One base config/modules_prepare per workspace; each bulk build deletes/reassembles the
entire target/provider source tree and recompiles it. Every build verifies base config
`8f9d1d2901dfbc77062764b4f9e21bc1000097392a36f8ba1eebd9c47d35f50e`
and official GKI ABI. No full GKI rebuild or cached target output substitutes for compilation.
GKI release is stamped `6.1.115-android14-11-g945dff7bc1bf`; Clang-r487747c, LLVM IAS,
-faddrsig and exact macro-prefix-map reproduce the stock stripped operands.

Object/link exit files must all be0; reject target compiler/modpost warnings/errors.
The four known CMDQ provider-CRC failures are preserved, not hidden or copied from stock.
Verify only an owned accepted module with:

```sh
LIEPPOS_VERIFY_MODULE=mtk-smi python3 /path/to/smi-recipe/scripts/verify.py \
  /space-free/new-ws/out/B1 /path/to/extracted-stock-modules /path/to/report
```

Select a module actually owned by the chosen family. CMDQ's cmdq_helper_inf accepts;
its other four drivers intentionally fail the full stock verifier. Stock operands are
read-only verification inputs and are never build code/data operands. No srcversion,
vermagic, code, data, ABI or signature normalization: only parsed GNU20-byte descriptor.

## Performed proof

`scripts/cleancheck.sh` cloned all four committed recipes without hardlinks, moved the
original development workspace and all four original recipe directories out of reach,
bootstrapped from the public mirror and freshly built ALL35 as B1/B2. Both builds completed
object/main/stock-provider modpost with exit0.35 raw plus35 stripped outputs and120
intermediate objects are deterministic; source trees, configurations, two module symvers
sets, natural external ABI tables and producer CRC/licence/KCFI witnesses also match.

The terminal comparison initially failed solely on nondeterministic ordering of four
unaccepted CRC-name sets. Sorting those names and rerunning comparison over preserved
outputs fixed it: no target/source change or recompile was needed. See check-determinism.py
and cleancheck-result.json. All31 accepted modules independently match complete stock ELF;
all four CMDQ residuals reproduce. Fifteen actual acceptance mutation cases pass.

## Patches and provider details

- 0001: Kbuild-only35-target/9-helper scope, inherited flags/composites retained, external
  absolute-src wildcard repair. No generic donor implementation rewrite.
- 0002: typed source reconstruction of display PWM names. clkdbg gains top_disp_pwm_sel,
  peraop_disp_pwm0/1; clkchk gains trace IDs269/270 and raises count269→271. One source
  blank line reproduces the stock BUG diagnostic lines1571/1589. Compiled pointers/code
  are regenerated normally; no stock array or instruction bytes are transplanted.
- Source lineage and semantic string-array evidence are preserved under evidence/.
- True stock-provider boundaries:152/156 CRC/licence/KCFI-prefix exact, four CMDQ CRC failures;
  all required prefix words match. All47 external slots regenerate from real source.
- A separate real public scpsys-dummy variant regenerates legacy depends=scpsys-dummy
  link metadata for DVFSRC/MT6878 SCP. It is NOT a shipped identity or invented batch member;
  the actual stock exporter is still checked separately. Its one different export licence
  is explicitly recorded, not conflated with the stock provider. No runtime substitution
  or safe loader change is inferred from CRC compatibility.

No phone, live CMDQ/DMA/IRQ/power operations, firmware commands or push.
