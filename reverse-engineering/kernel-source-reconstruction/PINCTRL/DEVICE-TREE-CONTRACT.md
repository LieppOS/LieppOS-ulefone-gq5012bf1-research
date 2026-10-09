# Stock DT → pinctrl/GPIO/EINT → consumer contract

## Operands and provenance

* Static stock merged DTB/DTBO: `workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dtb`,
  SHA256 `7ce69ab5bb4f9714446a262966d0478409a7e00a70c8f6d781461f9abb301104`.
* Existing read-only capture (not acquired in this task):
  `workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649/devicetree.tar`,
  SHA256 `c30d118138ea8df045a245b21afc888408b89ea090f6781f97c8b815211c595d`.
* `scripts/map-contract.py` parses binary FDT directly and captured DT filesystem separately;
  source table/field identities come from the fully stock-accepted pinned source.

Generated indexes preserve paths, property names, exact cells, function validity,
electrical settings, effective ancestor availability and references. `CONTROLLERS.json`
preserves every property of the two providers and EINT node, including inherited topology
in the full original operands. Effective okay does **not** mean fitted/probed/selected.
Unknown and unused alternatives are not silently removed.

## Provider registration

| Provider | Availability | Driver | Contract |
|---|---|---|---|
| /soc/pinctrl | implicit okay in both DTs | pinctrl-mt6878 → pinctrl-mtk-v2 | ten ordered MMIO banks, GPIO 2 cells, GPIO range0–195; IRQ 2 cells; EINT phandle |
| /soc/apirq@11ce0000 | implicit okay in both | v2 EINT code, not separate module | four instances, GIC parent IRQ SPI239,216 IDs/137 configured matrix entries |
| /soc/spmi@1cc04000/pmic@4/mt6363-pinctrl | implicit okay in both | pinctrl-mt6363 → v2 MT63xx backend | parent dev_get_regmap; one-based PMIC GPIO1–9; no SoC EINT |

MT6878 probe maps `reg` by **numeric order** (reg-names document it, not an arbitrary name
lookup), gets match data, creates one group per pin, registers/enables pinctrl, then EINT,
then gpiochip. EINT failure is nonfatal to probe; GPIO registration failure is fatal.
Pin function validity is checked against the stock descriptor list. GPIO request selects
mode0; direction output sets data before direction, with the SoC's race-free register path.

MT6363 obtains parent SPMI regmap, builds groups, excludes dummy from the physical pinctrl
registration, enables pinctrl, then adds gpiochip. No clock_get/regulator_get call or
clock/regulator property directly belongs to either pinctrl provider. SoC MMIO/EINT depend
on the platform/GIC; PMIC pinctrl depends on the parent SPMI/MFD/regmap probe. Indirect
parent bus clocks and PMIC power are separate owners, not certified by compiling pinctrl.

## State/consumer index

159 pinmux entries and124 references per operand. Standard **default** references:
`/yft_finger`, `/yft_camplight`, `/gpio-keys`, MSDC0 and MSDC1. Several default state nodes
are empty; their existence is not a pad initialization transaction. Remaining named states
include fingerprint reset/SPI/bias; camera reset/PDN/MCLK/OIS; audio interface on/off; and
multiple connfem variants. There are **no referenced states literally named sleep or idle**
for these providers in either operand. Driver noirq PM programs EINT masks, not generic pad
register retention or selection of an invented sleep state.

The static MSDC0 node is okay; bootloader disables it in the live DT (already documented
by STORAGE). Its184–195 mode1 MSDC0 declarations remain in the DT, but cannot be called
active runtime eMMC. GPIO191/192 thermal use and possible FEM state alternatives must be
considered independently. No controller status was altered by this task.

## Boot-critical consumer examples

* MSDC1 default and state_uhs both choose77–82 mode1. CMD/DAT pull-up code101 (0x65), CLK
  pull-down code102 (0x66), raw drive3; input-enable on CMD/DAT. These are encoded
  PUPD/R1/R0 controls, not a resistance in ohms or current in mA. CD GPIO14 flags0
  maps to configured EINT instance2/local1. Host IRQ itself goes to GIC, not EINT14.
* UFS host/M-PHY has no pinctrl state reference. Its clocks/regulators/PHY, already source
  documented in STORAGE and BOOT-CLOCK-CORE, remain unchanged. Presence of
  `UFS_MPHY_SCL/SDA` alternate functions on pins192/193 does not activate them.
* MT6375 parent interrupt uses SoC EINT15; its charger/TCPC children use the PMIC IRQ
  domain, not EINT numbers copied from their child `interrupts` cells.
* Debug `gpio_dump_regs_range` is a hard symbol dependency of certified `mtk-mmc`, as well
  as I2C; GPIO/EINT runtime binding remains a separate DT dependency from symbol resolution.

## Cross-subsystem guardrails

All48 GPIO specifiers per operand resolve to `/soc/pinctrl` (none to MT6363). The generator
explicitly handles the ODM underscore-named uSmart and thermal GPIO properties, using the
provider #gpio-cells; it does not treat numeric words as raw global GPIO IDs. All10 direct
SoC EINT consumer declarations are indexed separately from PMIC child interrupts.
Physical board nets, selected touch/FEM/camera variant, global GPIO base, actual electrical
state and pad voltage are UNKNOWN unless established in existing consumer research.
`PINMUX-MAPPING.md` cross-references those facts and lists potential overlap, not fabricated
simultaneous conflicts. No device-tree binding/source file or completed consumer was edited.
