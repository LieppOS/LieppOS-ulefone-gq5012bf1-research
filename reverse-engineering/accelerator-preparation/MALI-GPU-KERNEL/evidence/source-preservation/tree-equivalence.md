# Old local source repositories vs. public pins (2026-10-08)

Inspected `/home/armol/kernel-work/accelerator-mali-gpu-kernel/build/{kdm,gpu}`:

* Both were local git repositories with **no remote**, made by `git archive` + `git init`.
* `git status` was clean in both: no uncommitted or untracked edits.
* `build/kdm` had 7853 tracked files (6678 `.c`/`.h`, 606 Kbuild/Makefile).
* `build/gpu` had 510 tracked files (440 `.c`/`.h`, 41 Kbuild/Makefile).

The GKI `common` checkout carries one `assume-unchanged` file, `build.config.common`, from
earlier SYSTEM-DLKM work. `make` does not read it, and the new build uses its own fresh
`common` checkout.

| repo | commits | final tree |
|---|---|---|
| build/gpu | c8d458b pristine 5f75a3b subset → a26b975 = 580d08e subset → ec7e11b graft of 4 files from c3d070e | `9bd1368f96a922ab2b08a8d98dc582633b0180dd` |
| build/kdm | 3abe8be "pristine" 957dac → 4623436 Kbuild restrict → 6f0cb00 no gpueb/gpu_iommu → 2e0f942 ged+gpufreq from 5e41 | `b9d2d99ea1e90242d628b63422ee9997800ca36e` |

Reproduction from the public commits:

* **gpu:** the archive of `580d08eac018` (`gpu/{Kbuild,Makefile,mt6878,gpu_mali/Makefile,gpu_mali/mali_avalon/mali-r44p1}`)
  plus the 4 files from `c3d070e6155c` gives `9bd1368f…`, which **is the build/gpu tree**.
* **kdm:** the archive of `957dac185efe` plus kdm/0001–0002, with `ged/` and `gpufreq/` replaced
  from `5e415e059253`, gives `b9d2d99e…` (**= build/kdm**) when committed with `git add -A`.
  * The true pristine 957dac tree is `05f9c65d…`. `build/kdm`'s "pristine" commit was missing
    two files that the tree's own `.gitignore` (`*.i`) hid from `git add -A`:
    `drivers/input/touchscreen/FT3519/include/firmware/fw_sample.i` and
    `.../pramboot/FT5452J_Pramboot_V4.1_20210427.i`.
  * The maintained repo uses the complete tree (`git add -A -f`); its final tree is
    `39d806ce…`. No GPU object reads those files, and the output is stock-identical.
* **The local "pristine archive" of ALPS 5e41** (`lieppos/tinysys/trees/5e41` @ `2ae742fda9cd`,
  used for the earlier provider-CRC derivation) is *not* pristine: tree `ad891b7b…` vs public
  `9c61acc3…`.
  * It lacks 110 `Kbuild` files, has a different `.gitignore`, and has an extra `build.log`.
    No `.c`/`.h` file differs, which is why the earlier derivation borrowed 957dac's top
    `Kbuild`.
  * The maintained derivation builds the true public 5e41 tree. Its 30 CRCs are identical to
    the earlier ones and to stock.
  * Shared tinysys tree; not modified.
* **The `c3d070e9f373` hash written in the closure documents does not exist.** It was a
  wrong 12-character extension of `c3d070e`. The real commit is
  `c3d070e6155c9f373224fa2b17027d07583c37bc`, "[SCM][MT6878][Upgrade]
  alps-mp-u0.mp1.rc-V11.24", 2025-12-30, on mt6878/Galaga/16b and mt6878/Tetris/16b.
* **Hidden input of the old build:** `kout-base/Module.symvers`, copied from a camera-isp
  kout, is the GKI 12901745 `vmlinux.symvers` (sha256 `61933b61…`). The maintained bootstrap
  downloads the official CI artifact and verifies that hash; the repository also keeps a
  compressed fallback copy.
* **Hidden host workaround of the old build:** the old kout reused a `resolve_btfids` binary
  from another kout, because host libbpf fails `-Werror` under glibc 2.43. The maintained
  `make-kout.sh` builds it from source with
  `HOSTCFLAGS=-Wno-error=incompatible-pointer-types-discards-qualifiers`. Module output is
  unaffected.

**Old work directory hidden during the test:** `build/` was renamed to
`build.HIDDEN-during-clean-test` for the whole clean-checkout bootstrap and B1/B2 run, then
restored. The maintained scripts contain no reference to `/home/armol` or
`accelerator-mali-gpu-kernel`.
