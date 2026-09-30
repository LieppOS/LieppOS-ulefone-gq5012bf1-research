# Consumer IR blaster

## Corrected conclusion

**VERIFIED (static + captured runtime):** GQ5012BF1 has a complete software
ownership chain for PWM ConsumerIR. The AOSP `android.hardware.ir-service.example`
binary is the AIDL binder wrapper, not the only implementation. It calls the
legacy libhardware module selected by `ro.hardware.consumerir=common`, which is
stock `vendor/lib64/hw/consumerir.common.so` (`MTK IR HAL`).

```text
framework consumer_ir
 -> android.hardware.ir.IConsumerIr/default (AIDL v1)
 -> android.hardware.ir-service.example
 -> hw_get_module("consumerir")
 -> consumerir.common.so
 -> /dev/lirc0
 -> rc-core / mtk_irtx_pwm.ko
 -> mtk-pwm.ko / PWM0 / mt6369_vio28
```

The live capture shows the AIDL instance, framework `consumer_ir` service,
`android.hardware.consumerir` feature and `ro.hardware.consumerir=common`. It
was captured under a LieppOS GSI over the stock vendor stack, so the runtime
claim is limited to that environment; the stock vendor files independently
close the service/backend binding.

## Kernel/DT contract

**VERIFIED (stock object + live DT):** `mtk_irtx_pwm.ko` binds
`mediatek,irtx-pwm`, depends on `mtk-pwm`, registers an rc-core raw-TX device,
and consumes:

```text
pwm-ch = 0
pwm-data-invert = 0
dma-mask-bit = 35
pwm-supply = mt6369_vio28
regulator voltage = 2.8 V
PWM source clock assumption = 26 MHz
```

`modules.load` places `mtk-pwm.ko` immediately before `mtk_irtx_pwm.ko`. The
consumer uses MediaTek provider exports `pwm_set_spec_config()` and
`mt_pwm_disable()` with the same 72-byte `struct pwm_spec_config` found in the
public MT6878 donor tree.

## Userspace protocol

**VERIFIED (stock HAL disassembly):** the legacy module exposes six exact
carrier entries: 30, 33, 36, 38, 40 and 56 kHz. It opens `/dev/lirc0`, sets
carrier using ioctl `0x40046913`, sets 33% duty using ioctl `0x40046915`, then
writes a 32-bit microsecond pulse/space array. If the caller supplies an even
count, the HAL appends `1`; the kernel callback recognizes and removes that
sentinel.

The HAL also detects `/dev/ctrl` as an alternate HXD019 path. Its complete
external-controller protocol is not recoverable from this artifact and is
**UNKNOWN**.

## Distinctions

- `/irtx-pwm` is ConsumerIR transmission.
- `ln2403_pwm` belongs to the high-current camp/warning-light path and is not
  the IR carrier source.
- AW36515/AW36518 camera illumination drivers and the night-vision IR emitters
  are separate from this rc-core ConsumerIR path.
- Legacy `ueventd` entries for `/dev/irtx` and `/dev/ir-learning` exist, but the
  proven selected backend uses `/dev/lirc0`.

## Remaining validation

The software path is reconstructed, but physical function remains **UNVERIFIED**:

- identify the ConsumerIR emitter, transistor/driver and optical aperture;
- capture carrier/duty and pulse timing on authorized hardware;
- validate regulator/PWM cleanup and error handling;
- build against the exact 6.1.115 Android 14 GKI/KMI;
- verify `/dev/lirc0` ownership and enforcing SELinux policy in the target ROM;
- determine whether `/dev/ctrl` exists on the production handset and, if so,
  identify its HXD019 protocol.

Detailed disassembly reports, source reconstructions, hashes and copied evidence
are in sibling workspace `Reverse Engineer - PARTIAL/IR-BLASTER/`.
