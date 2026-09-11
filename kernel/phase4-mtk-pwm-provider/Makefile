ifneq ($(KERNELRELEASE),)
ccflags-y += -I$(srctree)/../lieppos/mtk-pwm-provider/include
ccflags-y += -I$(srctree)/../lieppos/mtk-pwm-provider/pwm_v2/include
obj-m += mtk-pwm.o
mtk-pwm-y := mtk_pwm.o pwm_v2/mtk_pwm_hal.o
else
.PHONY: all modules modules_install clean
all modules:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) modules
modules_install:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) modules_install
clean:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) clean
endif
