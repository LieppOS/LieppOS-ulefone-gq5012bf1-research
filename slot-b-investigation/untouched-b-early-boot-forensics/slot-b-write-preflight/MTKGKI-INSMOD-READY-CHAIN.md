# MTK GKI module-ready producer chain

The global property audit found that `vendor.all.modules.ready` is not simply
left at the value written by `init.mt6878.rc`.

`init.mtkgki.rc` contains a setter to zero and starts the `insmod_sh` module
loader. The MT6878 insmod configuration contains a command referencing
`vendor.all.modules.ready`, apparently forming the completion side of that
protocol.

This audit determines:

- whether init.mtkgki.rc is part of normal GQ5012BF1 boot;
- the exact trigger that changes modules.ready to 0;
- how init.insmod.sh interprets the MT6878 cfg;
- whether the cfg's ready command occurs only after module processing;
- whether the built cfg matches the known fixed source;
- the completed working-A control state.

If the module loader sets ready=0 and only restores ready=1 after processing
the cfg, failure or non-completion of `insmod_sh` becomes a direct candidate
for the Slot-B post-fs-data stall.

PHONE_MODIFIED=0
