# Condensed evidence: vendor (OEM / database) hardware claims

> **Reading note (2026-09-08).** This file *records claims verbatim*; it is not an inventory. Several
> claims below were later disproven or corrected by the verification pass — the verdict on each is
> listed at the end, and the authoritative status lives in `../../final/` and
> `../../verification/findings/`.

## S04 — Ulefone official spec sheet, `https://store.ulefone.com/pages/armor-29-pro-thermal-specs`
Claim quality **B (official marketing claim)**. Quoted claims relevant to this audit:

- "Armor 29 Pro Thermal Edition", MT6878T / Dimensity 7400, 12/16 GB RAM (+50 GB extended) + 512 GB ROM
- Main camera "**50MP Sony IMX989 GN1**" (contradiction — see `../../findings/contradictions.md`)
- 32 MP front, 64 MP macro, 108 MP periscope "with macro mode", 3.97″ rear screen 600 nits
- **Thermal: 640×512 @ 25 Hz; "super-resolution" 1280×1024 @ 3 fps**; "M170/M170L2" module naming in marketing text
- "4 infrared lights", night-vision camera mode
- **570 LED / 1000 lumen auxiliary light**, 3-level dimming (1 % / 50 % / 100 %) — measured on 2026-08-13 at 10 cm in `reports/night_light.md`
- Battery "2 × 5300 mAh = 10600 mAh", 120 W, **UFCS**, PD/PPS; 50 W wireless + 30 W reverse (per device `SystemConfig.java`: `WIRELESS_MAX_POWER=50000000`, `REVERSE_MAX_POWER=30000000`)
- Band table incl. LTE 1/2/3/4/5/7/8/12/17/20/28A/38/40/41/66, NR n1/3/5/7/8/20/28/38/41/66/77/78/79, 2G 850/900/1800/1900, 3G B1/2/4/5/8
- IP68/IP69K/IP69 (+MIL-STD-810H), "2 m / 30 min water"
- GNSS: GPS/GLONASS/Galileo/QZSS/BeiDou (+NavIC on GSMArena)
- Sensors: gravity, horizontal, light, posture, **proximity, step counter**, magnetic, **hall**, gyro, **pressure**, **temperature**

## S05 — GSMArena, `https://www.gsmarena.com/ulefone_armor_29_pro_thermal_5g-14104.php`
Claim quality **B (independent database)**. Relevant rows:

- Body: **688 g**, 33.8 mm thickness → rugged sealed chassis (largest dimension ⇒ large vapor chamber/heatsink mass; NOT verified internally)
- Main camera listed by geometry as **1/1.31″, 1.2 µm** pixels (i.e. does not match IMX989's 1″/1.6 µm ⇒ supports the "GN1-class, not IMX989" reading)
- Video: 4K@30, 1080p@30 — **no** slow-motion modes listed (consistent with chip/HAL 4K30 ceiling)
- **USB: USB Type-C 2.0** (⇒ no USB 3.x SuperSpeed, no DP alt-mode)
- **Radio: FM radio with RDS, "loudspeaker"**; WLAN Wi-Fi 6E class + hotspot; BT 5.x with **A2DP, LE-ADP(=Auracast/LE Audio ADP), BLE, aptX-HD (vendor string)**
- Combo connector: **USB OTG + pogo-pin accessory/magnetic connector** (accessory power/data pins)
- Secondary display 3.97″ AMOLED 600 nits; 570-LED light; NFC "yes (bank-card payment)" claim; IR blaster absent from list

## Vendor claims that could NOT be substantiated anywhere (recorded, not assumed)
- "50MP Sony IMX989 GN1" as a single part (self-contradictory string) → treated as unresolved sensor identity
- "108 MP periscope with macro mode" (driver name reports `S5KJN1MAIN2` = 50 MP-class die) → variant question
- "570 LED / 1000 lm" light (physically counted in `reports/night_light.md`: ring has far fewer emitters; 1000 lm implausible ⇒ measured radiance only)
- "IP69K / IP69 / 2 m 30 min" and "MIL-STD-810H" — no test report available
- 120 W wired / 50 W wireless / 30 W reverse charging — device-side config values seen (PD/PPS advertised caps, `WIRELESS_MAX_POWER`), but actual negotiation not tested
- Vapor-chamber/active-cooling presence: no teardown or FCC internal photos found for this SKU

## Verdict on each recorded claim after the verification pass

| Recorded claim | Verdict | Where |
|---|---|---|
| "50MP Sony IMX989 GN1" as one part | **Explained, not contradictory** — a dual-source slot (`imx989` / `s5kgm2sp` / `s5kgn1sp`); this unit probed **IMX989** | `camera-main-identity.md` |
| 108 MP periscope | **Withdrawn** — the third rear camera is a 50 MP ultrawide; no periscope exists in DT, HAL or the OEM's current spec | `camera-stream-configurations.md` |
| 3.97″ rear screen (S04 + S05) | **Wrong on both sources** — 1.04 inch, 340x340, Chipone CO5300 | `rear-display.md` |
| 2 m / 30 min water resistance | **Corrected to 1.5 m / 30 min**; IP68 + IP69K, MIL-STD-810H remain claim-level | `ip-mil-certification.md` |
| 2 x 5300 mAh | **Reinterpreted** — one 2S 7.74 V pack rated 10600 mAh; the 8594 mAh gauge value is still unexplained | `battery-pack.md` |
| UFCS | **Disproven** — kernel enumerates `SDP DCP CDP PD PD_PPS` only | `charging-capabilities.md` |
| 50 W wireless + 30 W reverse | **Disproven as wireless** — `WIRELESS_MAX_POWER`/`REVERSE_MAX_POWER` in `SystemConfig.java` are ODM option-catalogue values; no receiver hardware exists. Real capability is **10 W wired** reverse | `wireless-charging.md` |
| 120 W wired | **Config-level PROVEN** (6 A at 20 V); delivered power unmeasured | `charging-capabilities.md` |
| GSMArena "4K@30, 1080p@30 ⇒ 4K30 ceiling" | **Reclassified** — that observation came from the GSI camera app, not stock; HAL publishes far more stream configs | `camera-stream-configurations.md` |
| BT "LE-ADP (Auracast/LE Audio)" | **Not supported by evidence** — the enabled `bap.*` props were GSI defaults and BT was never switched on; LE Audio stays UNKNOWN | `bluetooth.md` |
| 570 LED / 1000 lm, vapor chamber, FM radio, pogo connector | 570-LED/1000 lm stays an OEM auxiliary-light claim; **active cooling disproven** (no fan/pump/TEC node anywhere); **FM radio now positively proven fitted**; pogo/accessory path unchanged | `cooling.md`, `fm-radio-and-headset-jack.md` |
| GSMArena 1/1.31″ GN1 geometry | Superseded as a *this-unit* statement: it describes the Samsung population of the same slot | `camera-main-identity.md` |
