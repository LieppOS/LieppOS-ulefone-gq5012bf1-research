# V16 pre-patch hypothesis

V15 established that an init-side assignment of:

    vendor.all.modules.ready=1

allows the MTK wait_for_prop command to return.

The normal producer still did not publish the property.

Working Slot A labels:

    /vendor/bin/init.insmod.sh

as:

    u:object_r:init_insmod_sh_exec:s0

The previous source audit found no matching file-context source rule in the
custom tree.

This is therefore the leading hypothesis for the normal producer failure:

1. init parses the insmod_sh service.
2. the `start insmod_sh` command itself returns.
3. the custom Slot-B executable may lack the stock init_insmod_sh_exec label
   and/or matching SELinux domain transition.
4. init therefore may reject or fail the service before normal execution.
5. init.insmod.sh never reaches its cfg setprop action.
6. vendor.all.modules.ready remains 0.

This is not yet proven until the built policy/file-context provenance is
compared with working Slot A.

Also corrected: the cfg source is:

    device/ulefone/armol/configs/vendor/init.insmod.mt6878.cfg

not the proprietary vendor path used by the previous audit.

PHONE_MODIFIED=0
