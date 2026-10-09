# GPIO and EINT hardware contract

## Four different number spaces

1. MT6878 pin/descriptor number: physical0–195; virtual EINT-only196–215.
2. GPIO-controller-relative DT offset: phandle /soc/pinctrl, offset, flags. SoC gpiochip
   registers 216 descriptors with **dynamic base=-1**. gpio-ranges covers physical0–195.
3. Legacy Linux global GPIO = assigned chip base + offset. Existing consumers using
   `of_get_named_gpio` receive that translated global integer; do not replace it with an
   assumed hard-coded offset. No global-base capture exists in the inspected snapshot.
4. EINT global ID → **DT instance/local-index matrix**, then word/bit within that instance.
   These coordinates are not GPIO MMIO direction bits.

Physical EINT-capable descriptors: **117**; virtual descriptors:20. The stock DT matrix
configures exactly137 entries out of a total216 IRQ-domain IDs. Others are not supported
just because the IRQ domain allocated them. GPIO149/151/152/191/192 have
NO_EINT_SUPPORT; the thermal/uSmart power pins are outputs, not interrupt inputs.

## EINT topology — static DT = captured live DT

PIO `/soc/pinctrl` is both gpio-controller and interrupt-controller (two cells), with
`mediatek,eint` pointing to `/soc/apirq@11ce0000`. The latter uses compatible
`mediatek,mt6983-eint`, **not mt6878-eint**, and contains the matrix consumed by v2.
No separate EINT kernel module is created; it is part of pinctrl-mtk-v2.

| instance | name | MMIO | configured entries |
|---:|---|---|---:|
| 0 | eint-e | 0x11ce0000 | 58 |
| 1 | eint-s | 0x11de0000 | 47 |
| 2 | eint-w | 0x11e60000 | 12 |
| 3 | eint-c | 0x1c01e000 | 20 |

Parent IRQ: GIC SPI239, flags4 (DT includes fourth affinity cell0). Parent
interrupt-controller is resolved through DT ancestry; PMIC child IRQ domains are not
mistaken for SoC EINT. Generated EINT consumer index has10 declarations per operand;
MT6375 child ADC/charger/TCPC IRQ numbers are correctly excluded from this SoC domain.

| pin/EINT | instance | local index | debounce supported | board use |
|---:|---:|---:|---|---|
| 2 | 0 | 2 | yes | NFC IRQ |
| 3 | 0 | 3 | yes | fingerprint IRQ (other declared uses not simultaneously proven) |
| 6 | 1 | 0 | yes | touch reset pad (EINT capability only) |
| 7 | 1 | 1 | yes | main touch IRQ |
| 14 | 2 | 1 | yes | microSD card detect |
| 15 | 2 | 2 | yes | MT6375 parent IRQ |
| 28 | 0 | 15 | yes | uSmart ID |
| 41 | 1 | 7 | no | amplifier IRQ declaration |
| 55 | 0 | 31 | see matrix | uSmart route is output; IRQ capability does not imply use |

Register addressing: instance base + register-kind offset + 4*floor(local_index/32),
bit=local_index%32. Core register offsets (stock table): status0x000, ACK0x040,
mask0x080, mask-set0x0c0, mask-clear0x100, sensitivity0x140, software0x200,
polarity0x300, domain-enable0x400, debounce control/set/clear0x500/600/700,
raw-status0xa00. Set/clear aliases and debounce byte packing follow `mtk-eint.c`, not a
GPIO register formula.

## Driver behavior (stock-exact, not performed here)

* Probe reads matrix quadruples (ID, instance, index, debounce); maps all four resources,
  sets IRQ chip/chained handler and creates linear domain. Register-access helpers reject
  unconfigured/invalid IDs, but `mtk_eint_find_irq` checks only IRQ mapping existence; all216
  domain IDs are mapped. A returned virq does not prove supported hardware. Legacy mode
  exists but is not the board's matrix configuration.
* IRQ resources translate EINT to GPIO descriptor; real pads enter specified EINT mux,
  input direction and SMT. Virtual descriptors skip physical mode writes.
* Mask/unmask/ACK, type/polarity, dual-edge flip, debounce and wake flags are implemented.
* suspend_noirq masks non-wake lines; resume_noirq restores cur_mask, with dsb(sy).
  This is not a generic full pad register save/restore routine or automatic DT sleep-state selector.
* EINT init failure is warned and GPIO/pinctrl probe can continue. Noirq PM functions still
  pass hw->eint to EINT routines; successful pad registration alone is insufficient proof
  that IRQ/wakeup paths are safe. Preserve code, investigate during controlled testing.

## Register examples proving offsets ≠ bit indices

| GPIO offset | MODE phys / bit | DIR phys / bit | DO phys / bit |
|---:|---|---|---|
| 28 | 0x10005330 /16 | 0x10005000 /28 | 0x10005100 /28 |
| 55 | 0x10005360 /28 | 0x10005010 /23 | 0x10005110 /23 |
| 152 | 0x10005430 /0 | 0x10005040 /24 | 0x10005140 /24 |
| 149 | 0x10005420 /20 | 0x10005040 /21 | 0x10005140 /21 |
| 191 | 0x10005470 /28 | 0x10005050 /31 | 0x10005150 /31 |
| 192 | 0x10005480 /0 | 0x10005060 /0 | 0x10005160 /0 |

Mode0 is GPIO, selected by the stock GPIO request callback. GPIO55/149 mode nibble's
high bit participates in mask-write semantics, not an arbitrary 4-bit mux selector.

## MT6363 is a separate namespace

PMIC child `/soc/spmi@1cc04000/pmic@4/mt6363-pinctrl` uses parent SPMI regmap, not these
SoC MMIO banks or EINT. Stock pin descriptors are **1–9 plus dummy0xffffffff**;
npins/ngrps10 support one-based numbering but only9 physical pins are registered with
pinctrl. No board GPIO consumer reference to this provider was found in either DT.
88 field entries cover direction/data/mode, SMT, pull-enable/select, drive, slew and
AD-switch (only pins1–7 for the latter). Register lock/unlock writes0x39e/39f (0 / 0x9c).
It has no SoC-EINT callbacks or noirq PM table. Treat it as an enabled provider, not proof of
active ten-pin peripheral wiring.
