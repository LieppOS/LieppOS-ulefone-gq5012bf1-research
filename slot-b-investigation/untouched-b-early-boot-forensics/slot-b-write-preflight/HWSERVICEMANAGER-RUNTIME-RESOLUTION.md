# hwservicemanager runtime path resolution

Follow-up after proving that the hwservicemanager executable exists in the
separate B system_ext image.

Questions checked:

- whether init explicitly starts the disabled service;
- where system_ext is mounted at runtime;
- whether `/system/system_ext/bin/hwservicemanager` is therefore valid;
- whether the required bootstrap linker exists;
- whether the executable contains the `hwservicemanager.ready` property logic.

No phone modification or boot was performed.
