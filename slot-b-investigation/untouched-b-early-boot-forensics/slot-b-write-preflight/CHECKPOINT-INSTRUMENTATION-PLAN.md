# Slot-B persistent checkpoint instrumentation plan

The missing-hwservicemanager-executable theory is closed:

- the B system_ext image contains `bin/hwservicemanager`;
- init explicitly starts the service;
- `/system/bin/bootstrap/linker64` exists;
- the binary contains `hwservicemanager.ready` handling.

A runtime hwservicemanager failure remains possible, but static inspection no
longer identifies a missing executable/start path.

The next diagnostic boot should persist init milestones outside vendor/system
so that the evidence survives manual recovery to Slot A.

Candidate milestones:

- early-init
- fs
- hwservicemanager.ready=true
- late-fs completed
- post-fs-data
- vendor.all.modules.ready=1
- apexd.status=activated
- odsign.key.done=1
- odsign.verification.done=1
- zygote start/running
- sys.boot_completed=1

Before modifying vendor_b again, `/metadata` availability and the first-stage
system_ext mount topology are being verified.
