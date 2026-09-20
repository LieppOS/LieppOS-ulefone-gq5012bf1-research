# V2/V3 instrumentation semantics correction

## V2

Property-trigger actions cannot be used as evidence for this failure.

Android queues `late-init` before `queue_property_triggers`. Property triggers
are enabled by the latter queued action. Slot B stalls while processing the
late-init boot chain, during late-fs, before that enable action is reached.

Therefore untouched V2 `on property:` markers do not establish service
lifecycle state.

## V3

Runtime builtin arguments are expanded before the builtin executes. A failed
property expansion prevents the `write` command from executing.

Therefore an unchanged V3 sentinel is a non-observation; it does not mean that
the property had an empty value.

The positive observation remains:

    servicemanager.ready=true

at the beginning of Slot-B late-fs.

The MT6878 late-fs action then waits for:

    hwservicemanager.ready=true

and does not progress to post-fs-data.

Current classification:

SLOT_B_LATE_FS_WAITING_FOR_HWSERVICEMANAGER_READY_WHILE_SERVICEMANAGER_READY_TRUE

The next static target is the generated property-context / SELinux policy for
`hwservicemanager.ready`, plus the hwservicemanager setter path.

PHONE_MODIFIED=0
