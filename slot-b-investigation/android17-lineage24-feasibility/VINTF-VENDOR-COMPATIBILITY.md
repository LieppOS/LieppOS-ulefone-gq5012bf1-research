# VINTF and vendor compatibility

## Captured Ulefone contract

**PROVEN from stock vendor:**

```text
vendor manifest target-level = 8          (Android U / Android 14 FCM)
vendor manifest sepolicy     = 34.0
vendor compatibility NDK     = 34
ro.product.first_api_level   = 35
runtime vendor/kernel        = Android 14-generation 6.1 stack
```

The product shipped on Android 15 while retaining an Android-U vendor contract.

## Android 17 compatibility retained

Lineage 24 source contains framework matrices `7`, `8`, `202404`, `202504`,
`202604` and `202704`. Its `compatibility_matrix.8.xml` is byte-identical to the
one in the Lineage 22.2 checkout. The GSI product carries VNDK snapshots
`31 32 33 34` and compatibility packages for old shipping API levels.

Android 17 sepolicy configuration explicitly supports:

```text
31.0 32.0 33.0 34.0 202404 202504
```

Both `system/sepolicy/prebuilts/api/34.0` and
`system/sepolicy/private/compat/34.0` exist. Therefore the vendor's policy and
NDK levels are intentionally grandfathered rather than accidentally accepted.

## Interface and ABI analysis

| Area | Result |
|---|---|
| VINTF FCM | level 8 remains selectable and its frozen matrix remains present |
| deprecated HIDL | GSI intentionally includes old allocator/memory and related compatibility services |
| AIDL stability | standard stable HAL contracts remain; proprietary `vendor.mediatek.*` AIDL still depends on Ulefone framework-side clients |
| binder | current 6.1 binder/binderfs config satisfies retained requirements |
| VNDK/vendor ABI | VNDK 34 snapshot is configured; vendor-private ABI is still runtime-sensitive |
| shipping API handling | device remains shipping API 35; do not rewrite it to 37 in the device tree |
| sepolicy | 34.0 mapping is present; new framework domains still require device policy integration |
| init/property namespaces | Android 17 is stricter; stock vendor properties must be declared through correct vendor contexts, not global hacks |
| kernel FCM | U/6.1 frozen requirements remain and exact config comparison passes |

## Explicit answer

**Can Android 17 theoretically boot with the current Ulefone kernel/vendor
without replacing either first?**

**LIKELY YES for an initial userspace boot, not proven.** This is based on four
independent facts: current A already boots Android 16 with this vendor; FCM 8 is
retained unchanged; VNDK/sepolicy 34 compatibility is explicit; exact U/6.1
kernel requirements pass. It is not a promise that radio, IMS, camera, graphics
or vendor extension clients work.

### Classification

- **PROVEN:** numeric contracts and retained compatibility data above.
- **LIKELY:** init, vold, servicemanager and standard HAL discovery can reach
  framework boot.
- **UNCERTAIN:** proprietary MediaTek extensions, framework classpath clients,
  graphics buffer ABI and every hardware service's behavior.
- **KNOWN BLOCKER:** direct shared-userdata boot is unsafe independently of
  VINTF; the official GSI layout also does not match B extents.
- **TEST TO CONFIRM:** host `checkvintf` on final target-files, then isolated
  hardware boot and exact missing-HAL/SELinux/service evidence.

`CURRENT_VENDOR_INITIAL_BOOT_PLAUSIBLE=1` is an engineering feasibility flag,
not a compatibility certification.
