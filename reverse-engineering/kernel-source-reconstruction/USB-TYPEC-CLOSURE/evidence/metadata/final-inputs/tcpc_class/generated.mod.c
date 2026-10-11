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

SYMBOL_CRC(tcpc_class, 0xdeb57525, "_gpl");
SYMBOL_CRC(tcpc_dev_get_by_name, 0xa4a78f74, "");
SYMBOL_CRC(tcpc_device_register, 0xf0a933ca, "");
SYMBOL_CRC(tcpc_device_irq_enable, 0x44229091, "");
SYMBOL_CRC(register_tcp_dev_notifier, 0x796a05c1, "");
SYMBOL_CRC(unregister_tcp_dev_notifier, 0x83986f60, "");
SYMBOL_CRC(tcpc_device_unregister, 0x126f9b9b, "");
SYMBOL_CRC(tcpc_get_dev_data, 0x30745b36, "");
SYMBOL_CRC(tcpci_lock_typec, 0x16e9a06b, "");
SYMBOL_CRC(tcpci_unlock_typec, 0x7a0d7b35, "");
SYMBOL_CRC(tcpc_typec_is_act_as_sink_role, 0xdad58a05, "");
SYMBOL_CRC(tcpc_typec_error_recovery, 0xbd7bcade, "");
SYMBOL_CRC(tcpc_typec_handle_wd, 0x117b6a26, "");
SYMBOL_CRC(tcpc_typec_handle_fod, 0xcec4c0ab, "");
SYMBOL_CRC(tcpc_typec_handle_ctd, 0xcbe57860, "");
SYMBOL_CRC(tcpc_typec_handle_otp, 0x5bcd512c, "");
SYMBOL_CRC(tcpm_check_pd_attached, 0xf0497754, "");
SYMBOL_CRC(tcpm_shutdown, 0x3b13f1ba, "");
SYMBOL_CRC(tcpm_check_suspend_pending, 0x446dd691, "");
SYMBOL_CRC(tcpm_suspend, 0x1ccba3ae, "");
SYMBOL_CRC(tcpm_resume, 0xf7af27dd, "");
SYMBOL_CRC(tcpm_inquire_remote_cc, 0x199e53c1, "");
SYMBOL_CRC(tcpm_inquire_typec_remote_rp_curr, 0x02babb98, "");
SYMBOL_CRC(tcpm_inquire_vbus_level, 0x37ef7b78, "");
SYMBOL_CRC(tcpm_inquire_cc_high, 0xebbadc4e, "");
SYMBOL_CRC(tcpm_inquire_cc_polarity, 0xe720eb7f, "");
SYMBOL_CRC(tcpm_inquire_typec_attach_state, 0xcab3ee37, "");
SYMBOL_CRC(tcpm_inquire_typec_role, 0xcee1cb56, "");
SYMBOL_CRC(tcpm_inquire_typec_role_def, 0x9c8c96c1, "");
SYMBOL_CRC(tcpm_inquire_floating_ground, 0xdbce5440, "");
SYMBOL_CRC(tcpm_inquire_typec_local_rp, 0xcefae7f6, "");
SYMBOL_CRC(tcpm_inquire_sink_vbus, 0x4f493c37, "");
SYMBOL_CRC(tcpm_typec_set_usb_sink_curr, 0x36e7a45e, "");
SYMBOL_CRC(tcpm_typec_set_rp_level, 0x6cb2477c, "");
SYMBOL_CRC(tcpm_typec_role_swap, 0x6b2df008, "");
SYMBOL_CRC(tcpm_typec_change_role, 0xa3197555, "");
SYMBOL_CRC(tcpm_typec_change_role_postpone, 0x6ab0f93c, "");
SYMBOL_CRC(tcpm_typec_error_recovery, 0xb68783c0, "");
SYMBOL_CRC(tcpm_typec_disable_function, 0x68c572c5, "");
SYMBOL_CRC(tcpm_inquire_pd_connected, 0x49fa07f5, "");
SYMBOL_CRC(tcpm_inquire_pd_prev_connected, 0x30bc6f6c, "");
SYMBOL_CRC(tcpm_inquire_pd_data_role, 0xb1c5baba, "");
SYMBOL_CRC(tcpm_inquire_pd_power_role, 0x24809e23, "");
SYMBOL_CRC(tcpm_inquire_pd_vconn_role, 0x50ccdfef, "");
SYMBOL_CRC(tcpm_inquire_pd_pe_ready, 0xb71abcbe, "");
SYMBOL_CRC(tcpm_inquire_cable_current, 0x2c74218a, "");
SYMBOL_CRC(tcpm_inquire_dpm_flags, 0xbd5e066e, "");
SYMBOL_CRC(tcpm_inquire_dpm_caps, 0xc1b2c7ca, "");
SYMBOL_CRC(tcpm_set_dpm_caps, 0x9d660ee8, "");
SYMBOL_CRC(tcpm_inquire_pd_contract, 0xb239d489, "");
SYMBOL_CRC(tcpm_inquire_cable_inform, 0x471362c2, "");
SYMBOL_CRC(tcpm_inquire_pd_partner_inform, 0xdcd686b4, "");
SYMBOL_CRC(tcpm_inquire_pd_partner_svids, 0x5b8bf021, "");
SYMBOL_CRC(tcpm_inquire_pd_partner_modes, 0xed17f18e, "");
SYMBOL_CRC(tcpm_inquire_pd_source_cap, 0xd78524b9, "");
SYMBOL_CRC(tcpm_inquire_pd_sink_cap, 0x4d35dfc4, "");
SYMBOL_CRC(tcpm_extract_power_cap_val, 0xa4ed0801, "");
SYMBOL_CRC(tcpm_get_remote_power_cap, 0xcc419b11, "");
SYMBOL_CRC(tcpm_inquire_select_source_cap, 0xb323a3bc, "");
SYMBOL_CRC(tcpm_inquire_pd_local_source_cap, 0xeadaa01a, "");
SYMBOL_CRC(tcpm_set_pd_local_source_cap, 0x7fbfbdb2, "");
SYMBOL_CRC(tcpm_inquire_usb_comm, 0x0f8d710f, "");
SYMBOL_CRC(tcpm_dpm_pd_power_swap, 0x437928a2, "");
SYMBOL_CRC(tcpm_dpm_pd_data_swap, 0x45a43826, "");
SYMBOL_CRC(tcpm_dpm_pd_vconn_swap, 0x4210d188, "");
SYMBOL_CRC(tcpm_dpm_pd_goto_min, 0x93100a83, "");
SYMBOL_CRC(tcpm_dpm_pd_soft_reset, 0x6ebda707, "");
SYMBOL_CRC(tcpm_dpm_pd_get_source_cap, 0x14d2ce3b, "");
SYMBOL_CRC(tcpm_dpm_pd_get_sink_cap, 0x528d2060, "");
SYMBOL_CRC(tcpm_dpm_pd_source_cap, 0x2d5a5aa7, "");
SYMBOL_CRC(tcpm_dpm_pd_request, 0xa8b410ba, "");
SYMBOL_CRC(tcpm_dpm_pd_request_ex, 0x34acd0c8, "");
SYMBOL_CRC(tcpm_dpm_pd_bist_cm2, 0xc20588e0, "");
SYMBOL_CRC(tcpm_dpm_pd_get_source_cap_ext, 0xb6ec622c, "");
SYMBOL_CRC(tcpm_dpm_pd_get_sink_cap_ext, 0xaad83e9e, "");
SYMBOL_CRC(tcpm_dpm_pd_fast_swap, 0xec9d2311, "");
SYMBOL_CRC(tcpm_dpm_pd_get_status, 0x7735d6d0, "");
SYMBOL_CRC(tcpm_dpm_pd_get_pps_status_raw, 0xb960d4cc, "");
SYMBOL_CRC(tcpm_dpm_pd_get_pps_status, 0xd1aab2d6, "");
SYMBOL_CRC(tcpm_dpm_pd_get_country_code, 0xd9eb66b0, "");
SYMBOL_CRC(tcpm_dpm_pd_get_country_info, 0x971b93ea, "");
SYMBOL_CRC(tcpm_dpm_pd_get_bat_cap, 0xbf56bfc4, "");
SYMBOL_CRC(tcpm_dpm_pd_get_bat_status, 0xe33fe9dd, "");
SYMBOL_CRC(tcpm_dpm_pd_get_mfrs_info, 0x3e10364b, "");
SYMBOL_CRC(tcpm_dpm_pd_get_revision, 0x3c1cfe5e, "");
SYMBOL_CRC(tcpm_dpm_pd_alert, 0x28f52f0e, "");
SYMBOL_CRC(tcpm_dpm_pd_hard_reset, 0x7f5ea3f3, "");
SYMBOL_CRC(tcpm_dpm_pd_error_recovery, 0xe770bd0b, "");
SYMBOL_CRC(tcpm_dpm_pd_cable_soft_reset, 0x771fc41a, "");
SYMBOL_CRC(tcpm_dpm_vdm_discover_cable_id, 0x528333c2, "");
SYMBOL_CRC(tcpm_dpm_vdm_discover_id, 0xf77445cb, "");
SYMBOL_CRC(tcpm_dpm_vdm_discover_svids, 0x89bf4005, "");
SYMBOL_CRC(tcpm_dpm_vdm_discover_modes, 0x189cfb28, "");
SYMBOL_CRC(tcpm_dpm_vdm_enter_mode, 0x2f366773, "");
SYMBOL_CRC(tcpm_dpm_vdm_exit_mode, 0x1368c96a, "");
SYMBOL_CRC(tcpm_dpm_vdm_attention, 0x043872b5, "");
SYMBOL_CRC(tcpm_inquire_dp_ufp_u_state, 0x46fc970e, "");
SYMBOL_CRC(tcpm_dpm_dp_attention, 0x33812ecb, "");
SYMBOL_CRC(tcpm_inquire_dp_dfp_u_state, 0x394d483f, "");
SYMBOL_CRC(tcpm_dpm_dp_status_update, 0xfff28377, "");
SYMBOL_CRC(tcpm_dpm_dp_config, 0x45276bee, "");
SYMBOL_CRC(tcpm_dpm_send_custom_vdm, 0xcdfb631a, "");
SYMBOL_CRC(tcpm_notify_vbus_stable, 0x603cfdd0, "");
SYMBOL_CRC(tcpm_inquire_pd_charging_policy, 0xd5cfd1ba, "");
SYMBOL_CRC(tcpm_inquire_pd_charging_policy_default, 0x03227713, "");
SYMBOL_CRC(tcpm_reset_pd_charging_policy, 0x57923183, "");
SYMBOL_CRC(tcpm_set_pd_charging_policy_default, 0x874eef32, "");
SYMBOL_CRC(tcpm_set_pd_charging_policy, 0x0f28b446, "");
SYMBOL_CRC(tcpm_set_direct_charge_en, 0x5dba6153, "");
SYMBOL_CRC(tcpm_inquire_during_direct_charge, 0xc618c81a, "");
SYMBOL_CRC(tcpm_set_exit_attached_snk_via_cc, 0x4e6f1354, "");
SYMBOL_CRC(tcpm_inquire_exit_attached_snk_via_cc, 0x8c66241a, "");
SYMBOL_CRC(tcpm_dpm_set_vconn_supply_mode, 0x420fa2c1, "");
SYMBOL_CRC(tcpm_set_apdo_charging_policy, 0xe946efe4, "");
SYMBOL_CRC(tcpm_inquire_pd_source_apdo, 0x999c38ed, "");
SYMBOL_CRC(tcpm_inquire_during_pps_charge, 0x9d043f92, "");
SYMBOL_CRC(tcpm_update_bat_status_wh, 0x3dcae187, "");
SYMBOL_CRC(tcpm_update_bat_status_soc, 0xb5aacbfd, "");
SYMBOL_CRC(tcpm_update_bat_last_full, 0x3a0e76e2, "");
SYMBOL_CRC(tcpm_update_pd_status_temp, 0xa3a167fd, "");
SYMBOL_CRC(tcpm_update_pd_status_input, 0xf16e7281, "");
SYMBOL_CRC(tcpm_update_pd_status_bat_input, 0x880a60cc, "");
SYMBOL_CRC(tcpm_update_pd_status_event, 0x04130f4f, "");
SYMBOL_CRC(tcpm_dpm_bk_event_cb, 0x63d932d1, "");
SYMBOL_CRC(tcpci_check_vbus_valid_from_ic, 0x1e30120f, "");
SYMBOL_CRC(tcpci_set_auto_dischg_discnt, 0xd4b9bc46, "");
SYMBOL_CRC(tcpci_get_vbus_voltage, 0xec512987, "");
SYMBOL_CRC(tcpci_check_vsafe0v, 0x26e948fc, "");
SYMBOL_CRC(tcpci_alert_status_clear, 0x788a3803, "");
SYMBOL_CRC(tcpci_fault_status_clear, 0xbec72adc, "");
SYMBOL_CRC(tcpci_set_alert_mask, 0x505d5b8e, "");
SYMBOL_CRC(tcpci_get_alert_mask, 0xff6ff075, "");
SYMBOL_CRC(tcpci_get_alert_status_and_mask, 0x75558413, "");
SYMBOL_CRC(tcpci_get_fault_status, 0x5e34c435, "");
SYMBOL_CRC(tcpci_get_power_status, 0x5e80ab1e, "");
SYMBOL_CRC(tcpci_init, 0x8bfbd3f9, "");
SYMBOL_CRC(tcpci_init_alert_mask, 0x8bb1753a, "");
SYMBOL_CRC(tcpci_get_cc, 0x48cf18b4, "");
SYMBOL_CRC(tcpci_is_plugged_in, 0xff65f0c0, "");
SYMBOL_CRC(tcpci_set_cc, 0xfde7a48f, "");
SYMBOL_CRC(tcpci_set_polarity, 0xe69f7467, "");
SYMBOL_CRC(tcpci_set_vconn, 0x6a7dd1cf, "");
SYMBOL_CRC(tcpci_set_low_power_mode, 0x8b81bb3e, "");
SYMBOL_CRC(tcpci_alert_vendor_defined_handler, 0x3a4731ab, "");
SYMBOL_CRC(tcpci_set_water_protection, 0x2280d6ab, "");
SYMBOL_CRC(tcpci_notify_wd_status, 0xedd9c0dc, "");
SYMBOL_CRC(tcpci_notify_fod_status, 0xecae9c3c, "");
SYMBOL_CRC(tcpci_notify_cable_type, 0x302b11af, "");
SYMBOL_CRC(tcpci_notify_typec_otp, 0x3ab425d5, "");
SYMBOL_CRC(tcpci_set_cc_hidet, 0xe368aada, "");
SYMBOL_CRC(tcpci_notify_wd0_state, 0x5f619089, "");
SYMBOL_CRC(tcpci_set_vbus_short_cc, 0x36d857e0, "");
SYMBOL_CRC(tcpci_notify_vbus_short_cc_status, 0x6536e1a8, "");
SYMBOL_CRC(tcpci_set_msg_header, 0x03ba5edf, "");
SYMBOL_CRC(tcpci_set_rx_enable, 0x8b724f24, "");
SYMBOL_CRC(tcpci_protocol_reset, 0x62a802dd, "");
SYMBOL_CRC(tcpci_get_message, 0xff9630d6, "");
SYMBOL_CRC(tcpci_transmit, 0x5c1974d5, "");
SYMBOL_CRC(tcpci_retransmit, 0xbe96a2fd, "");
SYMBOL_CRC(tcpci_set_bist_test_mode, 0x9c2cb0ad, "");
SYMBOL_CRC(tcpci_notify_typec_state, 0x0751ed09, "");
SYMBOL_CRC(tcpci_notify_role_swap, 0x7619d508, "");
SYMBOL_CRC(tcpci_notify_pd_mode, 0xaec48cfa, "");
SYMBOL_CRC(tcpci_notify_pd_state, 0xa371f411, "");
SYMBOL_CRC(tcpci_source_vbus, 0xee4d2fec, "");
SYMBOL_CRC(tcpci_sink_vbus, 0xd6133696, "");
SYMBOL_CRC(tcpci_disable_vbus_control, 0x4aa18541, "");
SYMBOL_CRC(tcpci_notify_attachwait_state, 0x12a8a119, "");
SYMBOL_CRC(tcpci_notify_ps_change, 0x5b985b7a, "");
SYMBOL_CRC(tcpci_notify_cc_hi, 0x6f2d399b, "");
SYMBOL_CRC(tcpci_notify_hard_reset_state, 0x3977dd1f, "");
SYMBOL_CRC(tcpci_notify_wait_new_cap, 0xd5c47879, "");
SYMBOL_CRC(tcpci_enter_mode, 0x4f6b893b, "");
SYMBOL_CRC(tcpci_exit_mode, 0xd0332d3d, "");
SYMBOL_CRC(tcpci_report_hpd_state, 0xcd11100d, "");
SYMBOL_CRC(tcpci_dp_status_update, 0x87a731b7, "");
SYMBOL_CRC(tcpci_dp_configure, 0x63accb82, "");
SYMBOL_CRC(tcpci_dp_attention, 0xf8e86337, "");
SYMBOL_CRC(tcpci_dp_notify_status_update_done, 0xfdcd0aa4, "");
SYMBOL_CRC(tcpci_dp_notify_config_start, 0x6b5fcb7f, "");
SYMBOL_CRC(tcpci_dp_notify_config_done, 0xa48abb75, "");
SYMBOL_CRC(tcpci_notify_cvdm, 0x4119ed50, "");
SYMBOL_CRC(tcpci_notify_alert, 0x213ed051, "");
SYMBOL_CRC(tcpci_notify_status, 0x336b1946, "");
SYMBOL_CRC(tcpci_notify_request_bat_info, 0x23a05a24, "");
SYMBOL_CRC(tcpci_alert_wakeup, 0x0ab94724, "");
SYMBOL_CRC(tcpci_alert, 0x95642690, "");
SYMBOL_CRC(rt_regmap_cache_sync, 0x46dbb47f, "");
SYMBOL_CRC(rt_regmap_cache_write_back, 0x118a17cb, "");
SYMBOL_CRC(rt_is_reg_volatile, 0xa594bdbd, "");
SYMBOL_CRC(rt_get_regsize, 0xc3a2fd54, "");
SYMBOL_CRC(rt_regmap_reg_write, 0xcf29e746, "");
SYMBOL_CRC(rt_asyn_regmap_reg_write, 0xbe9b2de7, "");
SYMBOL_CRC(rt_regmap_reg_read, 0x74712284, "");
SYMBOL_CRC(rt_regmap_update_bits, 0xc337fa78, "");
SYMBOL_CRC(rt_regmap_block_write, 0x2d523528, "");
SYMBOL_CRC(rt_asyn_regmap_block_write, 0xcda46cf1, "");
SYMBOL_CRC(rt_regmap_block_read, 0x48fa9008, "");
SYMBOL_CRC(rt_cache_getlasterror, 0x74b3bd52, "");
SYMBOL_CRC(rt_cache_clrlasterror, 0xa58f9f3a, "");
SYMBOL_CRC(rt_regmap_cache_reload, 0xd63b75b4, "");
SYMBOL_CRC(rt_regmap_add_debugfs, 0x0f242b8b, "");
SYMBOL_CRC(rt_regmap_device_register_ex, 0x284eacb0, "");
SYMBOL_CRC(rt_regmap_device_unregister, 0x89435810, "");

static const struct modversion_info ____versions[]
__used __section("__versions") = {
	{ 0x6af5a23e, "class_find_device" },
	{ 0xe2d5255a, "strcmp" },
	{ 0x92997ed8, "_printk" },
	{ 0xd50f026e, "devm_kmalloc" },
	{ 0x49cd25ed, "alloc_workqueue" },
	{ 0xe9ff63e4, "srcu_init_notifier_head" },
	{ 0xa571f6b0, "__mutex_init" },
	{ 0xd9a5ea54, "__init_waitqueue_head" },
	{ 0x784f05c, "dev_set_name" },
	{ 0xdadf3a62, "device_set_of_node_from_dev" },
	{ 0xfa063de, "device_register" },
	{ 0x37a0cba, "kfree" },
	{ 0x490c3055, "device_set_wakeup_capable" },
	{ 0x88b197f, "device_wakeup_enable" },
	{ 0x253af43d, "delayed_work_timer_fn" },
	{ 0x79cf5987, "init_timer_key" },
	{ 0xd5977bfb, "mutex_lock" },
	{ 0xed55cabd, "mutex_unlock" },
	{ 0x60e98d99, "power_supply_get_by_name" },
	{ 0x136209db, "power_supply_reg_notifier" },
	{ 0x48fb7437, "pd_dbg_info" },
	{ 0x2d3385d3, "system_wq" },
	{ 0xbf57e89e, "queue_delayed_work_on" },
	{ 0xf45524a, "srcu_notifier_chain_register" },
	{ 0x7436d39e, "_dev_notice" },
	{ 0x8177f433, "devm_kfree" },
	{ 0x4bc97c17, "srcu_notifier_chain_unregister" },
	{ 0xd6b17cf1, "device_unregister" },
	{ 0x13f8371b, "__class_create" },
	{ 0x7f96615d, "class_create_file_ns" },
	{ 0x748c8ec0, "of_find_node_opts_by_path" },
	{ 0x9da9550a, "of_get_property" },
	{ 0xd5fc0938, "class_destroy" },
	{ 0xa90ee98, "sched_setscheduler_nocheck" },
	{ 0xc2c193d2, "__stack_chk_fail" },
	{ 0xd351924c, "power_supply_get_property" },
	{ 0x656e4a6e, "snprintf" },
	{ 0x98cf60b3, "strlen" },
	{ 0x85df9b6c, "strsep" },
	{ 0x5c3c7387, "kstrtoull" },
	{ 0xf27ed00b, "_dev_err" },
	{ 0xc3055d20, "usleep_range_state" },
	{ 0x34db050b, "_raw_spin_lock_irqsave" },
	{ 0xd35cce70, "_raw_spin_unlock_irqrestore" },
	{ 0xfeb6361a, "alarm_start_relative" },
	{ 0xf3295ffe, "alarm_try_to_cancel" },
	{ 0x203392c6, "mutex_trylock" },
	{ 0x1348649e, "alt_cb_patch_nops" },
	{ 0xb0f4ab9f, "kthread_create_on_node" },
	{ 0x73e2bcf1, "wake_up_process" },
	{ 0x1fbe3658, "alarm_init" },
	{ 0xb3f7646e, "kthread_should_stop" },
	{ 0xfe487975, "init_wait_entry" },
	{ 0x8c26d495, "prepare_to_wait_event" },
	{ 0x1000e51, "schedule" },
	{ 0x92540fbf, "finish_wait" },
	{ 0xe2964344, "__wake_up" },
	{ 0x4fa9ae5c, "kthread_stop" },
	{ 0x4829a47e, "memcpy" },
	{ 0x56470118, "__warn_printk" },
	{ 0x7f02188f, "__msecs_to_jiffies" },
	{ 0x8ddd8aad, "schedule_timeout" },
	{ 0xf15b38a, "kmalloc_caches" },
	{ 0xb78e7543, "kmalloc_trace" },
	{ 0x732ac580, "queue_work_on" },
	{ 0x15ba50a6, "jiffies" },
	{ 0xffae8e8b, "nsecs_to_jiffies" },
	{ 0x1148c0ea, "flush_delayed_work" },
	{ 0x7f24de73, "jiffies_to_usecs" },
	{ 0xcbd4898c, "fortify_panic" },
	{ 0x312514b5, "srcu_notifier_call_chain" },
	{ 0xd653b126, "sched_clock" },
	{ 0x1d24c881, "___ratelimit" },
	{ 0xf8beca97, "cancel_delayed_work_sync" },
	{ 0x6626afca, "down" },
	{ 0xef3cb484, "_dev_info" },
	{ 0xcf2a6966, "up" },
	{ 0xc4f47221, "mod_delayed_work_on" },
	{ 0x72b8adcd, "debugfs_create_file" },
	{ 0x6401ce4f, "debugfs_create_dir" },
	{ 0x6fb25926, "debugfs_remove" },
	{ 0x113858c3, "simple_write_to_buffer" },
	{ 0x6a6e05bf, "kstrtou8" },
	{ 0x4adb51eb, "single_open" },
	{ 0x4be4820, "seq_printf" },
	{ 0x18d2d657, "seq_puts" },
	{ 0xa916b694, "strnlen" },
	{ 0x9c81ceff, "simple_read_from_buffer" },
	{ 0x11f8a681, "seq_lseek" },
	{ 0xd963f308, "seq_read" },
	{ 0xe8f7183d, "single_release" },
	{ 0xc473e973, "of_find_node_by_name" },
	{ 0x94a3f9c7, "of_property_read_variable_u32_array" },
	{ 0x4956eb3e, "of_property_read_variable_u8_array" },
	{  0xc9569, "of_property_read_string" },
	{ 0xe35274a3, "of_find_property" },
	{ 0x819bebd4, "mutex_is_locked" },
	{ 0xe088ef99, "pm_stay_awake" },
	{ 0xf28b90d8, "pm_relax" },
	{ 0xdcb764ad, "memset" },
	{ 0xaafdc258, "strcasecmp" },
	{ 0xea759d7f, "module_layout" },
};

MODULE_INFO(depends, "pd_dbg_info");


MODULE_INFO(srcversion, "4D57E32A74284A7BDBD3C58");
