# New finding - FM radio receiver and 3.5 mm headset jack (not in the original audit)

**Current claim:** absent from the original reports entirely.

**Previous confidence:** not assessed.

**New evidence**
* **FM radio, device tree**:
  ```
  /fm      compatible = "mediatek,fm"; family-id = <0x6983>; host-id = <0x6878>; conn-id = <0x205>;
  /fmradio compatible = "mediatek,fmradio"; fm_lna_gpio = <ctrl 72 0>; status = "okay";
  ```
  A discrete **FM LNA control GPIO** means a real receive path with an external low-noise amplifier stage, not a bare software stub.
* **FM firmware ships**: `vendor/firmware/fm_cust.cfg`, `soc_fm_v1_patch.bin`, `soc_fm_v1_coeff.bin` (alongside legacy MT662x/663x images for other chips).
* **A stock FM application ships**: `system_ext/app/YftFmRadio/YftFmRadio.apk`.
* **A user-facing switch exists**: `/sys/class/yft_device/yft_fm_switch`, and the platform node `/yft_device` carries `urxdo_gpio_select`.
* **3.5 mm headset jack**: `second_pmic@5/accdet`, `compatible = "mediatek,mt6369-accdet"`, `status = "okay"`, with `headset-three-key-threshold = <0 80 220 400>`, `headset-four-key-threshold = <0 58 121 192 400>`, `accdet-mic-mode = 1`, `accdet-plugout-debounce = 1`, an efuse calibration reference (`nvmem-names = "mt63xx-accdet-efuse"`) and an ADC channel `pmic_accdet`.
* **The two are linked**: `accdet` owns `gpio-accdet-fm-switch = <ctrl 195 0>` - the classic arrangement in which the wired headset cable is switched in to serve as the FM antenna.
* Ulefone's own specification lists a **Headphone Jack** for this model.
* The audio codec itself is inside the **MT6369** sub-PMIC (`mt6369codec`), with the **AW88394** smart amplifier at i2c `6-0034` handling the loudspeaker.

**Contradicting evidence:** none. FM was simply never examined in the original pass, and the GSI snapshot contained no FM application, which would have hidden it from a framework-only look.

**Internet sources:** VI4 (headphone jack listed by the OEM).

**Local evidence:** VL23, VL24.

**Read-only live evidence:** frozen capture (the FM radio was not active during the capture).

**Final conclusion**
The device has a **working FM radio receive path built into the MediaTek connectivity subsystem**, complete with an external LNA control line, per-chip FM firmware, a headset-cable antenna switch and a stock FM application - plus a **3.5 mm headset jack with full accessory detection and three/four-button remote support**, driven by the MT6369 codec. Neither appeared in the original inventory.

**Final confidence:** **PROVEN** (device tree with `status = "okay"`, dedicated GPIOs, firmware and a stock application all agree).

**Remaining uncertainty:** actual FM sensitivity, whether RDS is enabled, and whether FM transmit is possible (MediaTek ships `*_fm_v2_patch_tx.bin` images for some chips, but only the `soc_fm_v1` receive pair is present here, so **FM transmit should be assumed unavailable**). Reception quality needs a live test with headphones attached.

**Impact on final inventory:** YES - two capabilities are added to MASTER-HARDWARE-INVENTORY and the hidden/underused-capability report (FM radio is a genuine, fitted, stock-supported feature that any custom ROM would otherwise silently drop).

**Answers:** (1) FM RX + 3.5 mm jack both fitted and stock-supported; (2) RDS and sensitivity; (3) yes; (4) yes - tune with headphones attached; (5) partly; (6) no; (7) MediaTek connsys FM receiver + MT6369 accdet jack; (8) PROVEN; (9) yes; (10) yes; (11) yes.
