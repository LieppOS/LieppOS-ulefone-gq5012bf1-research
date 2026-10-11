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
	{ 0x94a3f9c7, "of_property_read_variable_u32_array" },
	{ 0x7436d39e, "_dev_notice" },
	{ 0x656e4a6e, "snprintf" },
	{ 0xa4a78f74, "tcpc_dev_get_by_name" },
	{ 0x9c8c96c1, "tcpm_inquire_typec_role_def" },
	{ 0xc278a2d2, "typec_register_port" },
	{ 0xc473d041, "dev_fwnode" },
	{ 0xfa4bbd79, "fwnode_typec_mux_get" },
	{ 0x796a05c1, "register_tcp_dev_notifier" },
	{ 0xc2c193d2, "__stack_chk_fail" },
	{ 0x2be254c6, "typec_unregister_port" },
	{ 0xfc8df340, "typec_mux_put" },
	{ 0x83986f60, "unregister_tcp_dev_notifier" },
	{ 0xff8dc427, "typec_set_pwr_opmode" },
	{ 0x9c7b0769, "typec_set_data_role" },
	{ 0x2ceb5865, "typec_set_pwr_role" },
	{ 0x6ab0f93c, "tcpm_typec_change_role_postpone" },
	{ 0xb6bd1071, "typec_register_partner" },
	{ 0x6b3d9465, "typec_mux_set" },
	{ 0x3d4ba090, "typec_partner_set_pd_revision" },
	{ 0xb9d5c074, "typec_partner_set_svdm_version" },
	{ 0xdcd686b4, "tcpm_inquire_pd_partner_inform" },
	{ 0x273e101f, "typec_partner_set_identity" },
	{ 0x6d0ae7ae, "typec_set_vconn_role" },
	{ 0x7d728b62, "typec_set_orientation" },
	{ 0xed5bd3c5, "typec_unregister_partner" },
	{ 0xf97fc2d7, "typec_get_drvdata" },
	{ 0xb1c5baba, "tcpm_inquire_pd_data_role" },
	{ 0x45a43826, "tcpm_dpm_pd_data_swap" },
	{ 0x24809e23, "tcpm_inquire_pd_power_role" },
	{ 0x437928a2, "tcpm_dpm_pd_power_swap" },
	{ 0x6b2df008, "tcpm_typec_role_swap" },
	{ 0x50ccdfef, "tcpm_inquire_pd_vconn_role" },
	{ 0x4210d188, "tcpm_dpm_pd_vconn_swap" },
	{ 0xdad58a05, "tcpc_typec_is_act_as_sink_role" },
	{ 0xa3197555, "tcpm_typec_change_role" },
	{ 0xea759d7f, "module_layout" },
};

MODULE_INFO(depends, "tcpc_class");

MODULE_ALIAS("of:N*T*Cmediatek,rt-pd-manager");
MODULE_ALIAS("of:N*T*Cmediatek,rt-pd-managerC*");

MODULE_INFO(srcversion, "48B276D3F1DDD74E905394C");
