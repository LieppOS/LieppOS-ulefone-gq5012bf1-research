# Existing canonical claim audit

| prior claim | old location | classification | correction/current result |
|---|---|---|---|
| GPIO28 LOW/HIGH = insert/remove; GPIO152/55 follow; HOST/NONE queued | `usmart-full-contract.md`, phase4 extcon contract | PROVEN | exact rebuilt source confirms |
| IRQ both edges, zero-delay work, probe-time sample | phase4 extcon contract | PROVEN, refined | IRQ is requested before boot sample; no debounce/retry |
| `yft_usb_flag` is checked at the head, before GPIO changes | phase4 extcon contract | STALE | GPIO152/55 and status change first; only role request is skipped |
| thermal removal under flag leaves uSmart GPIO/status stale | old full contract | STALE | removal still clears GPIO152/55/status; role alone remains HOST |
| SOURCE_VBUS/Type-C VBUS handling is suppressed by thermal flag | phase4 extcon contract | STALE | SOURCE_VBUS branch is not gated; ordinary role and psy work are gated |
| GPIO152 uSmart power is sourced by MT6375 `usb-otg-vbus` | full contract / SC851x report | SUPERSEDED/UNPROVEN | ID work never calls regulator APIs or GPIO37; only GPIO152 is proven. MT6375 boost is Type-C source power |
| GPIO55 is the thermal-camera route | older topology text | STALE | GPIO55 is uSmart route; thermal uses separate rails/mode controls |
| FM78100/thermal module and uSmart are one device | full contract topology/matrix | STALE | no FM78100 fitted; Tiny2-C and uSmart are distinct devices/control paths |
| YftSuperScreen writes `tiny2c_*` | full contract/userspace report | STALE | strings occur only in a bundled framework ActivityManager stub; own `com.yft.superscreen` code has no caller |
| M170infisens/M170infDlp are uSmart clients | full contract | STALE | they are internal thermal clients only |
| YftSystemUI reads uSmart status and knows endoscope package | software ledger | PROVEN, refined | exact `SystemUIService` checks status + any enumerated device and prompts if app missing; it does not launch/control hardware |
| FactoryMode supports an endoscope test | old high-level notes | PROVEN, expanded | `EndoscopeCustomTest` reads status and checks any USB device; `EndoscopeTest` launches the camera app |
| uSmartCamera is stock software | software ledger | PROVEN, refined | APK is a downloadable media resource, not installed under app/priv-app; no auto-installer reference found |
| uSmart is UVC only with no proprietary protocol | implied by naming | STALE/INCOMPLETE | app supports generic UVC and carries Sonix control transfers plus NS108x/U-Storage native paths |
| `uvc_insert_status` means successful UVC enumeration | name-based inference | STALE | it mirrors GPIO28 physical state and is set before role/enumeration |
| fixed accessory VID/PID/descriptors are known | old accessory matrix aspiration | UNKNOWN | no device capture; app filter list is expected support, not observed connector identity |
| independent live USB1 controller | old historical notes | STALE | one USB0/MTU3/U2 fabric; 11211000 path is dead |
| SC851x powers/controls uSmart or supports reverse charge | earlier hypothesis | SUPERSEDED | no software/DT edge; `reverse_charging_level` is a dead policy label |
| physical connector pin numbering and switch IC are known | old unknown list | UNKNOWN, NON-BLOCKING | software-visible signals are complete; board-only details remain |

No blocker remains for the observable hardware/software contract.
