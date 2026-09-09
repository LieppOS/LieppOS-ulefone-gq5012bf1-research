/* SPDX-License-Identifier: GPL-2.0 */
/*
 * GQ5012BF1 stock charger_class consumer ABI.
 *
 * The callback order through get_adc_accuracy is proven by the stock
 * sc8571_charger.ko relocation slots.  The total size (81 pointers) is proven
 * by its 648-byte sc8571_chg_ops object.  charger_device::driver_data at 0xe0
 * is proven by every stock mtk_sc8571_* callback.
 */
#ifndef _CHARGER_CLASS_STOCK_ABI_H
#define _CHARGER_CLASS_STOCK_ABI_H

#include <linux/device.h>
#include <linux/types.h>

enum adc_channel {
	ADC_CHANNEL_VBUS,
	ADC_CHANNEL_VSYS,
	ADC_CHANNEL_VBAT,
	ADC_CHANNEL_IBUS,
	ADC_CHANNEL_IBAT,
	ADC_CHANNEL_TEMP_JC,
	ADC_CHANNEL_USBID,
	ADC_CHANNEL_TS,
	ADC_CHANNEL_TBAT,
	ADC_CHANNEL_VOUT,
};

struct charger_properties {
	const char *alias_name;
};

struct charger_ops;

/* Only the stock-consumer-visible member is materialized. */
struct charger_device {
	u8 __stock_private[0xe0];
	void *driver_data;
};

struct charger_ops {
	int (*suspend)(struct charger_device *, pm_message_t);
	int (*resume)(struct charger_device *);
	int (*plug_in)(struct charger_device *);
	int (*plug_out)(struct charger_device *);
	int (*enable)(struct charger_device *, bool);
	int (*is_enabled)(struct charger_device *, bool *);
	int (*enable_chip)(struct charger_device *, bool);
	int (*is_chip_enabled)(struct charger_device *, bool *);
	int (*get_charging_current)(struct charger_device *, u32 *);
	int (*set_charging_current)(struct charger_device *, u32);
	int (*get_min_charging_current)(struct charger_device *, u32 *);
	int (*set_constant_voltage)(struct charger_device *, u32);
	int (*get_constant_voltage)(struct charger_device *, u32 *);
	int (*get_input_current)(struct charger_device *, u32 *);
	int (*set_input_current)(struct charger_device *, u32);
	int (*get_min_input_current)(struct charger_device *, u32 *);
	int (*set_boot_volt_times)(struct charger_device *, u32);
	int (*get_eoc_current)(struct charger_device *, u32 *);
	int (*set_eoc_current)(struct charger_device *, u32);
	int (*kick_wdt)(struct charger_device *);
	int (*event)(struct charger_device *, u32, u32);
	int (*enable_6pin_battery_charging)(struct charger_device *, bool);
	int (*send_ta_current_pattern)(struct charger_device *, bool);
	int (*send_ta20_current_pattern)(struct charger_device *, u32);
	int (*reset_ta)(struct charger_device *);
	int (*enable_cable_drop_comp)(struct charger_device *, bool);
	int (*set_mivr)(struct charger_device *, u32);
	int (*get_mivr)(struct charger_device *, u32 *);
	int (*get_mivr_state)(struct charger_device *, bool *);
	int (*is_powerpath_enabled)(struct charger_device *, bool *);
	int (*enable_powerpath)(struct charger_device *, bool);
	int (*enable_vbus_ovp)(struct charger_device *, bool);
	int (*is_safety_timer_enabled)(struct charger_device *, bool *);
	int (*enable_safety_timer)(struct charger_device *, bool);
	int (*enable_termination)(struct charger_device *, bool);
	int (*enable_direct_charging)(struct charger_device *, bool);
	int (*kick_direct_charging_wdt)(struct charger_device *);
	int (*set_direct_charging_ibusoc)(struct charger_device *, u32);
	int (*set_direct_charging_vbusov)(struct charger_device *, u32);
	int (*set_ibusocp)(struct charger_device *, u32);
	int (*set_vbusovp)(struct charger_device *, u32);
	int (*set_ibatocp)(struct charger_device *, u32);
	int (*set_vbatovp)(struct charger_device *, u32);
	int (*set_vbatovp_alarm)(struct charger_device *, u32);
	int (*reset_vbatovp_alarm)(struct charger_device *);
	int (*set_vbusovp_alarm)(struct charger_device *, u32);
	int (*reset_vbusovp_alarm)(struct charger_device *);
	int (*is_vbuslowerr)(struct charger_device *, bool *);
	int (*init_chip)(struct charger_device *);
	int (*enable_auto_trans)(struct charger_device *, bool);
	int (*set_auto_trans)(struct charger_device *, u32, bool);
	int (*set_operation_mode)(struct charger_device *, bool);
	int (*enable_otg)(struct charger_device *, bool);
	int (*enable_discharge)(struct charger_device *, bool);
	int (*set_boost_current_limit)(struct charger_device *, u32);
	int (*get_boost_current_limit)(struct charger_device *, u32 *);
	int (*get_boost_voltage_limit)(struct charger_device *, u32 *);
	int (*enable_chg_type_det)(struct charger_device *, bool);
	int (*run_aicl)(struct charger_device *, u32 *);
	int (*reset_eoc_state)(struct charger_device *);
	int (*safety_check)(struct charger_device *, u32);
	int (*is_charging_done)(struct charger_device *, bool *);
	int (*set_pe20_efficiency_table)(struct charger_device *);
	int (*dump_registers)(struct charger_device *);
	int (*get_adc)(struct charger_device *, enum adc_channel, int *, int *);
	int (*get_adc_accuracy)(struct charger_device *, enum adc_channel,
				int *, int *);
	int (*get_vbus_adc)(struct charger_device *, u32 *);
	int (*get_ibus_adc)(struct charger_device *, u32 *);
	int (*get_ibat_adc)(struct charger_device *, u32 *);
	int (*get_tchg_adc)(struct charger_device *, int *, int *);
	int (*get_zcv)(struct charger_device *, u32 *);
	int (*enable_usbid)(struct charger_device *, bool);
	int (*set_usbid_rup)(struct charger_device *, u32);
	int (*set_usbid_src_ton)(struct charger_device *, u32);
	int (*enable_usbid_floating)(struct charger_device *, bool);
	int (*enable_force_typec_otp)(struct charger_device *, bool);
	int (*enable_hidden_mode)(struct charger_device *, bool);
	int (*get_ctd_dischg_status)(struct charger_device *, u8 *);
	int (*enable_hz)(struct charger_device *, bool);
	int (*set_vac_ovp)(struct charger_device *, u32);
	int (*enable_vac_otgovp)(struct charger_device *, bool);
};

static inline void *charger_dev_get_drvdata(const struct charger_device *dev)
{
	return dev->driver_data;
}

extern struct charger_device *charger_device_register(
	const char *name, struct device *parent, void *devdata,
	const struct charger_ops *ops, const struct charger_properties *props);

#endif
