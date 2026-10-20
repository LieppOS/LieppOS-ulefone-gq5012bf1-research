# Phase 10 continuation

## Stopping state

Infrastructure branch `claude/kernel-infra-phase10`, HEAD `95489cd2ec7fc4a82a800d77c1298d7297a1832b`, in `/mnt/SamsungSSD/LieppOS-kernel-infra-phase8`.

Current working-tree lease: `gq5012bf1-mt6878-dev17:candidate-owner-fixes`. Its physical source/output paths remain at the dev14 tree home to preserve Kbuild command identities; predecessor artifacts are frozen. Do not delete the old-looking physical directory or independently reuse a predecessor's tree.

The candidate has a completed 742-module build, a 741-module offline staged set, and successful independent depmod validation. Its real release is still `6.1.115-mt6878-gq5012bf1-dev15+`. **Do not flash or call it deployable.**

## Read-only / offline reproduction

```bash
cd /mnt/SamsungSSD/LieppOS-kernel-infra-phase8/scripts
R=/home/armol/kernel-work/lieppos-kernel-p7
./lieppos-kernel capacity
./lieppos-kernel --root "$R" abi moduleset \
  --target gq5012bf1-mt6878-dev17:candidate-owner-fixes
./lieppos-kernel --root "$R" abi compat \
  --target gq5012bf1-mt6878-dev17:candidate-owner-fixes
./lieppos-kernel --root "$R" boot dt-declared \
  --target gq5012bf1-mt6878-dev17 --profile candidate-owner-fixes
./lieppos-kernel --root "$R" boot bundle \
  --target gq5012bf1-mt6878-dev17 --profile candidate-owner-fixes
./lieppos-kernel --root "$R" handoff \
  --target gq5012bf1-mt6878-dev17:full-device \
  --target gq5012bf1-mt6878-dev17:candidate-owner-fixes \
  --bundle "$R/bundles/gq5012bf1-mt6878-dev17-candidate-owner-fixes-in-tree" \
  --out "$R/runs/dev17-owner-handoff.json"
```

These commands analyze/re-stage existing outputs and compile declared DTs; they are not permission to launch a clean kernel rebuild. Bundle generation replaces this engine-owned generated bundle. Preserve copies of reports needed as historical evidence first. `abi moduleset` uses any current frozen-reference/previous-collection context; the saved Phase 10 reference evidence should not be overwritten with a self-comparison and relabeled independent proof.

Tests:

```bash
cd /mnt/SamsungSSD/LieppOS-kernel-infra-phase8/scripts/kernel-workspace
LIEPPOS_WS_TEST_ROOT=/home/armol/kernel-work/lieppos-kernel-p7/scratch \
  python3 -m unittest discover -s tests -q
```

Last result: 148 tests, OK, 11 skipped.

## Next source-owner actions

### DeepSeek

1. Review the two narrow candidate patch proposals in `scripts/kernel-workspace/kernel-engine/patches/proposal-dk17-*` (GP-header include selection and legacy CCU tristate build rule). Neither is an owner commit. The unmodified profile's compile failure is preserved in its stage log.
2. Choose the CCU integration contract: retain a declared ABI-verified link-only provider or implement an owner-designed two-pass modpost/symvers flow. Never stage both exporters. Keep original ELF metadata separate from regenerated loader dependencies.
3. Give the next owner source revision a distinct LOCALVERSION. Current dev15/dev16/dev17 vermagic strings collide despite distinct source identities.
4. Account for stock `rpmb_get_rw_size` usage in `rpmb_ioctl_ufs`; the candidate lacks this import. Do not reconstruct secure storage logic speculatively.
5. Resolve authorization of the six pending-overlap properties in the nominally trusted board overlay. Both board DTBOs are excluded from trusted-policy bundles today.
6. Confirm the timer built-in evidence and four absent module identities; a source/config built-in classification is not an authenticated `modules.builtin` entry or hardware validation.

### Codex / build integration

Profile `gq5012bf1-mt6878-dev15:codex-d42b118` is wired to the owner's committed in-tree contract. A real contract-only smoke fixture passed. The latest FPSGO/C2PS kernel compilation, strict modpost and runtime closure remain **NOT RUN / HOLD**.

First recheck capacity, filesystem health and projected write cost. Last metadata headroom was 5.86 GiB, below the 6 GiB clean-build restart gate. Do not launch a full clean profile build or weaken the gate. If a safe verified incremental tree handoff is arranged, preserve current artifacts and let the engine prove eligibility; do not bypass it. Keep NONLINEAR_FREQ_CTL and the platform scheduler interfaces enabled as required by the owner contract.

### Device owner / offline boot evidence

Supply authenticated authorized vendor_boot loader metadata and boot/vendor_boot/init_boot artifacts, bootconfig, and permitted DT/AVB/rollback policy evidence. Do not probe protected locations. No bootloader unlock, flashing, device connection, signing or key generation is authorized by this report.

All seven early-boot groups remain link-level-only. Unplaced modules are intentionally not autoloaded. Stock ELFs are not binary-compatible fallbacks for this target.

## Evidence locations

- Research snapshot: `DOCS/kernel-workspaces/phase10/evidence/`.
- Full engine bundle: `/home/armol/kernel-work/lieppos-kernel-p7/bundles/gq5012bf1-mt6878-dev17-candidate-owner-fixes-in-tree/`.
- Machine-readable owner handoff: engine `runs/dev17-owner-handoff.json`, also copied into the research snapshot.
- Codex contract smoke: engine `runs/codex-d42b118-contract-smoke.json` (not a kernel compile).
- Frozen dev15 reference summary and dev15→dev16 delta are copied separately so the historical 754-module proof remains identifiable.

No push. No removal of owner source/evidence or unrelated research files. Never revert the corrected WL2864C success return. Never use stock `.o` as source inputs.
