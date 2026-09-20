# hwservicemanager next-cause analysis

Runtime checkpointing proved that Slot B reaches the late-fs trigger but never
observes either:

- `init.svc.hwservicemanager=running`
- `hwservicemanager.ready=true`

Static inspection has now demoted:

- missing Lineage hwservicemanager executable;
- missing direct DT_NEEDED libraries;
- absence of the hwservicemanager SELinux type/file-context rule;
- an obvious init property setter forcing `hwservicemanager.disabled=true`;
- absence of an explicit `start hwservicemanager`.

A significant remaining difference is that the factory Ulefone
hwservicemanager binary and the Lineage B binary are not byte-identical.

The next audit compares their ELF interpreter, dependencies, init definition,
build identity and relevant runtime/error strings.

No phone modification was performed.
