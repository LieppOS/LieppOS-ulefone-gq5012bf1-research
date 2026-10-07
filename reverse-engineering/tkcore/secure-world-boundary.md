# TKCore secure-world boundary

TKCORE-DRV DONE covers the **normal-world kernel transport** only. The following cannot be
source-closed from the kernel side and are explicitly out of scope; none of them changes a
byte of `tkcore_drv.ko`.

| opaque item | where it lives | what the normal world knows |
|---|---|---|
| TrustKernel secure OS ("TrustKernel TEE-OS", TKCore, api levels 2.4.0/2.7.0 strings) | `tee.img` → `tee` sub-image (697 344 B, signed `cert1`/`cert2`), FF-A SP id 0x8001, S-EL1, 8 execution contexts | UUID, SP id, manifest, the SMC/FF-A function ids and return codes in `smc-map.tsv` |
| SPMC / EL3 firmware | `tee.img` → `atf` (TF-A BL31 with EL3 SPMC) | that it routes FF-A direct requests to the SP |
| Trusted Applications | `/vendor/app/t6/*.ta` (10 TAs) + `/data/vendor/t6/app` (service-provider TAs) | UUID file names; load requests arrive as supplicant RPCs |
| secure algorithms (keymaster/keymint, gatekeeper, DRM, fingerprint/face matching) | TAs | only the GP command transport |
| secure storage semantics (SFS format, RPMB layout, anti-rollback) | TKCore + teed | file paths and that RPMB frames are forwarded opaquely |
| cryptographic keys, RPMB auth key, device secrets, keybox | secure world / `/mnt/vendor/persist/keybox` (encrypted) | nothing |
| signed secure payloads / signer identities (`trustkernel/tos/sysmod_signer`, `caAzR`) | `tee.img`, TAs | signer name strings only |
| secure log ring format | written by TKCore, drained by tkcore.ko | placement (128 KiB, PA via 0xf2005705) |
| scheduler policy producing `BIND_CPU`/`EAFFINITY`/`ETHREAD_LIMIT` | TKCore | the normal-world reaction (proven) |
| meaning of OS revision triple | TKCore | printed form `tkcoreos-rev: %d.%d.%d-gp` |

Also outside TKCORE-DRV (normal world but separate components): `tkcore.ko` (TRUSTKERNEL-TEE /
TRUSTKERNEL-ABI-ISLAND, BLOCKED), `ffa_v10.ko` (FFA-V10, DONE), teed/libteec (userspace),
UFS RPMB driver (STORAGE).
