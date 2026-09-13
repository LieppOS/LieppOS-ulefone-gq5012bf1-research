# gz_main_mod — Android init / SELinux / userspace consumer contract

All evidence below comes from **already-committed stock partition extracts**.
No device operation was performed, no node was opened, and no service was
queried on hardware.

Generic "trusty" strings were explicitly **not** treated as evidence: only
references to the two device paths this module actually creates
(`/dev/gz_kree`, `/dev/gz_ffa_dev`) or to the SELinux type bound to them
count.

---

## 1. PROVEN — init

`vendor/etc/init/hw/init.mt6878.rc`:

```
562:    # gz device
563:    chmod 0660 /dev/gz_kree
564:    chown system system /dev/gz_kree
565:
566:    # gz ffa device
567:    chmod 0660 /dev/gz_ffa_dev
568:    chown system system /dev/gz_ffa_dev
```

| node | mode | owner | group |
|---|---|---|---|
| `/dev/gz_kree` | 0660 | `system` | `system` |
| `/dev/gz_ffa_dev` | 0660 | `system` | `system` |

Both are group-`system` read/write, world-inaccessible. There is no
property gate and no `service`/`on` trigger tied to either node beyond this
permission block.

## 2. PROVEN — SELinux

`vendor/etc/selinux/vendor_file_contexts:582`:

```
/dev/gz_kree(/.*)?        u:object_r:gz_device:s0
```

`vendor/etc/selinux/vendor_sepolicy.cil`:

```
1626: (type gz_device)
1627: (roletype object_r gz_device)
 782: (typeattributeset dev_type ( … gz_device gzvm_device … ))
```

Allow rules naming `gz_device` — these are the **complete** set in the shipped
vendor policy:

```
8672:  (allow mtk_hal_camera gz_device
          (chr_file (ioctl read write getattr lock append map open watch watch_reads)))
11794: (allow vpud_native   gz_device
          (chr_file (ioctl read write getattr lock append map open watch watch_reads)))
```

| domain | access | meaning |
|---|---|---|
| `mtk_hal_camera` | chr_file ioctl/read/write/open/… | the camera HAL is an authorised KREE client — consistent with the secure-camera paths that already depend on `gz_tz_system` |
| `vpud_native` | chr_file ioctl/read/write/open/… | the video/VPU daemon is an authorised KREE client |

`gz_device` is also present in the binary `precompiled_sepolicy`, confirming
the type is live in the enforced policy and not a stale CIL fragment.

**`/dev/gz_ffa_dev` has no `file_contexts` entry.** It therefore receives the
default `device` label rather than `gz_device`, and no shipped allow rule
grants any domain access to it under that label. Combined with the missing
`.compat_ioctl`, the FF-A node is effectively not reachable by normal vendor
domains in the stock configuration — it behaves as a
development/bring-up surface.

## 3. PROVEN — native library consumers

A content scan of `vendor/bin`, `vendor/lib64`, `vendor/lib` and `system`
found exactly two binaries referencing the `gz_kree` device name:

| path | role |
|---|---|
| `vendor/lib64/libgz_uree.so` | the GenieZone **UREE** userspace client library — the canonical userspace half of this module's KREE ABI |
| `vendor/lib64/liboemcrypto.so` | OEMCrypto; references the same device name |

`libgz_uree.so` is the library that turns the ioctl surface documented in
`kernel/phase4-gz-main-mod-ioctl-contract.md` into the vendor-facing UREE API.
Its presence confirms that the ioctl ABI, not a symbol ABI, is the real
compatibility contract for this module.

`liboemcrypto.so` is recorded **only** as a static string reference. No DRM,
Widevine, key or provisioning analysis was performed, and none is in scope.

## 4. LIKELY

| item | reasoning |
|---|---|
| the camera HAL and `vpud_native` reach `/dev/gz_kree` through `libgz_uree.so` rather than issuing raw ioctls | both are granted `gz_device` access and `libgz_uree.so` is the only general-purpose client library present |
| `system`-group ownership implies the clients run as, or drop to, group `system` | required by the 0660 mode, but not separately proven per-process |

## 5. UNKNOWN / not investigated

| item | why |
|---|---|
| which TA UUIDs each userspace client opens | requires secure-world / TA analysis, explicitly out of scope |
| runtime call sequences issued by the HALs | would require live device operation, forbidden by this task |
| VINTF/HIDL/AIDL manifest entries | none reference these device nodes; the ABI is a raw chardev, not a HAL interface |
| any KeyMint, Gatekeeper, RPMB or Widevine behaviour | out of scope and not analysed |

## 6. Replacement-safety conclusion

The userspace contract that must be preserved is:

1. a misc device named **`gz_kree`** (so `/dev/gz_kree` appears with the same
   name for the init permission block and the `file_contexts` regex to match);
2. the **9 ioctl command encodings** and their exact argument layouts;
3. the **compat** entry point, since 32-bit clients are supported;
4. the absence of `read`/`write`/`mmap`/`poll`, which clients rely on failing.

The source-built module reproduces all four exactly — every one of the 42
functions is byte-identical — so no committed init, SELinux, or vendor
userspace artifact needs to change.
