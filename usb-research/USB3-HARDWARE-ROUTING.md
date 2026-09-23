# Physical USB routing investigation

## Bottom line

`USB3_ELECTRICAL_IMPOSSIBILITY = UNKNOWN`.

Software and runtime evidence prove that stock uses only a USB2 High-Speed path. They do **not** prove the mainboard, interconnect, daughterboard or receptacle lacks dormant SuperSpeed copper.

The best public board image strongly supports a separate lower charging/USB daughterboard, but one top-side marketplace photograph cannot establish the lane netlist.

## Exact model/family material found

A replacement part is sold as **For Ulefone Armor 29 Pro Charging Port Board**, SKU `EDA006599748`. Its source photograph is frozen as:

- `evidence/EDA006599748-armor29pro-charging-board.jpg`;
- SHA-256 `6930efc7c12ce05f97e2f8ccfaefbc98fa3f2b7d5650b32b0f2d20aee5d1b420`;
- source and caveats in `USB-WEB-SOURCE-LEDGER.md`.

The visible board silkscreen is `BM65_SUB_V1.2`. Visible features include:

- a USB-C receptacle at the left edge;
- a dense, dual-row board-to-board connector near the lower-right edge;
- an RF/coax test or antenna connector;
- a large central mechanical/socket assembly;
- several small protection/power/passive packages near the USB-C receptacle;
- no clearly identifiable, marked SuperSpeed redriver/retimer in the photographed top side.

This is **STRONGLY_SUPPORTED** to be the Armor 29 Pro lower sub-board and strongly supports a separable connector board. It is not yet proven to be the exact PCB revision installed in this specific Thermal unit.

## What the image does and does not show

### Supported

- The Type-C receptacle is not necessarily soldered directly to the mainboard; a replaceable sub-board exists for this model family.
- A multi-contact board interconnect is available to carry power, USB2, microphone/antenna and other signals.
- High-power charging components can be split between this sub-board, mainboard and separate charger paths.

### Not determinable

- exact board-to-board connector pin count: the oblique/resampled marketplace image is insufficient for a reliable count;
- whether receptacle contacts A2/A3/A10/A11 and B2/B3/B10/B11 are populated;
- whether any SS TX/RX differential pairs leave the receptacle;
- whether traces continue through inner layers or the unseen underside;
- whether the board connector allocates pins to SS pairs;
- whether a redriver/retimer/mux sits on the unseen side or mainboard;
- whether the thermal and non-thermal variants use the same daughterboard revision.

No clear matched 5-Gbit/s differential pairs can be followed continuously in the public top-side photograph. That is an **UNKNOWN**, not an absence finding: black solder mask, image resolution and inner-layer routing hide nets.

## FCC material

FCC ID `2AOWK-5012` covers Shenzhen Gotron model 5012 / the GQ5012 family. Filing index sources list a 12-page internal-photo exhibit, attachment `8392091`, dated June 2025. Direct retrieval was blocked by anti-bot/security checks in this session, so no unviewed FCC photo is treated as evidence.

Obtaining and archiving this exhibit is a high-priority next step. It may show:

- both sides of the mainboard and sub-board;
- board-to-board flex/connector routing;
- shield-can placement;
- Type-C connector footprint and protection arrays;
- board revision markings.

Even FCC photos may be insufficient to resolve inner-layer differential pairs without X-ray or continuity testing.

## Hardware-specific questions

| Question | Current status | Reason |
|---|---|---|
| Type-C connector on separate daughterboard? | `STRONGLY_SUPPORTED` | exact-model replacement sub-board listing/photo |
| Mainboard-to-daughterboard interconnect exists? | `STRONGLY_SUPPORTED` | visible dense board connector |
| Exact connector pin count? | `UNKNOWN` | image not reliable enough for counting |
| Receptacle is 24-contact/full-featured? | `UNKNOWN` | contact tail/underside not visible |
| SS pairs leave receptacle? | `UNKNOWN` | no schematic/continuity/X-ray |
| SS pairs cross interconnect? | `UNKNOWN` | no pinout/trace proof |
| SS pairs reach an SoC U3 PHY? | `UNKNOWN`, strongly disfavored | no production U3 PHY in MT6878 source/DT |
| Physical SS mux/redriver exists? | `UNKNOWN`, no positive evidence | no identifiable part in visible photo/DT/module imports |
| USB2 D+/D− reaches Type-C port? | `PROVEN operationally` | external gadget enumerates at 480 Mbit/s |
| Same USB2 fabric reaches thermal camera? | `PROVEN operationally` | direct `11200000.xhci0` port-1 enumeration |

## Decisive physical experiment

Use a sacrificial/spare `BM65_SUB_V1.2` board or perform a service teardown only if loss of IP68/IP69K sealing is accepted.

1. Photograph both PCB sides orthogonally under a microscope before removing shields.
2. Record all board, connector and IC markings.
3. Count receptacle and board-connector contacts directly, not from the marketplace image.
4. With battery and all power disconnected, continuity-map USB-C:
   - USB2: A6/B6 (`D+`) and A7/B7 (`D−`);
   - SS RX: A10/A11 and B10/B11;
   - SS TX: A2/A3 and B2/B3;
   - CC1/CC2: A5/B5;
   - SBU1/SBU2: A8/B8.
5. Follow every candidate SS pair through ESD arrays, muxes and the board interconnect.
6. Repeat on the mainboard side toward the SoC/package or an identifiable PHY/mux.
7. If inner layers prevent continuity localization, use board X-ray or destructive layer imaging on a spare.
8. Identify whether GPIO 55 controls a USB2-only analog switch and whether GPIO 152 is solely load-switch/VBUS control.

Use resistance/continuity only on an unpowered isolated board. Do not inject voltage into CC, data, PMIC, calibration or battery nets.

## Non-destructive corroborating experiment

With stock software and a known-certified USB 3.x host/cable:

1. capture orientation A and flipped orientation B;
2. record host `lsusb -t`, USB descriptors and UDC `current_speed`/`maximum_speed`;
3. repeat with a validated SuperSpeed peripheral in OTG host mode;
4. record whether an SS companion root hub ever appears.

Expected result from current DT is High-Speed in both orientations. A negative result corroborates stock behavior but still cannot distinguish omitted software enablement from absent copper.

## Repair/warranty caution

Ulefone lists IP68/IP69K and a non-removable 21,200-mAh battery. Opening the phone can compromise seals and may damage the device. Physical inspection should use a spare daughterboard or professional service tooling whenever possible.
