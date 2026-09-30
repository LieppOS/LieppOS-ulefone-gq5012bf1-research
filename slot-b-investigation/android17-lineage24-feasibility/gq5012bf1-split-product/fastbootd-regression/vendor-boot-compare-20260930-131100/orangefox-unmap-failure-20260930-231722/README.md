# OrangeFox Unmap Super Devices failure

OrangeFox's UI `Unmap Super Devices` operation reported failure.

Previous evidence showed all A/B logical partitions mapped simultaneously,
with at least system_a and vendor_a mounted.

This capture records:

- mapper state after the failed unmap attempt
- dynamic-partition mounts
- OrangeFox recovery log messages around the unmap failure
- processes with cwd/root/executable/open FDs on dynamic mount paths
- relevant recovery service state

No mount, mapper, partition, super metadata, userdata, or slot state is
modified by this investigation.
