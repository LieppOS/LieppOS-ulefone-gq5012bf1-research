# TrustKernel Phase 3G — known-good Slot-A runtime baseline

Capture type: **read-only**, except for the separately authorized rollback-control `set-active=a` test documented in the rollback report. No module ioctl, partition write, secret operation or live module operation occurred.

Evidence root:

`workspace/phase4-tkcore-island/phase3g/device-before/`

## Boot and slot identity

- device: `5012BF3010001335`, GQ5012BF1 / Armor 29 Pro;
- active slot: A (`ro.boot.slot_suffix=_a`, root `bootctl=0`, Fastboot `current-slot:a`);
- A: bootable and successful;
- B: bootable and not successful;
- bootloader Fastboot: unlocked=yes, secure=no;
- kernel: `Linux localhost 6.1.115-android14-11-g6b18f0b574ab-ab12901745 #1 SMP PREEMPT ... aarch64`;
- SELinux: Enforcing;
- `sys.boot_completed=1`.

## Stock module state

`/proc/modules` contained all required modules:

- `ffa_v10` (users: `gz_main_mod,tmem_ffa,tkcore_drv`)
- `teeperf`
- `tkcore` (users: `tmem_ffa,microarray_fp_tee,tkcore_drv`)
- `tkcore_drv`
- `gz_tz_system`
- `tmem_ffa`
- `fingerprint`
- `microarray_fp_tee`
- `spi_mt65xx`

Loaded stock Build IDs exposed through `/sys/module/*/notes/.note.gnu.build-id`:

| Module | Stock loaded Build ID |
|---|---|
| `tkcore` | `6b6663820488959123f26a85dded547e305c56d6` |
| `tkcore_drv` | `8e73e9f92105915fe497b6c4cfbfffaf7b3fb2d9` |
| `tmem_ffa` | `8b25fc266c347dfd30da218cd041696a5e0471f7` |

These are distinct from the frozen Phase-3G source Build IDs and therefore provide a direct later loaded-identity discriminator even where the vendor-ramdisk module files are no longer mounted after first-stage init.

The mounted stock vendor_dlkm hashes included:

- `gz_tz_system.ko`: `4b29f9b401c43fe98373d17c0360340c0c58f2cc15e2dfbfd536a60bb9484e38`
- `tmem_ffa.ko`: `707e26674abbe7f9c695bb949d74fd5de04972d4bbb991cddc3a2ea9ab45f01b`

## Device/proc baseline

```text
crw------- 1 system system u:object_r:tkcore_admin_device:s0  /dev/tkcore_admin
crw-rw---- 1 root   system u:object_r:tkcore_client_device:s0 /dev/tkcore_client
crw-rw---- 1 root   system u:object_r:tkcore_client_device:s0 /dev/tkcore_fp
dr-xr-xr-x root root u:object_r:proc_tkcore:s0 /proc/tkcore
```

Shell access inside `/proc/tkcore` is denied by stock policy; existence, directory label and mode are the comparison baseline.

## TrustKernel and Android security baseline

Properties:

- `init.svc.teed=running`
- `vendor.trustkernel.fs.state=ready`
- `vendor.trustkernel.ready=true`
- `init.svc.keystore2=running`
- `init.svc.gatekeeperd=running`
- `init.svc.drm=running`
- `init.svc.mediadrm=running`

Processes:

- `teed --tzdev /dev/tkcore_admin ...`
- `android.hardware.security.keymint@3.0-service.trustkernel`
- `android.hardware.gatekeeper-service.trustkernel`
- `keystore2`
- `android.hardware.drm-service.widevine`

Binder services present:

- `android.hardware.security.keymint.IKeyMintDevice/default`
- `android.hardware.gatekeeper.IGatekeeper/default`
- `android.system.keystore2.IKeystoreService/default`
- `android.hardware.drm.IDrmFactory/widevine`

Keystore2 logged KeyMint version 300 for `TRUSTED_ENVIRONMENT`, successful shared-secret negotiation, and successful Keystore 2.0 registration.

## FBE/data baseline

- `ro.crypto.state=encrypted`
- `ro.crypto.type=file`
- `/data` mounted read-write F2FS with `inlinecrypt`
- framework boot complete

## Log/error baseline

Root dmesg and all logcat buffers were frozen after a clean A reboot. No `Unknown symbol`, module version disagreement, kernel WARN/OOPS, or TrustKernel-related AVC was found. SELinux AVC count in the captured log was 0.

Nine TrustKernel log entries report `KeyPH:load_data_from_persistent_object2 ... Failed to open PersistentObject` during the known-good stock-A boot. They are therefore **pre-existing stock baseline**, not automatically attributable to a later source-island boot. No continuous RPC/TEE failure loop was observed.

The stock image emits little module-init text into the retained dmesg window; runtime comparison must therefore use loaded module identity, nodes, service state, errors and TrustKernel properties in addition to log-line equality.
