# Slot-B effective critical-service reset boundary

## BoringSSL

BoringSSL remains closed as a prioritized reset cause.

## Important correction: textual `critical` does not always mean effective critical

Current-B zygote contains:

`critical window=${zygote.critical_window.minute:-off} target=zygote-fatal`

Exact Android init `ParseCritical()` semantics return successfully and
immediately when the expanded `window` value is `off`.

That return occurs before the parser sets `SVC_CRITICAL`.

Therefore a zygote declaration using this syntax is not effectively critical
when the property expansion produces `off`.

Current working-A property:

`zygote.critical_window.minute=ABSENT`

Current-B static property/setter hits:

`3`

Effective classification:

`ZYGOTE_CRITICAL_RUNTIME_VALUE_UNRESOLVED`

## Definite bare-critical services

The following current-B services use bare `critical` and therefore retain the
normal Android init fatal-crash behavior:

- `lmkd`
- `servicemanager`
- `hwservicemanager`

Before boot completion, a non-clean critical-service exit participates in the
critical crash counter. More than four failures can cause init's fatal reboot
path.

These services start asynchronously. Therefore later init progress and
USB/ADB visibility do not prove that they stayed healthy; init may continue
while one is repeatedly restarted.

## Historical evidence

The preceding Tier3 search excluding the proven Slot-A `fallback/` evidence
returned:

`NONE`

Thus there is currently no preserved direct Slot-B-era record identifying
`lmkd`, `servicemanager`, `hwservicemanager`, or zygote as the crashing
process.

Absence of preserved evidence does not close these asynchronous fatal paths.

## HBT / zygote override

Current B contains additional HBT zygote definitions under
`system_ext/etc/init/init.hbt.rc`, including an `override` service definition.

The generated evidence records:

- every current-B zygote definition;
- init rc parsing/import order source;
- the full HBT rc;
- app_process/app_process64/HBT executable identities.

This must be considered when determining the actual zygote executable used by
B.

## Safety

This investigation remained read-only on working Slot A and host-side for
Slot-B files.

No Slot-B boot was performed.

No partition, slot metadata, `/data`, `/metadata`, APEX state, or persistent
phone state was modified.
