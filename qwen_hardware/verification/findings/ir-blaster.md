# IR blaster kernel/HAL correction

Date: 2026-09-27

## Finding

The earlier statement that the image ships only an AOSP example/stub
ConsumerIR HAL is incorrect. The AOSP AIDL service is the binder-facing wrapper,
but the vendor image also ships a selected MediaTek legacy backend:

```text
ro.hardware.consumerir=common
/vendor/lib64/hw/consumerir.common.so
module id: consumerir
module name: MTK IR HAL
open name: transmitter
```

The service binary imports `hw_get_module` and the running capture registers
`android.hardware.ir.IConsumerIr/default` plus framework service `consumer_ir`.
The framework feature `android.hardware.consumerir` is present. That capture
used a LieppOS GSI over stock vendor, so it proves this vendor integration in the
captured environment; stock vendor files independently prove the static binding.

## Closed software chain

```text
IConsumerIr/default
 -> android.hardware.ir-service.example
 -> consumerir.common.so
 -> /dev/lirc0
 -> mtk_irtx_pwm.ko (RC_DRIVER_IR_RAW_TX)
 -> mtk-pwm.ko
 -> PWM channel 0 + mt6369_vio28 at 2.8 V
```

Live DT values are `pwm-ch=<0>`, `pwm-data-invert=<0>`,
`dma-mask-bit=<35>`, and `pwm-supply="mt6369_vio28"`.

The HAL advertises exact carriers 30/33/36/38/40/56 kHz, sets 33% duty, and uses
LIRC ioctls `0x40046913`/`0x40046915` before writing 32-bit microsecond
pulse/space durations. It appends a one-microsecond sentinel for even-length
patterns; the kernel strips that sentinel before generating its packed DMA
waveform.

## Confidence boundary

- Software ownership and ABI: **PROVEN** by stock ELF/module/DT/config and live
  service/property/feature evidence.
- Physical ConsumerIR emitter/circuit and emitted waveform: **UNVERIFIED**.
- Alternate `/dev/ctrl` HXD019 path: detected in the HAL but protocol/production
  presence remains **UNKNOWN**.

This finding supersedes the IR-specific statements in
`hidden-support-ics.md` and the prior final reports that said no real vendor IR
HAL was shipped. It does not change the separate night-vision/camera IR LED
analysis.
