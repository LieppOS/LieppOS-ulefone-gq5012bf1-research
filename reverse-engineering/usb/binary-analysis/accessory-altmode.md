# USB accessory and alternate-mode audit (static)

| feature | software | hardware/board | verdict |
|---|---|---|---|
| **DisplayPort Alt Mode** | TCPC DT `displayport { dfp-d: pin-assignment C/D/E; typec,receptacle }` (MTK template). `tcpc_class` DP DPM code. `rt_pd_manager` AMA_DP_* → `typec_mux_set` | no DP TX/PHY node in the MT6878 DT. `mux_switch` has no registered mux/redriver. USB IP is U2-only (no SS lanes to repurpose). `mediatek-drm` DP sub-objects are static-only (MEDIATEK-DRM research) | **NOT FUNCTIONAL**: declared, not realisable |
| **Analog audio accessory (Ra/Ra)** | the TCPC reports `TYPEC_ATTACHED_AUDIO`. `rt_pd_manager` logs it and registers partner `TYPEC_ACCESSORY_AUDIO`. The mux node has `accessory` | no audio switch (FSA4480-class) driver or DT node, no SBU/D± to codec route (`CONFIG_TYPEC_MUX_FSA4480` off). The audio research found no fitted passive USB-C analog audio path. SBU goes only to the MT6375 ADC for water detection | **NOT SUPPORTED** (detected only, no audio path) |
| **USB digital audio (host)** | GKI `SND_USB_AUDIO=y`. ADSP offload `usb_offload.ko` (exact) through `/soc/usb-offload` + `audio-xhci-sram`. `usb_boost` `usb-audio` | USB2 host path | **SUPPORTED** (USB2 host) |
| **Debug accessory (Rd/Rd, DBGACC_SNK)** | `TYPEC_ATTACHED_DEBUG` → rt_pd_manager HOST. DBGACC_SNK → sink. `en-ctd` cable type | — | handled as normal Type-C states. No CCD/debug-serial over SBU |
| **USB accessory (AOA)** | configfs `accessory.gs2` (GKI `USB_CONFIGFS_F_ACC=y`), PIDs 0x2d00–0x2d05 | gadget | **SUPPORTED** |
| **USB MIDI (gadget)** | `midi.gs5` (GKI `F_MIDI=y`), PID 0x2046/0x2048; KPOC `kpoc_midi` | gadget | **SUPPORTED** |
| **Ethernet gadget** | RNDIS `mtk_rndis.gs4` (vendor `mtk_usb_f_rndis` + `mtk_u_ether`, exact). NCM `ncm.gs6` (GKI). ECM/EEM built in GKI but not configured by init | gadget | RNDIS/NCM **SUPPORTED** |
| **USB Ethernet (host)** | GKI system_dlkm `usbnet`, `cdc_ether`, `cdc_ncm`, `cdc_eem`, `r8152`, `r8153_ecm`, `ax88179_178a`, `asix`, `aqc111`, `rtl8150` | USB2 host | **SUPPORTED** at USB2 speed |
| **UVC gadget** | GKI `USB_CONFIGFS_F_UVC=y` | not configured by stock init | available, unused |
| **Thermal camera (internal UVC host device)** | `extcon-mtk-usb` GPIO 28/55/152 + `yft_tiny2c_usb` rails | internal D± route | **SUPPORTED** (stock function) |
