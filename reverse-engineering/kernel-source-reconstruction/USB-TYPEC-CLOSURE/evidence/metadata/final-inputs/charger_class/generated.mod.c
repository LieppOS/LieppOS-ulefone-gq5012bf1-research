#include <linux/module.h>
#define INCLUDE_VERMAGIC
#include <linux/build-salt.h>
#include <linux/elfnote-lto.h>
#include <linux/export-internal.h>
#include <linux/vermagic.h>
#include <linux/compiler.h>

BUILD_SALT;
BUILD_LTO_INFO;

MODULE_INFO(vermagic, VERMAGIC_STRING);
MODULE_INFO(name, KBUILD_MODNAME);

__visible struct module __this_module
__section(".gnu.linkonce.this_module") = {
	.name = KBUILD_MODNAME,
	.init = init_module,
#ifdef CONFIG_MODULE_UNLOAD
	.exit = cleanup_module,
#endif
	.arch = MODULE_ARCH_INIT,
};

#ifdef CONFIG_RETPOLINE
MODULE_INFO(retpoline, "Y");
#endif

SYMBOL_CRC(charger_dev_enable, 0x30f0a568, "");
SYMBOL_CRC(charger_dev_is_enabled, 0x83734472, "");
SYMBOL_CRC(charger_dev_plug_in, 0x68d0b3f1, "");
SYMBOL_CRC(charger_dev_plug_out, 0x0ee593e7, "");
SYMBOL_CRC(charger_dev_do_event, 0xfa33b1df, "");
SYMBOL_CRC(charger_dev_enable_6pin_battery_charging, 0x55864a91, "");
SYMBOL_CRC(charger_dev_set_charging_current, 0x38139a75, "");
SYMBOL_CRC(charger_dev_get_charging_current, 0x83f875c9, "");
SYMBOL_CRC(charger_dev_get_min_charging_current, 0x56aa04f5, "");
SYMBOL_CRC(charger_dev_enable_chip, 0xc79cf02e, "");
SYMBOL_CRC(charger_dev_is_chip_enabled, 0xb5b1e481, "");
SYMBOL_CRC(charger_dev_enable_direct_charging, 0x6e87ec57, "");
SYMBOL_CRC(charger_dev_kick_direct_charging_wdt, 0xfa0f9c8f, "");
SYMBOL_CRC(charger_dev_get_vbus, 0x4c7b93c7, "");
SYMBOL_CRC(charger_dev_get_ibus, 0xd137f7e5, "");
SYMBOL_CRC(charger_dev_get_ibat, 0x5b3d2a6c, "");
SYMBOL_CRC(charger_dev_get_temperature, 0xf04c17bf, "");
SYMBOL_CRC(charger_dev_set_input_current, 0x73649ecd, "");
SYMBOL_CRC(charger_dev_get_input_current, 0x14c5cf3a, "");
SYMBOL_CRC(charger_dev_get_min_input_current, 0x18d0d07d, "");
SYMBOL_CRC(charger_dev_set_boot_volt_times, 0x8e92060b, "");
SYMBOL_CRC(charger_dev_set_eoc_current, 0xb2be25af, "");
SYMBOL_CRC(charger_dev_get_eoc_current, 0x814aef5c, "");
SYMBOL_CRC(charger_dev_kick_wdt, 0x285a24b8, "");
SYMBOL_CRC(charger_dev_set_constant_voltage, 0x1d135760, "");
SYMBOL_CRC(charger_dev_get_constant_voltage, 0x519808d0, "");
SYMBOL_CRC(charger_dev_dump_registers, 0xe683969d, "");
SYMBOL_CRC(charger_dev_is_charging_done, 0xe054553b, "");
SYMBOL_CRC(charger_dev_enable_vbus_ovp, 0x144f98cc, "");
SYMBOL_CRC(charger_dev_set_mivr, 0x705c85fa, "");
SYMBOL_CRC(charger_dev_get_mivr, 0x2c7745f2, "");
SYMBOL_CRC(charger_dev_enable_powerpath, 0x38ff0c31, "");
SYMBOL_CRC(charger_dev_is_powerpath_enabled, 0x69b96d90, "");
SYMBOL_CRC(charger_dev_enable_safety_timer, 0xe589c421, "");
SYMBOL_CRC(charger_dev_enable_hz, 0xf7820c10, "");
SYMBOL_CRC(charger_dev_set_vac_ovp, 0x7d805a4b, "");
SYMBOL_CRC(charger_dev_get_adc, 0x9982b04a, "");
SYMBOL_CRC(charger_dev_get_adc_accuracy, 0x397c881b, "");
SYMBOL_CRC(charger_dev_is_safety_timer_enabled, 0x0bce9b49, "");
SYMBOL_CRC(charger_dev_enable_termination, 0x4ef224f1, "");
SYMBOL_CRC(charger_dev_get_mivr_state, 0x66aa5b1c, "");
SYMBOL_CRC(charger_dev_send_ta_current_pattern, 0x7f17ba39, "");
SYMBOL_CRC(charger_dev_send_ta20_current_pattern, 0xbafdd76e, "");
SYMBOL_CRC(charger_dev_reset_ta, 0xa8e49cd4, "");
SYMBOL_CRC(charger_dev_set_pe20_efficiency_table, 0xa111168d, "");
SYMBOL_CRC(charger_dev_enable_cable_drop_comp, 0x5368820d, "");
SYMBOL_CRC(charger_dev_set_direct_charging_ibusoc, 0xe1730955, "");
SYMBOL_CRC(charger_dev_set_direct_charging_vbusov, 0x00f26e51, "");
SYMBOL_CRC(charger_dev_set_ibusocp, 0xec115415, "");
SYMBOL_CRC(charger_dev_set_vbusovp, 0xeb9d116b, "");
SYMBOL_CRC(charger_dev_set_ibatocp, 0x78ff654c, "");
SYMBOL_CRC(charger_dev_set_vbatovp, 0x7f732032, "");
SYMBOL_CRC(charger_dev_set_vbatovp_alarm, 0xefcb2590, "");
SYMBOL_CRC(charger_dev_reset_vbatovp_alarm, 0x87f95baf, "");
SYMBOL_CRC(charger_dev_set_vbusovp_alarm, 0x94b1cbbe, "");
SYMBOL_CRC(charger_dev_reset_vbusovp_alarm, 0x13176af6, "");
SYMBOL_CRC(charger_dev_is_vbuslowerr, 0x9f1a72b3, "");
SYMBOL_CRC(charger_dev_init_chip, 0xf4d52ef8, "");
SYMBOL_CRC(charger_dev_enable_auto_trans, 0x7a2d1b43, "");
SYMBOL_CRC(charger_dev_set_auto_trans, 0x62d66174, "");
SYMBOL_CRC(charger_dev_set_operation_mode, 0xd3dd00ae, "");
SYMBOL_CRC(charger_dev_enable_chg_type_det, 0xb5e7aa5a, "");
SYMBOL_CRC(charger_dev_enable_otg, 0x7e0563df, "");
SYMBOL_CRC(charger_dev_is_otg_enabled, 0x6acef963, "");
SYMBOL_CRC(charger_dev_enable_discharge, 0xa163536d, "");
SYMBOL_CRC(charger_dev_set_boost_current_limit, 0x6bd62bf6, "");
SYMBOL_CRC(charger_dev_get_zcv, 0x811b2170, "");
SYMBOL_CRC(charger_dev_run_aicl, 0xfe14941f, "");
SYMBOL_CRC(charger_dev_reset_eoc_state, 0xf362e95e, "");
SYMBOL_CRC(charger_dev_safety_check, 0x418cf3f1, "");
SYMBOL_CRC(charger_dev_notify, 0x11061b4c, "");
SYMBOL_CRC(charger_dev_enable_usbid, 0x5eb62234, "");
SYMBOL_CRC(charger_dev_set_usbid_rup, 0x94c1487e, "");
SYMBOL_CRC(charger_dev_set_usbid_src_ton, 0x28d8acc9, "");
SYMBOL_CRC(charger_dev_enable_usbid_floating, 0x8ac8972d, "");
SYMBOL_CRC(charger_dev_enable_force_typec_otp, 0xb802fc50, "");
SYMBOL_CRC(charger_dev_get_ctd_dischg_status, 0xa39824fc, "");
SYMBOL_CRC(charger_dev_enable_hidden_mode, 0xcb79ed9a, "");
SYMBOL_CRC(charger_dev_set_property, 0x6e4e1b23, "");
SYMBOL_CRC(charger_dev_get_property, 0x2be26d0d, "");
SYMBOL_CRC(register_charger_device_notifier, 0xc95804ab, "");
SYMBOL_CRC(unregister_charger_device_notifier, 0x687cdabe, "");
SYMBOL_CRC(charger_device_register, 0x36325d38, "");
SYMBOL_CRC(charger_device_unregister, 0xd5fda38f, "");
SYMBOL_CRC(get_charger_by_name, 0x899a2701, "");

static const struct modversion_info ____versions[]
__used __section("__versions") = {
	{ 0x312514b5, "srcu_notifier_call_chain" },
	{ 0xf45524a, "srcu_notifier_chain_register" },
	{ 0x4bc97c17, "srcu_notifier_chain_unregister" },
	{ 0xf15b38a, "kmalloc_caches" },
	{ 0xb78e7543, "kmalloc_trace" },
	{ 0xe9ff63e4, "srcu_init_notifier_head" },
	{ 0xa571f6b0, "__mutex_init" },
	{ 0x784f05c, "dev_set_name" },
	{ 0xfa063de, "device_register" },
	{ 0x37a0cba, "kfree" },
	{ 0xd5977bfb, "mutex_lock" },
	{ 0xed55cabd, "mutex_unlock" },
	{ 0xd6b17cf1, "device_unregister" },
	{ 0x6af5a23e, "class_find_device" },
	{ 0xe2d5255a, "strcmp" },
	{ 0x13f8371b, "__class_create" },
	{ 0x92997ed8, "_printk" },
	{ 0xd5fc0938, "class_destroy" },
	{ 0x656e4a6e, "snprintf" },
	{ 0xea759d7f, "module_layout" },
};

MODULE_INFO(depends, "");


MODULE_INFO(srcversion, "66ADA0AAEAEA649866AF7A8");
