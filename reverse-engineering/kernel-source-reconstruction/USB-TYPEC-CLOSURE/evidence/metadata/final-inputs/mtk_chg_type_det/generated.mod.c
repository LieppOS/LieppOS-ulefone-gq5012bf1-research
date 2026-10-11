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
	{ 0xd50f026e, "devm_kmalloc" },
	{ 0x94a3f9c7, "of_property_read_variable_u32_array" },
	{ 0xd9a5ea54, "__init_waitqueue_head" },
	{ 0xa571f6b0, "__mutex_init" },
	{ 0xb0f4ab9f, "kthread_create_on_node" },
	{ 0x7436d39e, "_dev_notice" },
	{ 0x656e4a6e, "snprintf" },
	{  0xc9569, "of_property_read_string" },
	{ 0x899a2701, "get_charger_by_name" },
	{ 0xddd61e77, "devm_power_supply_get_by_phandle" },
	{ 0xa4a78f74, "tcpc_dev_get_by_name" },
	{ 0x796a05c1, "register_tcp_dev_notifier" },
	{ 0x73e2bcf1, "wake_up_process" },
	{ 0xef3cb484, "_dev_info" },
	{ 0xc2c193d2, "__stack_chk_fail" },
	{ 0x4fa9ae5c, "kthread_stop" },
	{ 0x83986f60, "unregister_tcp_dev_notifier" },
	{ 0xcab3ee37, "tcpm_inquire_typec_attach_state" },
	{ 0xf8d710f, "tcpm_inquire_usb_comm" },
	{ 0xcc419b11, "tcpm_get_remote_power_cap" },
	{ 0xa163536d, "charger_dev_enable_discharge" },
	{ 0xb3f7646e, "kthread_should_stop" },
	{ 0xed55cabd, "mutex_unlock" },
	{ 0xd5977bfb, "mutex_lock" },
	{ 0x1348649e, "alt_cb_patch_nops" },
	{ 0x54344be5, "power_supply_set_property" },
	{ 0xfe487975, "init_wait_entry" },
	{ 0x8c26d495, "prepare_to_wait_event" },
	{ 0x92540fbf, "finish_wait" },
	{ 0x1000e51, "schedule" },
	{ 0xe2964344, "__wake_up" },
	{ 0xea759d7f, "module_layout" },
};

MODULE_INFO(depends, "charger_class,tcpc_class");

MODULE_ALIAS("of:N*T*Cmediatek,mtk_ctd");
MODULE_ALIAS("of:N*T*Cmediatek,mtk_ctdC*");

MODULE_INFO(srcversion, "F2C230777ABCBB6B44AEE0B");
