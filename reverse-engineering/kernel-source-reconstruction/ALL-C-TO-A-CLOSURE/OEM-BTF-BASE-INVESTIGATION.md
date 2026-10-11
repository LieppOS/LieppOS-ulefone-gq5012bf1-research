# OEM split-BTF base — reproduced from public source

Four selected vendor identities are now accepted: thermal-generic-adc, cfg80211,
mac80211 and vendor_dlkm bluetooth. The signed system_dlkm bluetooth is a different
identity and was not substituted or reclassified.

## Inputs that resolve the residual

- NothingOSS `android_kernel_6.1_nothing_mt6878` commit
  `c364c39ae8d83dfb5d72802a7718b756c238b07e`, tree
  `fb0bf39188577b248bb2bc537856964e13e1746c` (MTK ACK merge of GKI `6b18f0b574ab`).
- `gki_defconfig` plus NothingOSS KDM `mgk_64_k61_defconfig` at `957dac185efe` and
  the preserved vendor fragment.
- Clang r487747c from pinned prebuilts `7775eb113f960bc69a780b621d03a715914d4bca`.
- Pahole v1.23 from pinned kernel-build-tools `e905be252a53d20c52bd9e59df3ff8fdd46b9eab`.
- `KCFLAGS=-D__ANDROID_COMMON_KERNEL__` and release string
  `6.1.115-android14-11-g945dff7bc1bf`.

The public GKI base had 130351 types and 2300356 string bytes. A generic MTK ACK GKI-config
experiment had 130348 types; neither reproduced the OEM graph. Vendor configuration and
Kleaf-equivalent flags yield the right lineage. The release-string length matters too:
`UTS_RELEASE` appears as a character-array BTF type. A checkout-generated extra Git suffix
changes that array type. The recipe exports the pinned source tree without `.git` and
sets the evidenced OEM release, rather than allowing an unrelated checkout SHA suffix.

The reproduced `.BTF` has 130366 types, 2300745 string bytes, SHA256:
`cafe5987ff236b6385fb8ec2101d4ee27a4a11f0c6d366b3b3608e69e272202f`.
Each fresh recipe builds it, dumps it with an explicit separate ELF output, and checks this
hash. No stock .BTF payload, manual index remapping or stripping of module BTF is used.
A public local module-signing key path replaces the unavailable private key path when
building the base; that path does not enter its BTF graph. This base is an analysis/provider
input, not an accepted replacement boot kernel.

`KBUILD_MIXED_TREE` supplies the reproduced vmlinux BTF and official GKI 12901745 core
symvers separately. BTF provenance is not confused with core-kernel CRC provenance.

## Independent results

Connectivity build/final commit: `40bf42967a213af6faa45a6a579571973b8e5d15`.
Thermal build commit: `9e0e1a0df474f1e5a748d0302fba8445f13c996d`.
Thermal final commit: `ff6e97b3bf1f29c1e1fba4ba0c0e28493cbd0698` (README only).

- Connectivity: 17/17 maintained modules pass the strict verifier in B1/B2; raw stripped
  files are identical. All 577 intermediate objects are raw-identical. The former residual
  gate and all class-C skip paths are removed; BTF fields are now ordinary exact bytes.
- Thermal: 34/34 joint modules pass in B1/B2; stripped files differ only in GNU build IDs.
  130 vendor intermediate objects match after debug stripping; native intermediates and
  configs are separately recorded in the comparison JSON.
- Connectivity mutation tests: 44/44, including formerly tolerated type/name references.
- Thermal mutation tests: 11/11; only the documented GNU build-ID flip is accepted.
- Base `.BTF` bytes are identical in independent builds. The thermal base vmlinux files
  themselves differ; do not claim complete vmlinux binary identity from BTF identity.

All target executable bytes, initialized/BSS data, symbols, raw/semantic relocations,
imports/exports/CRCs/KCFI, modinfo, srcversion and BTF match stock under the sole GNU20
exception. See full ledgers under `evidence/connectivity/` and `evidence/thermal/`.
This common mechanism may help other BTF investigations, but no additional identities
were silently added to this closure scope or promoted.

## Continuation: same base closes the two DRM helpers (evidence/drm/)

The DRM helpers (Codex AUDIO-DEPENDENCIES-BATCH-02) had every non-BTF byte exact against the
public GKI12901745 base, with the same +15 types / +389 string-byte residual. Hypothesis: the
same source-generated OEM base closes them. The isolated recipe
`android_kernel_modules_audio_shared_infrastructure_ulefone_gq5012bf1-allc` @4697eac3 builds
the base in each workspace (`scripts/make-btf-base.sh`, BTF sha `cafe5987…`) and passes it via
`KBUILD_MIXED_TREE`; no target source, verifier or BTF byte changed.

Result in two fresh bundle clones (taskset 0-3, nice10, JOBS=4): unchanged strict verifier
12/12 PASS each (Codex's original recipe: 10 PASS + 2 REJECT). drm_display_helper 199 functions /
47 data / 90 imports / 140 exports / 2 KCFI / 2567 relocations; drm_dma_helper 19 / 14 / 40 / 14 /
3 / 169. Only the GNU20 range differs from stock. B1==B2 for all 12 raw modules and 265/265
intermediates; configs, symvers, target tree and base BTF identical. 34/34 actual ELF mutation
controls per build (code, rodata, data, import/export CRC, export name, modinfo, raw relocation,
symbol value, KCFI ID, BSS/section layout, BTF header/name/type/string, signature trailer;
GNU20 is the only accepted flip). Both helpers are now **A**. Six BTF-blocked identities
(thermal ADC, cfg80211, mac80211, vendor bluetooth, two DRM) are closed by one source correction.
