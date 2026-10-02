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
