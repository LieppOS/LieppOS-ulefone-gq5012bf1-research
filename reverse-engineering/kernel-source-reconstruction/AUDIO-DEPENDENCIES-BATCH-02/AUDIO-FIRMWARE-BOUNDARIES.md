# Kernel, firmware, userspace and GQ5012BF1 hardware boundaries

## Ownership layers

- **AP Linux:** MT6878 AFE/ALSA/ASoC, MT6369 host codec/accdet, amplifier host interface; ADSP/SCP/IPI host transport; reserved/shared memory, SLBC facade; CCCI/CCIF/DPMAIF/CCMNI controls, DMA, readiness/recovery, power/clock interfaces.
- **Audio DSP/SCP firmware:** proprietary signal-processing algorithms, offload/mixing and firmware-side message handling. Linux message structures/host queues are source evidence; firmware implementation is not.
- **Modem firmware:** radio/network/session speech handling and voice codecs executed on the baseband. CCCI exposes host communication only. No modem image reverse engineering, calibration change or firmware execution occurs here.
- **Android userspace:** vendor audio HAL, policy/routing, AudioFlinger, speech libraries, RIL/IMS and services. Endpoint/SELinux/static references are preserved evidence, not reconstructed HAL behavior or working voice calls.

## Hardware contract reused, not invented

| Finding | Status | Scope limit |
|---|---|---|
| MT6878 AFE and MD1/PCM1 configuration | ENABLED_IN_STOCK_DT | Existing verified AUDIO-BATCH-01 hardware report |
| MT6369 codec and accdet | STOCK_BINARY_IMPLEMENTATION / ENABLED_IN_STOCK_DT | Matched host drivers; no electrical test |
| AW88394 board amplifier identification | ENABLED_IN_STOCK_DT | Existing phone-specific board evidence; Claude owns AW883xx C closure |
| Earpiece, microphone connections, I2S4 speaker route | ENABLED_IN_STOCK_DT where established in prior report | Do not extend physical population/routing from generic source |
| CCCI audio/raw shared-memory devices | STOCK_BINARY_IMPLEMENTATION | Port/source/userspace references |
| SCP audio transport and ADSP IPI | STOCK_BINARY_IMPLEMENTATION | Host ABI/source coverage; firmware remains external |
| SLBC backend actually registered on MT6878 | UNKNOWN |32-function common facade is not proof of a hardware cache/SRAM backend |
| End-to-end uplink/downlink, offload, crash recovery, resume and latency | UNKNOWN | No runtime validation |
| Generic MT6897/6989 SLBC/SCMI implementation | PUBLIC_SOURCE_ONLY | Not assumed installed on this phone |

`PROVEN_RUNTIME` is reserved for explicitly preserved prior phone captures; **this task produces no new PROVEN_RUNTIME claim**. Readiness/state source code and an enabled DT node are different from successful operational firmware handshakes.

The exact graph distinguishes DIRECT_ELF_IMPORT from host registration, DT, userspace and firmware-mediated relations. Display callbacks and DMA heap are included for real transitive kernel ABI closure, not because a display driver is an audio engine.

All original firmware boundaries, raw stock inputs and hardware claims remain unchanged. Source parity supports a maintainable normal-world foundation, not proof of voice-call/audio functionality. OS integration, DSP/modem startup, module loading, hardware tests, calls and microphone recordings remain out of scope.
