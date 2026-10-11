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


static const struct modversion_info ____versions[]
__used __section("__versions") = {
	{ 0x894c433a, "__platform_driver_register" },
	{ 0xe1b15563, "platform_driver_unregister" },
	{ 0xef3cb484, "_dev_info" },
	{ 0xd50f026e, "devm_kmalloc" },
	{ 0x100b434b, "dev_get_regmap" },
	{ 0xf27ed00b, "_dev_err" },
	{ 0x4f49d69f, "device_property_read_string" },
	{ 0x752e64c4, "device_property_read_u32_array" },
	{ 0xd4b590ed, "device_property_present" },
	{ 0x7436d39e, "_dev_notice" },
	{ 0x253af43d, "delayed_work_timer_fn" },
	{ 0x79cf5987, "init_timer_key" },
	{ 0xa33a8bc2, "devm_iio_channel_get_all" },
	{ 0x126f9b9b, "tcpc_device_unregister" },
	{ 0xc2c193d2, "__stack_chk_fail" },
	{ 0x3ce4ca6f, "disable_irq" },
	{ 0x1c7ea990, "device_wakeup_disable" },
	{ 0x490c3055, "device_set_wakeup_capable" },
	{ 0xf8beca97, "cancel_delayed_work_sync" },
	{ 0x3b13f1ba, "tcpm_shutdown" },
	{ 0x8c0215f2, "pm_system_wakeup" },
	{ 0x16e9a06b, "tcpci_lock_typec" },
	{ 0xff65f0c0, "tcpci_is_plugged_in" },
	{ 0x7a0d7b35, "tcpci_unlock_typec" },
	{ 0x2d3385d3, "system_wq" },
	{ 0xbf57e89e, "queue_delayed_work_on" },
	{ 0x117b6a26, "tcpc_typec_handle_wd" },
	{ 0x6536e1a8, "tcpci_notify_vbus_short_cc_status" },
	{ 0xf0a933ca, "tcpc_device_register" },
	{ 0xc3055d20, "usleep_range_state" },
	{ 0x7923336f, "platform_get_irq_byname" },
	{ 0x88b197f, "device_wakeup_enable" },
	{ 0x570ef04, "devm_request_threaded_irq" },
	{ 0x1348649e, "alt_cb_patch_nops" },
	{ 0xfe487975, "init_wait_entry" },
	{ 0x8c26d495, "prepare_to_wait_event" },
	{ 0x1000e51, "schedule" },
	{ 0x92540fbf, "finish_wait" },
	{ 0xed962ff1, "regmap_bulk_read" },
	{ 0x6272e817, "regmap_bulk_write" },
	{ 0xcfc18bfc, "iio_read_channel_processed" },
	{ 0xf9a482f9, "msleep" },
	{ 0x30745b36, "tcpc_get_dev_data" },
	{ 0xeae3dfd6, "__const_udelay" },
	{ 0xa4a78f74, "tcpc_dev_get_by_name" },
	{ 0x48fb7437, "pd_dbg_info" },
	{ 0xdad58a05, "tcpc_typec_is_act_as_sink_role" },
	{ 0x4829a47e, "memcpy" },
	{ 0xd653b126, "sched_clock" },
	{ 0xab94724, "tcpci_alert_wakeup" },
	{ 0xc4f47221, "mod_delayed_work_on" },
	{ 0xcec4c0ab, "tcpc_typec_handle_fod" },
	{ 0xcbe57860, "tcpc_typec_handle_ctd" },
	{ 0x5bcd512c, "tcpc_typec_handle_otp" },
	{ 0x6f2d399b, "tcpci_notify_cc_hi" },
	{ 0x5f619089, "tcpci_notify_wd0_state" },
	{ 0xe088ef99, "pm_stay_awake" },
	{ 0x95642690, "tcpci_alert" },
	{ 0xf28b90d8, "pm_relax" },
	{ 0x1ccba3ae, "tcpm_suspend" },
	{ 0xf7af27dd, "tcpm_resume" },
	{ 0x446dd691, "tcpm_check_suspend_pending" },
	{ 0xea759d7f, "module_layout" },
};

MODULE_INFO(depends, "tcpc_class,pd_dbg_info");

MODULE_ALIAS("of:N*T*Cmediatek,mt6375-tcpc");
MODULE_ALIAS("of:N*T*Cmediatek,mt6375-tcpcC*");

MODULE_INFO(srcversion, "86B9C4E19D9B7E5A9933F96");
