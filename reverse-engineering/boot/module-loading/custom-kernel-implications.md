# Custom-kernel implications (analysis only, no redesign)

- **Loadable as-is**: all 411 vendor `.ko` (vendor_boot 196 + vendor_dlkm 215) are built for
  KMI `android14-6.1` with modversions; they load on any kernel whose exported symbol CRCs
  match and whose vermagic flags are `SMP preempt mod_unload modversions aarch64` (the
  release token is not compared). system_dlkm (60) are GKI-signed and must match the GKI
  build exactly (same `scmversion`), or be rebuilt and re-signed / replaced together.
- **KMI requirements**: unsigned vendor modules may not export GKI-protected symbols
  (kernel prints `Protected symbol`); a custom kernel that changes any KMI struct/CRC breaks
  every vendor module depending on it (FATAL if it is a first-stage module).
- **Built-in replacement**: when a driver becomes built-in, its `.ko` must be removed from
  the list *and* from `modules.dep`, and every `modules.dep` line naming it as a dependency
  must be regenerated (depmod), otherwise first-stage `InsmodWithDeps` fails on the missing
  file (FATAL) or second-stage modprobe logs and skips dependents. `modules.load.recovery`
  must be edited in step.
- **vendor.all.modules.ready** does not care about filenames — only that `init.insmod.sh`
  reaches its `setprop` line. Removing modules from the DLKM lists never blocks boot; a
  hanging module init does.
- **Moving modules between vendor_boot and vendor_dlkm**:
  - vendor_dlkm → vendor_boot: becomes strict/FATAL on failure; must appear in the ramdisk
    `modules.dep`; loads before SELinux and before `/vendor` exists (no firmware from
    `/vendor/firmware` at probe time unless deferred).
  - vendor_boot → vendor_dlkm: unavailable before first_stage_mount and in recovery;
    anything needed to mount storage (UFS, blocktag, rpmb), show the recovery UI, or provide
    first-stage console must stay in vendor_boot. The 13 duplicates show the recovery cost.
  - the post-fs-data barrier only covers vendor_dlkm/system_dlkm; modules moved to
    rc/property-triggered loading are not covered.
