# GQ5012BF1 modem / CCCI / RIL / IMS reverse engineering

## Outcome

The reconstructable Linux kernel side is closed:

* **16 / 16 modem-related modules source-identified and rebuilt**
* **1,055 / 1,055 functions** byte-identical
* **730 / 730 data objects** byte-identical
* every import/export/modversion/export CRC/modinfo/vermagic/section-size check exact
* only 20 build-id bytes per module differ, with zero differences outside build-id

The phone has one integrated **MT6878 MD1, generation 6299**. CCIF carries 75 control/char/IPC/smem
ports; DPMAIF v3 carries 20 CCMNI packet-data ports. The real GQ5012BF1 table has 95 entries and is
in `kernel/ccci-port-map.tsv`. Linux source closure is independent of the signed proprietary MD1
firmware, RIL and IMS code.

## Topology

```
Android Telephony / ImsService
   -> AIDL Radio V2 (slot1/slot2; IRadioIms V1)
   -> mtkfusionrild + librilfusion + libmtk[mipc]-ril
   -> /dev/ttyCMIPC1 -> CCCI char port -> CCIF -> MD1 (control/SIM/voice/IMS)

Android data <-> ccmni0..7,9..20 <-> CCCI port_net <-> DPMAIF v3 <-> MD1
Wi-Fi offload <-> mddp <-> CCCI ccci_0_200 + RAW_USB/RAW_NETD smem <-> MD1
Audio HAL <-> ccci_aud/raw_audio + AFE MD1 PCM1 <-> MD speech
```

MD image: `MT6878_S00`, NLWCG, `MOLY.NR17.R1.MP5.RC.MP.V23.9.P1`, built 2025-10-22.
Two removable SIMs operate DSDS; prior research proves no eSIM/eUICC.

## Scope status

| scope | status | result / boundary |
|---|---|---|
| MODEM-KERNEL-TRANSPORT | DONE | all 16 modules, topology, DT/smem, dependencies exact |
| CCCI-KERNEL | DONE | 5 modules; 562/562 functions, 346/346 data, ABI exact |
| DPMAIF-KERNEL | DONE | 222/222 functions, 125/125 data, ABI exact |
| CCMNI-KERNEL | DONE | ccmni+rps_perf; 28/28 functions, 13/13 data, ABI exact |
| MODEM-DATA-PATH | DONE for kernel | DPMAIF/CCMNI/mddp integration understood; MD data stack proprietary |
| RADIO-HAL-RIL | PARTIAL | AIDL/service/ELF/port boundary mapped; implementation proprietary |
| IMS | PARTIAL | framework/service/RIL/MD/audio/Wi-Fi boundary mapped; implementation proprietary |
| MODEM-FIRMWARE | PARTIAL | authoritative image/sub-image/config inventory; signed MD code opaque |
| MODEM-NVRAM-CALIBRATION | PARTIAL | ownership/category/consumer map; contents intentionally private |

## Navigation

* Hardware: [`hardware/topology.md`](hardware/topology.md),
  [`hardware/modem-memory-map.md`](hardware/modem-memory-map.md)
* Kernel inventory/source/dependencies: [`kernel/module-inventory.tsv`](kernel/module-inventory.tsv),
  [`kernel/source-map.tsv`](kernel/source-map.tsv),
  [`kernel/dependency-graph.md`](kernel/dependency-graph.md)
* CCCI: [`ccci/README.md`](ccci/README.md),
  [`kernel/ccci-port-map.tsv`](kernel/ccci-port-map.tsv)
* DPMAIF/data: [`dpmaif/README.md`](dpmaif/README.md),
  [`data-path/ccmni.md`](data-path/ccmni.md),
  [`data-path/mddp-integration.md`](data-path/mddp-integration.md)
* Userspace: [`userspace/radio-hal.md`](userspace/radio-hal.md),
  [`userspace/ril.md`](userspace/ril.md),
  [`userspace/service-map.md`](userspace/service-map.md),
  [`userspace/dependency-map.tsv`](userspace/dependency-map.tsv)
* IMS/SIM: [`ims/README.md`](ims/README.md), [`sim/topology.md`](sim/topology.md)
* Firmware/NV: [`firmware/boundary.md`](firmware/boundary.md),
  [`firmware/inventory.tsv`](firmware/inventory.tsv), [`nvram/boundary.md`](nvram/boundary.md)
* Cross-subsystem: [`telephony/feature-map.md`](telephony/feature-map.md),
  [`telephony/audio-voice.md`](telephony/audio-voice.md),
  [`telephony/connectivity.md`](telephony/connectivity.md)
* Deltas/differences: [`yft-modem-deltas.md`](yft-modem-deltas.md),
  [`binary-analysis/remaining-differences.md`](binary-analysis/remaining-differences.md)
* Reproduction: [`scripts/rebuild_all.sh`](scripts/rebuild_all.sh),
  [`notes/PROVENANCE.md`](notes/PROVENANCE.md)
* Future safe validation: [`runtime-test-plan.md`](runtime-test-plan.md)

## Hard boundary

Do not modify/re-sign the modem image and do not copy/read per-device modem NV. Exact Linux parity
does not imply source availability for baseband, RIL, IMS, carrier policy or RF calibration.
