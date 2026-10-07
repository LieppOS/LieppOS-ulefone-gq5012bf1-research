#!/bin/bash
# Stamped GKI 12901745 build reproducing the stock system_dlkm modules.
#   * BUILD_NUMBER=12901745 + --config=stamp  -> release 6.1.115-android14-11-g6b18f0b574ab-ab12901745,
#     scmversion g6b18f0b574ab (common @ 6b18f0b574ab, clean tree)
#   * -faddrsig in KCFLAGS: Android's own clang enables it by default, but this host (Gentoo) build
#     environment's clang default drops it; the stock modules carry .llvm_addrsig.
#     Injected via common/build.config.common, hidden from setlocalversion's dirty check with
#     `git update-index --assume-unchanged` so the release string stays clean.
set -euo pipefail
G=${G:-/home/armol/kernel-work/gki-12901745-workspace}
cd "$G/common"
[ "$(git rev-parse --short=12 HEAD)" = 6b18f0b574ab ]
grep -q -- '-D__ANDROID_COMMON_KERNEL__ -faddrsig"' build.config.common || {
  sed -i 's|^KCFLAGS="${KCFLAGS} -D__ANDROID_COMMON_KERNEL__"$|KCFLAGS="${KCFLAGS} -D__ANDROID_COMMON_KERNEL__ -faddrsig"|' build.config.common
  git update-index --assume-unchanged build.config.common; }
[ -z "$(git --no-optional-locks status -uno --porcelain)" ]
cd "$G" && BUILD_NUMBER=12901745 tools/bazel build --config=stamp //common:kernel_aarch64
