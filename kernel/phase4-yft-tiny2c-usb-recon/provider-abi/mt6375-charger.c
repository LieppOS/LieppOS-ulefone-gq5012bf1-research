// SPDX-License-Identifier: GPL-2.0
/*
 * Build-only ABI witness for the GQ5012BF1 mt6375-charger vendor delta.
 *
 * The real runtime provider is stock mt6375-charger.ko.  This deliberately
 * defines only the exact vendor-added data export consumed by
 * yft_tiny2c_usb.ko so genksyms/modpost derive its ABI naturally from C.
 * It must never be installed or loaded as a charger replacement.
 */
#include <linux/module.h>

int yft_usb_flag;
EXPORT_SYMBOL_GPL(yft_usb_flag);

MODULE_DESCRIPTION("Build-only ABI witness for stock mt6375-charger yft_usb_flag");
MODULE_LICENSE("GPL v2");
