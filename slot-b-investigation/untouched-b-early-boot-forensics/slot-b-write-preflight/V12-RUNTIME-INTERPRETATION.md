# V12 runtime interpretation

V12 is a diagnostic-only system build which bypasses
`vold::Keystore::earlyBootEnded()`.

## Proven runtime progression

Fresh Slot-B markers show:

- `v10-before-keymaster=1`
- `v10-after-keymaster=1`
- `v9-keymaster-passed=1`
- `v8-mtk-pfsd-start=1`

while:

- `v8-modules-ready-passed=0`

remained at its pre-boot seed timestamp.

Therefore V12 cleared the previously proven
`vdc keymaster earlyBootEnded` execution boundary.

The next directly observed blocking command is the MediaTek
post-fs-data wait for:

`vendor.all.modules.ready=1`

The V12 result does not prove the permanent fix is to bypass vold Keystore.
The bypass is diagnostic only.

Next investigation target:

1. `insmod_sh` service lifecycle
2. `init.insmod.sh` execution path
3. every writer of `vendor.all.modules.ready`
4. whether the service is running, stopped, restarting, or never started
   when MTK post-fs-data reaches its wait
5. whether module loading itself is hanging before the final property write

V12 system and V8 vendor hashes were verified unchanged after the trial.
pstore remained empty.
