# V15 runtime interpretation

## Lifecycle observations

v15-mtkgki-early-init=1
v15-after-ready-zero=1
v15-after-insmod-start=1
v15-insmod-running=0
v15-insmod-stopped=0

v15-ready-zero-at-postfsdata=1
v15-ready-one-at-postfsdata=0

v15-before-force-ready=1
v15-after-force-ready=1

40-vendor-modules-ready=0
v8-modules-ready-passed=1

## Interpretation rules

- early-init=1 and after-ready-zero=1 proves the mtkgki early-init action ran
  through the initial modules-ready=0 assignment.

- after-insmod-start=1 proves init returned from the start insmod_sh command.

- insmod-running=1 proves init observed the service enter running state.

- insmod-stopped=1 proves init later observed the oneshot service stop.

- before-force-ready=1 and after-force-ready=1 prove the explicit V15 init
  setprop command returned.

- 40-vendor-modules-ready=1 proves the property=1 trigger fired.

- v8-modules-ready-passed=1 proves the MTK wait_for_prop barrier returned.

Do not infer more than these marker transitions establish.

EXPERIMENT_PHONE_MODIFIED=1
CAPTURE_PHONE_MODIFIED=0
