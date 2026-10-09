# MT6878 pinmux and board mapping

## Evidence classes

* **PROVEN BOARD CONNECTION**: existing stock-consumer reconstruction plus DT and the
  already documented device path. This proves the software-to-board control contract;
  package-ball numbering, switch part numbers and PCB netlist remain UNKNOWN without schematics.
* **ENABLED DT CONFIGURATION**: a stock static/live declaration under available nodes;
  it does not prove that a state was selected or that every donor device is fitted.
* **DRIVER IMPLEMENTATION**: stock-exact source tables/logic, not active board use.
* **POSSIBLE BUT UNVERIFIED**: alternate functions, competing state declarations, unselected
  FEM/camera/touch alternatives or unsupported runtime assumptions.
* **UNKNOWN**: unobserved actual mode, voltage/current, physical net or global GPIO base.

Generated authoritative indexes (`evidence/hardware/`, generator `scripts/map-contract.py`):
`PIN-FUNCTIONS.tsv` (196 physical pins, 20 virtual interrupt descriptors),
`REGISTER-FIELDS.tsv`, `PULL-TYPES.tsv`, `MT6363-REGISTER-FIELDS.tsv`,
`DT-PIN-STATES.tsv`, `DT-CONSUMERS.tsv`, `DT-GPIO-REFERENCES.tsv`, `EINT-MATRIX.tsv`.
All 159 pinmux declarations per static/live operand decode to supported stock functions.
Those entries are preserved even if unreferenced. Pinmux word encoding is pin<<8 | mode;
**it is not a register index, Linux global GPIO or EINT instance coordinate**.

## Register mapping (DRIVER IMPLEMENTATION; DT base order matches)

| bank index | name | physical base |
|---:|---|---|
| 0 | gpio | 0x10005000 |
| 1 | iocfg_bl | 0x11d10000 |
| 2 | iocfg_bm | 0x11d30000 |
| 3 | iocfg_br | 0x11d40000 |
| 4 | iocfg_bl1 | 0x11d50000 |
| 5 | iocfg_br1 | 0x11d60000 |
| 6 | iocfg_lm | 0x11e20000 |
| 7 | iocfg_lt | 0x11e30000 |
| 8 | iocfg_rm | 0x11eb0000 |
| 9 | iocfg_rt | 0x11ec0000 |

For a field range, bits = s_bit + (pin-s_pin)*x_bits (or s_bit for a shared/fixed
PINS_FIELD_BASE). Offset = s_addr + x_addrs*floor(bits/32); bit = bits%32.
The source handles fields crossing a word and rejects absent/out-of-range fields.
The complete 2108-row ledger includes bank, physical register, width/mask, shared-field and
cross-word information. Shared electrical fields must not be treated as independent pins.
Race-free direction/data writes use SET +4 / CLR +8; mode uses +0xc mask-write with
modification-enable bit. The GPIO mode nibble's fourth bit is not another supported mux.

**Stock quirk:** MT6878 SR deliberately aliases the DIR table. Paris's `slew-rate` handler
writes SR; hence this property changes the same field as GPIO direction. It is not proof of
a separate calibrated slew-control register. Preserve the stock config rather than silently
interpreting it as a generic slew-rate tuning knob.

Pull types: 98 pins use PU/PD mask1; 52 use PUPD/R1/R0 mask4; 46 use PU/PD + RSEL mask9.
MT6878 has FLAG_DRIVE_SET_RAW: DT drive-strength values are **raw field codes**, not proven
mA. EH and advanced-drive behavior only applies to the populated EH pin/mux list.
IES/SMT, pull and drive tables are indexed separately and may reside in IOCFG banks.

## GQ5012BF1 cross-reference

| Interface | Exact pins/modes or GPIO offsets | Evidence / class |
|---|---|---|
| microSD MSDC1 | 77 CLK, 78 CMD, 79–82 DAT0–3, mode1; CD14 mode0/EINT14 | stock/live DT + already-certified storage host: PROVEN BOARD CONNECTION for host/CD path |
| UFS | no UFS-host pinctrl state reference | dedicated host/PHY resources, not GPIO-mode pads; DRIVER IMPLEMENTATION alternate `UFS_MPHY_SCL/SDA` on 192/193 mode4 is not board activation |
| uSmart | ID28, route55, power152, mode0 when requested as GPIO | `/extcon-usb` specifiers + exact `extcon-mtk-usb.c`, `kernel/usmart/`: PROVEN BOARD CONNECTION (software role/control, not rail rating) |
| Type-C | OTG companion37; MT6375 IRQ15; extcon ID28 | extcon/MT6375 existing reconstruction + DT; separate from uSmart power: PROVEN BOARD CONNECTION software contract |
| Tiny2-C thermal USB | 149 VDDIO, 191 3v3, 192 1v8, GPIO mode0 | `/yft_tiny2c_usb` + existing exact thermal companion; PROVEN BOARD CONNECTION controls; physical voltage depends on board switches, not pinctrl drv code |
| NFC ST21 | reset40, IRQ2, clock-request151 | DT declares these GPIO offsets, source tables permit mode0; ENABLED DT CONFIGURATION, see existing NFC closure for consumer behavior |
| fingerprint | reset30, EINT3; SPI pins60–63 mode2 (`SPI1_CLK/CSB/MO/MI`) and mode0 alternatives | DT + exact fingerprint contract: PROVEN BOARD CONNECTION software mapping; state names say spi0 but actual mux function is SPI1 |
| touch | main FocalTech reset6/IRQ7; alternative Ilitek/Chipone 6/7, Hynitron32/11 with power119 | ENABLED DT CONFIGURATION; not proof all touchscreen variants are fitted |
| normal camera | sensor0 reset26/PDN22/OIS121/MCLK94 mode1; sensor1 reset24/PDN122/MCLK93; sensor2 reset27/PDN120/MCLK95; sensor4 reset189/PDN3/OIS23/MCLK93 | ENABLED DT CONFIGURATION; sensor index/name is not proof of fitted sensor identity; existing camera sensor/HAL research remains authoritative |
| audio | 164 AUD_CLK_MOSI,166 AUD_DAT_MOSI0,170/171 MISO/VOW; DMIC2/3,27/28; I2S42–45 | driver/DT states, ENABLED DT CONFIGURATION; not all simultaneously selected |
| connectivity/FEM | candidate ANT_SEL muxes on33–43 and189–192, multiple `/connfem` named states | ENABLED DT CONFIGURATION; selected FEM depends on existing connfem selection evidence, not all declarations |
| GNSS | GPS-related functions in full pin table | DRIVER IMPLEMENTATION / POSSIBLE BUT UNVERIFIED external pad use; do not infer routing from function names |

Fingerprint `kernel/phase4-fingerprint-pinctrl-contract.md` retains exact lookup order and
setter error behavior. uSmart: `kernel/usmart/{driver-ownership,power-path,thermal-interaction}.md`.
Thermal: `reverse-engineering/thermal-camera/internal-usb/{hardware-path,power-sequence}.md`.
Storage: completed STORAGE DT contract. Camera: existing `reverse-engineering/camera-stack/`.
These completed components were neither rewritten nor promoted.

## Overlap risks (not proven active conflicts)

DT offers alternatives on physical lines: GPIO3 fingerprint/DMIC/camera sensor4 PDN;
GPIO28 uSmart ID/audio DMIC; GPIO37 OTG/FEM; GPIO40 NFC reset/FEM; GPIO191/192 thermal
controls/FEM/MSDC0 alternatives. Source pinctrl has one pin per group; mux availability
is not simultaneous ownership. GKI pinctrl handles state/mux owners, but Paris pmxops does
not set `.strict`; do not assume GPIO request excludes mux use. Legacy consumer drivers
can bypass a clean arbitration model. No runtime mode/owner snapshot was acquired here.
