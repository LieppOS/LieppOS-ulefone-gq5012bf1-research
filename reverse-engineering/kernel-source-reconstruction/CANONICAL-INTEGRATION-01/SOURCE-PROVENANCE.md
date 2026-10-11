# Source provenance

`SOURCE-REPOSITORIES.tsv` lists all 35 source locations referenced by the 344 A/B/C rows. Every
referenced `source_commit` exists in its repository (validator `SOURCE_COMMIT_NOT_IN_REPOSITORY`
also checks A/B). All are clean except an untracked pycache in smi_platform.

| Source location | HEAD | Rows (classes) | Missing referenced commits | Referenced commits off HEAD history |
|---|---|---|---|---|
| `.` | fc31148e055d | 4 (C:4) | NONE | NONE |
| `../android_kernel_modules_apusys_ulefone_gq5012bf1` | 924f66b779a6 | 2 (A:2) | NONE | NONE |
| `../android_kernel_modules_audio_shared_infrastructure_ulefone_gq5012bf1` | 4697eac32544 | 12 (A:12) | NONE | NONE |
| `../android_kernel_modules_audio_ulefone_gq5012bf1` | ec57573ca9f4 | 21 (A:20;C:1) | NONE | NONE |
| `../android_kernel_modules_boot_clock_ulefone_gq5012bf1` | e99d919709d7 | 6 (A:6) | NONE | NONE |
| `../android_kernel_modules_camera_isp_ulefone_gq5012bf1` | 96d223a3139a | 19 (A:18;B:1) | NONE | NONE |
| `../android_kernel_modules_charging_battery_ulefone_gq5012bf1` | 44ce4ff57556 | 14 (A:12;C:2) | NONE | b2a343a9d8664b77a63dc168 |
| `../android_kernel_modules_cmdq_ulefone_gq5012bf1` | 0b4b07f38397 | 5 (A:5) | NONE | NONE |
| `../android_kernel_modules_connectivity_ulefone_gq5012bf1` | 40bf42967a21 | 17 (A:17) | NONE | NONE |
| `../android_kernel_modules_gpu_ai_aux_ulefone_gq5012bf1` | aa21b33ee469 | 3 (A:3) | NONE | NONE |
| `../android_kernel_modules_gpu_ulefone_gq5012bf1` | 9d05ae8e22e6 | 8 (A:8) | NONE | NONE |
| `../android_kernel_modules_interconnect_emi_ulefone_gq5012bf1` | e03fc92f55b2 | 3 (A:3) | NONE | NONE |
| `../android_kernel_modules_iommu_aux_ulefone_gq5012bf1` | 07bacdb2ff76 | 3 (A:3) | NONE | NONE |
| `../android_kernel_modules_iommu_ulefone_gq5012bf1` | 110251e6d098 | 1 (A:1) | NONE | NONE |
| `../android_kernel_modules_mailbox_tinysys_ulefone_gq5012bf1` | e4d3683f3a35 | 7 (A:7) | NONE | NONE |
| `../android_kernel_modules_mdp_ulefone_gq5012bf1` | 060689bfb95e | 4 (A:4) | NONE | NONE |
| `../android_kernel_modules_memory_platform_ulefone_gq5012bf1` | 78cd676ac42a | 7 (A:7) | NONE | NONE |
| `../android_kernel_modules_met_instrumentation_ulefone_gq5012bf1` | 7839af7c1d40 | 10 (A:10) | NONE | NONE |
| `../android_kernel_modules_modem_audio_transport_ulefone_gq5012bf1` | 5a7980681a71 | 9 (A:9) | NONE | NONE |
| `../android_kernel_modules_pinctrl_ulefone_gq5012bf1` | 0c128caa3b6d | 4 (A:4) | NONE | NONE |
| `../android_kernel_modules_platform_diagnostics_ulefone_gq5012bf1` | 694b9db8c0a6 | 12 (A:12) | NONE | NONE |
| `../android_kernel_modules_pmif_spmi_ulefone_gq5012bf1` | 100c01a5b262 | 9 (A:9) | NONE | NONE |
| `../android_kernel_modules_power_platform_ulefone_gq5012bf1` | cd7f2fba32e0 | 25 (A:25) | NONE | NONE |
| `../android_kernel_modules_power_policy_ulefone_gq5012bf1` | de4756ceb05c | 23 (A:23) | NONE | NONE |
| `../android_kernel_modules_regulators_ulefone_gq5012bf1` | 33130d53c944 | 4 (A:4) | NONE | NONE |
| `../android_kernel_modules_scp_sensorhub_ulefone_gq5012bf1` | 26507aa653a0 | 3 (A:3) | NONE | NONE |
| `../android_kernel_modules_secure_diagnostics_ulefone_gq5012bf1` | ab3bd0f55af4 | 6 (A:6) | NONE | NONE |
| `../android_kernel_modules_slbc_ulefone_gq5012bf1` | 9e1c978ae4e6 | 1 (A:1) | NONE | NONE |
| `../android_kernel_modules_smi_platform_ulefone_gq5012bf1` | 7b8020b51c6b | 2 (A:2) | NONE | NONE |
| `../android_kernel_modules_storage_ulefone_gq5012bf1` | e9b29f3086e5 | 10 (A:10) | NONE | NONE |
| `../android_kernel_modules_thermal_cooling_ulefone_gq5012bf1` | ff6e97b3bf1f | 9 (A:9) | NONE | NONE |
| `../android_kernel_modules_usb_platform_ulefone_gq5012bf1` | b80b5b115548 | 10 (A:10) | NONE | NONE |
| `../android_kernel_modules_usb_typec_ulefone_gq5012bf1` | d41a2436c15f | 6 (A:3;C:3) | NONE | 758f9edc78c7a50d07b86291 |
| `../android_kernel_modules_vcodec_ulefone_gq5012bf1` | 682b3e957923 | 5 (A:5) | NONE | NONE |
| `../kernel-research/android-common-gq5012bf1` | 6b18f0b574ab | 60 (A:60) | NONE | NONE |

The two "off HEAD" entries are the USB-TYPEC-CLOSURE C rows: their commits live on the
`codex/usb-typec-closure` branch of the maintained charging/typec repositories (b2a343a9, 758f9edc),
exactly as that package recorded. Masters keep the 25 Batch04 A tips.

## Fast-forwarded maintained repositories (only source mutation)

| Family | Before | After | Bundle | verify exit | Tree == -allc clone |
|---|---|---|---|---:|---|
| cmdq | eb0a4760a5836794203b18b57b4c55bb51a5f7a6 | 0b4b07f38397ca6c0630b9edc5ccf2df9251da1d | cmdq-allc.bundle | 0 | yes |
| connectivity | d0b9e10fbb3bb4810de79fda190a4216cec65b00 | 40bf42967a213af6faa45a6a579571973b8e5d15 | connectivity-allc.bundle | 0 | yes |
| thermal_cooling | 75f8c710dcb605a47e657b20b2782bd9c4dc0b3c | ff6e97b3bf1f29c1e1fba4ba0c0e28493cbd0698 | thermal-allc.bundle | 0 | yes |
| audio_shared_infrastructure | 425ffd724462639899a71d3aa57da85b290037fe | 4697eac32544fbfaeab76f6d7a5367a8d8d32460 | drm-allc.bundle | 0 | yes |

Each new tip descends directly from the old one (2/2/2/1 commits), all repos were clean and idle,
`git fsck --connectivity-only` passes. Old tips remain in history, so every row still referencing
them (e.g. the CMDQ A row at eb0a4760 whose proof inputs did not change) stays valid. The
`-allc` clones and bundles are retained as independent recovery copies.

Codex source tips verified unchanged: audio ec57573c, scp_sensorhub 26507aa6, slbc 9e1c978a,
modem_audio_transport 5a798068, platform_diagnostics 694b9db8, met_instrumentation 7839af7c.
Bundles: 48/48 preserved research bundles verify (`evidence/bundle-verification.tsv`).
