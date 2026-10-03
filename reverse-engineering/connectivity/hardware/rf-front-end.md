# RF front end (static view)

## Proven

* **No external Wi-Fi/BT ePA/eLNA is active.** `connfem.ko` (now 94/94 functions, 45/45 data, ABI
  exact, `../connfem/README.md`) logs `connfem_is_available: FEM is not available`. BT logs
  `CONNFEM BTvid/pid == 0, ignore`. `vendor/firmware/connfem.cfg` is 0 bytes.
* ConnFem DT offers 7 ODM pairings: `wlan7207h-wlan7207c`, `qm42195-qm45197`,
  `sky85320-sky85720`, `mxd7751s-mxd7751s`, `nofem-sky85732`, `nofem-qm45197`,
  `rtc7620-nofem`. 12 HWID entries exist, only 8 are addressable (3 GPIOs), and the strap
  resolves to index 2 = nofem/nofem (`mt6637.md`).
* Wi-Fi is **2x2** (`CFG_SUPPORT_CONNAC2X_2x2=1`; the A-die exposes WF0 and WF1 register spaces,
  both reading id 0x6637) with **2.4 / 5 / 6 GHz** (`CFG_SUPPORT_WIFI_6G=1`,
  `CFG_SUPPORT_WIFI_6G_PWR_MODE=1`). That is Wi-Fi 6E (11ax). Not 11be: `CFG_SUPPORT_802_11BE=0`.
  NothingOSS's "WIFI: Disable 6GHz on MTK driver" (9b6cb5c) is **not** in the stock binary.
* BT antenna: `btmtk_intcmd_wmt_send_antenna_cmd ... Use default antenna setting`, so no board
  antenna-swap or TSSI table is matched for 6878/6637.
* GNSS: same A-die (no MT6686), L1+L5 (`MNL_Config.xml` `L1Only=0`, chip-6637 L5 DCB values).
* FM: separate LNA enable on **GPIO 72** (`fmradio/fm_lna_gpio`, driven 1 on
  `FM_IOCTL_POWERUP` and 0 on `FM_IOCTL_POWERDOWN`, `fm_module.c`). The antenna is the headset
  cable, switched by **GPIO 195** following ACCDET plug state (audio research,
  `../../audio/yft-audio-deltas.md`).

## Coexistence hooks (software)

* Wi-Fi/BT coex runs inside CONNSYS firmware. `BT_FW.cfg` coex keys are all `0x00` (firmware
  defaults).
* Wi-Fi ↔ LTE: `CFG_SUPPORT_GET_LTE_SAFE_CHANNEL=1` (CCCI query); `wlan_drv` depends on
  `ccci_md_all`.
* Wi-Fi ↔ modem data path: `mddp.ko` (132/132, 87/87 exact), `CFG_MTK_MDDP_SUPPORT=1`.
* Thermal / low battery: `wifi_cooling.ko`, connadp power throttling (`conn_pwr_*`), consys
  thermal zone (passive 119 °C).

## BLOCKED (teardown / RF measurement)

* Antenna count, placement and feed routing, diversity switches, matching networks.
* Whether any FEM footprint is populated but unstrapped (considered implausible).
