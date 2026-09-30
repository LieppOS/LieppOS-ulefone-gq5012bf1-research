> **Superseded in part (2026-09-08).** This file is first-pass working material. Where it disagrees with `../final/` or `../verification/findings/`, the verification pass wins.
>
> Two corrections apply to every subsystem file: (a) the 2026-08-31 capture was taken under a **LieppOS GSI**, so its framework-level observations are **not** stock Ulefone behaviour; and (b) `vendor/etc/init/hw/init.yft.rc` is a **platform-wide ODM option catalogue**, not this device's bill of materials.
>
> Thirteen previously unlisted parts - including the whole SPMI PMIC tier, CO5300, SC8510, the FM receiver and the 3.5 mm jack - are catalogued in `hidden-support-ics.md`, with datasheet ratings in `power-support-ics.md`.

# PCB support ICs and board topology

This file records **board-proven bindings** and separates them from exact electrical capability, which often needs a datasheet or package marking.

| Part / working identity | Address / bus | Role | Confidence |
|---|---|---|---|
| RT5133 | `5-0018` | SoC PMIC; large buck/LDO regulator tree | PROVEN |
| MT6375 | `5-0034` | charger/gauge/TCPC/PD ecosystem; Hall/audio support paths | PROVEN |
| RT6160(A) | `5-0075`, `6-0075` | always-on buck-boost rails (`vbif`, `vpp`, `vsrf1_ant`) | PROVEN binding / rail interpretation strong |
| SC8571 | `11-0066`, `6-0067` | direct-charge switched-capacitor master/slave | PROVEN binding |
| SC851x-class | `6-0069` | charge-pump companion/candidate | PROVEN binding, exact variant UNKNOWN |
| SH366003 | `9-0055` | third fuel gauge | PROVEN working name, die capability UNKNOWN |
| OCP2131 | `6-003e` | AMOLED bias/gate IC (`lcd_ocp2131`) | PROVEN |
| WL2864C | `11-0029` | display/camera rail LDO candidate | PROVEN binding, rail consumers UNKNOWN |
| AW88394 | `6-0034` | smart speaker PA | PROVEN exact die by chip ID |
| AW2013 | `11-0045` | RGB indicator LED sink | PROVEN |
| AW36515 / AW36518 variants | `6-0063`, `8-0063`, `12-0063` | flash/IR LED boost drivers | PROVEN |
| FM78100 / tiny2c_usb | `8-003c` | thermal-module tunnel/interface endpoint | PROVEN binding, exact silicon UNKNOWN |
| ST21NFC | `6-0008` | NFC controller | PROVEN family |
| ConnFem catalog | HWID GPIO 131/132/92 | RF FEM selection mux | PROVEN path; selected physical item UNKNOWN |
| Madev | `spi1.0` | fingerprint sensor | PROVEN transport |
| FT3680 | `spi3.0` | primary touch controller | PROVEN working driver identity |

The camera segment additionally contains four EEPROMs, three VCMs and one DW9781C OIS binding. The live bus evidence is preserved at `../evidence/local/buses-live.txt`.

## Unresolved support ICs

Public searches did not identify exact datasheets for RT5133, SC8571, SH366003, OCP2131, WL2864C, FM78100, CO5300 DDIC, VTDR6115, Hynitron or Madev die. Do not substitute a same-name part in a ROM without voltage/current/command compatibility testing.

Sources: S01–S03, S09–S11, S18–S22; merged DT and kernel phase4 contracts.
