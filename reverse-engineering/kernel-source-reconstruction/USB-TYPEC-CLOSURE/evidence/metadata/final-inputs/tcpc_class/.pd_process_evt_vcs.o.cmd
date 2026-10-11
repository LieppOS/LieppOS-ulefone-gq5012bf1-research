cmd_/home/armol/kernel-work/usb-typec-closure-01/src/kdm/drivers/misc/mediatek/typec/tcpc/pd_process_evt_vcs.o := clang -Wp,-MMD,/home/armol/kernel-work/usb-typec-closure-01/src/kdm/drivers/misc/mediatek/typec/tcpc/.pd_process_evt_vcs.o.d -nostdinc -I/home/armol/kernel-work/usb-typec-closure-01/src/kdm/include -I/home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include -I./arch/arm64/include/generated -I/home/armol/kernel-work/usb-typec-closure-01/common/include -I./include -I/home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/uapi -I./arch/arm64/include/generated/uapi -I/home/armol/kernel-work/usb-typec-closure-01/common/include/uapi -I./include/generated/uapi -include /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/compiler-version.h -include /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/kconfig.h -include /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/compiler_types.h -D__KERNEL__ -mlittle-endian -DKASAN_SHADOW_SCALE_SHIFT= -Qunused-arguments -fmacro-prefix-map=/home/armol/kernel-work/usb-typec-closure-01/common/= -Wall -Wundef -Werror=strict-prototypes -Wno-trigraphs -fno-strict-aliasing -fno-common -fshort-wchar -fno-PIE -Werror=implicit-function-declaration -Werror=implicit-int -Werror=return-type -Wno-format-security -std=gnu11 --target=aarch64-linux-gnu -fintegrated-as -Werror=unknown-warning-option -Werror=ignored-optimization-argument -mgeneral-regs-only -DCONFIG_CC_HAS_K_CONSTRAINT=1 -Wno-psabi -fasynchronous-unwind-tables -mbranch-protection=pac-ret -Wa,-march=armv8.5-a -DARM64_ASM_ARCH='"armv8.5-a"' -ffixed-x18 -DKASAN_SHADOW_SCALE_SHIFT= -fno-delete-null-pointer-checks -Wno-frame-address -Wno-address-of-packed-member -O2 -Wframe-larger-than=2048 -fstack-protector-strong -Wno-gnu -Wno-unused-but-set-variable -Wno-unused-const-variable -fno-omit-frame-pointer -fno-optimize-sibling-calls -ftrivial-auto-var-init=zero -fno-stack-clash-protection -fsanitize=kcfi -Wvla -Wno-pointer-sign -Wcast-function-type -Werror -Wimplicit-fallthrough -fno-strict-overflow -fno-stack-check -Werror=date-time -Werror=incompatible-pointer-types -Wno-initializer-overrides -Wno-sign-compare -Wno-pointer-to-enum-cast -Wno-tautological-constant-out-of-range-compare -Wno-unaligned-access -Wno-cast-function-type-strict -Wno-enum-compare-conditional -Wno-enum-enum-conversion -g -gdwarf-4 -D__ANDROID_COMMON_KERNEL__ -faddrsig -fmacro-prefix-map=/home/armol/kernel-work/usb-typec-closure-01/src/kdm/=../kernel_device_modules-6.1/ -mstack-protector-guard=sysreg -mstack-protector-guard-reg=sp_el0 -mstack-protector-guard-offset=1592 -Werror -I/home/armol/kernel-work/usb-typec-closure-01/src/kdm/include -I/home/armol/kernel-work/usb-typec-closure-01/src/kdm/include/uapi -I/home/armol/kernel-work/usb-typec-closure-01/src/kdm/drivers/misc/mediatek/typec/tcpc -Wall -Werror -DCONFIG_RT_REGMAP -I/home/armol/kernel-work/usb-typec-closure-01/src/kdm/drivers/power/supply/ -I/home/armol/kernel-work/usb-typec-closure-01/src/kdm/drivers/mfd/ -DCONFIG_RT_REGMAP=1 -DCONFIG_TCPC_CLASS_MODULE=1 -DCONFIG_USB_POWER_DELIVERY_MODULE=1 -DCONFIG_PD_DBG_INFO_MODULE=1 -DCONFIG_MTK_TYPEC_WATER_DETECT=1  -fsanitize=array-bounds -fsanitize=local-bounds -fsanitize-undefined-trap-on-error  -DMODULE  -DKBUILD_BASENAME='"pd_process_evt_vcs"' -DKBUILD_MODNAME='"tcpc_class"' -D__KBUILD_MODNAME=kmod_tcpc_class -c -o /home/armol/kernel-work/usb-typec-closure-01/src/kdm/drivers/misc/mediatek/typec/tcpc/pd_process_evt_vcs.o /home/armol/kernel-work/usb-typec-closure-01/src/kdm/drivers/misc/mediatek/typec/tcpc/pd_process_evt_vcs.c  

source_/home/armol/kernel-work/usb-typec-closure-01/src/kdm/drivers/misc/mediatek/typec/tcpc/pd_process_evt_vcs.o := /home/armol/kernel-work/usb-typec-closure-01/src/kdm/drivers/misc/mediatek/typec/tcpc/pd_process_evt_vcs.c

deps_/home/armol/kernel-work/usb-typec-closure-01/src/kdm/drivers/misc/mediatek/typec/tcpc/pd_process_evt_vcs.o := \
    $(wildcard include/config/USB_PD_VCONN_SWAP) \
    $(wildcard include/config/USB_PD_VCONN_READY_TOUT) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/compiler-version.h \
    $(wildcard include/config/CC_VERSION_TEXT) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/kconfig.h \
    $(wildcard include/config/CPU_BIG_ENDIAN) \
    $(wildcard include/config/BOOGER) \
    $(wildcard include/config/FOO) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/compiler_types.h \
    $(wildcard include/config/DEBUG_INFO_BTF) \
    $(wildcard include/config/PAHOLE_HAS_BTF_TAG) \
    $(wildcard include/config/HAVE_ARCH_COMPILER_H) \
    $(wildcard include/config/CC_HAS_ASM_INLINE) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/compiler_attributes.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/compiler-clang.h \
    $(wildcard include/config/ARCH_USE_BUILTIN_BSWAP) \
    $(wildcard include/config/CLANG_VERSION) \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/compiler.h \
  /home/armol/kernel-work/usb-typec-closure-01/src/kdm/drivers/misc/mediatek/typec/tcpc/inc/pd_core.h \
    $(wildcard include/config/USB_PD_REV30) \
    $(wildcard include/config/USB_PD_VCONN_SAFE5V_ONLY) \
    $(wildcard include/config/USB_PD_RENEGOTIATION_COUNTER) \
    $(wildcard include/config/USB_PD_KEEP_PARTNER_ID) \
    $(wildcard include/config/USB_PD_KEEP_SVIDS) \
    $(wildcard include/config/USB_PD_REV30_ALERT_REMOTE) \
    $(wildcard include/config/USB_PD_REV30_ALERT_LOCAL) \
    $(wildcard include/config/USB_PD_REV30_STATUS_LOCAL) \
    $(wildcard include/config/USB_PD_DISCARD_AND_UNEXPECT_MSG) \
    $(wildcard include/config/USB_PD_REV30_BAT_INFO) \
    $(wildcard include/config/USB_PD_REV30_COUNTRY_AUTHORITY) \
    $(wildcard include/config/USB_PD_ERROR_RECOVERY_ONCE) \
    $(wildcard include/config/USB_PD_IGNORE_PS_RDY_AFTER_PR_SWAP) \
    $(wildcard include/config/USB_PD_REV30_PPS_SINK) \
    $(wildcard include/config/USB_PD_CUSTOM_DBGACC) \
    $(wildcard include/config/USB_PD_TCPM_CB_2ND) \
    $(wildcard include/config/USB_PD_BLOCK_TCPM) \
    $(wildcard include/config/USB_PD_REV30_SRC_CAP_EXT_LOCAL) \
    $(wildcard include/config/USB_PD_REV30_MFRS_INFO_LOCAL) \
    $(wildcard include/config/USB_PD_REV30_STATUS_LOCAL_TEMP) \
    $(wildcard include/config/RECV_BAT_ABSENT_NOTIFY) \
    $(wildcard include/config/USB_PD_DIRECT_CHARGE) \
    $(wildcard include/config/USB_POWER_DELIVERY) \
    $(wildcard include/config/SUPPORT_SOUTHCHIP_PDPHY) \
  /home/armol/kernel-work/usb-typec-closure-01/src/kdm/drivers/misc/mediatek/typec/tcpc/inc/tcpci_timer.h \
    $(wildcard include/config/USB_PD_VCONN_STABLE_DELAY) \
    $(wildcard include/config/USB_PD_REV30_PPS_SOURCE) \
    $(wildcard include/config/USB_PD_SAFE0V_DELAY) \
    $(wildcard include/config/USB_PD_SAFE0V_TOUT) \
    $(wildcard include/config/USB_PD_SAFE5V_DELAY) \
    $(wildcard include/config/USB_PD_RETRY_CRC_DISCARD) \
    $(wildcard include/config/USB_PD_VBUS_STABLE_TOUT) \
    $(wildcard include/config/USB_PD_REV30_SNK_FLOW_DELAY_STARTUP) \
    $(wildcard include/config/USB_PD_WAIT_BC12) \
    $(wildcard include/config/WATER_DETECTION) \
    $(wildcard include/config/TYPEC_CAP_NORP_SRC) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/kernel.h \
    $(wildcard include/config/PREEMPT_VOLUNTARY_BUILD) \
    $(wildcard include/config/PREEMPT_DYNAMIC) \
    $(wildcard include/config/HAVE_PREEMPT_DYNAMIC_CALL) \
    $(wildcard include/config/HAVE_PREEMPT_DYNAMIC_KEY) \
    $(wildcard include/config/PREEMPT_) \
    $(wildcard include/config/DEBUG_ATOMIC_SLEEP) \
    $(wildcard include/config/SMP) \
    $(wildcard include/config/MMU) \
    $(wildcard include/config/PROVE_LOCKING) \
    $(wildcard include/config/TRACING) \
    $(wildcard include/config/FTRACE_MCOUNT_RECORD) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/stdarg.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/align.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/const.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/vdso/const.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/const.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/limits.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/limits.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/types.h \
    $(wildcard include/config/HAVE_UID16) \
    $(wildcard include/config/UID16) \
    $(wildcard include/config/ARCH_DMA_ADDR_T_64BIT) \
    $(wildcard include/config/PHYS_ADDR_T_64BIT) \
    $(wildcard include/config/64BIT) \
    $(wildcard include/config/ARCH_32BIT_USTAT_F_TINODE) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/types.h \
  arch/arm64/include/generated/uapi/asm/types.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/asm-generic/types.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/int-ll64.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/asm-generic/int-ll64.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/uapi/asm/bitsperlong.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/bitsperlong.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/asm-generic/bitsperlong.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/posix_types.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/stddef.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/stddef.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/uapi/asm/posix_types.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/asm-generic/posix_types.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/vdso/limits.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/linkage.h \
    $(wildcard include/config/ARCH_USE_SYM_ANNOTATIONS) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/stringify.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/export.h \
    $(wildcard include/config/MODVERSIONS) \
    $(wildcard include/config/HAVE_ARCH_PREL32_RELOCATIONS) \
    $(wildcard include/config/MODULES) \
    $(wildcard include/config/TRIM_UNUSED_KSYMS) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/compiler.h \
    $(wildcard include/config/TRACE_BRANCH_PROFILING) \
    $(wildcard include/config/PROFILE_ALL_BRANCHES) \
    $(wildcard include/config/OBJTOOL) \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/rwonce.h \
    $(wildcard include/config/LTO) \
    $(wildcard include/config/AS_HAS_LDAPR) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/rwonce.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/kasan-checks.h \
    $(wildcard include/config/KASAN_GENERIC) \
    $(wildcard include/config/KASAN_SW_TAGS) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/kcsan-checks.h \
    $(wildcard include/config/KCSAN) \
    $(wildcard include/config/KCSAN_WEAK_MEMORY) \
    $(wildcard include/config/KCSAN_IGNORE_ATOMICS) \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/linkage.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/container_of.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/build_bug.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/err.h \
  arch/arm64/include/generated/uapi/asm/errno.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/asm-generic/errno.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/asm-generic/errno-base.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/bitops.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/bits.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/vdso/bits.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/typecheck.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/kernel.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/sysinfo.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/bitops/generic-non-atomic.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/barrier.h \
    $(wildcard include/config/ARM64_PSEUDO_NMI) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/barrier.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/bitops.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/bitops/builtin-__ffs.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/bitops/builtin-ffs.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/bitops/builtin-__fls.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/bitops/builtin-fls.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/bitops/ffz.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/bitops/fls64.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/bitops/sched.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/bitops/hweight.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/bitops/arch_hweight.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/bitops/const_hweight.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/bitops/atomic.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/atomic.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/atomic.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/cmpxchg.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/lse.h \
    $(wildcard include/config/ARM64_LSE_ATOMICS) \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/atomic_ll_sc.h \
    $(wildcard include/config/CC_HAS_K_CONSTRAINT) \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/alternative.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/alternative-macros.h \
  arch/arm64/include/generated/asm/cpucaps.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/insn-def.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/brk-imm.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/init.h \
    $(wildcard include/config/STRICT_KERNEL_RWX) \
    $(wildcard include/config/STRICT_MODULE_RWX) \
    $(wildcard include/config/LTO_CLANG) \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/atomic_lse.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/atomic/atomic-arch-fallback.h \
    $(wildcard include/config/GENERIC_ATOMIC64) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/atomic/atomic-long.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/atomic/atomic-instrumented.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/instrumented.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/kmsan-checks.h \
    $(wildcard include/config/KMSAN) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/bitops/instrumented-atomic.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/bitops/lock.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/bitops/instrumented-lock.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/bitops/non-atomic.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/bitops/non-instrumented-non-atomic.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/bitops/le.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/uapi/asm/byteorder.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/byteorder/little_endian.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/byteorder/little_endian.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/swab.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/swab.h \
  arch/arm64/include/generated/uapi/asm/swab.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/asm-generic/swab.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/byteorder/generic.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/bitops/ext2-atomic-setbit.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/kstrtox.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/log2.h \
    $(wildcard include/config/ARCH_HAS_ILOG2_U32) \
    $(wildcard include/config/ARCH_HAS_ILOG2_U64) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/math.h \
  arch/arm64/include/generated/asm/div64.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/div64.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/minmax.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/panic.h \
    $(wildcard include/config/PANIC_TIMEOUT) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/printk.h \
    $(wildcard include/config/MESSAGE_LOGLEVEL_DEFAULT) \
    $(wildcard include/config/CONSOLE_LOGLEVEL_DEFAULT) \
    $(wildcard include/config/CONSOLE_LOGLEVEL_QUIET) \
    $(wildcard include/config/EARLY_PRINTK) \
    $(wildcard include/config/PRINTK) \
    $(wildcard include/config/PRINTK_INDEX) \
    $(wildcard include/config/DYNAMIC_DEBUG) \
    $(wildcard include/config/DYNAMIC_DEBUG_CORE) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/kern_levels.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/ratelimit_types.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/param.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/uapi/asm/param.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/param.h \
    $(wildcard include/config/HZ) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/asm-generic/param.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/spinlock_types_raw.h \
    $(wildcard include/config/DEBUG_SPINLOCK) \
    $(wildcard include/config/DEBUG_LOCK_ALLOC) \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/spinlock_types.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/qspinlock_types.h \
    $(wildcard include/config/NR_CPUS) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/qrwlock_types.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/lockdep_types.h \
    $(wildcard include/config/PROVE_RAW_LOCK_NESTING) \
    $(wildcard include/config/LOCKDEP) \
    $(wildcard include/config/LOCK_STAT) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/once_lite.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/static_call_types.h \
    $(wildcard include/config/HAVE_STATIC_CALL) \
    $(wildcard include/config/HAVE_STATIC_CALL_INLINE) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/instruction_pointer.h \
  /home/armol/kernel-work/usb-typec-closure-01/src/kdm/drivers/misc/mediatek/typec/tcpc/inc/tcpci_config.h \
    $(wildcard include/config/TYPEC_USE_DIS_VBUS_CTRL) \
    $(wildcard include/config/TYPEC_CAP_TRY_SOURCE) \
    $(wildcard include/config/TYPEC_CAP_DBGACC) \
    $(wildcard include/config/TYPEC_CAP_DBGACC_SNK) \
    $(wildcard include/config/TYPEC_ATTACHED_SRC_SAFE0V_DELAY) \
    $(wildcard include/config/TYPEC_ATTACHED_SRC_SAFE0V_TIMEOUT) \
    $(wildcard include/config/TYPEC_LEGACY3_ALWAYS_LOCAL_RP) \
    $(wildcard include/config/TYPEC_CAP_ROLE_SWAP) \
    $(wildcard include/config/TYPEC_CAP_DISCHARGE_TOUT) \
    $(wildcard include/config/TYPEC_CAP_FORCE_DISCHARGE) \
    $(wildcard include/config/TYPEC_CAP_EXT_DISCHARGE) \
    $(wildcard include/config/TYPEC_CAP_AUDIO_ACC_SINK_VBUS) \
    $(wildcard include/config/TYPEC_NOTIFY_ATTACHWAIT_SNK) \
    $(wildcard include/config/TYPEC_NOTIFY_ATTACHWAIT_SRC) \
    $(wildcard include/config/TYPEC_SNK_ONLY_WHEN_SUSPEND) \
    $(wildcard include/config/TCPC_LOG_WITH_PORT_NAME) \
    $(wildcard include/config/TCPC_DBG_PRESTR) \
    $(wildcard include/config/TCPC_WATCHDOG_EN) \
    $(wildcard include/config/SOUTHCHIP_INT_INVAILD_RETRY_MAX) \
    $(wildcard include/config/SOUTHCHIP_ERROR_MSG_CNT_MAX) \
    $(wildcard include/config/TYPEC_SNK_CURR_DFT) \
    $(wildcard include/config/TYPEC_SRC_CURR_DFT) \
    $(wildcard include/config/TYPEC_SNK_CURR_LIMIT) \
    $(wildcard include/config/TCPC_CLOCK_GATING) \
    $(wildcard include/config/TCPC_I2CRST_EN) \
    $(wildcard include/config/TCPC_SHUTDOWN_VBUS_DISABLE) \
    $(wildcard include/config/TCPC_NOTIFICATION_NON_BLOCKING) \
    $(wildcard include/config/PD_BEGUG_ON) \
    $(wildcard include/config/USB_PD_DR_SWAP) \
    $(wildcard include/config/USB_PD_PR_SWAP) \
    $(wildcard include/config/USB_PD_PE_SINK) \
    $(wildcard include/config/USB_PD_PE_SOURCE) \
    $(wildcard include/config/USB_PD_DISABLE_PE) \
    $(wildcard include/config/USB_PD_TCPM_CB_RETRY) \
    $(wildcard include/config/USB_PD_REV30_SRC_FLOW_DELAY_STARTUP) \
    $(wildcard include/config/USB_PD_REV30_SRC_CAP_EXT_REMOTE) \
    $(wildcard include/config/USB_PD_REV30_BAT_CAP_LOCAL) \
    $(wildcard include/config/USB_PD_REV30_BAT_CAP_REMOTE) \
    $(wildcard include/config/USB_PD_REV30_BAT_STATUS_LOCAL) \
    $(wildcard include/config/USB_PD_REV30_BAT_STATUS_REMOTE) \
    $(wildcard include/config/USB_PD_REV30_MFRS_INFO_REMOTE) \
    $(wildcard include/config/USB_PD_REV30_COUNTRY_CODE_LOCAL) \
    $(wildcard include/config/USB_PD_REV30_COUNTRY_CODE_REMOTE) \
    $(wildcard include/config/USB_PD_REV30_COUNTRY_INFO_LOCAL) \
    $(wildcard include/config/USB_PD_REV30_COUNTRY_INFO_REMOTE) \
    $(wildcard include/config/USB_PD_REV30_STATUS_REMOTE) \
    $(wildcard include/config/USB_PD_REV30_CHUNKING_BY_PE) \
    $(wildcard include/config/USB_PD_DPM_AUTO_SEND_ALERT) \
    $(wildcard include/config/USB_PD_DPM_AUTO_GET_STATUS) \
    $(wildcard include/config/USB_PD_DFP_FLOW_DELAY) \
    $(wildcard include/config/USB_PD_DFP_FLOW_DELAY_STARTUP) \
    $(wildcard include/config/USB_PD_DFP_FLOW_DELAY_DRSWAP) \
    $(wildcard include/config/USB_PD_DFP_FLOW_DELAY_RESET) \
    $(wildcard include/config/USB_PD_UFP_FLOW_DELAY) \
    $(wildcard include/config/USB_PD_ATTEMPT_DISCOVER_ID) \
    $(wildcard include/config/USB_PD_ATTEMPT_DISCOVER_SVIDS) \
    $(wildcard include/config/USB_PD_DISCOVER_CABLE_REQUEST_VCONN) \
    $(wildcard include/config/USB_PD_DISCOVER_CABLE_RETURN_VCONN) \
    $(wildcard include/config/USB_PD_PR_SWAP_ERROR_RECOVERY) \
    $(wildcard include/config/USB_PD_SNK_DFT_NO_GOOD_CRC) \
    $(wildcard include/config/USB_PD_CHECK_RX_PENDING_IF_SRTOUT) \
    $(wildcard include/config/USB_PD_IGNORE_HRESET_COMPLETE_TIMER) \
    $(wildcard include/config/USB_PD_RETRY_HRESET) \
    $(wildcard include/config/USB_PD_CHECK_DATA_ROLE) \
    $(wildcard include/config/USB_PD_PARTNER_CTRL_MSG_FIRST) \
    $(wildcard include/config/USB_PD_SNK_IGNORE_HRESET_IF_TYPEC_ONLY) \
    $(wildcard include/config/USB_PD_SRC_HIGHCAP_POWER) \
    $(wildcard include/config/USB_PD_SRC_TRY_PR_SWAP_IF_BAD_PW) \
    $(wildcard include/config/USB_PD_SRC_REJECT_PR_SWAP_IF_GOOD_PW) \
    $(wildcard include/config/USB_PD_DPM_SVDM_RETRY) \
    $(wildcard include/config/USB_PD_DFP_FLOW_RETRY_MAX) \
    $(wildcard include/config/USB_PD_CUSTOM_VDM_TOUT) \
    $(wildcard include/config/USB_PD_DFP_FLOW_DLY) \
    $(wildcard include/config/USB_PD_UFP_FLOW_DLY) \
    $(wildcard include/config/USB_PD_PPS_REQUEST_INTERVAL) \
    $(wildcard include/config/USB_PD_DBG_ALWAYS_LOCAL_RP) \
    $(wildcard include/config/USB_PD_DBG_IGRONE_TIMEOUT) \
    $(wildcard include/config/USB_PD_DBG_DP_DFP_D_AUTO_UPDATE) \
    $(wildcard include/config/USB_PD_DBG_DP_UFP_U_AUTO_UPDATE) \
    $(wildcard include/config/USB_PD_DBG_DP_UFP_U_AUTO_ATTENTION) \
    $(wildcard include/config/MTK_TYPEC_WATER_DETECT) \
    $(wildcard include/config/WD_SBU_CALIB_INIT) \
    $(wildcard include/config/WD_SBU_PL_BOUND) \
    $(wildcard include/config/WD_SBU_PL_LBOUND_C2C) \
    $(wildcard include/config/WD_SBU_PL_UBOUND_C2C) \
    $(wildcard include/config/WD_SBU_PL_RETRY) \
    $(wildcard include/config/WD_SBU_PH_RETRY) \
    $(wildcard include/config/WD_SBU_PH_AUDDEV) \
    $(wildcard include/config/WD_SBU_PH_LBOUND) \
    $(wildcard include/config/WD_SBU_PH_LBOUND1_C2C) \
    $(wildcard include/config/WD_SBU_PH_UBOUND1_C2C) \
    $(wildcard include/config/WD_SBU_PH_UBOUND2_C2C) \
    $(wildcard include/config/WD_SBU_AUD_UBOUND) \
    $(wildcard include/config/WD_PROTECT_RETRY_COUNT) \
    $(wildcard include/config/WD_DURING_PLUGGED_IN) \
    $(wildcard include/config/WD_SBU_PH_TITAN_LBOUND) \
    $(wildcard include/config/WD_SBU_PH_TITAN_UBOUND) \
    $(wildcard include/config/CABLE_TYPE_DETECTION) \
  /home/armol/kernel-work/usb-typec-closure-01/src/kdm/drivers/misc/mediatek/typec/tcpc/inc/tcpci_pd_config.h \
  /home/armol/kernel-work/usb-typec-closure-01/src/kdm/drivers/misc/mediatek/typec/tcpc/inc/tcpci_pd30_config.h \
  /home/armol/kernel-work/usb-typec-closure-01/src/kdm/drivers/misc/mediatek/typec/tcpc/inc/tcpci_event.h \
  /home/armol/kernel-work/usb-typec-closure-01/src/kdm/drivers/misc/mediatek/typec/tcpc/inc/tcpm.h \
    $(wildcard include/config/TYPEC_CAP_CUSTOM_SRC) \
    $(wildcard include/config/TCPC_CLASS) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/notifier.h \
    $(wildcard include/config/TREE_SRCU) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/errno.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/errno.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/mutex.h \
    $(wildcard include/config/PREEMPT_RT) \
    $(wildcard include/config/MUTEX_SPIN_ON_OWNER) \
    $(wildcard include/config/DEBUG_MUTEXES) \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/current.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/list.h \
    $(wildcard include/config/DEBUG_LIST) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/poison.h \
    $(wildcard include/config/ILLEGAL_POINTER_VALUE) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/spinlock_types.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/rwlock_types.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/lockdep.h \
    $(wildcard include/config/DEBUG_LOCKING_API_SELFTESTS) \
    $(wildcard include/config/PREEMPT_COUNT) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/smp.h \
    $(wildcard include/config/UP_LATE_INIT) \
    $(wildcard include/config/DEBUG_PREEMPT) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/cpumask.h \
    $(wildcard include/config/FORCE_NR_CPUS) \
    $(wildcard include/config/HOTPLUG_CPU) \
    $(wildcard include/config/DEBUG_PER_CPU_MAPS) \
    $(wildcard include/config/CPUMASK_OFFSTACK) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/threads.h \
    $(wildcard include/config/BASE_SMALL) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/bitmap.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/find.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/string.h \
    $(wildcard include/config/BINARY_PRINTF) \
    $(wildcard include/config/FORTIFY_SOURCE) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/overflow.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/string.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/string.h \
    $(wildcard include/config/ARCH_HAS_UACCESS_FLUSHCACHE) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/fortify-string.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/bug.h \
    $(wildcard include/config/GENERIC_BUG) \
    $(wildcard include/config/BUG_ON_DATA_CORRUPTION) \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/bug.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/asm-bug.h \
    $(wildcard include/config/DEBUG_BUGVERBOSE) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/bug.h \
    $(wildcard include/config/BUG) \
    $(wildcard include/config/GENERIC_BUG_RELATIVE_POINTERS) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/instrumentation.h \
    $(wildcard include/config/NOINSTR_VALIDATION) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/gfp_types.h \
    $(wildcard include/config/KASAN_HW_TAGS) \
    $(wildcard include/config/CMA) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/numa.h \
    $(wildcard include/config/NODES_SHIFT) \
    $(wildcard include/config/NUMA_KEEP_MEMINFO) \
    $(wildcard include/config/NUMA) \
    $(wildcard include/config/HAVE_ARCH_NODE_DEV_GROUP) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/smp_types.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/llist.h \
    $(wildcard include/config/ARCH_HAVE_NMI_SAFE_CMPXCHG) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/preempt.h \
    $(wildcard include/config/TRACE_PREEMPT_TOGGLE) \
    $(wildcard include/config/PREEMPTION) \
    $(wildcard include/config/PREEMPT_NOTIFIERS) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/cleanup.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/preempt.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/jump_label.h \
    $(wildcard include/config/JUMP_LABEL) \
    $(wildcard include/config/HAVE_ARCH_JUMP_LABEL_RELATIVE) \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/jump_label.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/insn.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/thread_info.h \
    $(wildcard include/config/THREAD_INFO_IN_TASK) \
    $(wildcard include/config/GENERIC_ENTRY) \
    $(wildcard include/config/HAVE_ARCH_WITHIN_STACK_FRAMES) \
    $(wildcard include/config/HARDENED_USERCOPY) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/restart_block.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/time64.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/math64.h \
    $(wildcard include/config/ARCH_SUPPORTS_INT128) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/vdso/math64.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/vdso/time64.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/time.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/time_types.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/thread_info.h \
    $(wildcard include/config/ARM64_SW_TTBR0_PAN) \
    $(wildcard include/config/SHADOW_CALL_STACK) \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/memory.h \
    $(wildcard include/config/ARM64_VA_BITS) \
    $(wildcard include/config/KASAN_SHADOW_OFFSET) \
    $(wildcard include/config/KASAN) \
    $(wildcard include/config/VMAP_STACK) \
    $(wildcard include/config/ARM64_4K_PAGES) \
    $(wildcard include/config/DEBUG_VIRTUAL) \
    $(wildcard include/config/ZONE_DMA) \
    $(wildcard include/config/ZONE_DMA32) \
    $(wildcard include/config/EFI) \
    $(wildcard include/config/ARM_GIC_V3_ITS) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/sizes.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/page-def.h \
    $(wildcard include/config/ARM64_PAGE_SHIFT) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/mmdebug.h \
    $(wildcard include/config/DEBUG_VM) \
    $(wildcard include/config/DEBUG_VM_IRQSOFF) \
    $(wildcard include/config/DEBUG_VM_PGFLAGS) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/memory_model.h \
    $(wildcard include/config/FLATMEM) \
    $(wildcard include/config/SPARSEMEM_VMEMMAP) \
    $(wildcard include/config/SPARSEMEM) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/pfn.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/stack_pointer.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/smp.h \
    $(wildcard include/config/ARM64_ACPI_PARKING_PROTOCOL) \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/percpu.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/sysreg.h \
    $(wildcard include/config/BROKEN_GAS_INST) \
    $(wildcard include/config/ARM64_PA_BITS_52) \
    $(wildcard include/config/ARM64_16K_PAGES) \
    $(wildcard include/config/ARM64_64K_PAGES) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/kasan-tags.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/gpr-num.h \
  arch/arm64/include/generated/asm/sysreg-defs.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/bitfield.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/percpu.h \
    $(wildcard include/config/HAVE_SETUP_PER_CPU_AREA) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/percpu-defs.h \
    $(wildcard include/config/DEBUG_FORCE_WEAK_PER_CPU) \
    $(wildcard include/config/AMD_MEM_ENCRYPT) \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/processor.h \
    $(wildcard include/config/COMPAT) \
    $(wildcard include/config/KUSER_HELPERS) \
    $(wildcard include/config/ARM64_FORCE_52BIT) \
    $(wildcard include/config/HAVE_HW_BREAKPOINT) \
    $(wildcard include/config/ARM64_PTR_AUTH) \
    $(wildcard include/config/ARM64_PTR_AUTH_KERNEL) \
    $(wildcard include/config/ARM64_MTE) \
    $(wildcard include/config/ARM64_TAGGED_ADDR_ABI) \
    $(wildcard include/config/GCC_PLUGIN_STACKLEAK) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/cache.h \
    $(wildcard include/config/ARCH_HAS_CACHE_LINE_SIZE) \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/cache.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/kasan-enabled.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/static_key.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/cputype.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/mte-def.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/android_vendor.h \
    $(wildcard include/config/ANDROID_VENDOR_OEM_DATA) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/android_kabi.h \
    $(wildcard include/config/ANDROID_KABI_RESERVE) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/vdso/processor.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/vdso/processor.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/cpufeature.h \
    $(wildcard include/config/ARM64_PAN) \
    $(wildcard include/config/ARM64_SVE) \
    $(wildcard include/config/ARM64_SME) \
    $(wildcard include/config/ARM64_CNP) \
    $(wildcard include/config/ARM64_DEBUG_PRIORITY_MASKING) \
    $(wildcard include/config/ARM64_BTI) \
    $(wildcard include/config/ARM64_TLB_RANGE) \
    $(wildcard include/config/ARM64_PA_BITS) \
    $(wildcard include/config/ARM64_HW_AFDBM) \
    $(wildcard include/config/ARM64_AMU_EXTN) \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/hwcap.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/uapi/asm/hwcap.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/hw_breakpoint.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/virt.h \
    $(wildcard include/config/KVM) \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/ptrace.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/uapi/asm/ptrace.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/uapi/asm/sve_context.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/sections.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/sections.h \
    $(wildcard include/config/HAVE_FUNCTION_DESCRIPTORS) \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/kasan.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/mte-kasan.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/pgtable-types.h \
    $(wildcard include/config/PGTABLE_LEVELS) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/pgtable-nopud.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/pgtable-nop4d.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/pgtable-hwdef.h \
    $(wildcard include/config/ARM64_CONT_PTE_SHIFT) \
    $(wildcard include/config/ARM64_CONT_PMD_SHIFT) \
    $(wildcard include/config/ARM64_VA_BITS_52) \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/pointer_auth.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/prctl.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/random.h \
    $(wildcard include/config/VMGENID) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/once.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/random.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/ioctl.h \
  arch/arm64/include/generated/uapi/asm/ioctl.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/ioctl.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/asm-generic/ioctl.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/irqnr.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/irqnr.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/prandom.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/percpu.h \
    $(wildcard include/config/NEED_PER_CPU_EMBED_FIRST_CHUNK) \
    $(wildcard include/config/NEED_PER_CPU_PAGE_FIRST_CHUNK) \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/archrandom.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/arm-smccc.h \
    $(wildcard include/config/ARM64) \
    $(wildcard include/config/HAVE_ARM_SMCCC) \
    $(wildcard include/config/ARM) \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/spectre.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/fpsimd.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/uapi/asm/sigcontext.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/osq_lock.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/debug_locks.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/rwsem.h \
    $(wildcard include/config/RWSEM_SPIN_ON_OWNER) \
    $(wildcard include/config/DEBUG_RWSEMS) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/spinlock.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/irqflags.h \
    $(wildcard include/config/TRACE_IRQFLAGS) \
    $(wildcard include/config/IRQSOFF_TRACER) \
    $(wildcard include/config/PREEMPT_TRACER) \
    $(wildcard include/config/DEBUG_IRQFLAGS) \
    $(wildcard include/config/TRACE_IRQFLAGS_SUPPORT) \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/irqflags.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/bottom_half.h \
  arch/arm64/include/generated/asm/mmiowb.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/mmiowb.h \
    $(wildcard include/config/MMIOWB) \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/spinlock.h \
  arch/arm64/include/generated/asm/qspinlock.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/qspinlock.h \
  arch/arm64/include/generated/asm/qrwlock.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/qrwlock.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/rwlock.h \
    $(wildcard include/config/PREEMPT) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/spinlock_api_smp.h \
    $(wildcard include/config/INLINE_SPIN_LOCK) \
    $(wildcard include/config/INLINE_SPIN_LOCK_BH) \
    $(wildcard include/config/INLINE_SPIN_LOCK_IRQ) \
    $(wildcard include/config/INLINE_SPIN_LOCK_IRQSAVE) \
    $(wildcard include/config/INLINE_SPIN_TRYLOCK) \
    $(wildcard include/config/INLINE_SPIN_TRYLOCK_BH) \
    $(wildcard include/config/UNINLINE_SPIN_UNLOCK) \
    $(wildcard include/config/INLINE_SPIN_UNLOCK_BH) \
    $(wildcard include/config/INLINE_SPIN_UNLOCK_IRQ) \
    $(wildcard include/config/INLINE_SPIN_UNLOCK_IRQRESTORE) \
    $(wildcard include/config/GENERIC_LOCKBREAK) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/rwlock_api_smp.h \
    $(wildcard include/config/INLINE_READ_LOCK) \
    $(wildcard include/config/INLINE_WRITE_LOCK) \
    $(wildcard include/config/INLINE_READ_LOCK_BH) \
    $(wildcard include/config/INLINE_WRITE_LOCK_BH) \
    $(wildcard include/config/INLINE_READ_LOCK_IRQ) \
    $(wildcard include/config/INLINE_WRITE_LOCK_IRQ) \
    $(wildcard include/config/INLINE_READ_LOCK_IRQSAVE) \
    $(wildcard include/config/INLINE_WRITE_LOCK_IRQSAVE) \
    $(wildcard include/config/INLINE_READ_TRYLOCK) \
    $(wildcard include/config/INLINE_WRITE_TRYLOCK) \
    $(wildcard include/config/INLINE_READ_UNLOCK) \
    $(wildcard include/config/INLINE_WRITE_UNLOCK) \
    $(wildcard include/config/INLINE_READ_UNLOCK_BH) \
    $(wildcard include/config/INLINE_WRITE_UNLOCK_BH) \
    $(wildcard include/config/INLINE_READ_UNLOCK_IRQ) \
    $(wildcard include/config/INLINE_WRITE_UNLOCK_IRQ) \
    $(wildcard include/config/INLINE_READ_UNLOCK_IRQRESTORE) \
    $(wildcard include/config/INLINE_WRITE_UNLOCK_IRQRESTORE) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/srcu.h \
    $(wildcard include/config/TINY_SRCU) \
    $(wildcard include/config/SRCU) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/rcupdate.h \
    $(wildcard include/config/PREEMPT_RCU) \
    $(wildcard include/config/TINY_RCU) \
    $(wildcard include/config/RCU_STRICT_GRACE_PERIOD) \
    $(wildcard include/config/RCU_LAZY) \
    $(wildcard include/config/TASKS_RCU_GENERIC) \
    $(wildcard include/config/RCU_STALL_COMMON) \
    $(wildcard include/config/NO_HZ_FULL) \
    $(wildcard include/config/KVM_XFER_TO_GUEST_WORK) \
    $(wildcard include/config/RCU_NOCB_CPU) \
    $(wildcard include/config/TASKS_RCU) \
    $(wildcard include/config/TASKS_TRACE_RCU) \
    $(wildcard include/config/TASKS_RUDE_RCU) \
    $(wildcard include/config/TREE_RCU) \
    $(wildcard include/config/DEBUG_OBJECTS_RCU_HEAD) \
    $(wildcard include/config/PROVE_RCU) \
    $(wildcard include/config/ARCH_WEAK_RELEASE_ACQUIRE) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/context_tracking_irq.h \
    $(wildcard include/config/CONTEXT_TRACKING_IDLE) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/rcutree.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/workqueue.h \
    $(wildcard include/config/DEBUG_OBJECTS_WORK) \
    $(wildcard include/config/FREEZER) \
    $(wildcard include/config/SYSFS) \
    $(wildcard include/config/WQ_WATCHDOG) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/timer.h \
    $(wildcard include/config/DEBUG_OBJECTS_TIMERS) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/ktime.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/time.h \
    $(wildcard include/config/POSIX_TIMERS) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/time32.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/timex.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/timex.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/timex.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/arch_timer.h \
    $(wildcard include/config/ARM_ARCH_TIMER_OOL_WORKAROUND) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/clocksource/arm_arch_timer.h \
    $(wildcard include/config/ARM_ARCH_TIMER) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/timecounter.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/timex.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/vdso/time32.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/vdso/time.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/jiffies.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/vdso/jiffies.h \
  include/generated/timeconst.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/vdso/ktime.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/timekeeping.h \
    $(wildcard include/config/GENERIC_CMOS_UPDATE) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/clocksource_ids.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/debugobjects.h \
    $(wildcard include/config/DEBUG_OBJECTS) \
    $(wildcard include/config/DEBUG_OBJECTS_FREE) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/rcu_segcblist.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/srcutree.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/rcu_node_tree.h \
    $(wildcard include/config/RCU_FANOUT) \
    $(wildcard include/config/RCU_FANOUT_LEAF) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/completion.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/swait.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/wait.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/wait.h \
  /home/armol/kernel-work/usb-typec-closure-01/src/kdm/drivers/misc/mediatek/typec/tcpc/inc/tcpm_pd.h \
    $(wildcard include/config/USB_PD_REV30_CHUNKING) \
  /home/armol/kernel-work/usb-typec-closure-01/src/kdm/drivers/misc/mediatek/typec/tcpc/inc/pd_dbg_info.h \
    $(wildcard include/config/PD_DBG_INFO) \
  /home/armol/kernel-work/usb-typec-closure-01/src/kdm/drivers/misc/mediatek/typec/tcpc/inc/pd_process_evt.h \
  /home/armol/kernel-work/usb-typec-closure-01/src/kdm/drivers/misc/mediatek/typec/tcpc/inc/tcpci.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/device.h \
    $(wildcard include/config/GENERIC_MSI_IRQ_DOMAIN) \
    $(wildcard include/config/GENERIC_MSI_IRQ) \
    $(wildcard include/config/ENERGY_MODEL) \
    $(wildcard include/config/PINCTRL) \
    $(wildcard include/config/DMA_OPS) \
    $(wildcard include/config/DMA_DECLARE_COHERENT) \
    $(wildcard include/config/DMA_CMA) \
    $(wildcard include/config/SWIOTLB) \
    $(wildcard include/config/ARCH_HAS_SYNC_DMA_FOR_DEVICE) \
    $(wildcard include/config/ARCH_HAS_SYNC_DMA_FOR_CPU) \
    $(wildcard include/config/ARCH_HAS_SYNC_DMA_FOR_CPU_ALL) \
    $(wildcard include/config/DMA_OPS_BYPASS) \
    $(wildcard include/config/PM_SLEEP) \
    $(wildcard include/config/OF) \
    $(wildcard include/config/DEVTMPFS) \
    $(wildcard include/config/SYSFS_DEPRECATED) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/dev_printk.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/ratelimit.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/sched.h \
    $(wildcard include/config/VIRT_CPU_ACCOUNTING_NATIVE) \
    $(wildcard include/config/SCHED_INFO) \
    $(wildcard include/config/SCHEDSTATS) \
    $(wildcard include/config/SCHED_CORE) \
    $(wildcard include/config/FAIR_GROUP_SCHED) \
    $(wildcard include/config/RT_GROUP_SCHED) \
    $(wildcard include/config/RT_MUTEXES) \
    $(wildcard include/config/UCLAMP_TASK) \
    $(wildcard include/config/UCLAMP_BUCKETS_COUNT) \
    $(wildcard include/config/KMAP_LOCAL) \
    $(wildcard include/config/CGROUP_SCHED) \
    $(wildcard include/config/BLK_DEV_IO_TRACE) \
    $(wildcard include/config/PSI) \
    $(wildcard include/config/MEMCG) \
    $(wildcard include/config/LRU_GEN) \
    $(wildcard include/config/COMPAT_BRK) \
    $(wildcard include/config/CGROUPS) \
    $(wildcard include/config/BLK_CGROUP) \
    $(wildcard include/config/PAGE_OWNER) \
    $(wildcard include/config/EVENTFD) \
    $(wildcard include/config/IOMMU_SVA) \
    $(wildcard include/config/CPU_SUP_INTEL) \
    $(wildcard include/config/TASK_DELAY_ACCT) \
    $(wildcard include/config/STACKPROTECTOR) \
    $(wildcard include/config/ARCH_HAS_SCALED_CPUTIME) \
    $(wildcard include/config/CPU_FREQ_TIMES) \
    $(wildcard include/config/VIRT_CPU_ACCOUNTING_GEN) \
    $(wildcard include/config/POSIX_CPUTIMERS) \
    $(wildcard include/config/POSIX_CPU_TIMERS_TASK_WORK) \
    $(wildcard include/config/KEYS) \
    $(wildcard include/config/SYSVIPC) \
    $(wildcard include/config/DETECT_HUNG_TASK) \
    $(wildcard include/config/IO_URING) \
    $(wildcard include/config/AUDIT) \
    $(wildcard include/config/AUDITSYSCALL) \
    $(wildcard include/config/UBSAN) \
    $(wildcard include/config/UBSAN_TRAP) \
    $(wildcard include/config/COMPACTION) \
    $(wildcard include/config/TASK_XACCT) \
    $(wildcard include/config/CPUSETS) \
    $(wildcard include/config/X86_CPU_RESCTRL) \
    $(wildcard include/config/FUTEX) \
    $(wildcard include/config/PERF_EVENTS) \
    $(wildcard include/config/NUMA_BALANCING) \
    $(wildcard include/config/RSEQ) \
    $(wildcard include/config/FAULT_INJECTION) \
    $(wildcard include/config/LATENCYTOP) \
    $(wildcard include/config/KUNIT) \
    $(wildcard include/config/FUNCTION_GRAPH_TRACER) \
    $(wildcard include/config/KCOV) \
    $(wildcard include/config/UPROBES) \
    $(wildcard include/config/BCACHE) \
    $(wildcard include/config/LIVEPATCH) \
    $(wildcard include/config/SECURITY) \
    $(wildcard include/config/BPF_SYSCALL) \
    $(wildcard include/config/X86_MCE) \
    $(wildcard include/config/KRETPROBES) \
    $(wildcard include/config/RETHOOK) \
    $(wildcard include/config/ARCH_HAS_PARANOID_L1D_FLUSH) \
    $(wildcard include/config/RV) \
    $(wildcard include/config/ARCH_TASK_STRUCT_ON_STACK) \
    $(wildcard include/config/PREEMPT_NONE) \
    $(wildcard include/config/PREEMPT_VOLUNTARY) \
    $(wildcard include/config/DEBUG_RSEQ) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/sched.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/pid.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/rculist.h \
    $(wildcard include/config/PROVE_RCU_LIST) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/refcount.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/sem.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/sem.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/ipc.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/uidgid.h \
    $(wildcard include/config/MULTIUSER) \
    $(wildcard include/config/USER_NS) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/highuid.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/rhashtable-types.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/ipc.h \
  arch/arm64/include/generated/uapi/asm/ipcbuf.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/asm-generic/ipcbuf.h \
  arch/arm64/include/generated/uapi/asm/sembuf.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/asm-generic/sembuf.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/shm.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/page.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/personality.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/personality.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/getorder.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/shm.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/asm-generic/hugetlb_encode.h \
  arch/arm64/include/generated/uapi/asm/shmbuf.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/asm-generic/shmbuf.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/shmparam.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/shmparam.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/kmsan_types.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/plist.h \
    $(wildcard include/config/DEBUG_PLIST) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/hrtimer.h \
    $(wildcard include/config/HIGH_RES_TIMERS) \
    $(wildcard include/config/TIME_LOW_RES) \
    $(wildcard include/config/TIMERFD) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/hrtimer_defs.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/rbtree.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/rbtree_types.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/seqlock.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/timerqueue.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/seccomp.h \
    $(wildcard include/config/SECCOMP) \
    $(wildcard include/config/HAVE_ARCH_SECCOMP_FILTER) \
    $(wildcard include/config/SECCOMP_FILTER) \
    $(wildcard include/config/CHECKPOINT_RESTORE) \
    $(wildcard include/config/SECCOMP_CACHE_DEBUG) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/seccomp.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/seccomp.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/unistd.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/uapi/asm/unistd.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/asm-generic/unistd.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/seccomp.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/unistd.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/nodemask.h \
    $(wildcard include/config/HIGHMEM) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/resource.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/resource.h \
  arch/arm64/include/generated/uapi/asm/resource.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/resource.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/asm-generic/resource.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/latencytop.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/sched/prio.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/sched/types.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/signal_types.h \
    $(wildcard include/config/OLD_SIGACTION) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/signal.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/signal.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/uapi/asm/signal.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/signal.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/asm-generic/signal.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/asm-generic/signal-defs.h \
  arch/arm64/include/generated/uapi/asm/siginfo.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/asm-generic/siginfo.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/syscall_user_dispatch.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/mm_types_task.h \
    $(wildcard include/config/ARCH_WANT_BATCHED_UNMAP_TLB_FLUSH) \
    $(wildcard include/config/SPLIT_PTLOCK_CPUS) \
    $(wildcard include/config/ARCH_ENABLE_SPLIT_PMD_PTLOCK) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/task_io_accounting.h \
    $(wildcard include/config/TASK_IO_ACCOUNTING) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/posix-timers.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/alarmtimer.h \
    $(wildcard include/config/RTC_CLASS) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/rseq.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/kcsan.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/rv.h \
    $(wildcard include/config/RV_REACTORS) \
  arch/arm64/include/generated/asm/kmap_size.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/kmap_size.h \
    $(wildcard include/config/DEBUG_KMAP_LOCAL) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/energy_model.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/kobject.h \
    $(wildcard include/config/UEVENT_HELPER) \
    $(wildcard include/config/DEBUG_KOBJECT_RELEASE) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/sysfs.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/kernfs.h \
    $(wildcard include/config/KERNFS) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/idr.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/radix-tree.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/xarray.h \
    $(wildcard include/config/XARRAY_MULTI) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/gfp.h \
    $(wildcard include/config/ZONE_DEVICE) \
    $(wildcard include/config/CONTIG_ALLOC) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/mmzone.h \
    $(wildcard include/config/ARCH_FORCE_MAX_ORDER) \
    $(wildcard include/config/MEMORY_ISOLATION) \
    $(wildcard include/config/SWAP) \
    $(wildcard include/config/TRANSPARENT_HUGEPAGE) \
    $(wildcard include/config/LRU_GEN_STATS) \
    $(wildcard include/config/MEMORY_HOTPLUG) \
    $(wildcard include/config/PAGE_EXTENSION) \
    $(wildcard include/config/DEFERRED_STRUCT_PAGE_INIT) \
    $(wildcard include/config/HAVE_MEMORYLESS_NODES) \
    $(wildcard include/config/SPARSEMEM_EXTREME) \
    $(wildcard include/config/HAVE_ARCH_PFN_VALID) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/list_nulls.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/pageblock-flags.h \
    $(wildcard include/config/HUGETLB_PAGE) \
    $(wildcard include/config/HUGETLB_PAGE_SIZE_VARIABLE) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/page-flags-layout.h \
  include/generated/bounds.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/sparsemem.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/mm_types.h \
    $(wildcard include/config/HAVE_ALIGNED_STRUCT_PAGE) \
    $(wildcard include/config/USERFAULTFD) \
    $(wildcard include/config/PER_VMA_LOCK) \
    $(wildcard include/config/HAVE_ARCH_COMPAT_MMAP_BASES) \
    $(wildcard include/config/MEMBARRIER) \
    $(wildcard include/config/AIO) \
    $(wildcard include/config/MMU_NOTIFIER) \
    $(wildcard include/config/KSM) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/auxvec.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/auxvec.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/uapi/asm/auxvec.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/kref.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/maple_tree.h \
    $(wildcard include/config/MAPLE_RCU_DISABLED) \
    $(wildcard include/config/DEBUG_MAPLE_TREE_VERBOSE) \
    $(wildcard include/config/DEBUG_MAPLE_TREE) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/uprobes.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/uprobes.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/debug-monitors.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/esr.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/probes.h \
    $(wildcard include/config/KPROBES) \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/mmu.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/page-flags.h \
    $(wildcard include/config/ARCH_USES_PG_UNCACHED) \
    $(wildcard include/config/MEMORY_FAILURE) \
    $(wildcard include/config/PAGE_IDLE_FLAG) \
    $(wildcard include/config/HUGETLB_PAGE_OPTIMIZE_VMEMMAP) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/local_lock.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/local_lock_internal.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/memory_hotplug.h \
    $(wildcard include/config/HAVE_ARCH_NODEDATA_EXTENSION) \
    $(wildcard include/config/ARCH_HAS_ADD_PAGES) \
    $(wildcard include/config/MEMORY_HOTREMOVE) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/topology.h \
    $(wildcard include/config/USE_PERCPU_NUMA_NODE_ID) \
    $(wildcard include/config/SCHED_SMT) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/arch_topology.h \
    $(wildcard include/config/ACPI_CPPC_LIB) \
    $(wildcard include/config/GENERIC_ARCH_TOPOLOGY) \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/topology.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/topology.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/sched/mm.h \
    $(wildcard include/config/ARCH_HAS_MEMBARRIER_CALLBACKS) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/sync_core.h \
    $(wildcard include/config/ARCH_HAS_SYNC_CORE_BEFORE_USERMODE) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/ioasid.h \
    $(wildcard include/config/IOASID) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/kobject_ns.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/stat.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/stat.h \
  arch/arm64/include/generated/uapi/asm/stat.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/asm-generic/stat.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/compat.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/compat.h \
    $(wildcard include/config/COMPAT_FOR_U64_ALIGNMENT) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/sched/task_stack.h \
    $(wildcard include/config/STACK_GROWSUP) \
    $(wildcard include/config/DEBUG_STACK_USAGE) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/magic.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/stat.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/sched/cpufreq.h \
    $(wildcard include/config/CPU_FREQ) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/sched/topology.h \
    $(wildcard include/config/SCHED_DEBUG) \
    $(wildcard include/config/SCHED_CLUSTER) \
    $(wildcard include/config/SCHED_MC) \
    $(wildcard include/config/CPU_FREQ_GOV_SCHEDUTIL) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/sched/idle.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/sched/sd_flags.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/ioport.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/klist.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/pm.h \
    $(wildcard include/config/VT_CONSOLE_SLEEP) \
    $(wildcard include/config/CXL_SUSPEND) \
    $(wildcard include/config/PM) \
    $(wildcard include/config/PM_CLK) \
    $(wildcard include/config/PM_GENERIC_DOMAINS) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/device/bus.h \
    $(wildcard include/config/ACPI) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/device/class.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/device/driver.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/module.h \
    $(wildcard include/config/MODULES_TREE_LOOKUP) \
    $(wildcard include/config/STACKTRACE_BUILD_ID) \
    $(wildcard include/config/ARCH_USES_CFI_TRAPS) \
    $(wildcard include/config/ARCH_WANTS_MODULES_DATA_IN_VMALLOC) \
    $(wildcard include/config/KALLSYMS) \
    $(wildcard include/config/TRACEPOINTS) \
    $(wildcard include/config/BPF_EVENTS) \
    $(wildcard include/config/DEBUG_INFO_BTF_MODULES) \
    $(wildcard include/config/EVENT_TRACING) \
    $(wildcard include/config/MODULE_UNLOAD) \
    $(wildcard include/config/CONSTRUCTORS) \
    $(wildcard include/config/FUNCTION_ERROR_INJECTION) \
    $(wildcard include/config/RETPOLINE) \
    $(wildcard include/config/MODULE_SIG) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/buildid.h \
    $(wildcard include/config/CRASH_CORE) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/kmod.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/umh.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/sysctl.h \
    $(wildcard include/config/SYSCTL) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/sysctl.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/elf.h \
    $(wildcard include/config/ARCH_USE_GNU_PROPERTY) \
    $(wildcard include/config/ARCH_HAVE_ELF_PROT) \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/elf.h \
    $(wildcard include/config/COMPAT_VDSO) \
  arch/arm64/include/generated/asm/user.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/user.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/elf.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/elf-em.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/fs.h \
    $(wildcard include/config/READ_ONLY_THP_FOR_FS) \
    $(wildcard include/config/FS_POSIX_ACL) \
    $(wildcard include/config/CGROUP_WRITEBACK) \
    $(wildcard include/config/IMA) \
    $(wildcard include/config/FILE_LOCKING) \
    $(wildcard include/config/FSNOTIFY) \
    $(wildcard include/config/FS_ENCRYPTION) \
    $(wildcard include/config/FS_VERITY) \
    $(wildcard include/config/EPOLL) \
    $(wildcard include/config/UNICODE) \
    $(wildcard include/config/QUOTA) \
    $(wildcard include/config/FS_DAX) \
    $(wildcard include/config/BLOCK) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/wait_bit.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/kdev_t.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/kdev_t.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/dcache.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/rculist_bl.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/list_bl.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/bit_spinlock.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/lockref.h \
    $(wildcard include/config/ARCH_USE_CMPXCHG_LOCKREF) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/stringhash.h \
    $(wildcard include/config/DCACHE_WORD_ACCESS) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/hash.h \
    $(wildcard include/config/HAVE_ARCH_HASH) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/path.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/list_lru.h \
    $(wildcard include/config/MEMCG_KMEM) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/shrinker.h \
    $(wildcard include/config/SHRINKER_DEBUG) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/capability.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/capability.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/semaphore.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/fcntl.h \
    $(wildcard include/config/ARCH_32BIT_OFF_T) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/fcntl.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/uapi/asm/fcntl.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/asm-generic/fcntl.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/openat2.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/migrate_mode.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/percpu-rwsem.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/rcuwait.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/sched/signal.h \
    $(wildcard include/config/SCHED_AUTOGROUP) \
    $(wildcard include/config/BSD_PROCESS_ACCT) \
    $(wildcard include/config/TASKSTATS) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/signal.h \
    $(wildcard include/config/DYNAMIC_SIGFRAME) \
    $(wildcard include/config/PROC_FS) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/sched/jobctl.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/sched/task.h \
    $(wildcard include/config/HAVE_EXIT_THREAD) \
    $(wildcard include/config/ARCH_WANTS_DYNAMIC_TASK_STRUCT) \
    $(wildcard include/config/HAVE_ARCH_THREAD_STRUCT_WHITELIST) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/uaccess.h \
    $(wildcard include/config/ARCH_HAS_SUBPAGE_FAULTS) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/fault-inject-usercopy.h \
    $(wildcard include/config/FAULT_INJECTION_USERCOPY) \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/uaccess.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/kernel-pgtable.h \
    $(wildcard include/config/RANDOMIZE_BASE) \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/boot.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/asm-extable.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/mte.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/extable.h \
    $(wildcard include/config/BPF_JIT) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/access_ok.h \
    $(wildcard include/config/ALTERNATE_USER_ADDRESS_SPACE) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/cred.h \
    $(wildcard include/config/DEBUG_CREDENTIALS) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/key.h \
    $(wildcard include/config/KEY_NOTIFICATIONS) \
    $(wildcard include/config/NET) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/assoc_array.h \
    $(wildcard include/config/ASSOCIATIVE_ARRAY) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/sched/user.h \
    $(wildcard include/config/VFIO_PCI_ZDEV_KVM) \
    $(wildcard include/config/WATCH_QUEUE) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/percpu_counter.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/rcu_sync.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/delayed_call.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/uuid.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/uuid.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/errseq.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/ioprio.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/sched/rt.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/iocontext.h \
    $(wildcard include/config/BLK_ICQ) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/ioprio.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/fs_types.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/mount.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/mnt_idmapping.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/slab.h \
    $(wildcard include/config/DEBUG_SLAB) \
    $(wildcard include/config/FAILSLAB) \
    $(wildcard include/config/KFENCE) \
    $(wildcard include/config/SLAB) \
    $(wildcard include/config/SLUB) \
    $(wildcard include/config/SLOB) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/percpu-refcount.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/kasan.h \
    $(wildcard include/config/KASAN_STACK) \
    $(wildcard include/config/KASAN_VMALLOC) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/fs.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/quota.h \
    $(wildcard include/config/QUOTA_NETLINK_INTERFACE) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/dqblk_xfs.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/dqblk_v1.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/dqblk_v2.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/dqblk_qtree.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/projid.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/quota.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/nfs_fs_i.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/moduleparam.h \
    $(wildcard include/config/ALPHA) \
    $(wildcard include/config/IA64) \
    $(wildcard include/config/PPC64) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/rbtree_latch.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/error-injection.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/error-injection.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/tracepoint-defs.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/module.h \
    $(wildcard include/config/ARM64_MODULE_PLTS) \
    $(wildcard include/config/DYNAMIC_FTRACE) \
    $(wildcard include/config/HAVE_MOD_ARCH_SPECIFIC) \
    $(wildcard include/config/ARM64_ERRATUM_843419) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/module.h \
    $(wildcard include/config/MODULES_USE_ELF_REL) \
    $(wildcard include/config/MODULES_USE_ELF_RELA) \
  /home/armol/kernel-work/usb-typec-closure-01/common/arch/arm64/include/asm/device.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/pm_wakeup.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/cpu.h \
    $(wildcard include/config/PM_SLEEP_SMP) \
    $(wildcard include/config/PM_SLEEP_SMP_NONZERO_CPU) \
    $(wildcard include/config/ARCH_HAS_CPU_FINALIZE_INIT) \
    $(wildcard include/config/HOTPLUG_SMT) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/node.h \
    $(wildcard include/config/HMEM_REPORTING) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/cpuhotplug.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/delay.h \
  arch/arm64/include/generated/asm/delay.h \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/asm-generic/delay.h \
  /home/armol/kernel-work/usb-typec-closure-01/src/kdm/drivers/misc/mediatek/typec/tcpc/inc/tcpci_core.h \
    $(wildcard include/config/TYPEC_NOTIFY_ATTACHWAIT) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/linux/platform_device.h \
    $(wildcard include/config/SUSPEND) \
    $(wildcard include/config/HIBERNATE_CALLBACKS) \
    $(wildcard include/config/SUPERH) \
  /home/armol/kernel-work/usb-typec-closure-01/common/include/uapi/linux/sched/types.h \
  /home/armol/kernel-work/usb-typec-closure-01/src/kdm/drivers/misc/mediatek/typec/tcpc/inc/std_tcpci_v10.h \
  /home/armol/kernel-work/usb-typec-closure-01/src/kdm/drivers/misc/mediatek/typec/tcpc/inc/pd_policy_engine.h \

/home/armol/kernel-work/usb-typec-closure-01/src/kdm/drivers/misc/mediatek/typec/tcpc/pd_process_evt_vcs.o: $(deps_/home/armol/kernel-work/usb-typec-closure-01/src/kdm/drivers/misc/mediatek/typec/tcpc/pd_process_evt_vcs.o)

$(deps_/home/armol/kernel-work/usb-typec-closure-01/src/kdm/drivers/misc/mediatek/typec/tcpc/pd_process_evt_vcs.o):
