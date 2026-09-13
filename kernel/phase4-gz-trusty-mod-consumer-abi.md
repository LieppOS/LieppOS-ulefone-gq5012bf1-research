# GQ5012BF1 `gz_trusty_mod` consumer ABI

Provider: **Trusty SMC/NOP**. All CRC values below are natural outputs of unchanged pinned source.

| Export | Class | Stock CRC | Consumers / required CRC | Source declaration | Natural donor | Final |
|---|---|---:|---|---|---:|---:|
| `get_smcnr_dev` | `EXPORT_SYMBOL` | `0x5fdc32d1` | `gz_ipc_mod.ko` `0x5fdc32d1`<br>`gz_irq_mod.ko` `0x5fdc32d1`<br>`gz_log_mod.ko` `0x5fdc32d1`<br>`gz_main_mod.ko` `0x5fdc32d1`<br>`gz_virtio_mod.ko` `0x5fdc32d1`<br>`sapu.ko` `0x5fdc32d1` | `uint32_t get_smcnr_dev(enum smc_functions fid, struct device *dev)` | `0x5fdc32d1` | `0x5fdc32d1` |
| `trusty_adjust_task_attr` | `EXPORT_SYMBOL` | `0x756ff09a` | `gz_main_mod.ko` `0x756ff09a` | `int trusty_adjust_task_attr(struct device *dev, struct trusty_task_attr *manual_task_attr)` | `0x756ff09a` | `0x756ff09a` |
| `trusty_call_notifier_register` | `EXPORT_SYMBOL` | `0x5dfe70c3` | `gz_irq_mod.ko` `0x5dfe70c3`<br>`gz_log_mod.ko` `0x5dfe70c3`<br>`gz_virtio_mod.ko` `0x5dfe70c3` | `int trusty_call_notifier_register(struct device *dev, struct notifier_block *n)` | `0x5dfe70c3` | `0x5dfe70c3` |
| `trusty_call_notifier_unregister` | `EXPORT_SYMBOL` | `0xe471605a` | `gz_irq_mod.ko` `0xe471605a`<br>`gz_log_mod.ko` `0xe471605a`<br>`gz_virtio_mod.ko` `0xe471605a` | `int trusty_call_notifier_unregister(struct device *dev, struct notifier_block *n)` | `0xe471605a` | `0xe471605a` |
| `trusty_callback_notifier_register` | `EXPORT_SYMBOL` | `0x74a6228c` | `gz_virtio_mod.ko` `0x74a6228c` | `int trusty_callback_notifier_register(struct device *dev, struct notifier_block *n)` | `0x74a6228c` | `0x74a6228c` |
| `trusty_callback_notifier_unregister` | `EXPORT_SYMBOL` | `0x16f52a10` | `gz_virtio_mod.ko` `0x16f52a10` | `int trusty_callback_notifier_unregister(struct device *dev, struct notifier_block *n)` | `0x16f52a10` | `0x16f52a10` |
| `trusty_dequeue_nop` | `EXPORT_SYMBOL` | `0xdd2a1d22` | `gz_virtio_mod.ko` `0xdd2a1d22` | `void trusty_dequeue_nop(struct device *dev, struct trusty_nop *nop)` | `0xdd2a1d22` | `0xdd2a1d22` |
| `trusty_dump_systrace` | `EXPORT_SYMBOL` | `0x1d65a617` | `gz_virtio_mod.ko` `0x1d65a617` | `int trusty_dump_systrace(struct device *dev, void *data)` | `0x1d65a617` | `0x1d65a617` |
| `trusty_enqueue_nop` | `EXPORT_SYMBOL` | `0x0d91978b` | `gz_irq_mod.ko` `0x0d91978b`<br>`gz_tz_system.ko` `0x0d91978b`<br>`gz_virtio_mod.ko` `0x0d91978b` | `void trusty_enqueue_nop(struct device *dev, struct trusty_nop *nop, int cpu)` | `0x0d91978b` | `0x0d91978b` |
| `trusty_fast_call32` | `EXPORT_SYMBOL` | `0x0c06e871` | `gz_ipc_mod.ko` `0x0c06e871`<br>`gz_irq_mod.ko` `0x0c06e871`<br>`gz_log_mod.ko` `0x0c06e871`<br>`gz_main_mod.ko` `0x0c06e871`<br>`gz_virtio_mod.ko` `0x0c06e871` | `s32 trusty_fast_call32(struct device *dev, u32 smcnr, u32 a0, u32 a1, u32 a2)` | `0x0c06e871` | `0x0c06e871` |
| `trusty_get_api_version` | `EXPORT_SYMBOL` | `0xbfe5cfb0` | `gz_ipc_mod.ko` `0xbfe5cfb0`<br>`gz_virtio_mod.ko` `0xbfe5cfb0` | `u32 trusty_get_api_version(struct device *dev)` | `0xbfe5cfb0` | `0xbfe5cfb0` |
| `trusty_nop_set_switch_pri` | `EXPORT_SYMBOL_GPL` | `0x124e8423` | `gz_main_mod.ko` `0x124e8423` | `int trusty_nop_set_switch_pri(uint32_t policy)` | `0x124e8423` | `0x124e8423` |
| `trusty_std_call32` | `EXPORT_SYMBOL` | `0x1816bb67` | `gz_log_mod.ko` `0x1816bb67`<br>`gz_main_mod.ko` `0x1816bb67`<br>`gz_tz_system.ko` `0x1816bb67`<br>`gz_virtio_mod.ko` `0x1816bb67`<br>`sapu.ko` `0x1816bb67` | `s32 trusty_std_call32(struct device *dev, u32 smcnr, u32 a0, u32 a1, u32 a2)` | `0x1816bb67` | `0x1816bb67` |
| `trusty_version_str_get` | `EXPORT_SYMBOL` | `0x4fa52631` | `gz_log_mod.ko` `0x4fa52631` | `const char *trusty_version_str_get(struct device *dev)` | `0x4fa52631` | `0x4fa52631` |

- direct consumers: **7**
- consumer edges: **34**
- consumed exports: **14/14**
- broken edges after source build: **0**

Machine evidence:
- `phase4-gz-trusty-mod-consumer-edges.tsv` (stock scan)
- `phase4-gz-transport-consumer-acceptance.tsv` (natural rebuilt acceptance)
- `phase4-gz-trusty-mod-exports.tsv` (export class/CRC)
