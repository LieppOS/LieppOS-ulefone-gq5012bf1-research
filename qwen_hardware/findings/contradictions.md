# Contradiction register

**Revised 2026-09-08** by the verification pass (`../verification/`). Every contradiction the first pass recorded has now been either resolved, corrected or restated precisely.

| # | Contradiction as originally recorded | Resolution | Where |
|---:|---|---|---|
| C1 | "50 MP Sony IMX989 GN1" mixes two incompatible sensor identities; GSMArena says 1/1.31" / 1.2 um while the live driver says IMX989 | **Not a contradiction - a dual-source slot.** `sensor0` declares `imx989`, `s5kgm2sp` and `s5kgn1sp` and binds by sensor-ID probe. This unit probed **IMX989** (Sony-specific 4096x3072 RAW vs Samsung 4080x3072); Ulefone documents the Samsung population. Retail lots differ. | `camera-main-identity.md` |
| C2 | "108 MP periscope" conflicts with `S5KJN1MAIN2_MIPI_RAW` | The third rear camera is a **50 MP ultrawide** (16 mm, f/2.2, 117.3 deg with autofocus per the OEM). No periscope exists in the device tree, the HAL or Ulefone's current specification. **Withdrawn.** | `camera-stream-configurations.md` |
| C3 | 10600 mAh marketing does not reconcile with the 8.4 V reading and the 8594 mAh gauge field | **Topology resolved:** it is a **2S pack, 7.74 V nominal, 8.90 V CV**; "21200 mAh" is the 3.87 V-equivalent of 10600 mAh at 7.74 V, and 8.4 V is simply 2 x 4.2 V at 79 % SoC. **One number remains open:** the gauge's design/FCC field reads 8594 mAh, about 19 % below the rating. | `battery-pack.md` |
| C4 | "570 LEDs / 1000 lumens" conflicts with the local emitter-count evidence | Restated as an **OEM claim about the auxiliary camping light** driven from `/yft_camplight` (red/blue/power GPIOs plus an "LN2403" driver). No datasheet for that driver was found, so radiant output stays unverified. | `hidden-support-ics.md` |
| C5 | MT6369 versus RT5133 at I2C `5-0018` | **Both parts exist, on different buses.** MT6369 is the **sub-PMIC on SPMI slave 5** (audio codec, headset accdet, `VIBR` haptic LDO); RT5133 is an **8-channel camera LDO PMIC on I2C 5-0018**. The dispute was a category error. | `power-support-ics.md` |
| C6 | Rear display recorded as 3.97 inch | **Corrected to 1.04 inch / 340x340 / 600 nits**, matching the Hynitron digitizer geometry and the OEM specification, on a **Chipone CO5300** driver. | `rear-display.md` |
| C7 | Water resistance recorded as 2 m / 30 min | **Corrected to 1.5 m / 30 min**; ratings are IP68 + IP69K (IP69 and IP69K are the same designation) plus MIL-STD-810H. | `ip-mil-certification.md` |
| C8 | Wireless charging listed at 50 W with 30 W reverse | **Disproven.** No device-tree node, no `wireless` power supply, no receiver IC; the OEM claims **10 W wired** reverse only. The `mt5786group` paths belong to a platform-wide ODM init file. | `wireless-charging.md` |
| C9 | UFCS suspected alongside PD/PPS | **Disproven.** The kernel enumerates `SDP DCP CDP PD PD_PPS`; no UFCS artefact exists anywhere. | `charging-capabilities.md` |
| C10 | ConnFem "10 candidates, selected pair unknown" implied hidden RF options | **Resolved:** the board resolves to **`nofem + nofem`**; the alternatives belong to other boards. | `connfem-selected-fem.md` |
| C11 *(new)* | Framework observations were treated as stock behaviour | **The capture was a LieppOS GSI over stock vendor/kernel.** Hardware facts stand; framework facts do not describe stock. | `00-snapshot-provenance-correction.md` |
| C12 *(new)* | `init.yft.rc` appeared to describe this device | It is a **platform-wide ODM option catalogue** referencing wireless charging, LRA haptics, a discrete FM tuner, a projector motor, a rangefinder and dual gauges on buses that do not exist here. | `hidden-support-ics.md` |

**No known contradiction is left unresolved.** The remaining open items are quantitative unknowns, not conflicts - they are listed in `../final/UNKNOWN-HARDWARE.md`.
