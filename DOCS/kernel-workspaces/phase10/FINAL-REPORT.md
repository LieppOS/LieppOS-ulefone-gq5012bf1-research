# Phase 10 — source integration and offline boot closure

## Actual result: PARTIAL, non-deployable

The dev17 **candidate-owner-fixes** profile completed a genuine source-built kernel and 742-module build. The offline bundle selects 741 modules and independently passes depmod with **zero unknown symbols and zero version disagreements**. The untouched dev17 full-device profile failed compilation; the successful candidate contains two explicitly proposed, not owner-committed, build-rule patches. This is not an unmodified owner build or a hardware-ready ROM.

Infrastructure repository: `/mnt/SamsungSSD/LieppOS-kernel-infra-phase8`, branch `claude/kernel-infra-phase10`.

Final infrastructure HEAD: `95489cd2ec7fc4a82a800d77c1298d7297a1832b`.

Implementation commits in this finishing pass:

- `35aec52ec78676483bea8224c9981393a3303242`: owner-overlay integration, dev17 candidate proposals, link-only provider staging, machine-readable owner handoffs and regression fixtures.
- `95489cd2ec7fc4a82a800d77c1298d7297a1832b`: exclude stock fallback ELFs only when an authenticated `modules.builtin` entry proves a built-in counterpart; accurately label generated loader-graph edges.

Phone-specific reports are committed in this research repository, separately from infrastructure source. This report and the adjacent evidence files constitute the research delivery; the containing research commit identifies them without a self-referential hash.

## Source/build identities

| Item | Actual identity/result |
|---|---|
| dev15 owner source | `1aa773e5feb354a36d0273da61c7fcf7873595c5` |
| dev16 owner source | `446ad5e4ee5b31a8f9ae8b3d92c6a788e20f2a57` |
| dev17 owner source | `c933d3ae32807025aaa88fdc8c2eafb22f66a135` |
| Latest Codex source consumed here | `d42b118e6824fba339bc4dbc6771c6b684815dfb` |
| dev17 candidate private build HEAD | `70a15925e029680b1aadac29d156f553717a9890` |
| Candidate source classification | MIXED_SOURCE: owner commit + identified sealed FT3680 firmware-table overlay + two proposed build-rule patches |
| Actual kernel release, dev15/dev16/dev17 candidate | `6.1.115-mt6878-gq5012bf1-dev15+` |
| dev17 candidate Image SHA256 | `153862636b6d8872d26ebfbc2d8833df7fbff8baf8e4f90cda91bfe81a4bd404` |
| Candidate config SHA256 | `9887fe52e71a374f5f3f9c0645d33bb655d29058878bce93f1911dac37f22f14` |
| Canonical Module.symvers SHA256 | `c9ffa107093c92d3f93d59b7feadef6f5c5e4f1c67830e1e29db5f9f8009624c` |
| Candidate exports | 19,759 total: 15,188 vmlinux + 4,571 module exports; 481 external-module exports included |
| New BTF-enabled build | NOT RUN; this candidate is BTF-off |

The release collision is **FAIL**, not silently renamed to dev16/dev17. Source revisions, sealed overlays, synthetic build commits, actual release strings and artifact digests remain separate fields.

## Dev15 reference and dev16 integration

The platform has working dev15/dev16/dev17 descriptors and authenticated committed-source imports. A path-stable working-tree handoff preserves Kbuild-recorded paths while freezing predecessor artifact collections.

The independent dev15 set contains **754/754** modules, with a closed current-target symbol/CRC graph. Against the owner's frozen reference, the recorded classes are:

- 747 `LOADED_CONTENT_IDENTICAL`;
- 4 `PATH_STRINGS_ONLY`;
- 1 `BUILD_PATH_OR_TIMESTAMP_ONLY`;
- 2 `ABI_IDENTICAL_CONTENT_DIFFERENT`.

These classes are not a claim that all 754 entire ELF files are byte-identical. The raw build also reports duplicate exporters and modinfo/provider-choice inconsistencies; a closed symbol graph alone does not authorize staging all providers together.

The real dev16 source build produced 754 modules. Its Image and canonical symvers match dev15; 752 module files match and two changed (`yft_devinfo` and WLAN). The source identity is dev16 even though the owner retained the dev15 release string. See `evidence/delta-dev15-dev16.json` and `evidence/dev15-reference-summary.json`.

## RPMB / TrustKernel

Candidate configuration disables Trustonic and selects `CONFIG_TRUSTKERNEL_TEE_SUPPORT=m`. `rpmb-mtk.ko` imports the RPMB/UFS providers, not a Trustonic/mobicore provider. Its actual dependency metadata is `ufs-mediatek-mod,rpmb`; the stock dependency name `ufs-mediatek-mod-ise` does not name the shipped plain UFS provider.

A genuine failure in the owner dev17 build was:

```
drivers/misc/mediatek/geniezone/tz_system.c:49:10: error: 'tee_client_api.h' file not found
```

The candidate applies `proposal-dk17-geniezone-trustkernel-gp-header`: a narrow include-path proposal, not a rewrite of production TEE code. The source owner must review/commit its final form.

There is still an authentic source/stock difference: stock `rpmb-mtk` imports `rpmb_get_rw_size`; this candidate does not. Relocation inspection places the stock call in `rpmb_ioctl_ufs`. No matching local original implementation was found during this pass. **No speculative RPMB implementation was substituted.** DeepSeek must account for this difference; symbol closure does not prove RPMB protocol parity.

RPMB, storage/UFS and TrustKernel early-boot groups are `CLOSED_AT_LINK_LEVEL_ONLY`. The missing input is the authenticated stock **vendor_boot modules.load / loader configuration**, together with boot artifacts needed to establish actual first-stage behavior. Stock ELF placement does not prove the loader includes a module. No RPMB command or secure-world session was performed.

## Camera providers and validated loader substitution

The dev17 source selects external ISP7SP-family camera providers, including `mtk_ccuv`, ISP7SP camsys, imgsensor and ISP7SP DPE. Twelve donor/competing module outputs disappeared relative to dev15, including Trustonic outputs and legacy camera families.

With `CONFIG_MTK_CCU_RPROC_LEGACY=n`, in-tree modpost cannot resolve `mtk_ccu_rproc_ipc_send` / `mtk_ccu_ipc_register` for `mtk-vmm-isp71-regulator` and `mtk-mmdvfs-ccu`; external ccusys is built later. Simply enabling the bool puts the legacy provider in vmlinux and produces undefined module-only SMI/ICC/dma-buf/mrdump references.

The candidate's second narrow proposal, `proposal-dk17-ccu-legacy-module-only`, uses the parent `CONFIG_MTK_CCU_RPROC=m` value under the legacy bool gate. It builds `mtk_ccu.ko` only as an in-tree link-time provider. Packaging explicitly selects `mtk_ccuv.ko` instead.

All six legacy exports have identical CRCs in the source-built substitute. Every CCU import needed by the affected regulator, mmdvfs, imgsensor and ISP7SP camsys consumers is satisfied. These are **target CRCs**, not a stock-ABI compatibility claim. The raw build retains six duplicate-export findings; the staged bundle contains only the selected exporter.

The engine preserves original ELF `depends` metadata and separately generates substituted loader dependencies. It rejects missing substitutes, CRC drift, missing exports, empty export sets, duplicate declarations and substitution chains/self-references. It verifies ELF digests and metadata before using the generated graph. Depmod independently verifies the staged result.

The raw module-set's two remaining `depends-inconsistent` findings concern imgsensor and ISP7SP camsys: equivalent-provider modpost ordering differs between in-tree/external builds. The selected staging graph is closed; this is not achieved by editing compiled ELFs.

## Device-tree provenance

Four declared dev17 DT artifacts compiled; all three declared overlay applications succeeded offline. The two board DTBOs independently reproduce owner artifacts byte-for-byte:

| Artifact | SHA256 | Effective trust |
|---|---|---|
| Board, nominally trusted | `e9896d333cd3be163a890df6eed525fe6770dd73a6e0c4e635eb7994e8459c8a` | PROVENANCE_PENDING |
| Board, explicitly pending | `a34b20311d56a2a2c7387724e1e5ca857f7b0bdd19217e4b71276f0d9a546583` | PROVENANCE_PENDING |

The nominally trusted board overlay shares **six properties** with registered pending content and is automatically downgraded. Both board overlays are excluded from the trusted-policy bundle. The platform base remains TRUSTED_AUTHORIZED; the donor board remains REFERENCE_BOARD_ONLY. Neither proves device-specific hardware integration. The device-tree consistency check remains MISSING.

No disputed DT values were silently promoted. Provenance overlap is a conservative exclusion, not a declaration that independently sourced identical values can never be authorized; the source owner needs permitted evidence to resolve it.

## Latest Codex FPSGO/C2PS

The dev15 `codex-d42b118` profile consumes the committed owner integration contract and enables `CONFIG_LIEPPOS_PERFORMANCE=m` and `CONFIG_LIEPPOS_C2PS=m`. Existing platform settings are retained, including `CONFIG_NONLINEAR_FREQ_CTL=y`, `CONFIG_MTK_OPP_CAP_INFO=y`, and `CONFIG_MTK_SCHEDULER=m`.

A real contract smoke test applied the owner patch to the two authentic dev15 base files, copied the authenticated owner payload into the declared destination and committed a clean private fixture. Both base/patched file digests and the owner patch digest were checked. This was **contract application only, not a kernel build**.

Full latest-Codex compilation/strict modpost: **NOT RUN**. Runtime readiness: **UNPROVEN**, acceptance **HOLD**. The fixture cannot establish nonlinear-frequency compile success, teardown safety, scheduler behavior or a closed FPSGO/C2PS runtime graph. Older Codex build results do not certify this revision.

A new clean profile build was not launched below the 6 GiB metadata restart gate. Resume only after a safe capacity projection or a separately verified incremental transfer plan. Do not disable nonlinear-frequency interfaces to make compilation pass.

## Offline Android bundle and remaining blockers

Bundle:

```
/home/armol/kernel-work/lieppos-kernel-p7/bundles/gq5012bf1-mt6878-dev17-candidate-owner-fixes-in-tree
```

- 741 staged modules: vendor_boot 195; vendor_dlkm 198; system_dlkm 58; unplaced 290.
- Unplaced modules are not automatically loaded.
- Staged ABI, module_layout, vermagic, provider closure, first-stage dependency ordering and depmod checks: PASS.
- Seven early-boot groups (camera, charging/PD, display, RPMB, storage/UFS, TrustKernel, touch): CLOSED_AT_LINK_LEVEL_ONLY, not complete boot readiness.
- Stock corpus: 393/398 identities source-built; 277 interface-equivalent and 116 interface-drift relative to stock. One absent `.ko` is classified built-in by source/config analysis; four have no build rule.
- Stock compatibility: all 398 stock ELFs classify CRC-mismatch against this target. Do not mix them into the new module set.
- Conservative fallback report lists five stock identities: `c2ps_perf_ioctl`, `fpsgo`, `hbt`, `mtk_c2ps`, `timer-mediatek`. The last is classified built-in by source/config analysis but has no matching entry in the authenticated `modules.builtin` list; that stronger packaging proof is absent, so it is not silently removed from fallback requirements.

Six explicit bundle blockers remain:

1. `remaining-stock-modules-abi` — FAIL;
2. `device-tree` — MISSING;
3. `stock-boot-images` — MISSING;
4. `bootconfig` — MISSING;
5. `avb-signing-prerequisites` — BLOCKED;
6. `kernel-release-identity` — FAIL.

Required owner evidence includes authenticated boot/vendor_boot/init_boot images and loader metadata, bootconfig, DT authorization, AVB chain/rollback policy and an explicit signing/bootloader decision. No keys or loader lists were fabricated. The machine-readable handoff additionally records source/compiler failures, raw duplicate-provider findings and per-module boot-input requests.

## Verification, safety and resumption

Final regression run: **148 tests, OK, 11 skipped** (137 executed). The btrfs-backed workspace fixtures were enabled with `LIEPPOS_WS_TEST_ROOT`; unavailable optional integration fixtures remain skipped. Log: `evidence/phase10-final-unittest.log`.

Final capacity measurement: **5.86 GiB metadata headroom**, **109.53 GiB free**. No clean full kernel build was launched in this finishing pass; only unit/integration fixtures, DT compilation, ABI analysis and offline staging ran. The existing 4 GiB hard floor and 6 GiB clean-build restart margin were not weakened.

Strict historical stock certification remains **440/458**, LieppOS experimental OK **6/458**, hardware-validated replacements **0**. Protected directory access: NO. Phone access: NO. Push: NO. Production owner worktrees were not changed. The corrected `wl2864c_ldo_en` success return was not reverted. Stock `.o` files were not source-build inputs. Unrelated existing research files `-.0` and `-.1` were left alone.

See [RESUME.md](RESUME.md) for reproducible commands and remaining owner actions. Hash-bearing reports are preserved under [evidence/](evidence/); kernel images and module binaries remain in the engine workspace, not duplicated into Git.
