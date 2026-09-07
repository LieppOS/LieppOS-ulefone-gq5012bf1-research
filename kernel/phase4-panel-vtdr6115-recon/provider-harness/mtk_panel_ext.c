// SPDX-License-Identifier: GPL-2.0
/* BUILD HARNESS ONLY; never ship or load. See README in the research report. */
#include <linux/module.h>
#include <linux/export.h>
#include "mtk_panel_ext_stock_abi.h"

int mtk_panel_ext_create(struct device *dev,
			 struct mtk_panel_params *ext_params,
			 struct mtk_panel_funcs *ext_funcs,
			 struct drm_panel *panel)
{
	return -ENODEV;
}
EXPORT_SYMBOL_GPL(mtk_panel_ext_create);

int mtk_panel_tch_handle_reg(struct drm_panel *panel)
{
	return -ENODEV;
}
EXPORT_SYMBOL_GPL(mtk_panel_tch_handle_reg);

struct mtk_panel_ext *find_panel_ext(struct drm_panel *panel)
{
	return NULL;
}
EXPORT_SYMBOL_GPL(find_panel_ext);

struct mtk_panel_ctx *find_panel_ctx(struct drm_panel *panel)
{
	return NULL;
}
EXPORT_SYMBOL_GPL(find_panel_ctx);

int mtk_panel_detach(struct mtk_panel_ctx *ctx)
{
	return -ENODEV;
}
EXPORT_SYMBOL_GPL(mtk_panel_detach);

void mtk_panel_remove(struct mtk_panel_ctx *ctx)
{
}
EXPORT_SYMBOL_GPL(mtk_panel_remove);

MODULE_DESCRIPTION("LieppOS build harness for stock mtk_panel_ext symbols");
MODULE_LICENSE("GPL v2");
