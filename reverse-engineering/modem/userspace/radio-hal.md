# Radio HAL (stock vendor, static)

## VINTF (`vendor/etc/vintf/manifest.xml`)

| HAL | version | instances |
|---|---|---|
| android.hardware.radio.config | AIDL **V2** | IRadioConfig/default |
| android.hardware.radio.data | V2 | IRadioData/slot1, slot2 |
| android.hardware.radio.messaging | V2 | slot1, slot2 |
| android.hardware.radio.modem | V2 | slot1, slot2, imsSlot1, imsSlot2, se1, se2 |
| android.hardware.radio.network | V2 | slot1, slot2, imsSlot1, imsSlot2 |
| android.hardware.radio.sim | V2 | slot1, slot2, imsSlot1, imsSlot2, se1, se2 |
| android.hardware.radio.voice | V2 | slot1, slot2, imsSlot1, imsSlot2 |
| android.hardware.radio.ims | V1 | IRadioIms/slot1, slot2 |
| android.hardware.radio.sap | V1 | ISap/slot1, slot2 |
| vendor.mediatek.hardware.mtkradioex.{data V2, modem V2, voice, sim, network, messaging, ims, rcs, dch} | V1 unless noted | slot1, slot2 |
| vendor.mediatek.hardware.atci | V1 | IAtcid/default |
| vendor.mediatek.hardware.mdmonitor | - | IMDMonitorService/default (md_monitor) |
| vendor.mediatek.hardware.nvram | - | INvram/default |
| vendor.mediatek.hardware.netdagent | V1 | INetdagents/default |
| vendor.mediatek.hardware.videotelephony | - | IVideoTelephony/default (vtservice_aidl) |

Radio HAL V2 is the Android 14 generation. The `imsSlotN` instances are MediaTek's IMS-side
copies of the modem, network, sim and voice HALs, consumed by `ImsService.apk`. The `seN`
instances are for the secure element (`ro.vendor.mtk_uicc_clf=1`).

## Implementation

* `vendor.ril-daemon-mtk`: `/vendor/bin/hw/mtkfusionrild -l libmtk-ril.so` (`mtkrild.rc`;
  user radio; capabilities BLOCK_SUSPEND/NET_ADMIN/NET_RAW/WAKE_ALARM).
  * Started on `vendor.ril.mtk=1` or **`ro.vendor.mtk_mipc_support=1`**, which stock sets.
  * Sockets: `sap_uim_socket1`, `rild-oem`, `volte_imsvt1`, `rild-atci`.
* `librilfusion.so` hosts every AIDL service above. Its NEEDED list includes all nine
  `android.hardware.radio.*-ndk` and sixteen `vendor.mediatek.hardware.mtkradioex.*-ndk`
  libraries.
* `ro.vendor.mtk_ril_mode = c6m_1rild`: gen6 modem, one rild for both SIMs.
  `ro.vendor.mtk_mipc_support = 1`: modem control is **MIPC** (MediaTek IPC framing) over
  `/dev/ttyCMIPC1` (rild), not AT over a mux.
* Fallback/aux libs in vendor:
  * `libmtk-ril.so`, `libmtkmipc-ril.so` (RIL handlers, also open `ccci_mdx_sta` / `ccci_pin_sta` / `ttyC6`)
  * `libvia-ril.so`, `libviamipc-ril.so` (C2K/VIA)
  * `libgwsd{v2,v3}-ril.so` (gaming/Wi-Fi data)
  * `libreference-ril.so` (AOSP, unused)
  * `libwpfa.so` (Wi-Fi packet filter agent, `/dev/ccci_wifi_proxy`)
  * `libcarrierconfig.so`

Exact HAL ELF NEEDED lists and the kernel interfaces each binary touches are in
`dependency-map.tsv`.
