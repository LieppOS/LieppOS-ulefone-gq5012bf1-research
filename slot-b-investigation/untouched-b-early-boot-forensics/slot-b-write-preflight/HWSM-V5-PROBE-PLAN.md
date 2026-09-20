# hwservicemanager V5 main-init running-state probe

The V4 subcontext audit established an important distinction.

For commands originating from `/vendor/etc/init`:

- `write` executes in the vendor-init subcontext;
- `wait_for_prop` does not execute there;
- for `wait_for_prop`, vendor-side argument expansion occurs first, after
  which the builtin executes in main init.

The MT6878 command:

    wait_for_prop hwservicemanager.ready "true"

contains literal arguments. Therefore its actual wait is performed by main
init and is not equivalent to V4's vendor-init property expansion.

The V4 `init.svc.*=ABSENT` values must therefore not be interpreted as proof
that those services did not run.

V5 uses main-init `wait_for_prop` as a service-state probe during post-fs:

    init.svc.servicemanager = running
    init.svc.hwservicemanager = running

Persistent markers surround both waits.

Interpretation:

- `v5-sm-running=1` proves servicemanager reached running;
- `v5-hwsm-before=1` but `v5-hwsm-running=0` means hwservicemanager did not
  reach running;
- `v5-hwsm-running=1` and `v5-complete=1` prove hwservicemanager was already
  running before the later MTK wait for `hwservicemanager.ready=true`.

PHONE_MODIFIED=0
