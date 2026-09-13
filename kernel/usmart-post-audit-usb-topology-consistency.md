# uSmart post-audit USB-topology documentation consistency

## 1. Scope

Documentation-only synchronization removing stale current-state wording that
implied uSmart runs over a second "USB1" controller. No reverse engineering, no
source reconstruction, no module build, no Kbuild/BUILD.bazel/Makefile change,
no `Module.symvers` change, no DT/DTBO change, no phone interaction, no
`insmod`/`rmmod`, no sysfs writes, no GPIO/I2C access, no flashing, no reboot,
no slot change, no runtime uSmart testing.

Reconstruction statuses of every module are unchanged by this pass.

## 2. Files audited

Repo-wide searches were run for `USB1`, `usb1`, `11211000.usb1`,
`uSmart.*USB1`, `USB1.*uSmart`, `extcon.*USB1`, `USB1.*extcon`,
`SC851x.*uSmart`, `uSmart.*SC851x`. Every hit file was inspected with context:

- `kernel/phase4-remaining-module-dependency-graph.md`
- `kernel/phase4-remaining-module-triage.md`
- `kernel/module-replacement-plan.md`
- `kernel/unknown-exact-audit.md`
- `kernel/phase4-sc851x-reconstruction.md`
- `kernel/phase4-yft-tiny2c-usb-usmart-contract.md`
- `kernel/phase4-yft-tiny2c-usb-reconstruction.md`
- `kernel/phase4-yft-tiny2c-usb-usb-contract.md`
- `kernel/phase4-yft-tiny2c-usb-thermal-camera-contract.md`
- `kernel/phase4-yft-tiny2c-usb-hardware-contract.md`
- `kernel/usmart-full-contract.md`
- `kernel/usmart/usmart-software-evidence.md`
- `kernel/usmart/usmart-sc851x-power-path.md`
- `kernel/phase4-remaining-module-triage.tsv`
- `docs/hardware-map.md`
- `TODO/kernel-enhancement-roadmap.md`
- `TODO/battery-telemetry-tracker.md`
- `TODO_Usmart/todo_suggestions.md`
- `TODO_Usmart/walkie_talkie.md`
- `TODO_Usmart/meshtastic_todo_ideas.md`
- `qwen_hardware/qwen-thermal/search/sources.md`
- `slot-b-investigation/06-android-followup.txt` (raw)
- `evidence/boot-hang-2026-08-29/policy/**` CIL policy files (raw)

The dedicated uSmart audit (`kernel/usmart-full-contract.md`) already carried
the correct topology and was left unchanged.

## 3. Files changed

| file | nature of change |
|---|---|
| `kernel/phase4-remaining-module-dependency-graph.md` | uSmart VBUS/control graph rewritten to the shared-fabric form |
| `kernel/phase4-remaining-module-triage.md` | uSmart VBUS/control sentence rewritten |
| `kernel/module-replacement-plan.md` | uSmart mapping rewritten |
| `kernel/unknown-exact-audit.md` | uSmart control/VBUS mapping rewritten |
| `kernel/phase4-sc851x-reconstruction.md` | stock uSmart/UVC path sentence rewritten |
| `kernel/phase4-yft-tiny2c-usb-usmart-contract.md` | `SHARED_USB_PATH` row and direct uSmart chain diagram rewritten |
| `kernel/phase4-yft-tiny2c-usb-reconstruction.md` | two routing sentences rewritten |
| `kernel/phase4-yft-tiny2c-usb-usb-contract.md` | host-mode row rewritten |
| `kernel/phase4-yft-tiny2c-usb-thermal-camera-contract.md` | routing diagram line rewritten |
| `kernel/phase4-yft-tiny2c-usb-hardware-contract.md` | block diagram edge and questions 3 and 4 rewritten |
| `kernel/usmart/usmart-software-evidence.md` | one "UVC/USB1 host path" phrase corrected (raw `init.rc`/fstab quotes untouched) |
| `kernel/usmart/usmart-sc851x-power-path.md` | host-route graph line and one bullet now name the shared fabric and label `11211000.usb1` as the dead userspace path |
| `docs/hardware-map.md` | USB/uSmart row rewritten; legacy path explicitly marked as having no live DT controller |
| `TODO/kernel-enhancement-roadmap.md` | uSmart lead-in sentence and two state-machine lines rewritten |
| `TODO/battery-telemetry-tracker.md` | list item rewritten |
| `TODO_Usmart/todo_suggestions.md` | topology diagram line and one checklist item rewritten |
| `TODO_Usmart/walkie_talkie.md` | topology diagram line and one checklist item rewritten |
| `TODO_Usmart/meshtastic_todo_ideas.md` | eight routing references rewritten |
| `kernel/usmart-post-audit-usb-topology-consistency.md` | this audit (new) |

## 4. Stale current-state claims corrected

| file | before (stale) | after |
|---|---|---|
| dependency graph | `MT6375 OTG → extcon-mtk-usb → USB1/UVC GPIOs` | `MT6375 usb-otg-vbus → extcon-mtk-usb → shared USB0 / MTU3 / USB2 fabric → UVC switch / accessory-power GPIOs` |
| triage | "uSmart VBUS/control uses USB1 and MT6375 OTG" | MT6375 `usb-otg-vbus` + `extcon-mtk-usb` over the shared USB0 / MTU3 / USB2 fabric; no second controller |
| replacement plan | "maps to USB1/extcon and MT6375 `usb-otg-vbus`" | "maps to `extcon-mtk-usb`, MT6375 `usb-otg-vbus`, and the shared USB0 / MTU3 / USB2 fabric" |
| unknown-exact audit | "separately mapped to USB1/extcon and MT6375 `usb-otg-vbus`" | `extcon-mtk-usb`, MT6375 `usb-otg-vbus`, shared fabric |
| sc851x report | "implemented by `extcon-mtk-usb.ko`, USB1/xHCI, …" | `extcon-mtk-usb.ko` over the shared USB0 / MTU3 / USB2 PHY / xHCI fabric |
| tiny2c uSmart contract | "different UVC GPIO/USB1 controls"; `-> USB1/UVC switch/detect GPIO path ->` | shared-fabric wording in both the table row and the chain diagram |
| tiny2c reconstruction | "separate extcon/MT6375/USB1 path"; "MT6375 OTG -> extcon -> USB1/UVC GPIOs" | shared-fabric wording in both |
| tiny2c USB contract | "extcon/USB1 establishes the host route" | `extcon-mtk-usb` establishes the host route on the shared fabric |
| tiny2c thermal-camera contract | "extcon-mtk-usb / MT6375 / USB1 routing and VBUS" | routing over the shared USB0 / MTU3 / USB2 fabric |
| tiny2c hardware contract | "separate extcon/USB1 + MT6375 path"; "Shares USB1?" … "operates the board USB1 host/route"; "beyond the proven USB1/extcon route" | shared-fabric wording; question reworded to "Shares the board USB fabric?" with the explicit "not a second USB controller" statement |
| usmart software evidence | "consistent with the stock UVC/USB1 host path" | "stock UVC host path over the shared USB0 / MTU3 / USB2 fabric" |
| usmart SC851x power path | graph node "USB host controller: 11211000.usb1/11210000.xhci"; "the USB1 path is enumerated/mounted as `usbotg` host media" | shared-fabric host route, with the legacy node retained and labelled dead |
| `docs/hardware-map.md` | "accessory host path `11211000.usb1`/xHCI … VERIFIED stock control path" | shared USB0 / MTU3 / USB2 PHY / xHCI fabric routed by `extcon-mtk-usb`; legacy `11211000.usb1` marked as having no live DT controller |
| kernel-enhancement roadmap | "MT6375 OTG / USB1 path"; "USB1 PHY suspended"; "route USB1" | shared-fabric wording in all three |
| battery telemetry tracker | "uSmart/USB1" | "uSmart / shared USB0 fabric" |
| `TODO_Usmart/todo_suggestions.md` | "USB1 / UVC routing"; "Confirm USB1 controller mapping." | shared-fabric routing; "Confirm shared USB0 / MTU3 / xHCI fabric mapping (no second controller exists)." |
| `TODO_Usmart/walkie_talkie.md` | "USB1 / UVC routing"; "over the uSmart USB1 path" | shared-fabric wording in both |
| `TODO_Usmart/meshtastic_todo_ideas.md` | "→ USB1/UVC GPIO routing"; "USB1 enumerates the device"; "USB1 routing" (list, heading, diagram, two checklists, one summary) | shared USB0 / MTU3 / USB2 fabric wording throughout |

## 5. Historical / dead-path references intentionally retained

- `slot-b-investigation/06-android-followup.txt` — raw stock fstab line
  `/devices/platform/soc/11211000.usb1/11210000.xhci* … voldmanaged=usbotg:auto`
  (`RAW_EVIDENCE_DO_NOT_EDIT`).
- `kernel/usmart/usmart-software-evidence.md` — verbatim `init.yft.rc` chmod of
  `/sys/devices/platform/soc/11211000.usb1/mode` and the verbatim fstab block
  (`RAW_EVIDENCE_DO_NOT_EDIT`).
- `kernel/usmart-full-contract.md` — "The legacy `11211000.usb1` userspace path
  has no live DT controller", "independent USB1 controller → `NO_STOCK_SUPPORT`",
  "There is no live `11211000.usb1` …", "tries the dead USB1 path", "Do not add
  USB1, SC851x ownership or reverse-charge controls" (`CURRENT_VALID` /
  `DEAD_PATH_EVIDENCE`).
- `kernel/usmart/usmart-sc851x-power-path.md` — "no phandle edge between the
  SC8510 node and `extcon-usb`, USB1, MT6375 OTG …" (negative DT statement,
  `CURRENT_VALID`) and the retained-but-labelled dead `11211000.usb1` fstab
  reference (`DEAD_PATH_EVIDENCE`).
- `evidence/boot-hang-2026-08-29/policy/**` CIL files — stock `genfscon`
  entries naming `extcon-usb1` / `extcon_usb1` sysfs paths
  (`RAW_EVIDENCE_DO_NOT_EDIT`).

None of these describe uSmart as running on a live second USB controller.

## 6. Authoritative current uSmart USB topology

```text
uSmart
   ↓
extcon-mtk-usb
   ↓
shared USB0 / MTU3 / USB2 PHY / xHCI
```

```text
MT6375 usb-otg-vbus
   ↓
extcon-mtk-usb
   ↓
Type-C / source-power coordination
```

Control lines, kept distinct:

| line | role |
|---|---|
| GPIO 28 | accessory detect |
| GPIO 55 | UVC / USB path switch |
| GPIO 152 | accessory power / VBUS switch (accessory rail) |
| GPIO 37 | Type-C source-VBUS companion (separate from GPIO 152) |

GPIO 152 and GPIO 37 are **not** the same path: GPIO 152 is the uSmart
accessory power/VBUS switch, GPIO 37 is the Type-C source-VBUS companion in the
MT6375 `usb-otg-vbus` coordination path.

Thermal-camera auxiliary path (separate from uSmart control):

```text
yft_tiny2c_usb
   ├─ GPIO 149
   ├─ GPIO 191
   ├─ GPIO 192
   ├─ FM78100 @ I2C 0x3c, expected ID 0x4c59
   └─ writes yft_usb_flag
```

Preserved facts, unchanged by this pass:

- `extcon-mtk-usb` is the central uSmart accessory-detect / path-switch / role
  driver.
- MT6375 owns `usb-otg-vbus` and `yft_usb_flag`.
- `yft_tiny2c_usb` is thermal-camera rail and FM78100 ID glue only.
- One shared USB0 / MTU3 / xHCI / USB2 stack exists; `11211000.usb1` is not a
  live alternate controller.
- SC851x is **not** on the proven uSmart control/VBUS path.
- `reverse_charging_level` — `NO_STOCK_SUPPORT`.
- Physical connector pinout — still unknown.
- Whether the phone can charge through uSmart — **NOT PROVEN**.

No new electrical conclusions were introduced.

## 7. Grep results and classifications

Post-cleanup classification of every remaining match (`USB1|usb1|11211000.usb1`
and the uSmart/extcon/SC851x cross-forms):

| location | classification |
|---|---|
| `evidence/boot-hang-2026-08-29/policy/**` CIL `genfscon` `extcon-usb1` / `extcon_usb1` entries | `RAW_EVIDENCE_DO_NOT_EDIT` |
| `slot-b-investigation/06-android-followup.txt` stock fstab line | `RAW_EVIDENCE_DO_NOT_EDIT` |
| `kernel/usmart/usmart-software-evidence.md` verbatim `init.yft.rc` / fstab quotes | `RAW_EVIDENCE_DO_NOT_EDIT` |
| `kernel/usmart-full-contract.md` dead-path and `NO_STOCK_SUPPORT` statements | `CURRENT_VALID` / `DEAD_PATH_EVIDENCE` |
| `kernel/usmart/usmart-sc851x-power-path.md` labelled dead `11211000.usb1` fstab reference | `DEAD_PATH_EVIDENCE` |
| `kernel/usmart/usmart-sc851x-power-path.md` "no phandle edge … USB1 …" | `CURRENT_VALID` (negative statement) |
| `docs/hardware-map.md` legacy-path note | `DEAD_PATH_EVIDENCE` |
| every rewritten kernel/TODO/docs sentence listed in §4 | `CURRENT_VALID` |
| this audit's quoted "before" strings in §4 and §5 | `HISTORICAL_VALID` (quoted corrections, not status claims) |
| `qwen_hardware/qwen-thermal/search/sources.md` `workspace/phase4-sc851x/usmart/...` file paths | `FALSE_POSITIVE` |

Remaining current-state claims that uSmart uses USB1: none.
Remaining current-state claims that `11211000.usb1` is a live controller: none.

## 8. CURRENT_STALE count

`CURRENT_STALE = 0`

## 9. Consistency invariants

| # | invariant | result |
|---:|---|---|
| 1 | no CURRENT statement says uSmart uses USB1 | PASS |
| 2 | no CURRENT statement says `11211000.usb1` is live | PASS |
| 3 | current uSmart topology names the shared USB0 / MTU3 / USB2 fabric | PASS |
| 4 | `extcon-mtk-usb` remains the central uSmart USB control driver | PASS |
| 5 | MT6375 `usb-otg-vbus` remains the source-power regulator | PASS |
| 6 | GPIO 152 remains the accessory power path | PASS |
| 7 | GPIO 37 remains the Type-C source-VBUS companion | PASS |
| 8 | SC851x remains excluded from the proven uSmart path | PASS |
| 9 | useful historical/dead `11211000.usb1` references retained | PASS |
| 10 | no unsupported physical/electrical conclusions added | PASS |
| 11 | reconstruction statuses unchanged | PASS |
| 12 | no source/build files modified | PASS |

## 10. Final verdict

**USMART USB TOPOLOGY CONSISTENCY: PASS**
