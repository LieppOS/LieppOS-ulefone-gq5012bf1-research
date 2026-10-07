# uSmart full contract — GQ5012BF1

**Effectively complete (offline static closure, 2026-10-07).** uSmart is the proprietary
physical expansion connector for Ulefone E01/E02/E03 endoscopes and C01 microscope. At
the phone side it is not a proprietary bus: it is an alternate connector for the single
USB2 host fabric, plus an active-low detect input and two board-control outputs.

```text
uSmart connector
  ID/detect ─────────→ GPIO28 (LOW inserted, both-edge IRQ)
  accessory power ←── GPIO152 HIGH
  USB D+/D− ─────────→ GPIO55-selected route ─→ usb2-phy0 ─→ MTU3 ─→ xHCI
  ground/power return → board-only wiring
```

Insertion is kernel-autonomous: power HIGH → route HIGH → `uvc_insert_status=1` →
queue HOST. Removal performs power LOW → route LOW → status 0 → queue NONE. There are
no delays, debounce, retries, accessory identification or enumeration feedback in this
state machine. GPIO152's exact source voltage/current and the connector pin numbering
are not visible statically.

| file | content |
|---|---|
| `STATUS.md` | closure criteria and residuals |
| `claim-audit.md` | old canonical claim classification |
| `hardware-contract.md` | connector-level contract and physical boundary |
| `gpio-contract.tsv` | exact GPIO28/55/152 behavior |
| `insertion-state-machine.md` | IRQ, boot, insert and remove ordering |
| `power-path.md` | accessory power vs MT6375 Type-C VBUS |
| `usb-routing.md` / `usb-role.md` | route and HOST/NONE ownership |
| `accessory-enumeration.md` | stock app filters, UVC and supported-device boundary |
| `userspace-clients.tsv` | genuine callers; false YftSuperScreen attribution removed |
| `userspace-control-interface.tsv` | complete uSmart sysfs ABI |
| `typec-interaction.md` / `thermal-interaction.md` | shared-fabric conflicts |
| `driver-ownership.md` | exact module/source ownership |
| `accessory-protocol.md` | standard USB vs optional proprietary app protocols; audio/video |
| `failure-semantics.md` | static failures and stale-state behavior |
| `stale-claims.md` | corrected prior claims |
| `lieppos-porting-contract.md` | minimum replacement contract |

Authoritative low-level sources are referenced, not rebuilt: exact
`extcon-mtk-usb.ko`/source and the already-DONE EXTERNAL-USB and
INTERNAL-THERMAL-USB integration reports.
