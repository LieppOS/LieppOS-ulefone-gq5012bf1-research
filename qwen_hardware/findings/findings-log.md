# Findings log — GQ5012BF1 hardware audit

Format per entry: subsystem · finding · evidence · source · confidence · changes inventory? · next step.
Dated by audit date (2026-09-08); the live-device capture itself is frozen at 2026-08-31 11:56.

---

## L01 · Device identity · Android 15 stock build on the `GQ5012BF1` EEA product

- **Finding**: `Ulefone/GQ5012BF1_EEA/GQ5012BF1:15/AP3A.240905.015.A2/1761131274`, baseband
  `MOLY.NR17.R1.MP5.RC.MP.V23.9.P1`, `persist.vendor.connsys.chipid = 0x6878`,
  custom version `DZ_M170_Ulefone_EEA_Armor29Pro_20251022_V35`, serial `5012BF3010001335`.
- **Evidence**: live snapshot `identity.txt`, `../hardware/MASTER-HARDWARE-INVENTORY.md` §1.
- **Confidence**: PROVEN · **Changes inventory**: no (baseline) · **Next**: none.

## L02 · SoC · Platform is MediaTek MT6878 family, marketed as Dimensity 7400 / MT6878T

- **Finding**: every kernel/HAL string says `mt6878` (`ro.boot.hardware`, `ro.board.platform`,
  `connsys_d_die_cfg_mt6878`, ISP tuning DB `mt6878/`); Ulefone spec sheet names the part
  Dimensity 7400 / "CPU: MT6878T".
- **Evidence**: live props + official spec + GSMArena.
- **Confidence**: PROVEN (platform) / STRONGLY_SUPPORTED (commercial name) · **Changes inventory**: no
  · **Next**: confirm Dimensity 7400 CPU/GPU/APU/modem block spec from MediaTek product page.

## L03 · Audio / Smart PA · the "unknown" speaker amplifier is Awinic AW88394

- **Finding**: the generic `speaker_amp` binding at I2C `6-0034` (module `mtk_sp_spk_amp`) is
  driven by `aw883xx_driver.ko`. Fitted part = **AW88394**, chip-ID register `0x00` = `0x2049`;
  the module also carries `0x2066` / `0x2183` tables (alternate family parts, not fitted).
  Reset GPIO 193, IRQ GPIO 41, 5 I2C retries @5 ms, `mtk_spk_type = 5` (`MTK_SPK_AWINIC_AW883XX`),
  ALSA rates 8 k–96 k, S16/S24/S32.
- **Evidence**: `../kernel/phase4-aw883xx-hardware-contract.md`, `../kernel/phase4-aw883xx-dt-contract.md`,
  live `buses.txt` (`6-0034` → `speaker_amp`).
- **Confidence**: PROVEN · **Changes inventory**: **YES** (prior inventory had this UNKNOWN) ·
  **Next**: AW883xx datasheet capability sheet → unused features (AS2 analog boost, VBAT/Ipeak
  SPD保护, 96 k support, ACF scene profiles).

## L04 · Power · `5-0018` is a Crichtek RT5133 PMIC, not the MT6369 audio codec

- **Finding**: live I2C enumeration binds `richtek,rt5133` at `5-0018`; the prior inventory recorded
  "MT6369 I2C binding at 5-0018". Both cannot be true — the ALSA card name proves an MT6369-class
  codec exists, but the I2C child at that address is RT5133.
- **Evidence**: live `buses.txt`; `docs/audio.md`; prior inventory §21.
- **Confidence**: PROVEN (RT5133 present) / UNKNOWN (whether MT6369 sits on a separate bus) ·
  **Changes inventory**: **YES** (correction) · **Next**: confirm MT6369/MT6368 codec binding from
  codec-dump paths rather than I2C child listing.

## L05 · Display support ICs · panel bias/gate IC is Wuxin OCP2131 on `6-003e`

- **Finding**: `6-003e` binds `mediatek_drm_gateic` with DT node name `lcd_ocp2131`,
  compatible `mediatek,i2c_lcd_bias` → LCD bias / gate-IC rail driver on I2C-6.
- **Evidence**: live `buses.txt`.
- **Confidence**: PROVEN (binding) · **Changes inventory**: **YES** (new board-level IC) ·
  **Next**: OCP2131 datasheet (positive/negative output rails, I2C control, protection).

## L06 · Camera / illumination · three separate Awinic flash ICs, only one dual-channel

- **Finding**: `aw36515` @`6-0063` = dual-channel (LED0/LED1, independent flash regs `0x03`/`0x04`
  and torch regs `0x05`/`0x06`, shared mode bits `0x01[3:2]`, shared external-strobe GPIO
  `flash-externel = <0x89 0x74 0x00>` = GPIO 116); `aw36518` @`8-0063` and `aw36518_v2` @`12-0063`
  are single-channel (`if (led_no) return 0`), with no chip-ID gate on the AW36518 path.
- **Evidence**: `../kernel/phase4-aw36515-hardware-contract.md`, `phase4-aw36518-hardware-contract.md`,
  live `buses.txt`.
- **Confidence**: PROVEN · **Changes inventory**: no (adds channel-level detail) ·
  **Next**: AW36515/AW36518 datasheet max per-channel current vs stock-programmed codes.

## L07 · Notification LED · AW2013 enabled by GPIO 188, not a regulator; 5 mA full-scale per channel

- **Finding**: chip-ID reg `0x00` must read `0x33`; three channels red/green/blue each
  `led-max-microamp = 5000`, `imax` code 1 (5 mA), stock fixed brightness red 64 / green 64 / blue 128;
  power is a GPIO (`aw2013-pwd-gpio` = 188, active high) with no regulator consumer; hardware blink
  only (130 ms step), no breathing.
- **Evidence**: `../kernel/phase4-leds-rgb-aw2013-hardware-contract.md`, `-dt-contract.md`.
- **Confidence**: PROVEN · **Changes inventory**: no (adds unused-feature detail) · **Next**: none.

## L08 · Display · VTDR6115 DDIC, 4-lane DSI video mode at 870 Mbit/s/lane, DSC 1.1, HBM via DCS 0x51

- **Finding**: 1080×2400 AMOLED, 4 data lanes, RGB888, 870 Mb/s/lane, 435 MHz PLL,
  `mode_flags = 0x0e05` (VIDEO + SYNC_PULSE + LPM + CLOCK_NON_CONTINUOUS + NO_EOT), refresh chosen
  by DCS `6c 00/01/02` = 60/90/120 Hz, 12-bit DCS `0x51` brightness, HBM enable `51 0f ff` /
  disable `51 03 ff` exposed through `/sys/class/primary_lcm/set_hbm_backlight`; **no AOD/doze, CABC
  or local-HBM command implementation exists in stock**; ATA/ID readback is a stub.
- **Evidence**: `../kernel/phase4-panel-vtdr6115-hardware-contract.md`, `-dt-contract.md`.
- **Confidence**: PROVEN · **Changes inventory**: **YES** (AOD/CABC/DDIC-ID findings) ·
  **Next**: VTDR6115 datasheet for max refresh/HDR paths; panel vendor identity.

## L09 · Display (stock policy) · framework reports 60/90/120 Hz, HDR10+HLG+DolbyVision, 500 nit cap

- **Finding**: `supportedRefreshRates [120.00001, 90.0, 60.0]`, active mode 60 Hz at snapshot,
  `supportedHdrTypes=[2,3,4]`, `mMaxLuminance=500.0 / mMaxAverageLuminance=500.0`, `mHbmMode=off`,
  `persist.vendor.sys.pq.mdp.vp.hdr10.panel.dtmo.panelnits.max = 490`,
  `ro.vendor.pq.mtk_hdr10_panel_dtmo_support = 0`; `supportedColorModes=[0]` (NATIVE only).
- **Evidence**: live `displays.txt`, `identity.txt`.
- **Confidence**: PROVEN · **Changes inventory**: no, feeds capability matrix · **Next**: compare with
  marketing "2200 nits peak" claim → gap analysis.

## L10 · Touchscreen · FT3680 on SPI3 @6 MHz with in-module firmware; module_list has 3 records

- **Finding**: DT `/soc/spi3@11013000/focaltech@39`, compatible `focaltech,fts`, CS0, 6 MHz,
  IRQ GPIO 7, reset GPIO 6; firmware is **built into the module** (118 972-byte image) because
  `/vendor/firmware` contains no `focaltech_ts_fw_*.bin`; `upgrade_setting_list`/`module_list` carry
  **3 module records with only record 0 populated** → other supported touch variants are unprovisioned;
  gesture wake through `yft_tpd_gesture` (`tpgesture_*`), FHP misc devices `fhp_ft`/`fhp_input`.
- **Evidence**: `../kernel/phase4-focaltech-ft3680-reconstruction.md`, live `buses.txt`.
- **Confidence**: PROVEN · **Changes inventory**: no (adds variant + unused-feature detail) ·
  **Next**: FT3680 datasheet capability list (10 pts, glove/wet/cover, pen) vs enabled sysfs paths.

## L11 · Touch/board variants · two more touch-class bindings exist on I2C-0

- **Finding**: `0-0015 hyn_ts` (`hynitron,hyn_ts`) = rear mini-display touch (populated and in use);
  `0-0041 ilitek` (`tchip,ilitek`) and `0-0048 chipone-tddi` (`chipone-tddi`, bound by
  `mediatek_drm_gateic`) are additionally probed on the same adapter.
- **Evidence**: live `buses.txt`.
- **Confidence**: PROVEN (binding) / UNKNOWN (physical population of the ilitek part) ·
  **Changes inventory**: **YES** (new candidates) · **Next**: DT status + userspace consumers to
  classify ilitek as installed vs software-only.

## L12 · Sensors · 4 physical sensor ICs; everything else is MTK/AOSP fusion

- **Finding**: 22 h/w sensors exposed, of which only 6 entries map to physical ICs:
  `icm4n607_acc` + `icm4n607_gyro` (IvenSense ICM-4N607, 12.5–400 Hz), `mmc5603` (Memsic MMC5603,
  5–50 Hz, FIFO 4500/600), `stk3a5x_als` + `stk3a5x_ps` (Sensortek STK3A5X, on-change, ps is wakeUp),
  `spl07` (Goer SPL07 barometer, 1–10 Hz, FIFO 4500/300). All remaining entries are vendor `mtk`
  or `AOSP` (orientation, gravity, linear_acc, rotvec, step counter/detector, tilt, wake gesture, …).
- **Evidence**: live `sensors.txt` (full dump).
- **Confidence**: PROVEN · **Changes inventory**: no (confirms count; adds rate/FIFO detail) ·
  **Next**: per-datasheet ranges/resolution + unused features (tap-to-wake, WoW, FIFO watermarking).

## L13 · Thermal core · module I2C node is named `fm78100` on `8-003c`

- **Finding**: the thermal module's in-phone I2C endpoint DT node name is `fm78100` with compatible
  `mediatek,tiny2c_usb`, bound by `yft_tiny2c_usb` / `tiny2c_usb-sensor`.
- **Evidence**: live `buses.txt`.
- **Confidence**: PROVEN (binding) · **Changes inventory**: **YES** (new part number to identify) ·
  **Next**: identify FM78100 (likely shutter/motor or interface ASIC) via vendor search.

## L14 · Fingerprint · Madev/Microarray SPI capacitive die behind TrustKernel TEE

- **Finding**: `spi1.0` binds `madev` (module `microarray_fp_tee`, node `madev_finger`); device nodes
  `/dev/madev0` (`mafinger_device` SELinux label) and `/dev/tkcore_fp` (`tkcore_client_device`);
  DT exposes `reset-gpio`, `int-gpio`, `interrupts = <3 1 3 0>`, `debounce = <3 0>`, `status = "okay"`
  and 16 pinctrl states incl. SPI0 mi/mo/clk/cs as-SPI and as-GPIO fallbacks.
- **Evidence**: live `fingerprint.txt`, `buses.txt`, `../kernel/phase4-yft-devinfo-reconstruction.md`,
  prior inventory §22.
- **Confidence**: PROVEN (presence + transport) · **Changes inventory**: no · **Next**: exact Madev
  die part number search; whether GESTURE/wake features are compiled out.

## L15 · RF front-end · stock uses the legacy MediaTek ePA/eLNA ConnFem path with an 8-way HWID

- **Finding**: merged FDT `connfem` compatible `mediatek,mt6878-connfem`, Ulefone overlay subtree
  `epa-elna-mtk`, HWID read from GPIO 131 / 132 / 92 (⇒ 8 HWIDs), a 10-entry FEM catalog
  (`nofem`, `wlan7207h`, `wlan7207c`, `qm42195`, `qm45197`, `sky85320`, `sky85720`, `mxd7751s`,
  `sky85732`, `rtc7620`), BT flags 6/7/8/10/11 = `epa-elna`, 3/4/5/9 = `bypass`, Wi-Fi flags-3..11
  empty. DTBO fragment 39 carries the GQ5012BF1 selection with a 24-element `parts` array whose
  indexing is still unconfirmed.
- **Evidence**: `../kernel/phase4-connfem-reconstruction.md`.
- **Confidence**: PROVEN (config path) / UNKNOWN (physically selected FEM pair) ·
  **Changes inventory**: **YES** (FEM candidate set + BT ePA/eLNA map) ·
  **Next**: recover runtime HWID → selected FEM pair; then datasheet per band.

## L16 · Haptics · single vibrator, no LRA characteristics, effect-only API

- **Finding**: `VibratorManagerService` → `vibratorIds=[1]`, per-vibrator `capabilities=[]`,
  `capabilitiesFlags=0`, `supportedEffects=[CLICK, DOUBLE_CLICK, TICK, HEAVY_CLICK, TEXTURE_TICK]`,
  `supportedPrimitives=[]`, `supportedBraking=[]`, `mMinFrequencyHz/mMaxFrequencyHz/
  mMaxOutputAccelerationGs = NaN`, `compositionSizeMax=256`, `primitiveDelayMax=1000`,
  amplitude scales LOW/NONE/HIGH/VERY_HIGH = 0.714/1.0/1.4/1.96, `rampStepDurationMs=5`.
- **Evidence**: live `lights-vibrator.txt`.
- **Confidence**: PROVEN · **Changes inventory**: no (adds unused-feature evidence) ·
  **Next**: identify the haptic driver IC (no dedicated I2C child visible → PMIC/GPIO path).

## L17 · Build coverage · 215 stock DLKM modules, 1891 proprietary entries, 55 VINTF manifests

- **Evidence**: `../workspace/gq5012bf1/reports/device-tree-audit.md`.
- **Confidence**: PROVEN · **Changes inventory**: no · **Next**: none (scoping).

## L18 · NFC · STMicro ST21NFC at `6-0008` with dual-SIM eSE routing

- **Evidence**: live `buses.txt`, `st21nfc_fw.bin`/`st21nfc_fw7.bin`,
  `ro.vendor.mtk_nfc_addon_support=1`, `nfc_routing_watchdog=true`; deep-dive corpus
  `../hardware/nfc/`, `../workspace/phase4-st21nfc-analysis/`.
- **Confidence**: PROVEN (controller) · **Next**: exact ST2x variant (ST21NFC-B/D?) from firmware
  header + `st21nfc` module strings.

---

## W19 · Web capability pass — documented camera/platform ceilings

- **Finding**: Samsung JN1 material supports 50 MP/0.64 µm, 4K60 and 1080p240; OV64B material supports 64 MP, 8K30, 4K60, 180-fps binned modes and staggered HDR; Dimensity 7400 material supports FHD+144-class display and 200-MP ISP.
- **Evidence**: `../search/sources.md` S06–S08, S12/S13; `../evidence/datasheets/chip-capabilities.md`.
- **Confidence**: STRONGLY_SUPPORTED (vendor/press) · **Changes inventory**: YES (chip-vs-stock gap) · **Next**: decode exact HAL stream arrays and test modes.

## W20 · Web capability pass — NFC, GNSS and connectivity

- **Finding**: ST21NFCB/D family supports 13.56-MHz card/reader/P2P/eSE-class operation; live properties prove MT6637-class Wi-Fi/GNSS ADIE (`0x6637`) and L5 support flag (`vendor.debug.gps.support.l5=1`).
- **Evidence**: live `properties-filtered.txt`, `connectivity.txt`; `../search/sources.md` S06/S19/S20.
- **Confidence**: PROVEN (board IDs/services) / STRONGLY_SUPPORTED (family caps) · **Changes inventory**: YES · **Next**: runtime Wi-Fi/BT/GNSS feature and ConnFem HWID tests.

## W21 · Web capability pass — power and thermal module remain identity gaps

- **Finding**: RT6160A reference confirms 3-A buck-boost/2.2–5.5-V class for live `rt6160` rails; comparable InfiRay/T2-class modules support 640×512/12-µm/25-Hz thermal imaging and radiometry, but exact FM78100/M170 die is not public.
- **Evidence**: `../search/sources.md` S18/S21; live DT/bus; `../evidence/datasheets/chip-capabilities.md`.
- **Confidence**: PROVEN (bindings) / POSSIBLE (analogue caps) · **Changes inventory**: YES · **Next**: read module ID/registers and power-rail limits.

## W22 · Audit deliverables completed

- **Finding**: The `qwen_hardware/` workspace now contains every required subsystem report (plus cross-reference reports for misc/rugged features), evidence extracts, web-search log, findings/candidate/contradiction logs, progress files and all five final reports. Exact unresolved identities are retained as UNKNOWN rather than guessed.
- **Evidence**: `../README.md`, `../final/`, `../subsystems/`, `../evidence/`, `../search/`.
- **Confidence**: PROVEN · **Changes inventory**: YES (final workspace) · **Next**: optional live/teardown verification listed in `progress/TODO.md`.
