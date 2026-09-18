# BP1A lunch modernization and vendor-image build

## Lunch modernization

The armol device tree contained legacy two-component lunch choices while this
Android build system requires:

`<product>-<release>-<variant>`

The release configuration was validated as:

`bp1a`

The device tree now declares:

- `lineage_armol-bp1a-user`
- `lineage_armol-bp1a-userdebug`
- `lineage_armol-bp1a-eng`

The obsolete `vendorsetup.sh` using `add_lunch_combo` was removed.

Device-tree commit:

`5833c3bddad1be64f4b62bcc93afcffdf240eefc`

## MT6878 insmod configuration

Exact stock SHA256:

`683d5f45ddf50f6091ce5bbcf4b90d3e92b4bd5ebf05bebab0d59ccf8b112c98`

The build target used:

`lineage_armol-bp1a-userdebug`

The `vendorimage` target completed successfully.

Generated vendor-tree configuration:

`/mnt/SamsungSSD/android/lineage-22.2/out/target/product/armol/vendor/etc/init.insmod.mt6878.cfg`

Generated configuration SHA256:

`683d5f45ddf50f6091ce5bbcf4b90d3e92b4bd5ebf05bebab0d59ccf8b112c98`

Exact match:

`PASS`

## vendor.img

Path:

`/mnt/SamsungSSD/android/lineage-22.2/out/target/product/armol/vendor.img`

Size:

`816353280`

SHA256:

`850a58b16357597e0fa93f7d5ab9443c85e1b49df33b0e86fa1d2d393044ca50`

Type:

`EROFS filesystem, compat: SB_CHKSUM MTIME, blocksize=12, exslots=0, uuid=c052e527-893b-5833-b105-149a2831daca, incompat: LZ4_0PADDING`

## Status

The source-side missing-insmod defect is now present in the generated vendor
staging tree with the exact verified stock bytes.

The next step is read-only inspection of the actual built `vendor.img` and
AVB comparison with the current Slot-B vendor payload.

No phone, flashing, or slot operation occurred in this step.
