# V14 runtime interpretation

V14 removed all module loading from `init.insmod.sh` while preserving the
original final:

    setprop vendor.all.modules.ready 1

The Slot-B boot still did not reach ADB/UI and both:

    v8-modules-ready-passed=0
    40-vendor-modules-ready=0

remained unreached.

Therefore neither the vendor nor system_dlkm modprobe operation is required
to reproduce the modules-ready stall.

The next investigation target is the `insmod_sh` execution path itself:
service start/exec, cfg access/parsing, process lifetime, SELinux/property
publication, and the final setprop operation.

V14 remains diagnostic only.

EXPERIMENT_PHONE_MODIFIED=1
CAPTURE_PHONE_MODIFIED=0
