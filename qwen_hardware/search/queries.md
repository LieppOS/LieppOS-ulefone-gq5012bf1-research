> **Pass-2 pointer (2026-09-08).** First-pass working material. Where anything here conflicts with `../final/` or `../verification/findings/`, the verification pass wins. Two blanket corrections apply: the 2026-08-31 capture ran a **LieppOS GSI**, so its framework-level observations are not stock Ulefone behaviour; and `vendor/etc/init/hw/init.yft.rc` is a **platform-wide ODM option catalogue**, not this board's bill of materials.

# Useful search queries (GQ5012BF1 hardware audit)

Format: `provider` · query · why it was useful · what it yielded.

| Provider | Query | Why useful | Yield |
|---|---|---|---|
| exa | `MediaTek Dimensity 7400 MT6878T specifications CPU Mali-G615 MC2 APU 5G modem` | pins the commercial part to the DT-reported MT6878 family and gives modem/ISP/APU claims | core block list (A78/A55, G615, APU 655, R16 3CC-CA modem) |
| fetch (direct) | `https://www.cpudb.cc/soc/mediatek-dimensity-7400` | machine-readable SoC spec table | LPDDR5 @3200 MHz, 4×16-bit, 25.6 Gb/s, UFS 3.1, 200 MP ISP, 4K30 capture, Mali-G615 MP2 128 shader, Vulkan 1.3 |
| fetch (direct) | `https://store.ulefone.com/pages/armor-29-pro-thermal-specs` | OEM-authored spec sheet (claim-quality: official) | full factory spec incl. thermal core, flash, GNSS list, IP ratings |
| fetch (direct) | `https://www.gsmarena.com/ulefone_armor_29_pro_thermal_5g-14104.php` | independent DB (band list, USB gen, FM, weights) | 4G/5G band lists, USB 2.0, FM RDS, accessory connector, 688 g/33.8 mm |
| anysearch | `Awinic AW88394 smart audio amplifier datasheet output power I2S boost` | smart-PA capability layer | 5.3 W/8 Ω @1 %, 10.25 V smart boost, Class-K, I2S/TDM |
| anysearch | `Awinic AW36515 AW36518 flash LED driver datasheet torch current mA I2C` | flash-driver capability | AW36515 = boost dual-channel flash/IR driver (2 A-class), AW36518 = independent 1.5 A single-channel |
| anysearch | `AW2013 Awinic 3 channel LED driver datasheet max current breathing pattern` | notification-LED capability vs stock | 3-ch, ≤15 mA/LED 4-level, auto-breathing pattern engine |
| anysearch | `FocalTech FT3680 capacitive touch controller datasheet ...` | touch capability family check | FT3680 not publicly documented; FT3683G family = 10-finger, 360 Hz report, GOLED/POLED, waterproof/heavy-rain touch |
| anysearch | `Samsung ISOCell S5KJN1 ... video modes`, `OmniVision OV64B ... 4K60 1080p240 HDR` | sensor capability vs stock modes | JN1: 50 MP 0.64 µm, 4K60/1080p240; OV64B: 8K30, 4K60, 180 fps binned, 3-exposure staggered HDR, on-chip remosaic |
| anysearch | `Sony IMX989 specifications 8K30 4K120 10-bit ...` | main-sensor capability | 1″-class 50.3 MP, dual-gain/DOL HDR, 8K/4K120 class modes |
| anysearch | `Dimensity 7400 specifications Wi-Fi 6E Bluetooth 5.4 USB display 144Hz` | SoC connectivity/display ceilings | MiraVision 955, WFHD+@120 / FHD+@144, 200 MP ISP, Wi-Fi 6E |
| anysearch | `MediaTek MT6639 wireless combo Wi-Fi 6E ... specifications` | combo-chip family reference (MT6637 not public) | family-level: 2×2 11ax + BT5.x + GNSS; MT6635 precedent documented publicly |
| anysearch | `STMicroelectronics ST21NFC-B ST21D NFC controller eSE MIFARE Felica` | NFC controller family capability | ST21NFCB/ST21NFCD: 13.56 MHz CLF, card/reader/P2P, MIFARE/Felica, 4×4 mm WFBGA |
| anysearch | `Goermicro SPL07 barometric sensor datasheet` | barometer range | SPL07-003: 300–1100 hPa, −40…85 °C |
| anysearch | `Memsic MMC5603 magnetometer datasheet range output data rate` | mag capability | ±30 G, 20-bit, 0.0625 mG/LSB, ≤1000 Hz ODR, ~2 mG noise |
| anysearch | `InvenSense ICM-42631 ICM-4N607 6-axis IMU datasheet FIFO` | IMU family capability reference | ICM-4N607 not public; family: ±2/4/8/16 g, ±15.6…2000 dps, 4 kHz+ ODR, APEX engine |
| anysearch | `Southchip SC8571 ... charge pump`, `SH366003 fuel gauge`, `Richtek RT5133 RT6160` | power-chain identification | SC8571/SH366003 datasheets not public; RT6160(A) = 3 ACOT buck-boost, 2.2–5.5 V, 3 A |
| anysearch | `QM42195 QM45197 FEM Wi-Fi 6E 5-7GHz ... SKY85320 SKY85732` | FEM candidate identity | QM42195 = Qorvo 5-7 GHz Wi-Fi 6E/7 FEM; Skyworks 6 GHz Wi-Fi FEM family for SKY853x |
| anysearch | `InfiRay M170 thermal module 640x512 12um NETD 25Hz radiometry shutter` | thermal core analogue | 640×512/12 µm/25 Hz radiometric 12 µm LWIR cores, −20…550 °C, ≤40–50 mK class |
| anysearch | `Hynitron touch controller hyn_ts` | rear-screen touch IC | no public datasheet ⇒ part remains vendor-only |
| anysearch | `Ulefone Armor 29 Pro Thermal teardown vapor chamber` | mechanical/BOM evidence | no teardown for this SKU (only Armor 28 Ultra owner teardown) |
