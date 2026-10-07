# AC020-UVC — STATUS (2026-10-07)

**DONE (static).** Scope: USB identity, descriptor tree, UVC capabilities, wire frame
format, kernel binding, userspace transport path, standard/XU/vendor control protocol,
endpoint roles, stream start/stop, firmware and calibration boundaries, relation to
FM78100-COMPANION and the internal USB role path. Proprietary radiometry/image algorithms
and module firmware internals are out of scope (THERMOVUE-T2).

| DONE criterion | result |
|---|---|
| identity | AC020 = InfiRay SDK family name; module Tiny2-C (TC2-C) 256×192; no bridge — PROVEN |
| VID/PID / interface topology | 3474:4321 bcdDevice 2.00, EF/02/01, 1 config (0xDF), IAD; if0 VC + EP 0x83 int 64 B/4 ms; if1 VS alt0/alt1 + EP 0x81 iso 1024 B — PROVEN (firmware descriptors + capture) |
| UVC descriptors / formats | UVC 1.10; IT/PU without controls; no XU; YUY2 16 bpp, 256×194 and 256×386 @25 Hz — PROVEN |
| frame transport | 256×386 negotiated by stock; 98 304 B image + 1 024 B info + 98 304 B u16-LE temperature — PROVEN (layout); temperature semantics proprietary |
| kernel binding | GKI built-in uvcvideo binds; apps detach and use usbfs; no custom driver (parity N/A) — PROVEN |
| userspace path | M170infisens → libAC020sdk (DriverType 5) → libusbuvccamera020 (stream) + iruvc_usb_* (control) + libircmd020 (commands) — PROVEN |
| standard controls / XU | none / none — PROVEN |
| vendor protocol | EP0 0x41/0x20, 0xC1/0x22, 0xC1/0x21, wValue/wIndex 0; frame header layout; 224-entry command header table with stock callers — PROVEN |
| endpoints | EP0 CONTROL (UVC + vendor); 0x83 CONTROL (UVC status interrupt, libuvc); 0x81 VIDEO (+ in-band metadata/temperature) — PROVEN |
| firmware boundary | module boots from flash; update only by explicit SDK upgrade (vdcmd + DFU); images recorded by hash — PROVEN; ROM-mode USB identity UNKNOWN (update path only) |
| calibration boundary | module flash files read/written over vdcmd `adv_cfg_file_*`; app assets generic — PROVEN (ownership/transport) |
| FM78100 / USB role | same ASIC's I2C ID port, boot-only; power `yft_tiny2c_usb`, role `tiny2c_mode`; GPIO 55/152 not involved — PROVEN (closed components) |

Residual, non-blocking:

- running firmware version of this unit not read live (identity fields equal 00.00.04.07);
- FactoryMode `InfirayEcoTest` asks for 256×384, which 04.07 does not advertise (static
  failure −51) — vendor test-app residue, not transport;
- per-command parameter meanings beyond vendor symbol names; info-line bytes not consumed
  by stock;
- radiometry and image algorithms (proprietary).

## Workspace

Moved `Reverse Engineer - PARTIAL/AC020-UVC` → `Reverse Engineer - DONE/` on 2026-10-07
(index totals 77/53/3 → 78/52/3). Earlier notes/source kept; closure files copied with
provenance (28 manifest rows); README, EVIDENCE-INDEX, PROVENANCE regenerated;
`notes/CLASSIFICATION-CHANGE.md` added. No other pack linked to the PARTIAL path.
manifest-audit: 3949/3949 rows resolve, trees 78/52/3, no drift in AC020-UVC
(pre-existing drift in 5 unrelated packs and 495 unregistered files unchanged).
`scripts/reproduce.sh` resolves stock paths relative to this research tree.

## Notes for other components (not edited)

- FM78100-COMPANION `firmware-boundary.md` cites `sys_reset_to_rom 0x0805` (donor value);
  AC020 value is frame 0x01 / module 0x01 / sub 0x42 (`stale-claims.md` #6).
- `qwen_hardware/qwen-thermal/re/protocol/vdcmd-uvc-transport.md` describes the unreachable
  donor framing (`stale-claims.md` #1–#2).
