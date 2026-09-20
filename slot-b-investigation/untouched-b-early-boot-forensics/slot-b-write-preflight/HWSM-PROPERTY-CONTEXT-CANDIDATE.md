# hwservicemanager property-context root-cause candidate

The Slot-B system property contexts do not contain the platform mapping:

    hwservicemanager. -> hwservicemanager_prop

However, the current Lineage source tree contains that mapping and SELinux
policy grants the hwservicemanager domain permission to set the corresponding
property type.

This is significant because hwservicemanager calls:

    property_set("hwservicemanager.ready", "true")

and treats failure to set that property as non-fatal.

The MT6878 vendor late-fs path then blocks on:

    wait_for_prop hwservicemanager.ready "true"

This provides a direct mechanism matching the observed Slot-B runtime stall.

The next test is to regenerate plat_property_contexts from the current source
and determine whether the existing B system artifact is stale.

PHONE_MODIFIED=0
