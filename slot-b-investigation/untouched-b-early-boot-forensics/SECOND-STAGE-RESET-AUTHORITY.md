# Current Slot-B second-stage reset authority

The exact current Slot-B EROFS filesystems were mounted read-only and their
Android init definitions searched for explicit reboot/fatal paths.

Named reset authorities found include:

- `vold`
  - `reboot_on_failure reboot,vold-failed`

- `apexd`
  - `reboot_on_failure reboot,apexd-failed`

- `apexd-bootstrap`
  - `reboot_on_failure reboot,bootloader,bootstrap-apexd-failed`

- vendor/system BoringSSL self tests
  - explicit `reboot,boringssl-self-check-failed`

- netbpfload
  - explicit reboot-on-failure path

- zygote
  - critical service with `target=zygote-fatal`

- servicemanager, hwservicemanager, lmkd and other critical services
  - init critical-service crash handling applies

This does not identify the failing component by itself.

However, `vold` and `apexd` are especially relevant because Slot A and Slot B
share persistent userdata and metadata state while the Android system image
sets are different. A failure while consuming shared FBE/APEX state can
therefore produce an explicit Android-initiated reboot without requiring a
kernel panic or PL/LK watchdog failure.

The historical `bootloader` boot-reason evidence is not independently proof of
`apexd-bootstrap` failure because manual bootloader recovery occurred during
the experiment.

Next steps are:

1. verify every reboot-on-failure service executable exists;
2. establish exact Android-15 init critical-service semantics from the source
   tree;
3. inspect shared APEX and vold metadata read-only, without extracting FBE key
   material;
4. compare current B fatal-service definitions against known-working factory
   V15 definitions.
