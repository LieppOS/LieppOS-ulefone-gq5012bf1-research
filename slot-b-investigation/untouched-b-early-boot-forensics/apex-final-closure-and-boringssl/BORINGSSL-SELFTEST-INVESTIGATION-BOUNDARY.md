# Slot-B BoringSSL self-test investigation boundary

BoringSSL remains one of the explicit second-stage Android reboot authorities.

The exact Slot-B init rules are being audited for services carrying:

`reboot_on_failure reboot,boringssl-self-check-failed`

This investigation records:

- exact current-B self-test binaries;
- ELF identity and Build IDs;
- direct DT_NEEDED dependencies;
- static library availability;
- corresponding working-A services/files;
- preserved historical Tier3 failure strings.

No self-test binary from current B is executed on working A.

No slot, partition, APEX, filesystem, boot-control, crypto, or persistent
device state is modified.

The branch remains unclassified until the exact B init service definition,
binary dependency closure, and historical evidence are reconciled.
