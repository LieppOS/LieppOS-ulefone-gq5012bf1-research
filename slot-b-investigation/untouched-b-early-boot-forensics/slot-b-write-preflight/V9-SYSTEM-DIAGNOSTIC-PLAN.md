# V9 system post-fs-data diagnostic

V8 proves the MT6878 post-fs-data action itself was not reached.

The main system init.rc post-fs-data action is registered earlier and begins
with the synchronous command:

    exec - system system -- /system/bin/vdc checkpoint prepareCheckpoint

V9 will instrument the main system post-fs-data action directly.

Before modifying system_b, this audit confirms:

- the canonical system init.rc source;
- root vbmeta_b chaining;
- the private AVB key corresponding to the existing vbmeta_system_b public key;
- that system_b can remain at its existing exact partition size.

No Slot-B system write is performed by this audit.

PHONE_MODIFIED=0
