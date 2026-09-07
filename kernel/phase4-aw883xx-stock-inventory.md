# Phase 1 — stock ELF inventory: aw883xx_driver.ko

Oracle SHA256 3bc4722c6550abb9cfd75d06602c2a1bff8d0b6af58708324479ef6a0d22c9b4, 331808 bytes.

## Section summary
idx  name                               type              addr              offset  size    entsize  flags
0    NULL                               0000000000000000  000000            000000  00      0        0
1    __ksymtab                          PROGBITS          0000000000000000  000040  000018  00       A
2    __kcrctab                          PROGBITS          0000000000000000  000058  000008  00       A
3    .altinstructions                   PROGBITS          0000000000000000  000060  000240  00       A
4    __bug_table                        PROGBITS          0000000000000000  0002a0  00000c  00       WA
5    __jump_table                       PROGBITS          0000000000000000  0002b0  000080  00       WA
6    .plt                               PROGBITS          0000000000000000  000330  000001  00       AX
7    .init.plt                          PROGBITS          0000000000000000  000331  000001  00       AX
8    .text.ftrace_trampoline            PROGBITS          0000000000000000  000332  000001  00       AX
9    .hyp.text                          PROGBITS          0000000000000000  001000  000000  00       AX
10   .hyp.bss                           PROGBITS          0000000000000000  001000  000000  00       AX
11   .hyp.rodata                        PROGBITS          0000000000000000  001000  000000  00       AX
12   .hyp.data                          PROGBITS          0000000000000000  001000  000000  00       AX
13   .init.eh_frame                     PROGBITS          0000000000000000  001000  003050  00       A
14   .text                              PROGBITS          0000000000000000  004050  0183e0  00       AX
15   .rela.text                         RELA              0000000000000000  0273c8  01dd18  18       I
16   .rodata                            PROGBITS          0000000000000000  01c430  000d19  00       A
17   .modinfo                           PROGBITS          0000000000000000  01d149  0002cc  00       A
18   .rodata.str1.1                     PROGBITS          0000000000000000  01d415  007fe1  01       AMS
19   .data                              PROGBITS          0000000000000000  0253f8  000820  00       WA
20   .rela.data                         RELA              0000000000000000  0450e0  000be8  18       I
21   .comment                           PROGBITS          0000000000000000  045cc8  0000b9  01       MS
22   .rela.eh_frame                     RELA              0000000000000000  045d88  001620  18       I
23   .llvm_addrsig                      LLVM_ADDRSIG      0000000000000000  0473a8  00010e  00       E
24   .rela.altinstructions              RELA              0000000000000000  0474b8  000900  18       I
25   .rela__jump_table                  RELA              0000000000000000  047db8  000240  18       I
26   .rela.rodata                       RELA              0000000000000000  047ff8  000348  18       I
27   .rela__bug_table                   RELA              0000000000000000  048340  000030  18       I
28   .rodata.str                        PROGBITS          0000000000000000  025c18  00001c  01       AMS
29   .bss                               NOBITS            0000000000000000  025c38  000032  00       WA
30   __ksymtab_strings                  PROGBITS          0000000000000000  025c38  000026  01       AMS
31   .rela___ksymtab+aw883xx_i2c_probe  RELA              0000000000000000  048370  000090  18       I
32   .note.Linux                        NOTE              0000000000000000  025c60  000030  00       A
33   .gnu.linkonce.this_module          PROGBITS          0000000000000000  025cc0  000440  00       WA
34   __versions                         PROGBITS          0000000000000000  026100  001280  00       A
35   .note.gnu.build-id                 NOTE              0000000000000000  027380  000024  00       A
36   .note.gnu.property                 NOTE              0000000000000000  0273a8  000020  00       A
37   .note.GNU-stack                    PROGBITS          0000000000000000  048400  000000  00       0
38   .symtab                            SYMTAB            0000000000000000  048400  005a00  18       40
39   .shstrtab                          STRTAB            0000000000000000  04de00  0001ca  00       0
40   .strtab                            STRTAB            0000000000000000  04dfca  002614  00       0

## Counters
- ELF type: REL (relocatable), AArch64, 41 sections
- defined FUNC symbols: 236  (all in .text; total 98436 bytes of function text)
- defined OBJECT symbols: 86
- undefined (imported) symbols: 73
- __versions records: 74 (73 imports + module_layout)
- exported symbols: 2
- relocations: 5615
- .rodata.str1.1 strings: 991

## Init/exit
There is NO .init.text, .exit.text, .init.data or .exit.data section and
no .rela.gnu.linkonce.this_module: struct module .init and .exit are NULL.
The module has no module_init()/module_exit() and no MODULE_DEVICE_TABLE
(.modinfo contains no alias= record).  It is a library module.

## Exports
symbol              crc
aw883xx_i2c_probe   0x713728fc
aw883xx_i2c_remove  0xb3e48038

## Translation-unit link order (recovered from .text layout)
0x000004  aw883xx_monitor.c        first symbol aw883xx_monitor_start
0x001b14  aw883xx_bin_parse.c      first symbol aw883xx_dev_dsp_data_order
0x003a94  aw883xx_device.c         first symbol aw883xx_dev_get_list_head
0x008694  aw883xx_init.c           first symbol aw883xx_init_check_chipid
0x0089a0  aw883xx_calib.c          first symbol aw883xx_cali_check_result
0x00e974  aw883xx_spin.c           first symbol aw883xx_spin_check_mode
0x00f7e0  aw883xx.c                first symbol aw883xx_get_version
0x015844  aw883xx_pid_2049_init.c  first symbol aw883xx_pid_2049_dev_init
0x017078  aw883xx_pid_2066_init.c  first symbol aw883xx_pid_2066_dev_init
0x017bac  aw883xx_pid_2183_init.c  first symbol aw883xx_pid_2183_dev_init

## .modinfo layout
    import_ns=VFS_internal_I_am_really_a_filesystem_and_am_NOT_a_driver
    import_ns=VFS_internal_I_am_really_a_filesystem_and_am_NOT_a_driver
    import_ns=VFS_internal_I_am_really_a_filesystem_and_am_NOT_a_driver
    import_ns=VFS_internal_I_am_really_a_filesystem_and_am_NOT_a_driver
    import_ns=VFS_internal_I_am_really_a_filesystem_and_am_NOT_a_driver
    description=ASoC AW883XX Smart PA Driver
    license=GPL v2
    import_ns=VFS_internal_I_am_really_a_filesystem_and_am_NOT_a_driver
    import_ns=VFS_internal_I_am_really_a_filesystem_and_am_NOT_a_driver
    import_ns=VFS_internal_I_am_really_a_filesystem_and_am_NOT_a_driver
    vermagic=6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64
    name=aw883xx_driver
    depends=

The 8 import_ns records are not a vendor addition: MODULE_IMPORT_NS lives in
aw883xx.h, and exactly 8 of the 10 translation units include that header
(aw883xx_bin_parse.c and aw883xx_device.c do not).  Their .modinfo positions
(5 before description/license, 3 after) are a direct consequence of the link
order above and were reproduced exactly by the rebuild.

## Interfaces present in the stock binary
- ASoC component:      snd_soc_register_component / snd_soc_unregister_component,
                       snd_soc_add_component_controls, snd_soc_dapm_new_controls,
                       snd_soc_dapm_add_routes, snd_soc_info_volsw
                       .rodata: soc_codec_dev_aw883xx (368 B), aw883xx_dai (224 B),
                       aw883xx_dai_ops (184 B), aw883xx_dapm_widgets (1280 B),
                       aw883xx_audio_map (192 B), aw883xx_switch, aw_spin
- sysfs device group:  aw883xx_attribute_group / aw883xx_attributes (13 attrs)
                       reg rw drv_ver dsp_rw awrw fade_step dbg_prof spk_temp
                       phase_sync fade_en dsp_re i2c_log_en dsp
- sysfs monitor group: aw_monitor_attr_group -> monitor, monitor_update
- sysfs cali group:    aw_cali_attr_group -> cali_time cali_re cali_f0 cali_f0_q re_range
- class:              "smartpa" (aw_cali_class) with class attributes
                       cali_time re25_calib f0_calib f0_q_calib re_range
- miscdevice:         "aw_smartpa" (misc_cali, aw_cali_misc_fops, 272 B)
- workqueues:         alloc_workqueue + delayed_work (monitor + dsp monitor + start work)
- timers:             init_timer_key x3 (delayed_work_timer_fn)
- IRQ:                devm_request_threaded_irq / devm_free_irq, gpiod_to_irq
- GPIO:               devm_gpio_request_one, of_get_named_gpio_flags,
                      gpiod_set_raw_value_cansleep
- firmware:           request_firmware / release_firmware
- power supply:       power_supply_get_by_name / power_supply_get_property
- NO regmap:          direct i2c_transfer / i2c_transfer_buffer_flags only
- NO procfs, NO debugfs, NO of_device_id table, NO i2c_driver registration
