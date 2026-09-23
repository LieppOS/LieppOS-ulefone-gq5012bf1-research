# USB3 feasibility verdict

## Overall verdict

**UNKNOWN — NEED PCB EVIDENCE**.

Stock USB3 operation is not merely disabled by an obvious property: the effective DT has no production U3 PHY at all, the independent MT6878 donor has the same USB2-only topology, and runtime creates no SuperSpeed root hub. The product is therefore **likely hardware-limited in its current design**, but “confirmed hardware-limited” would require silicon/package and PCB evidence that is not yet available.

## Independent answers

| Question | Answer | Confidence |
|---|---|---|
| A. SoC supports USB3? | No publicly implemented production U3 path was found. Transistor/package-level capability remains unknown; secondary PhoneDB claims conflict with OEM kernel source. | UNKNOWN, strongly disfavored |
| B. Stock kernel supports USB3? | Generic MTU3/xHCI/XS-PHY code supports USB3-capable sibling SoCs, but this stock instance has no U3 PHY configuration. | Generic code YES; target path NO |
| C. GQ5012BF1 DT supports USB3? | No. It references only USB2 and caps MTU3 at High-Speed. | DISPROVEN |
| D. GQ5012BF1 mainboard routes USB3? | Not established. | UNKNOWN |
| E. Daughterboard routes USB3? | Not established from the one-sided `BM65_SUB_V1.2` photograph. | UNKNOWN |
| F. External connector routes USB3? | Receptacle contact population/net continuity is not visible. | UNKNOWN |
| G. Stock software enables USB3? | No. UDC maximum is High-Speed and xHCI exposes only a USB2 root hub. | DISPROVEN |
| H. Daughterboard-only upgrade plausible? | Only if SS pairs already reach the mating connector. No evidence shows that; current topology makes it unlikely. | UNKNOWN / currently unlikely |
| I. Kernel/DT-only upgrade plausible? | No valid MT6878 U3 PHY node, registers, calibration or physical lanes are known. | UNKNOWN at silicon level / currently implausible |

## Five-case classification

### Case 1 — SoC lacks accessible USB3

**Consistent with all authoritative implementation evidence.** If true, USB3 requires an external controller plus board redesign and cannot be enabled through DT/kernel changes.

### Case 2 — SoC may support USB3, but mainboard omits SS lanes

**Also consistent and likely.** A daughterboard replacement would not help.

### Case 3 — SS lanes reach the daughterboard connector, stock daughterboard omits them

**Possible but unsupported.** The visible dense connector has enough unknown contacts that this cannot be excluded. Continuity is required before designing a board.

### Case 4 — Mainboard and daughterboard carry SS lanes; DT/kernel disables them

**Physically possible but poorly supported.** Stock and donor source omit the required U3 PHY description rather than merely disabling it.

### Case 5 — everything wired/enabled, negotiation stuck at 480 Mbit/s

**Disproven for current stock software**, because the U3 PHY is not enabled/described and no SS root hub exists.

## Why a simple DT edit is unsafe

Changing `maximum-speed` to `super-speed` would leave all of these unresolved:

- no production MT6878 U3 PHY node;
- no known U3 register base;
- no MTU3 USB3 PHY phandle;
- no U3 efuse/calibration data;
- no verified clock/reset/power-domain contract;
- no physical orientation mux/redriver;
- no board-lane proof.

At best, the edit would be ignored or fail probe. At worst, unsupported register or power changes could break the shared USB2 path, including the thermal camera.

## Daughterboard replacement decision rule

A custom daughterboard is worth designing only after all four SS differential pairs are proven at the board-to-board connector:

- TX1± and RX1±;
- TX2± and RX2±.

The custom board would then also need correct Type-C orientation routing, ESD protection, controlled impedance and validated connector footprints. If those pairs are absent at the connector, daughterboard replacement cannot enable USB3.

## Kernel-only decision rule

Kernel/DT work becomes rational only after:

1. primary MT6878 documentation or verified hardware establishes a production U3 PHY/register block;
2. mainboard continuity proves SS pairs reach the port path;
3. required clocks, resets, power, efuse and orientation controls are identified.

Until then, USB3 kernel work is speculative and risks the proven USB2/thermal system.

## Single highest-value next experiment

On a spare `BM65_SUB_V1.2` board and, ideally, a spare mating mainboard, perform a **battery-disconnected continuity map of all eight USB-C SuperSpeed contacts through the daughterboard and board-to-board connector toward the mainboard/SoC side**.

This non-powered test most directly distinguishes Cases 2 and 3 and can falsify the daughterboard-only-upgrade hypothesis. Use microscope documentation and continuity/resistance only; do not inject voltage or destructively probe the in-service sealed phone.
