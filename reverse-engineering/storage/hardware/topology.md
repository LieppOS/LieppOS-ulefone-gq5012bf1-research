# GQ5012BF1 storage hardware topology (static)

Sources:

- Live DT: read-only capture `workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649/devicetree.tar`, decoded in [`live-dt-storage-nodes.txt`](live-dt-storage-nodes.txt).
- Donor DT: MTK ALPS `5e415e059253` `arch/arm64/boot/dts/mediatek/mt6878.dts` + `cust_mt6878_msdc.dtsi`.
- Preloader/LK UFS log already captured in `slot-b-investigation/untouched-b-early-boot-forensics/post-firmware-pl-lk-decoded.txt` (sha256 `2340b771…`). This is existing evidence; no new device access was made.

## Controllers

| block | DT node | MMIO | IRQ (GIC SPI) | driver (module) | status |
|---|---|---|---|---|---|
| UFS host (UFSHCI) | `soc/ufshci@112b0000`, `mediatek,mt8183-ufshci` | `0x112b0000` size `0x2300` | 393 (`0x189`), level-high | `ufshcd-mtk` (`ufs-mediatek-mod.ko`) | **boot device** (`ro.boot.boot_devices = bootdevice, soc/112b0000.ufshci`) |
| UFS M-PHY | `soc/ufsphy@112a0000`, `mediatek,mt8183-ufsphy`, `mphy-ver = <1>` | `0x112a0000` size `0x10000` | — | `phy-mtk-ufs.ko` | active (`phys = <&ufsphy>`) |
| MSDC1 (SD) | `soc/mmc@11240000`, `mediatek,mt6878-mmc`, `host-index = <1>` | `0x11240000`/`0x1000` + top `0x11d80000`/`0x1000` | 388 (`0x184`) | `mtk-mmc.ko` | **okay** (microSD) |
| MSDC0 (eMMC) | `soc/mmc@11230000`, `host-index = <0>` | `0x11230000`/`0x10000` + `0x11f60000`/`0x1000` | 387 | — | **disabled** (board is UFS) |

## UFS host contract (live DT = donor `mt6878.dts`, unchanged)

- **Clocks (13):**
  - topckgen `CLK_TOP_UFS_SEL` (41), `AES_UFSFDE_SEL` (40) and `UFS_MBIST_SEL` (42)
  - `ufscfg_ao` (`0x112b8000`): UNIPRO_TX_SYM, RX_SYM0, RX_SYM1, UNIPRO_SYS, UNIPRO_SAP_CFG, PHY_TOP_AHB_S_BUS
  - `ufscfg_pdn` (`0x112bb000`): UFSHCI, UFSHCI_AES, UFSHCI_AHB, UFSHCI_AXI
  - `freq-table-hz` is 13 × `<0 0>`, so the core does no frequency management.
- **Resets:** `ufscfg_pdn` reset controller: `unipro_rst` (0), `crypto_rst` (1), `hci_rst` (2).
- **Supplies:** `vcc-supply` is MT6363 `vemc` (1.2–3.5 V range). `vccq-supply` is MT6363 `vufs12` (0.55–1.85 V). There is **no** `vccq2-supply`. MT6363 `vufs18` exists but is used by MSDC0 `vqmmc` (disabled node).
- **Vendor booleans present:** `mediatek,ufs-qos`, `mediatek,ufs-mphy-debug`, `mediatek,ufs-disable-mcq`, `mediatek,ufs-rtff-mtcmos`, `mediatek,ufs-bypass-vccqx-lpm`.
- **Vendor booleans absent** (all parsed by the driver): `ufs-boost-crypt`, `ufs-support-va09`, `ufs-disable-ah8`, `ufs-broken-vcc`, `ufs-pmc-via-fastauto`, `ufs-tx-skew-fix`, `ufs-broken-rtc`, `ufs-vcc-by-num`/`-by-ver`. The `clkscale`/`clk-scale-up-vcore-min` nodes and the `ufs_sel_max_src`/`ufs_sel_min_src` clocks are also absent.
- **Boot command line:** `ufshcd_core.poll_queues=0`.
- **Lanes/gear:** not set in DT. The driver offers host capability HS-G5 (`host_cap.hs_{rx,tx}_gear = UFS_HS_G5`), the GKI default 2 lanes and Rate B, and negotiates the minimum with the device. The device's own `PA_MaxRxHSGear` was not captured, so the **negotiated gear is unproven**. UFS 3.1 devices top out at HS-G4.

## UFS device (existing preloader/LK evidence)

Decoded from the JEDEC descriptor dumps printed by PL/LK:

| field | value | meaning |
|---|---|---|
| `wManufacturerID` | `0x012C` | Micron (`UFS_VENDOR_MICRON`) |
| product string | `MT512GBCAV8U31` | as printed by LK `ufs id:` |
| FW revision string | `0108` | |
| `wSpecVersion` | `0x0310` | UFS 3.1 |
| `bNumberLU` / `bNumberWLU` | 3 / 4 | |
| `bBootEnable` / `bInitPowerMode` / `bSecurityLU` | 1 / 1 / 1 | |
| `bQueueDepth` | `0x20` | 32 (single doorbell queue; MCQ disabled anyway) |
| `bUFSFeaturesSupport` | `0xBB` | |
| `dExtendedUFSFeaturesSupport` | `0x800003BB` | FFU, PSA, refresh, too-high-temp, too-low-temp, HPB, **WriteBooster**, performance-throttling (+ vendor bit 31) |
| `wHPBVersion` / `bHPBControl` | `0x0200` / 1 | HPB 2.0, device control mode |
| `bWriteBoosterBufferPreserveUserSpaceEn` / `bWriteBoosterBufferType` | 1 / 0 | user-space-reduction preserved, **LU-dedicated** WB buffer |
| health (LK `life cycle check`) | `bPreEOLInfo = 1`, `bDeviceLifeTimeEstA = 1`, `B = 1` | normal; 0–10 % used **at the time of that capture** |
| UniPro (LK) | granularity 6/6, PA_TActivate 5 (host) / 1 (peer), PA_Hibern8Time 5 / 1 | |

Configuration descriptor (LU layout, 4 KiB logical blocks, thin provisioning type 2):

| LU | bLUEnable | bBootLunID | memory type | dNumAllocUnits | notes |
|---|---|---|---|---|---|
| 0 | 1 | **1 (Boot LU A)** | 3 (enhanced 1) | 3 | preloader A |
| 1 | 1 | **2 (Boot LU B)** | 3 | 3 | preloader B |
| 2 | **2** (HPB-enabled LU) | 0 | normal | `0x1DCB0` | user LU (`sdc`). `wLUMaxActiveHPBRegions = 0x773`. `dLUNumWriteBoosterBufferAllocUnits = 0x1E00` |

RPMB well-known LU `0xC4` (unit descriptor):

- `bLogicalBlockSize` 8, so 256-byte frames; `qLogicalBlockCount` `0x10000`, so 16 MiB. This matches tkcore `RPMB size is 16777216 Bytes`.
- `bRPMBRegionEnable = 0x06` and the configuration header sets region sizes 1 and 2. LK prints region0 `0xfc0000`, region1 `0x20000`, region2 `0x20000`, region3 0.
- Reliable-write size 64 (tkcore `Reliable Write Sector Count is 64`).
- Linux exposes the W-LU as SCSI LUN `0xC144` (`49476`), the `/dev/0:0:0:49476` node used by `mtk_storageproxyd`.

The boot-control HAL selects Boot LU A/B by writing `bBootLunEn` = slot+1 through `/dev/ufs-bsg0` (see [`../ab-ota/boot-control.md`](../ab-ota/boot-control.md)).

## microSD (MSDC1) contract

Live DT: see [`../microsd/dt-contract.md`](../microsd/dt-contract.md). In summary:

- 4-bit bus, `max-frequency` 200 MHz.
- SDR12/25/50/104 and DDR50; `no-mmc` and `no-sdio`.
- `cd-gpios = <&pio 14 0>` (GPIO14, active-high), `cd-debounce-delay-ms = 0`.
- `vmmc` is MT6369 `vmch-eint-low`, `vqmmc` is MT6369 `vmc`; `ocr-voltage = 0x30000` (2.8–3.0 V).
- Pins GPIO77..82 use MSDC1 function 1. The `default` and `state_uhs` pinctrl states are identical: drive 3, CMD/DAT pull-up R1R0=01, CLK pull-down R1R0=10.
- There is no write-protect GPIO.
