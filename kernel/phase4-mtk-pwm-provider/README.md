# MT6878 legacy MTK PWM provider source snapshot

This is the genuine source-built provider used to generate `Module.symvers` for
the LN2403 reconstruction. It is not a symbol/CRC shim and contains no patched
or hand-written CRC.

## Provenance

Copied from the local Nothing MT6878 tree; the only textual normalization is
removal of one extra terminal blank line from `mtk_pwm.c` (no token change):

`/home/armol/androido_dalykai/LieppOS custom ROM/kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/`

Source paths:

- `pwm/mtk_pwm.c`
- `pwm/pwm_v2/mtk_pwm_hal.c`
- `include/mt-plat/mtk_pwm.h`
- `include/mt-plat/mtk_pwm_hal.h`
- `include/mt-plat/mtk_pwm_hal_pub.h`
- `include/mach/mtk_pwm_prv.h`

`Makefile` and `BUILD.bazel` are the exact-GKI integration wrapper. The source
was built against `//common:kernel_aarch64`; the generated CRCs are:

- `pwm_set_spec_config`: `0xa54c8591`
- `mt_pwm_disable`: `0xd602ce35`

Both equal the stock `mtk-pwm.ko` exports and stock `leds-ln2403.ko` imports.
The provider module is a build-time proof/dependency for this task; installing
or testing it is outside this static-only reconstruction.

## Source SHA256

- `mtk_pwm.c`: `b21d6e386d35dfdb31763a13bb0c66bf9ac56d277222cedfe0be5cee646c0b21`
  (upstream/local original with extra terminal blank: `9981b3c73185d0391076b52ebe0a1cba1ec75935973f768461312f94e789dfbc`)
- `pwm_v2/mtk_pwm_hal.c`: `eeeefe673c279ff65998d67865bc9f121964530315b34a38faa45d12be8db496`
- `include/mt-plat/mtk_pwm.h`: `fe2017c363b459aee1b874f0d8cf43aac61b671a006ab5b5a06be5b83fa87c59`
- `include/mt-plat/mtk_pwm_hal.h`: `362dc80ec97855b7a67b06443fdf7c7e4a666ea0443635c35c011b4e05d19957`
- `include/mt-plat/mtk_pwm_hal_pub.h`: `439b316e8b44005f878e0a3e814763fce83d66977299c09832594382b879f7`
- `pwm_v2/include/mach/mtk_pwm_prv.h`: `336933c2c3d3f9f56bf88c064863f18b8c770f7b15477dcd5c9f9ac186d43fb7`
