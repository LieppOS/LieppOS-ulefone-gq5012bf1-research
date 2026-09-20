# hwservicemanager V4 interpretation

Runtime V4 established:

- early-init reached;
- fs reached;
- post-fs reached;
- late-fs began;
- the complete V4 late-fs diagnostic action executed;
- `servicemanager.ready` was observed as `true`;
- `hwservicemanager.ready` expanded to the V4 default `ABSENT`;
- `hwservicemanager.disabled` expanded to `ABSENT`;
- `init.svc.servicemanager` expanded to `ABSENT`;
- `init.svc.hwservicemanager` expanded to `ABSENT`;
- pstore remained empty.

The V4 `init.svc.*` results are not yet interpreted as actual service state.

The diagnostic RC is installed under `/vendor/etc/init`, and Android init can
execute vendor actions through the vendor-init subcontext. Property visibility
must therefore be established before treating an `ABSENT` expansion as proof
that a property did not exist globally.

The next static audit checks:

1. whether `write` executes in the vendor subcontext;
2. whether `wait_for_prop` executes there or in main init;
3. whether vendor_init can read hwservicemanager_prop;
4. whether vendor_init can read init_service_status_private_prop.

PHONE_MODIFIED=0
