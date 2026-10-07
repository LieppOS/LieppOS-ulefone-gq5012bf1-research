# uSmart full contract — STATUS

**EFFECTIVELY COMPLETE (static, 2026-10-07).** No registered workspace component exists,
so this is canonical supporting research rather than a workspace status transition.

| criterion | result |
|---|---|
| physical function | proprietary mechanical expansion connector carrying USB2 D+/D−, switched accessory power and active-low ID; intended camera/endoscope family identified — CLOSED |
| GPIO contract | GPIO28 input/IRQ; GPIO55 route; GPIO152 accessory power; polarity/default/order/failures mapped — CLOSED |
| insertion/removal/boot | both-edge ONESHOT IRQ, zero-delay work, no debounce; exact insert/remove/probe state machine — CLOSED |
| power | GPIO152 is the only uSmart power control used on ID transitions; MT6375/GPIO37 path is Type-C-only; exact rail source/rating board-only — CLOSED boundary |
| route/role | GPIO55 HIGH uSmart, LOW external/default; unconditional HOST/NONE queue; shared xHCI path — CLOSED |
| enumeration | no fixed captured uSmart descriptor; stock app's class/VID:PID filters and usbfs/libusb ownership mapped — CLOSED software boundary |
| status ABI | `uvc_insert_status` is physical GPIO state only, not enumeration/UVC success; all genuine readers mapped — CLOSED |
| protocol | connector/kernel protocol is only detect/power/route/standard USB; stock app additionally carries generic UVC plus accessory-specific Sonix/NS108x/U-Storage protocols — CLOSED boundary |
| Type-C/thermal | route and role races, no uSmart gate, thermal gate ordering and recovery mapped — CLOSED |
| userspace | YftSystemUI, FactoryMode and downloadable uSmartCamera mapped; YftSuperScreen false attribution retracted — CLOSED |
| audio/video | USB camera input/local preview-recording; no display output or analog audio; generic USB Audio remains class-driver capability — CLOSED |
| LieppOS | minimum compatible and safer serialized contract specified — CLOSED |

Non-blocking unknowns: connector pin numbers/contact count; analog switch/load-switch
part numbers and PCB netlist; GPIO152 rail voltage/current/inrush; actual descriptors of
each E01/E02/E03/C01 revision; which optional proprietary camera path each uses. No
software-visible uSmart state remains unresolved.
