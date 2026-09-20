# V10 source-path interpretation

V10 runtime proved that init enters and does not return from:

    /system/bin/vdc keymaster earlyBootEnded

Source tracing gives the path:

    vdc
      -> IVold::earlyBootEnded()
      -> VoldNativeService::earlyBootEnded()
           ENFORCE_SYSTEM_OR_ROOT
           ACQUIRE_LOCK
           initializeIncFs()
           Keystore::earlyBootEnded()
      -> AServiceManager_waitForService("android.security.maintenance")
      -> IKeystoreMaintenance::earlyBootEnded()

Therefore the next unresolved blocking boundaries include:

1. acquisition of the vold global lock;
2. initializeIncFs();
3. waiting for android.security.maintenance;
4. synchronous IKeystoreMaintenance::earlyBootEnded();
5. work performed by keystore2 / KeyMint beneath that call.

Generic NXP and Trusty KeyMint implementations found by the broad source
search are not evidence of the actual Ulefone KeyMint backend.

PHONE_MODIFIED=0
