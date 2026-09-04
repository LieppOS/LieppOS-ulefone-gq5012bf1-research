# Exact GQ5012BF1 GKI build inputs

Android CI build: `12901745`

Target: `kernel_aarch64`

Branch: `aosp_kernel-common-android14-6.1-2024-12`

Key source revisions from BUILD_INFO:

| Repository | Revision |
|---|---|
| kernel/common | `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09` |
| kernel/build | `c0156661aa24e62647ea34d21fbd13d2b93dd89c` |
| kernel/configs | `76dd129942d2d1a1ccaa3ea0effa682e9e1828ac` |
| kernel/manifest | `c6de413eac1ce136d34190e99a34101c036fd3ad` |
| kernel/prebuilts/build-tools | `e905be252a53d20c52bd9e59df3ff8fdd46b9eab` |
| clang prebuilts | `7775eb113f960bc69a780b621d03a715914d4bca` |

The official CI build command used Kleaf/Bazel with `--config=android_ci` and
produced the GKI artifacts including Image, vmlinux, System.map,
vmlinux.symvers, boot images, modules and ABI reports.

This manifest/build metadata is the preferred reproducibility reference if an
exact recreation of GKI build 12901745 is required.
