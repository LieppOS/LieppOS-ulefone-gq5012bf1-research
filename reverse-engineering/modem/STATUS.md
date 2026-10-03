# Modem research status

Status date: 2026-10-03

## Kernel closure

| module group | modules | functions | data | ABI | source |
|---|---:|---:|---:|---|---|
| CCCI core/control | 5 | 562/562 | 346/346 | exact | MTK fae67a9257dc |
| DPMAIF | 1 | 222/222 | 125/125 | exact | MTK fae67a9257dc |
| CCMNI/RPS | 2 | 28/28 | 13/13 | exact | NothingOSS 957dac1 trees |
| MDDP | 1 | 132/132 | 87/87 | exact | 957dac1; already closed in connectivity |
| MD power/thermal | 3 | 57/57 | 109/109 | exact | mdpm/cooling 957dac1; throttling 6df320423600 |
| C2K USB rawbulk | 4 | 54/54 | 50/50 | exact | 957dac1 |
| **total** | **15** | **1,055/1,055** | **730/730** | **exact** | mixed exact component revisions |

Whole-file status: every module differs only in 20 GNU build-id bytes; zero other bytes differ.

## Evidence closure

| item | status |
|---|---|
| stock modem-module inventory | complete (hash, size, vermagic, deps, ABI, KCFI, sections, build ID, source/commit) |
| exact source search | complete across NothingOSS history; candidate revisions ruled out by parity |
| CCCI FSM/boot/exception/reset/debug | mapped |
| actual port table | 95/95 decoded; channel/HIF/queue/device/ops/consumer table published |
| DT / LK / smem memory map | mapped from GQ5012BF1 DT and existing live capture |
| DPMAIF v3 / CCMNI / RPS | mapped, exact |
| mddp relation | mapped without reopening connectivity scope |
| Radio AIDL/RIL service/ELF/node map | complete static boundary |
| IMS/VoLTE/WFC/VT/RCS map | complete static boundary; proprietary behavior remains |
| two-SIM DSDS topology | mapped; eSIM absence reused |
| modem firmware/sub-images/config | inventory complete; payload remains proprietary |
| modem NV/calibration | ownership/categories/consumers mapped; data intentionally uninspected |
| supported features | conservative static classification complete; exact RF bands unknown |
| audio/connectivity integration | modem-facing dependency graph complete |
| YFT deltas | kernel source delta none; configuration/firmware deltas listed |

## Scoped classifications

* **DONE:** MODEM-KERNEL-TRANSPORT, CCCI-KERNEL, DPMAIF-KERNEL, CCMNI-KERNEL.
* **PARTIAL:** RADIO-HAL-RIL, IMS, MODEM-FIRMWARE, NVRAM-CALIBRATION.
* **BLOCKED:** no Linux kernel source item. Exact band/SAR/calibration decoding requires proprietary
  DRDI/MCF/NV formats or authorized documentation; runtime state checks are optional and listed in
  `runtime-test-plan.md`.

## Best next subsystem

The next highest-value modem work is **Radio HAL/RIL userspace protocol reconstruction** (MIPC
framing and request map) if an open replacement is required. It is independent of the now-closed
kernel. Firmware/RF reverse engineering is lower-value and constrained by signed proprietary code
and private calibration.
