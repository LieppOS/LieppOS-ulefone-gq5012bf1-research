# Normal-world modem speech/kernel interfaces

## Evidence-qualified path

| Interface | Evidence level | Kernel boundary |
|---|---|---|
| Audio common→`get_md_resv_mem_info` | STOCK_BINARY_IMPLEMENTATION | CCCI util provides reserved modem-memory discovery |
| Audio common→`get_smem_phy_start_addr` | STOCK_BINARY_IMPLEMENTATION | CCCI core provides physical shared-memory region lookup |
| `/dev/ccci_aud`, RX7/TX6 | STOCK_BINARY_IMPLEMENTATION | CCCI AUDIO character/control packets on CCIF; preserved stock port table |
| `/dev/ccci_raw_audio` | STOCK_BINARY_IMPLEMENTATION | RAW_AUDIO shared-memory port;52KiB fallback is a source default, not proof of actual runtime reservation |
| `/dev/usip` / RAW_USIP | STOCK_BINARY_IMPLEMENTATION | Audio common host-side shared mapping; speech algorithm lies beyond Linux |
| MT6878 MD1/PCM1 DAI | ENABLED_IN_STOCK_DT | Existing AUDIO-BATCH-01 board/AFE report; do not equate control packets with PCM sample transport |
| Audio HAL opens CCCI audio endpoints | STOCK_BINARY_IMPLEMENTATION | Preserved vendor userspace string/open evidence and SELinux policy, not a new live test |
| Successful voice call / physical uplink/downlink | UNKNOWN | Not exercised by source parity or this offline mission |

Corrected provenance: the actual stock audio imports resolve `get_md_resv_mem_info` to **ccci_util_lib** and `get_smem_phy_start_addr` to **ccci_md_all**. Historical generic prose assigning both to util is superseded by `AUDIO-DEPENDENCY-GRAPH.tsv`.

## Preserved GQ5012BF1 hardware contract

This reuses AUDIO-BATCH-01/AUDIO-HARDWARE-TOPOLOGY.md at f00bd8af7e6bd4fde4355ae67e8392feab596a80; no board route is inferred from the new generic modem source.

| Preserved phone interface | Exact relationship | Evidence level |
|---|---|---|
| AFE | MT6878 PCM@0x11050000; stock compatible mediatek,mt6878-sound; saved bound driver | ENABLED_IN_STOCK_DT; PROVEN_RUNTIME (prior capture, not a new test) |
| Speaker/feedback I2S | One AW88394, PID0x2049, I2C6@0x34; speaker_amp bound; I2S_OUT4/I2S_IN4 stock spk-i2s0x19/0x18 | PROVEN_RUNTIME for amp; ENABLED_IN_STOCK_DT for I2S |
| Codec/earpiece | MT6369 machine/codec; internal RCV from MTKAIF DL/ADDA and MD1 PCM or DL1; product RCV_PATH_INT=yes/SPK_PATH_NO_ANA=yes | ENABLED_IN_STOCK_DT; preserved product-specific route evidence |
| Microphones | Main AIN0/PGA_L/ADC_L/MISO0; sub AIN2/PGA_R/ADC_R/MISO1; headset MIC_BIAS_1/AIN1/ADC_L; prior board report, not generic MediaTek reference population | Preserved phone-specific report; physical placement UNKNOWN |
| SCP/DSP transport | RV55 tasks; scp-audio-mbox@0x1cbe0000; reserved audio0x5c0000/IPI-DMA0x200000/logger0x180000 | ENABLED_IN_STOCK_DT; actual firmware algorithm UNKNOWN |
| Clock/power | MT6878 ADSP clocks; MT6685 DCXO; MT6369 regulators on SPMI USID5 | STOCK_BINARY_IMPLEMENTATION |
| Generic SLBC backend/cache | MT6897/6989 optional backend implementations | PUBLIC_SOURCE_ONLY; not an MT6878 registration claim |

No amplifier firmware, speaker calibration, codec nvmem, microphone recording or end-to-end audio operation was touched. AW883xx remains another owner's C target. Kernel stock matching alone does not certify physical routing or a successful call.

## Host transport and state

CCCI core implements port dispatch, shared-memory controls, character devices, modem readiness/exception coordination and registered HIF operations. CCIF is the control/character/speech packet path. DPMAIF and CCMNI/RPS implement cellular packet transport and scheduling; they are part of the coherent host family but **voice samples do not traverse DPMAIF/CCMNI**. No proprietary voice codec or network/RF algorithm has been reconstructed.

The CCCI SCP FSM bridge uses registered callbacks/IPI to coordinate MD/SCP state. This is a source-supported registration edge, not a reverse direct ELF import guessed from architectural similarity. Audio IPI, ADSP and SCP source were already reconstructed in previous owned batches; here they are graph providers and source-only ABI witnesses where required, never repeated target certifications.

## Buffers, power and failure boundaries

Reserved-memory lookup, DMA/shared buffers and Linux readiness/recovery mechanics are source-controlled. Audio SLBC callers use an exported common-ops facade; absent backend callbacks return `-ENODEV`. Generic MT6897/6989 SCMI/cache implementations are PUBLIC_SOURCE_ONLY, not proof of an MT6878 backend registration. `system_heap` is a genuine transitive DRM/CCCI shared-buffer provider, not presumed speech-sample allocator.

Modem power-model, display MIPI/oscillator callbacks, clocks, DVFS and suspend/debug providers establish host coordination interfaces. A matched module does not prove DSP/modem firmware initialization, interrupt timing, end-to-end latency or board routing. Exception, crash recovery and resume paths require later controlled integration/device validation; none was attempted.

References: existing modem `kernel/ccci-port-map.tsv`, `binary-analysis/md_ccci_ports.stock.tsv`, `telephony/audio-voice.md`; verified audio hardware/DSP reports; exact current ABI graph and complete compiled-source ledgers. No new microphone recording, call, firmware execution or phone access.
