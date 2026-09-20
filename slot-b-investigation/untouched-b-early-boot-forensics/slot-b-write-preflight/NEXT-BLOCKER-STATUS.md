# Next Slot-B blocker status

## chipinfo

The previous producer search initially showed only the consumer:

`wait_for_prop ro.vendor.soc.model_ready 1`

Inspection of `/vendor/bin/chipinfo` showed that chipinfo itself explicitly
sets:

`ro.vendor.soc.model_ready=1`

Therefore this is not a missing-producer case like the earlier
`vendor.all.modules.ready` blocker.

The live Slot-A environment is not an equivalent control for this helper:
the live-A chipinfo hash was empty and the relevant live-A properties were
unset.

## current priority

The MT6878 vendor init path performs a hard late-fs wait on:

`hwservicemanager.ready=true`

before continuing to `mount_all --late`.

The hwservicemanager service definition, start ordering, and executable are
therefore the next static chain being audited.
