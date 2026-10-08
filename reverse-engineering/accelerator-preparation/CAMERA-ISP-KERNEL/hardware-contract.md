# Hardware contract — CAMERA-ISP-KERNEL

The stock selected base DT + overlay exposes **35** camera-owned nodes on MT6878T. The
complete lossless rows, including every property and resolved provider argument, are in
[dt-nodes.tsv](dt-nodes.tsv); clocks, power domains, IOMMU, mailbox and reset phandles are
resolved in [dt-providers.tsv](dt-providers.tsv).

## Board-visible blocks

| block | compatible / node | parent-bus register range | DT interrupt spec (SPI) |
|---|---|---|---|
| SENINF top | `mediatek,seninf-core` `/soc/seninf-top@1a00e000` | `0x1a00e000 + 0x18000` plus secondary ranges | 152, 149 |
| CSI inputs | four `mediatek,seninf` children | child of SENINF top | — |
| sensors | four `mediatek,imgsensor` nodes (`sensor0`, `sensor1`, `sensor2`, `sensor4`) | I²C address `0x10` on three controllers | — |
| camsys top | `mediatek,mt6878-camisp` | `0x1a000000 + 0x1000` | — |
| RAW A/B | `mediatek,cam-raw` | `0x1a030000`, `0x1a070000` (0x8000 each plus secondary ranges) | 136, 138 |
| RMS A/B | `mediatek,cam-rms` | `0x1a040000`, `0x1a080000` | — |
| YUV A/B | `mediatek,cam-yuv` | `0x1a050000`, `0x1a090000` | 137, 139 |
| CAMSV | `camsv1` `0x1a100000`; `camsv2` `0x1a101000`; `camsv5` `0x1a104000` | 0x1000 each plus secondary ranges | 651–656, 663–665, 669, 670, 673 |
| MRAW | `mraw1@1a130000` | `0x1a130000 + 0x8000` plus secondary ranges | 153 |
| PDA | `mediatek,camera-pda` | `0x1a180000 + 0x1000` | 150 |
| IMG_SYS | `mediatek,imgsys-isp7sp-mt6878` | `0x15000000 + 0x4000` plus module ranges | — |
| HCP / CMDQ | `hcp7sp` / `imgsys-cmdq-7sp` | `0x15001000`, `0x15002000` (0x4000 each) | — |
| AIE | `mediatek,aie-isp7sp-2` | `0x15310000 + 0x1000` | — |
| CCU | `ccu_rproc@1b080000`, `ccu_rproc1@1b180000` | 0x9000 each | 648 on primary |
| VMM SPM | `mediatek,vmm_spm_mt6878` | `0x1c001000 + 0x1000` | — |

Also present are IMG_SYS/MRAW syscons, `remoteproc-ccd`, camisp larbs and CCU camera
coordination nodes. All 35 rows are `okay` or implicitly enabled.

Addresses above are **parent-bus addresses**, not asserted CPU physical addresses until
all ancestor `ranges` translations are applied. SPI numbers are decoded DT interrupt
cells, not observed Linux IRQ numbers.

## Driver-to-DT match

Stock module `of:` aliases match the board for HCP, IMG_SYS CMDQ/ISP7sp, CCD remoteproc,
CCU, camsys/SENINF/RAW/RMS/YUV/CAMSV/MRAW, AIE, PDA and imgsensor. The complete
alias-to-board comparison is in [module-dt-match.tsv](module-dt-match.tsv).

No matching compatible is present for `mediatek,ipesys-me`. For drivers without stock
`of:` aliases, the accepted source separately identifies DPE's `mediatek,dvp`/`dvs`/`dvgf`,
the VMM ISP71 regulator's `mediatek,ispdvfs`, and notifier's `mediatek,vmm_notifier`; all
five strings are absent from the merged board DT. C2PS is a software scheduling interface,
not a DT-bound hardware block. Some modules are helper/child or software-created devices;
for DPE and IPESYS-ME, absence means the shipped module may remain unbound on this board.
`mtk_imgsys_v4l2`, RPMsg, debug, glue and scheduler modules likewise need not own a direct
DT node. This distinction prevents treating “module shipped” as “hardware instantiated”.

## Ownership boundary

This component owns normal-world ISP/SENINF/CCU/AIE/DPE/PDA/VMM **kernel code only**.
Sensor dies, EEPROMs, lens/VCM/OIS, flash and camera LDO rails retain their named DONE
owners. CCU firmware, CameraProvider/HAL, 3A, tuning and calibration interpretation remain
in `CAMERA-HAL-ISP`.

## Static-versus-runtime limit

The DT proves configured topology, resource cells and compatible matching. It does not
prove electrical population, regulator sequencing, clock rates, successful probe, live
IRQ routing, IOMMU attachment, firmware boot, stream execution or throughput. Those remain
on-device acceptance items in [source-to-userspace-contract.md](source-to-userspace-contract.md).
