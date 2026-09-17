# Slot-B Conscrypt/APEX BoringSSL static equivalence v2

## Context

Exact Android init event-queue analysis established that historical USB/ADB
progress does not, by itself, exclude the Conscrypt/APEX BoringSSL self-test.

The vendor BoringSSL test runs synchronously during `early-init`.

The platform/system BoringSSL test runs synchronously during `init`.

Those earlier stages are strongly excluded by later Android boot progress.

The remaining BoringSSL branch is the Conscrypt/APEX self-test triggered by:

`apexd.status=ready`

## Current-B Conscrypt package

Path:

`/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/slot-b-investigation/untouched-b-early-boot-forensics/b-mounts/system/system/apex/com.android.conscrypt.capex`

Package type:

`CAPEX`

Package SHA256:

`b0c430d432bf9e13fef15f333501b74fd5a2700cf228cbb2862d159632c21e4a`

Normalized original APEX SHA256:

`d4eb6fdf5559439d9e2d273d6cea717ac6df36d83804b546a1f46d652bcf6866`

APEX public-key SHA256:

`0a3360aed11e40d5577de3a2d08664a9fc2d0e9378d0efe08879ff2adf517a68`

Payload extraction method:

`debugfs`

## 64-bit equivalence

B Conscrypt self-test SHA256:

`1945ec6d1001495bffc11dae26adb3db8462fcfac3c146697f5cc21676c93cc4`

B Conscrypt libcrypto SHA256:

`55cac6cb4581a9533ad56a66579804fb44a7fb7d1afb8f9ae63e36ff248679f3`

B system self-test SHA256:

`1945ec6d1001495bffc11dae26adb3db8462fcfac3c146697f5cc21676c93cc4`

B system libcrypto SHA256:

`660fa9a8e01922171c300d60aa862d3cea8b1752c4b73ae0c459d2b9d73f15f7`

Working-A active Conscrypt self-test SHA256:

`2067633d07d888bb5368580b168e37221f0289c3a4a66f6cc177a2719a81f438`

Working-A active Conscrypt libcrypto SHA256:

`7afa79cb1ec59abc67de1852aa2e5dbc6ee093b143f7bcb12f40c3cd79874b71`

Exact B-APEX vs B-system 64-bit pair:

`0`

Exact B-APEX vs working-A-active 64-bit pair:

`0`

Definite local bitness failures:

`0`

Direct preserved historical failure hit:

`0`

## Verdict

APEX_BORINGSSL_REMAINS_NARROW_CANDIDATE: the current-B Conscrypt 64-bit executable/libcrypto pair is not proven byte-equivalent to either the earlier B system pair or the working-A active pair. This does not prove failure, but it remains a runtime-capable candidate.

## Safety

The phone remained booted on working Slot A.

Slot B was not booted.

No B executable was run.

No file was copied onto the phone.

No partition, slot metadata, APEX state, `/data`, `/metadata`, or persistent
Android state was modified.

The only writes were host-side research evidence files in this repository.
