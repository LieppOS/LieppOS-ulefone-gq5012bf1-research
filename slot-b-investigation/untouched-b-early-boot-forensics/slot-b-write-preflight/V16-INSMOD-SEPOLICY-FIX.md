# V16 init.insmod SELinux repair candidate

Working Slot A contains:

    /vendor/bin/init\.insmod\.sh
        u:object_r:init_insmod_sh_exec:s0

and an `init_insmod_sh` domain with an init domain transition, module loading
permissions, system_dlkm access, and permission to publish the MTK vendor
property.

The custom build lacked the init.insmod.sh file-context mapping.

V16 restores the normal module-loader path:

    modprobe|*
    system_dlkm vendor

and removes the V15 forced modules-ready assignment.

It adds the reconstructed init_insmod_sh executable label and domain policy.

This stage modifies source trees only. No image was flashed and Slot B was
not activated.

PHONE_MODIFIED=0
