# U14 - rear sub-display panel and driver IC

**Current claim:** "Rear 3.97-inch AMOLED/mini-display, OEM 600-nit claim; Hynitron `hyn_ts` at `0-0015`; exact panel/DDIC UNKNOWN."

**Previous confidence:** UNKNOWN, and the size figure was wrong.

**New evidence**
* **The driver name identifies the DDIC.** `spi0.0` binds to `/sys/bus/spi/drivers/spi_tiny_lcd_co5300`, module `spi_tiny_co5300_lcd` (also shipped as `vendor_dlkm/lib/modules/spi_tiny_co5300_lcd.ko`). The DT node is `soc/spi0@11010000/tiny_lcd`, `compatible = "hxytech, spi_tiny_lcd"` - "hxytech" being the module house, `co5300` the controller.
* **Panel interface**: SPI0 at `spi-max-frequency = 60000000` (60 MHz), with `tiny_lcd,dc-ctrl-gpio`, `reset-gpio`, `te_gpio`, `en-1v8-gpio`, `en-2v8-gpio`, and an ADC channel `tiny_lcd_adc`. A 60 MHz QSPI-class link with a D/C line and a tearing-effect input is the classic small-AMOLED-with-RAM topology.
* **Digitizer geometry pins the panel size**: `hynitron@15` declares `display-coords = <340 340>` and `max-touch-number = <1>`.
* **The OEM specification matches exactly**: GSMArena lists "Secondary display on the back: **AMOLED, 1.04 inches, 340 x 340 pixels, 600 nits (peak)**", and Ulefone's own pages advertise a "1.04-inch Rear Sub-Display".
* **CO5300 is a Chipone single-chip LTPS AMOLED driver** with embedded RAM, gate drivers and timing controller, used for small round/square smartwatch-class panels (e.g. 1.43-inch 466x466 over MIPI-DSI/QSPI).
* The rear panel is **not** an Android display: `dumpsys display` enumerates only display 0 (1080x2400). It is driven privately by the vendor stack, with `/sys/class/second_lcm/yft_set_backlight` and `/sys/class/second_gesture_tp/{yft_gesture_status, yft_extlcm_aod_status}` in the ODM init script.
* A second, unused main-panel option also exists: `soc/dsi0@1401a000/panel2@1`, `compatible = "jdi,nt36672e,vdo,60hz"` - a JDI panel with a Novatek NT36672E DDIC, i.e. an alternative LCD main display for another variant. The fitted main panel is `yft_vtdr6115_fhdp_dsi_cmd_hx_dphy_667_ky_lcm_drv` (from `/chosen/bootargs` and `atag,videolfb`).

**Contradicting evidence**
The original audit's "3.97-inch" figure is contradicted by both the digitizer geometry (340x340) and the OEM specification (1.04 inch). It appears to have been imported from a different Ulefone model.

**Internet sources:** VI5 (1.04", 340x340, 600 nits), VI3 (1.04" rear sub-display), VI16/VI17 (CO5300 identity and class).

**Local evidence:** VL13, VL15, VL1.

**Read-only live evidence:** `buses.txt` driver bindings and `displays.txt` (only one Android display) from the frozen capture.

**Final conclusion**
The rear sub-display is a **1.04-inch, 340 x 340 AMOLED, 600 nits peak, driven by a Chipone CO5300 single-chip AMOLED driver over SPI0 at 60 MHz**, with a **Hynitron single-touch digitizer** at i2c `0-0015`, exposed only through vendor sysfs (backlight, gesture, AOD status) and never as an Android display. The main panel remains the **VTDR6115-class FHD+ AMOLED command-mode panel**, with a JDI/NT36672E LCD alternative present in the device tree but unused.

**Final confidence:** DDIC = Chipone CO5300 - **PROVEN** (driver + module name binding). Panel size/resolution/brightness - **PROVEN** (digitizer geometry + OEM spec agree). AMOLED panel maker - **TEARDOWN_REQUIRED**.

**Remaining uncertainty:** the panel glass vendor and the exact CO5300 sub-variant need a flex-cable/package marking.

**Impact on final inventory:** YES - a factual correction (3.97" -> 1.04"/340x340) plus a newly named DDIC; the hardware-variants report gains the JDI/NT36672E alternative main panel.

**Answers:** (1) 1.04" 340x340 AMOLED on Chipone CO5300 via SPI0, Hynitron touch; (2) panel-maker marking; (3) yes; (4) yes; (5) yes; (6) only for the glass vendor; (7) Chipone CO5300 + 1.04" 340x340 AMOLED; (8) PROVEN; (9) yes; (10) yes; (11) yes.

## Second-pass update (2026-09-08)

* `spi0.0` binds `spi_tiny_lcd_co5300` (module `spi_tiny_co5300_lcd` loaded). The DT node `tiny_lcd` is
  `compatible = "hxytech,spi_tiny_lcd"` at `spi-max-frequency = <60000000>` with `dc-ctrl` 190, `reset`
  154, `te` 31, `en-1v8` 118, `en-2v8` 29 - the SPI/QSPI + TE wiring class the CO5300 datasheet describes
  (VI16, VI17, VI33). The interface is now quantified, not just named.
* The panel is **not** an Android display: `displays.txt` shows exactly one HWC display (`Built-in Screen`,
  1080 x 2400, `pnpId=MTK`, `displayName="MTKDEV"`, density 480, xDpi 397.6 / yDpi 393.3) while the rear
  panel survives only as the `hyn_ts` digitizer (native 340 x 340) plus vendor sysfs (VL28). Strongest
  available confirmation that the sub-display is a vendor-private surface, never a `DisplayManager` display.
* Geometry/brightness corroborated externally: 1.04" AMOLED, **340 x 340**, 600 nits peak, 60 Hz,
  touch-interactive, inside the rear camera island (VI1, VI5, VI25, VI26).
