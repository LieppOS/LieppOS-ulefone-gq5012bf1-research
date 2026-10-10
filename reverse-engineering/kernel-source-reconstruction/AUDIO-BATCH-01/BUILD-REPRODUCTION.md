# AUDIO-BATCH-01 build reproduction

Maintained repository: `../android_kernel_modules_audio_ulefone_gq5012bf1` @ `ec57573ca9f48c92b8485137064840025525f23f`
Recoverable bundle: `/home/armol/kernel-work/codex-audio-batch-01/bundle/audio-ec57573c….bundle`
(sha256 in `evidence/cleancheck/bundle.sha256`).

## Immutable inputs

| Input | Location (offline mirror) | Verification |
|---|---|---|
| kernel/common `6b18f0b5` | `/home/armol/kernel-work/interconnect-pin-mirror/common.git` | git tree `710eb859` |
| clang r487747c `7775eb11` | same mirror, `clang-r487747c.tar` | tree id `8eb8e3af`, version string |
| KDM `957dac18` (Kconfig) / ALPS `5e415e05` (C) | same mirror, `kdm.git` / `alps5e41.git` | trees `05f9c65d` / `9c61acc3` |
| GKI 12901745 `vmlinux.symvers` | same mirror (or `reference/*.xz`) | sha256 in `reference/` |
| Awinic aw883xx `4f52a107` | `/home/armol/kernel-work/codex-audio-batch-01/mirror/aw883xx.git` (bare clone of the public repo) | tree `eb07f433` |

Shared mirrors are read only. The Awinic mirror was cloned from the existing local checkout of
`github.com/awinic-driver/aw883xx` without changing it.

## Commands

```sh
export TMPDIR=/tmp LIEPPOS_IOMMU_MIRROR=/home/armol/kernel-work/interconnect-pin-mirror \
       LIEPPOS_AUDIO_MIRROR=/home/armol/kernel-work/codex-audio-batch-01/mirror
R=../android_kernel_modules_audio_ulefone_gq5012bf1
bash $R/scripts/bootstrap.sh /space-free/ws          # fetch+verify every pin
bash $R/scripts/make-kout.sh /space-free/ws          # .config sha256 b826d842…
bash $R/scripts/bulk-build.sh /space-free/ws B1      # assemble (tree 0bc655ac…), witnesses, 21 targets
bash $R/scripts/accept.sh /space-free/ws/out/B1 <dir with the 21 stock .ko>
```

Independent check (as run): `scripts/cleancheck.sh <bundle> <commit> <base> <stock>` was run
inside `bwrap --dev-bind / / --tmpfs <dev repo> --tmpfs <dev workspace>`. Both development paths
were empty inside the namespace, and nothing was renamed or modified (`evidence/cleancheck/run-cleancheck.sh`, `run.log`).
The check builds two fresh workspaces, B1 and B2, compares them, and accepts both against stock. It took 2 min 32 s on 64 cores.

## Recipe-owned deltas over pristine inputs

- `reference/gq5012bf1-audio.config`: RT5512, HL5280 and SCP debug off. These are the only ODM Kconfig differences, recovered from the historical kout.
- Patches 0002–0006 (source): see `BATCH-SUMMARY.md`.
- Patch 0009: Kbuild `obj-*` routing only. Provider units compile for witnesses and are removed before modpost.
- `kb.sh`: `-fdebug-prefix-map=<ws>/=/lieppos-audio-ws/` rewrites DWARF paths only. Stripped
  acceptance is unaffected, and independent workspaces become byte-identical.

## Normalization

The only normalization is zeroing the 20-byte GNU build-ID descriptor. `srcversion`, `vermagic`,
CRCs and every other byte are compared raw. `batch-full.Module.symvers` is compared with kbuild's
absolute module-path column normalised, because that column is not part of any shipped artifact.
