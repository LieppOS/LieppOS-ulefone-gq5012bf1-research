# Fastbootd after successful OrangeFox super unmap

OrangeFox's first `Unmap Super Devices` attempt failed while system_a and
vendor_a were mounted.

After stopping the recovery TrustKernel security services and unmounting:

- /mnt/system_a
- /vendor

a second OrangeFox `Unmap Super Devices` operation successfully removed all
observed A/B dynamic partition mapper devices, including system, system_ext,
product, vendor and DLKM mappings.

The MediaTek AIDL BootControl service remained healthy with two slots and
current slot A.

This test starts fastbootd after that clean state and checks whether it can
create/open the logical partitions itself.

No partition image is flashed, resized, erased, or otherwise modified.
`partition-size` may create transient device-mapper mappings as part of
fastbootd's normal logical-partition open path.
