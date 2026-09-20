# V11 runtime interpretation

V11 was built with the final Keystore2 KeyMint propagation call replaced by
Ok(()).

The valid seeded runtime produced fresh execution through:

    v10-before-keymaster=1

but retained the pre-boot zero seed for:

    v10-after-keymaster=0

Therefore:

    /system/bin/vdc keymaster earlyBootEnded

still did not return during the observed Slot-B boot even though the V11
Keystore2 binary contains the KeyMint-propagation bypass.

This does NOT by itself prove that set_up_boot_level_cache() is blocking.
Possible remaining boundaries include:

- vold work before Keystore::earlyBootEnded();
- Keystore maintenance-service acquisition;
- Binder transaction/dispatch into Keystore2;
- Keystore2 permission processing;
- SuperKeyManager::set_up_boot_level_cache().

V12 will bypass the entire vold Keystore::earlyBootEnded() function while
leaving the preceding VoldNativeService path intact.

PHONE_MODIFIED=0
