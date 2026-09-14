# GQ5012BF1 — extcon-mtk-usb source search (Phase 3)

Static/offline only. No device was touched.

Target: `extcon-mtk-usb.ko`, sha256
`9e6adf23de6729f9983f680be75c8aca9eabe22aa6efcaafe7704257b37cb2bf`, 46864 bytes,
vermagic `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64`.

## 1. Searched token set

`extcon-mtk-usb`, `extcon_mtk_usb`, `mediatek,extcon-usb`, `yft_usb_flag`,
`uvc_insert_status`, `tiny2c_mode`, `uvc_switch_gpio`, `uvc_vbus_gpio`,
`otg_gpio_select`, `bypss-typec-sink`, `YFT_OTG_yft_otg_gpio`,
`mtk_usb_extcon_set_role`, `mtk_usb_idpin_handle`, `vbus_limit_cur`,
`smt_u2_cc_mode`.

## 2. Result: the device's own source drop does NOT contain this driver

The Ulefone/UsMart kernel source drop (`Fibo_Fone_P3226`, 164 archives) ships **no
extcon driver at all**. It declares `CONFIG_USB_CTRL_MT6800_CHARGER_CON` in
`drivers/extcon/Kconfig` + `Makefile` but provides neither the Kconfig symbol nor
the `.c` file, so that tree's extcon `obj-*` resolves to nothing.

Consequence: closure cannot come from a Ulefone source diff. It must come from a
donor plus the stock binary.

## 3. Donor located (pinned revisions match the task spec exactly)

```
tree      /home/armol/androido_dalykai/LieppOS custom ROM/kernel-research/nothing-mt6878
device_modules  957dac185efe46cbf6336b0fff9516d84c8cd78f   (matches pinned)
kernel_modules  5f75a3b13e8135d45b4b0b70ec893345144f70df   (matches pinned)
kernel          d6343dbbb3eaeaf4a2a52d6ef6a30501a09ea464

file      device_modules/drivers/misc/mediatek/extcon/extcon-mtk-usb.c
lines     758
sha256    ad7a82001ff8f8820582ed2af2f02c7a7cdc9f50f6b2f990380b06e4c0fcc16f
header    device_modules/drivers/misc/mediatek/extcon/extcon-mtk-usb.h
```

## 4. Why this donor and not generic upstream extcon

The stock `.ko` is **not stripped**: its `.symtab` carries the vendor's real
function names with exact offsets and sizes. 17 of the donor's 19 functions
appear in the stock symbol table under identical names, and every donor string
and call sequence is present in stock `.text`. Generic upstream
`drivers/extcon/*` shares none of this naming (`mtk_usb_extcon_*`,
`mtk_extcon_tcpc_notifier`, `usb_cc_smt_procfs_*`) and was therefore **not** used
as an exact donor.

## 5. Classification

**`SOURCE_DELTA_REQUIRED`**

The donor is the correct upstream-of-vendor code base but is not the shipped
source: the Ulefone build adds a YFT/thermal-camera delta (5 extra functions,
13 extra imports) and drops the donor's `charger_class` path. The measured
delta is in `phase4-extcon-mtk-usb-RED.md`.

| candidate | verdict |
|---|---|
| UsMart `Fibo_Fone_P3226` drop | NO_USEFUL_SOURCE (driver absent) |
| Nothing MT6878 `device_modules` v17 donor | SOURCE_DELTA_REQUIRED (adopted) |
| generic upstream `drivers/extcon` | STRUCTURAL_DONOR_ONLY (not used) |
