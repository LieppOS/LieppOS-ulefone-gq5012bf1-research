# Bluetooth (MT6637-BT-KERNEL / BT-KERNEL-TRANSPORT)

**Status: BT-KERNEL-TRANSPORT = DONE.** BT-CONTROLLER-FIRMWARE and BT-VENDOR-HAL stay
proprietary ([`firmware-boundary.md`](firmware-boundary.md)).

## Architecture (proven)

```
Android Bluetooth (system: com.android.bluetooth, Gabeldorsche stack)
  └─ AIDL android.hardware.bluetooth (bluetooth_hal_service = android.hardware.bluetooth-service-mediatek)
       [HIDL @1.1 service also shipped: android.hardware.bluetooth@1.1-service-mediatek, VTS only]
       └─ libbluetooth_mtk.so / libbluetooth_mtk_pure.so: open("/dev/stpbt"), H4 HCI framing,
          BT_FW.cfg vendor cmds, /proc/stpbt/bt_fw_version → persist.vendor.connsys.* props
            └─ bt_drv_6878.ko  (char dev "stpbt", driver "mtk_bt_chrdev"; DT "mediatek,bt" @0x18800000,
               IRQ 693 (bgf2ap) + 132 (conn2ap sw irq))
                 ├─ BTIF/CCIF to the BGF MCU inside MT6878 CONNSYS (CHIP_IF_BTIF, SUPPORT_BEIF=1)
                 ├─ conninfra_pwr_on/off, sub_drv_ops (pre-cal, reset, coredump), connfem query,
                 │  connadp power throttling (bt_pwrctrl_pre_on: lp_cur_bat_lv)
                 └─ MT6637 A-die BT RF
  HCI device: no Linux hci0 for the main controller. bt_drv imports hci_alloc_dev_priv,
  hci_register_dev and hci_recv_frame from bluetooth.ko (btmtk_main.c is linked in), but
  btmtk_register_hci_device() is only called under `#if (USE_DEVICE_NODE == 0)`
  (btmtk_btif_main.c:1679-1681). The build uses USE_DEVICE_NODE=1, so HCI goes through
  /dev/stpbt to the userspace stack.
```

Transport = **BTIF (internal SoC UART-like FIFO + CCIF) to the CONNSYS BGF MCU**, not an external
UART/SDIO/USB. `uarthub` is disabled in DT, and `hci_uart`/`btsdio`/`btbcm`/`btqca` (GKI
system_dlkm) are generic modules with no MT6878 consumer.

## Kernel modules

| module | functions | data | ABI | source / build |
|---|---:|---:|---|---|
| `bt_drv_6878.ko` | **294/294** | **118/118** | exact (imports 186, modversions 187, export 1, modinfo 8 incl. `version=7.0.2020121701:turnkey`) | NothingOSS kernel_modules 2115d27 `bt/mt66xx/6878` → `btif/Kbuild`, `BT_PLATFORM=6878`, `TARGET_BUILD_VARIANT` unset ⇒ `FW_LOG_DEFAULT_ON=1`, `BUILD_QA_DBG=1`; 6878 flags `SUPPORT_BEIF=1 SUPPORT_BIN2IMG=1 CFG_BT_ATF_SUPPORT=0 DTS_REORDERED=1 BT_COREDUMP_CHECK=1` |
| `bluetooth.ko` (vendor_dlkm copy) | 1257/1257 | 153/153 | exact | GKI `net/bluetooth`, vendor in-tree build (scm g945dff7bc1bf). The system_dlkm GKI copy is code-identical (1257/153) and is listed first in system_dlkm `modules.load` |
| `mtk-btcvsd.ko` | 32/32 | 18/18 | exact | KDM `sound/soc/mediatek/common/mtk-btcvsd.c` (SCO CVSD/mSBC PCM between AFE and BT) |
| `connfem.ko` | 94/94 | 45/45 | exact | BT FEM query: returns nofem |

## Power / firmware path

* `bt_hw_and_mcu_on()` with `SUPPORT_BIN2IMG == 1`: **no firmware download by Linux**.
  `bgfsys_check_conninfra_ready()`, then the FW version is read from connsys EMI
  (`emi_ap_phy_base + FW_VERSION_OFFSET_ADDRESS`), then `bgfsys_power_on()`. The BT/BGF-MCU image
  is preloaded by LK from partition `connsys_bt` (sub-image `connsys_bt_mt6878_mt6637`). DMESG:
  `bt_hw_and_mcu_on support bin to img`, `FW version:
  [t-neptune-main-soc7_0-2104-RAYAS_SOC7_0_E1_ASIC_BT_BWH_OFF-20241028193456]`.
* After power-on the driver sends internal WMT commands: connfem info, antenna, antswap (ignored,
  no 6878/6637 key), power, UTC sync, blank status.
* `BT_FW.cfg` (vendor/firmware): coex keys all 0, `bt_antswap[6878][6631]` (not matched),
  `bt_tssi_from_wifi: 3`, `bt_tssi_target: 3776`.
* Init: `init.bt_drv.rc` insmods `bt_drv_${ro.vendor.bt.platform}` (= 6878) when
  `vendor.connsys.driver.ready` is set (`ro.vendor.bt.connac3=no`).

## Audio interaction

* SCO/eSCO voice: `mtk-btcvsd` PCM (BT CVSD/mSBC over the BT-CVSD SRAM interface).
* A2DP offload (`persist.bluetooth.a2dp_offload.cap=sbc-aac`) and LE Audio offload
  (`ro.bluetooth.leaudio_offload.supported=true`, `persist.vendor.bluetooth.leaudio_mode=ums-cg`)
  go through `android.hardware.bluetooth.audio-impl-mediatek.so` and the audio HAL/ADSP
  (proprietary). LE Audio broadcast source/assist and unicast client are enabled by props.

## Vendor commands statically visible

`BT_FW.cfg` `#VENDOR_CMD:` examples (commented out). `libbluetooth_mtk.so` exposes
`GORMcmd_HCC_Fw_Cfg_Cmd`, `get_bt_patch_version` and `parse_fw_cfg_para`. The HCI vendor opcodes
themselves are inside the proprietary library and were not decompiled.
