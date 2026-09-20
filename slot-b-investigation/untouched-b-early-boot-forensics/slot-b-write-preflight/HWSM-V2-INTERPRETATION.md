# hwservicemanager lifecycle V2 interpretation

The V2 runtime experiment did not observe any property-triggered lifecycle
checkpoint.

This includes the controls:

- `init.svc.servicemanager=running`
- `init.svc.vndservicemanager=running`

and all hwservicemanager lifecycle/ready checkpoints.

The untouched markers retained their pre-seed timestamps. In contrast,
`early-init`, `fs`, `post-fs`, and the diagnostic `late-fs` event marker were
rewritten during the actual Slot-B boot.

Therefore the diagnostic RC was parsed and its event actions were operational.

The evidence does NOT currently justify treating the failure as uniquely
hwservicemanager-specific. Either:

1. the essential service starts fail before observable init service-state
   transitions; or
2. the assumptions used by the property-trigger instrumentation are incorrect
   for this point in Android init execution.

The Android 15 init implementation must be audited before another boot.

The proven broader runtime boundary remains:

- B reaches early-init;
- B reaches fs/post-fs;
- B begins late-fs;
- B does not reach post-fs-data;
- the MT6878 late-fs path contains a wait for
  `hwservicemanager.ready=true`;
- pstore remains empty.

No phone modification was performed.
