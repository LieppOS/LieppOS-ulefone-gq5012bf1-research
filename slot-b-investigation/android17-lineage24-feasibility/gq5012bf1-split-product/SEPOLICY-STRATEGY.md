# SELinux policy strategy

```text
Android 17 platform sepolicy version = 202604
BOARD_SEPOLICY_VERS              = 202604
BOARD_API_LEVEL                  = 202604
captured vendor plat version     = 34.0
captured vendor_sepolicy.cil     = 1165608 bytes
captured vendor property contexts= 42250 bytes
```

The final system contains platform mapping material for older vendor policy.
The unchanged vendor supplies its split `vendor_sepolicy.cil`,
`plat_pub_versioned.cil`, vendor file contexts, service contexts, and property
contexts at runtime.

This first framework build deliberately adds no device allow rules. It does not
install the compliance-GSI `userdebug_plat_sepolicy.cil` (3,441,656 bytes), set
permissive mode, add blanket allows, or relabel vendor files speculatively.

The next policy milestone is an isolated first boot with actual Android 17 AVC,
property, service-manager, and hwservice-manager logs. Fixes must then be
minimal and assigned to platform, system_ext/product, or vendor policy according
to ownership. Existing vendor property namespaces remain authoritative until a
specific Android 17 conflict is observed.
