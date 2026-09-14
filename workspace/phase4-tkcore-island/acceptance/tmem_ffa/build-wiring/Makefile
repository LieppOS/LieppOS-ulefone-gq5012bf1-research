# Exact-GKI out-of-tree build of the MediaTek trusted-memory subsystem module
# tmem_ffa (GQ5012BF1 stock vendor_dlkm module, load index V:152).
#
# src/ is a byte-identical copy of
#   nothing-mt6878/device_modules/drivers/misc/mediatek/trusted_mem/
# at pinned device_modules 957dac185efe46cbf6336b0fff9516d84c8cd78f - the same
# revision that produced the already-source-closed ffa_v10.ko.
#
# inc/ holds the byte-identical external vendor headers the trusted_mem
# Makefile pulls in through -I paths at that same revision:
#   inc/kree, inc/tz_cross  <- drivers/misc/mediatek/geniezone/public/
#   inc/teec                <- drivers/tee/teei/510/common/include/
#
# The object list is the vendor Makefile's tmem_ffa-y list with the stock
# device's proven config set (see BUILD.bazel and the RED report).  No driver
# source is modified; only build plumbing lives in this file.
ifneq ($(KERNELRELEASE),)

TMEM_SRC := $(srctree)/$(src)/src

# stock tmem_ffa.ko carries .llvm_addrsig (vendor built with -faddrsig)
ccflags-y += -faddrsig

ccflags-y += -DCONFIG_MTK_TRUSTED_MEMORY_SUBSYSTEM=1
ccflags-y += -DCONFIG_MTK_ENABLE_GENIEZONE=1
ccflags-y += -DCONFIG_ARM_FFA_TRANSPORT=1
ccflags-y += -DCONFIG_MTK_GZ_KREE=1
ccflags-y += -DCONFIG_MTK_SECURE_MEM_SUPPORT=1
ccflags-y += -DCONFIG_MTK_WFD_SMEM_SUPPORT=1
ccflags-y += -DCONFIG_MTK_PROT_MEM_SUPPORT=1
ccflags-y += -DCONFIG_MTK_SEC_VIDEO_PATH_SUPPORT=1
ccflags-y += -DCONFIG_ALLOC_TMEM_WITH_HIGH_FREQ=1
ccflags-y += -DCONFIG_MTK_PROT_MEM_SSHEAP_V2=1
ccflags-y += -DCONFIG_MICROTRUST_TEE_SUPPORT=1
ccflags-y += -DTEE_DEVICES_SUPPORT
ccflags-y += -DMTEE_DEVICES_SUPPORT

ccflags-y += -I$(TMEM_SRC)
ccflags-y += -I$(TMEM_SRC)/public
ccflags-y += -I$(TMEM_SRC)/ssmr
ccflags-y += -I$(TMEM_SRC)/ssheap
ccflags-y += -I$(TMEM_SRC)/tmemperf
# Phase 3F: the common TrustKernel authority precedes the frozen donor copy so
# the single #include "tee_client_api.h" resolves to the island authority.
ccflags-y += -I$(srctree)/$(src)/include/trustkernel
ccflags-y += -I$(srctree)/$(src)/include
ccflags-y += -I$(srctree)/$(src)/inc
ccflags-y += -I$(srctree)/$(src)/inc/teec

obj-m += tmem_ffa.o
tmem_ffa-y += src/dev_mgr.o
tmem_ffa-y += src/entry.o
tmem_ffa-y += src/region_mgr.o
tmem_ffa-y += src/ssmr_mgr.o
tmem_ffa-y += src/peer_mgr.o
tmem_ffa-y += src/proc.o
tmem_ffa-y += src/ssheap_proc.o
tmem_ffa-y += src/alloc_api.o
tmem_ffa-y += src/ssmr/memory_ssmr.o
tmem_ffa-y += src/ssheap/ssheap_lib.o
tmem_ffa-y += src/tmemperf/tmemperf.o
tmem_ffa-y += src/tee_devices.o
tmem_ffa-y += src/tee_impl/tee_invoke.o
tmem_ffa-y += src/tee_impl/tee_ops.o
tmem_ffa-y += src/mtee_devices.o
tmem_ffa-y += src/mtee_impl/mtee_ops.o
tmem_ffa-y += src/mtee_impl/mtee_invoke.o
tmem_ffa-y += src/mtee_impl/tmem_ffa.o

# Phase-3F provider ABI records - ALL natural, zero stock witnesses:
#   //lieppos/tkcore-island  final reconstructed tkcore (7 TEEC_* edges)
#   //lieppos/ffa-v10        real source-built FF-A provider
#   //lieppos/gz-tz-system   real source-built GenieZone provider (9 KREE_* edges)
LIEPPOS_TKCORE_SYMVERS := \
	$(wildcard $(COMMON_OUT_DIR)/lieppos/tkcore-island/Module.symvers)
LIEPPOS_FFA_SYMVERS := \
	$(wildcard $(COMMON_OUT_DIR)/lieppos/ffa-v10/Module.symvers)
LIEPPOS_GZ_SYMVERS := \
	$(wildcard $(COMMON_OUT_DIR)/lieppos/gz-tz-system/Module.symvers)
KBUILD_EXTRA_SYMBOLS += $(LIEPPOS_TKCORE_SYMVERS) $(LIEPPOS_FFA_SYMVERS) $(LIEPPOS_GZ_SYMVERS)

else
.PHONY: all modules modules_install clean
all modules:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) modules
modules_install:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) modules_install
clean:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) clean
endif
