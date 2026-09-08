# Mandatory RED: Sony WL2868C donor

Donor: Sony `wl2868c-regulator.c` / `.h`, source commit `7e42db1690b5…`; frozen under `workspace/phase4-custom-ldo-wl2868/donors/sony-7e42db1690b5/`.

## RED result

**STRUCTURAL_DONOR_ONLY.** The donor was not treated as a source match and no donor source was edited. Its implementation is a regulator-framework driver using regmap and `devm_regulator_register`; the stock oracle is a raw-I2C custom driver with `misc_register`, `wl2864c_fops`, `wl2864c_read`/`write`, and the exported `will_ldo_*` ABI.

The donor has compatible `willsemi,wl2868c`; stock has `will,wl2864c_pmu`. The donor has no `will_ldo_vout` or `will_ldo_en` exports, no `memdup_user` path, and no stock `reset`/`vin1_en` probe sequence. Its voltage tables are useful only as family context and were not copied as proof of stock semantics.

## Build attempt

The pristine donor build harness is at `/home/armol/kernel-work/gki-12901745-workspace/lieppos/custom-ldo-wl2868-recon/donor-red/`. Exact-GKI attempts are preserved in `sony-donor-red-build-attempt1.log` and `sony-donor-red-build-attempt3.log`. Both stopped in the shared GKI kernel build before donor compilation because clang could not create temporary files in the Bazel action environment; this is an environment/build blocker, not a donor-source result. The logs also show an interactive KASAN config prompt, so no build success is claimed.
