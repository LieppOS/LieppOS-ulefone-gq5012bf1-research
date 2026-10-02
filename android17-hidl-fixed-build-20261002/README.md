# Android 17 HIDL-fixed userspace build

Build result: SUCCESS

Command:
`m -j48 systemimage systemextimage productimage`

Ninja completed 46040 steps successfully.

8a3d844f35c6d4f5039878a7e72a65c664ded243b9e749d49390bc4118bc2030  /mnt/SamsungSSD/android/lineage-24.0/out/target/product/gq5012bf1/system.img
4187b58a47ad36cd5b4e58f87c642ac4a73c617d241d796cdff53f451d41d84b  /mnt/SamsungSSD/android/lineage-24.0/out/target/product/gq5012bf1/system_ext.img
e2130d8fda18ffe2cb2b94a16659acd28b160127175547afee4a876539b6135a  /mnt/SamsungSSD/android/lineage-24.0/out/target/product/gq5012bf1/product.img

## Slot-B capacity verification

Exact image sizes match the already-established Slot-B logical partition sizes byte-for-byte:

- system.img: 665391104 / system_b: 665391104
- system_ext.img: 366891008 / system_ext_b: 366891008
- product.img: 337686528 / product_b: 337686528

Result:

- SYSTEM_FITS=1
- SYSTEM_EXT_FITS=1
- PRODUCT_FITS=1
- no super resize required

## Post-HIDL offline validation

- Android 17 checkvintf: COMPATIBLE (exit 0)
- Tested exact newly built system/system_ext/product images
- Stock Ulefone vendor/ODM inputs retained
- HIDL allocator manifest successfully parsed from system_ext
- secilc exit: 255

## Corrected split-SELinux verification

- stock vendor hash gate: PASS
- stock plat_pub_versioned.cil: bd4c019a2f2faeaf7b682be718e416f83ca22c6ff5e0754280693ae212bcd352
- stock vendor_sepolicy.cil: 282b405b13cdb830999a9f932dbbd78cf6adbe7c15a11c769f548c8d65fb04fd
- vendor policy mapping version: 34.0
- secilc exit: 0
- SELinux split-policy result: PASS
