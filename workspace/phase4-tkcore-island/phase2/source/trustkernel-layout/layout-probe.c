// SPDX-License-Identifier: GPL-2.0
/*
 * TrustKernel island layout probe.
 *
 * Analysis-only module: no driver behaviour.  It forces the compiler to
 * evaluate every layout assertion in trustkernel/layout-assert.h against the
 * real exact-GKI headers, so a wrong offset in the reconstructed type graph
 * breaks the build instead of silently shipping a wrong type graph.
 */
#include <linux/module.h>

#include <trustkernel/layout-assert.h>

static int __init tk_layout_probe_init(void)
{
	return 0;
}

static void __exit tk_layout_probe_exit(void)
{
}

module_init(tk_layout_probe_init);
module_exit(tk_layout_probe_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("LieppOS TrustKernel island layout probe (analysis only)");
