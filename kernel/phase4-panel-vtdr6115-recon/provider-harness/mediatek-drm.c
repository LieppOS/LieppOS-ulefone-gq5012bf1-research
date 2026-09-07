// SPDX-License-Identifier: GPL-2.0
/* BUILD HARNESS ONLY; never ship or load. */
#include <linux/module.h>
#include <linux/export.h>
#include "mtk_panel_ext_stock_abi.h"

int ddic_dsi_send_cmd_for_fp(u8 *tx_buf, int size)
{
	return -ENODEV;
}
EXPORT_SYMBOL_GPL(ddic_dsi_send_cmd_for_fp);

MODULE_DESCRIPTION("LieppOS build harness for stock mediatek-drm symbol");
MODULE_LICENSE("GPL v2");
