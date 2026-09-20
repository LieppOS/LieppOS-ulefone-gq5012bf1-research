# hwservicemanager runtime path topology audit

The stock and Lineage hwservicemanager executables have different build IDs
and hashes, but static comparison found:

- the same `/system/bin/bootstrap/linker64` interpreter;
- the same direct DT_NEEDED libraries;
- the same hwservicemanager init service definition;
- equivalent relevant runtime/error/property strings.

The binary-version hypothesis is therefore demoted.

A correction to the previous path audit is required.

The extracted B system image is system-as-root. Therefore runtime:

`/system/system_ext/bin/hwservicemanager`

must be resolved through the system image's actual runtime `/system`
directory, represented host-side beneath:

`b-mounts/system/system/`

The previous audit inspected `b-mounts/system/system_ext`, which is not the
same runtime pathname.

This audit tests whether the required compatibility path/symlink from
`/system/system_ext` to the separately mounted `/system_ext` partition exists.

This is directly relevant because runtime checkpointing proved that init
reaches late-fs but never observes `init.svc.hwservicemanager=running` or
`hwservicemanager.ready=true`.

No phone modification was performed.
