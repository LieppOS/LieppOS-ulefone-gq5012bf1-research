# V8 module-ready static interpretation

The normal MT6878 init script initializes:

    vendor.all.modules.ready=1

during `early-init`.

Later, its `on post-fs-data` action waits for:

    vendor.all.modules.ready=1

Therefore that wait is not a strong blocker candidate unless some intervening
action changes the property away from 1.

This audit enumerates every built init-script reference and setter for the
property before deciding whether the V8 runtime boot test is still necessary.

The already committed V8 instrumentation remains useful because it can prove
whether the real MTK post-fs-data action itself begins.

PHONE_MODIFIED=0
