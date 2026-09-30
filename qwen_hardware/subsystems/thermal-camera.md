> **Superseded in part (2026-09-08).** This file is first-pass working material. Where it disagrees with `../final/` or `../verification/findings/`, the verification pass wins.
>
> Two corrections apply to every subsystem file: (a) the 2026-08-31 capture was taken under a **LieppOS GSI**, so its framework-level observations are **not** stock Ulefone behaviour; and (b) `vendor/etc/init/hw/init.yft.rc` is a **platform-wide ODM option catalogue**, not this device's bill of materials.
>
> The core is an **InfiRay/InfiSense Mini640-class module with an AC020 ASIC**, and the `fm78100` node is only its power/ID endpoint. See `thermal-detector.md` and `fm78100-role.md`.

# Thermal-imaging camera (FLIR-class LWIR core) — unique hardware

## Hardware found — PROVEN
| Item | Value | Evidence |
|---|---|---|
| In-phone interface IC | DT node **`fm78100`**, compatible **`mediatek,tiny2c_usb`**, bound by `yft_tiny2c_usb` / `tiny2c_usb-sensor`, address **`8-003c`** | live `buses.txt`; `kernel/phase4-yft-devinfo-*` |
| Module endpoints | `miko_src_sensor@0` (sensor pipe) and `miko_mcu@0` (module MCU), FM128-style transport, I2C slave `0x3c` | merged FDT + `yft_*` DLKMs |
| Resolution / rate (claim) | **640 × 512 @ 25 Hz**; "super-resolution" **1280 × 1024 @ 3 fps** | OEM spec sheet S04 |
| Module naming (claim) | "M170 / M170L2" | OEM marketing text S04 |
| Shutter/FFC | shutter-capable core class (analogue parts expose FFC shutter) | S21 analogue — UNKNOWN for this unit |

## Chip capabilities — PARTLY UNKNOWN (no public datasheet for FM78100 / M170)
Comparable 640×512/12 µm LWIR VOx modules (InfiRay M3640T / T2-class "customized 12 µm thermal imaging chip", Contrastech/GST 640×512 25 Hz radiometric cores):

| Property | Analogue class |
|---|---|
| Format | 640×512 LWIR, 12 µm pixel, ~50° lens; 25 Hz (some 50 Hz) |
| Sensitivity | NETD ≤40–50 mK |
| Radiometry | optional −20 … +550 °C measurement mode |
| Flat-field correction | mechanical shutter (FFC) or shutterless |
| Transport | USB/UVC or MIPI + I2C control MCU |
| Extras | palette/AGC/EE/DDE in module DSP, temperature alarm triggers |

## Board configuration (layer 2)
* Thermal core is **not** on the MTK sensor pipe: it is reachable through a dedicated `tiny2c_usb` (I2C-over-USB-tunnel class) endpoint on adapter 8 plus a module MCU ⇒ the core is an autonomous camera module with its own DSP, controlled by `miko_*` vendor nodes.
* Vendor natives include AC020 (USB accessory camera), UVC, and "IR camera / IR command" services ⇒ the module can be addressed either as a UVC/AC020 camera or via the vendor command channel.
* The rear mini-display stack (**1.04-inch, 340x340, Chipone CO5300**; `hyn_ts` single-touch on `0-0015`) is driven by the same vendor `yft_*` family, i.e. one supplier provides the thermal and auxiliary-display plumbing.

## Stock usage (layer 3)
* Stock ships the thermal pipeline as OEM app + vendor services; standard Android camera HAL exposes **4** logical cameras (all silicon CIS) — the thermal core is **not** a fifth `ICameraDevice`, so third-party camera apps never see it.
* The `miko_src_sensor@0` / `miko_mcu@0` nodes and `st21nfc`-style firmware blobs for the mini LCD (`lcd_fw.img`) confirm both auxiliary peripherals are handled outside the standard camera framework.

## Unused / hidden capabilities
1. **Radiometric temperature measurement** (analogue class −20…550 °C) — never exposed to any system API; only in the OEM thermal app.
2. **Shutter/FFC control** and module-side AGC/palette/DDE/EE parameters — accessible only through the private `miko`/`yft` command channel.
3. **Third-party visibility**: because there is no camera-HAL level enumeration, the thermal core could be surfaced as an additional camera device (AC020/UVC path exists in stock natives) — nothing in stock does this for external apps.
4. **1280×1024 super-resolution mode @3 fps** — a module resolution beyond native 640×512 that stock only uses inside its own app.
5. The 4 IR LEDs (night-vision illumination, `misc-hardware.md`) are the same illumination family the thermal module is paired with in marketing; nothing links IR-LED drive to thermal capture in stock.

## Missing information / next verification (needs root or vendor protocol RE)
* FM78100 identity: is it a shutter/motor ASIC, an I2C mux/tunnel bridge, or the module's link PHY? → read `yft_tiny2c_usb` driver strings + module ID reads with root.
* M170/M170L2 core vendor (InfiRay/Micram/IRay-class) and whether it is radiometric: query module registers over `0x3c`, or open the module connector (destructive).
* Actual NETD, spectral band (8–14 µm), lens focal length/FOV: no measurement possible from ADB ⇒ UNKNOWN.
* Whether the mini rear display can mirror thermal preview without the OEM app (`tiny_lcd_miscdev` ABI).
