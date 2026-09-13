# GQ5012BF1 `gz_ipc_mod` consumer ABI

Provider: **Trusty IPC (TIPC)**. All CRC values below are natural outputs of unchanged pinned source.

| Export | Class | Stock CRC | Consumers / required CRC | Source declaration | Natural donor | Final |
|---|---|---:|---|---|---:|---:|
| `port_lookup_tid` | `EXPORT_SYMBOL` | `0x141326e4` | `gz_tz_system.ko` `0x141326e4` | `int port_lookup_tid(const char *port, enum tee_id_t *o_tid)` | `0x141326e4` | `0x141326e4` |
| `tipc_chan_connect` | `EXPORT_SYMBOL` | `0xf1154a70` | *none in 471-module stock scan* | `int tipc_chan_connect(struct tipc_chan *chan, const char *port)` | `0xf1154a70` | `0xf1154a70` |
| `tipc_chan_destroy` | `EXPORT_SYMBOL` | `0x38abb9f7` | *none in 471-module stock scan* | `void tipc_chan_destroy(struct tipc_chan *chan)` | `0x38abb9f7` | `0x38abb9f7` |
| `tipc_chan_get_rxbuf` | `EXPORT_SYMBOL` | `0xfebab79c` | *none in 471-module stock scan* | `struct tipc_msg_buf *tipc_chan_get_rxbuf(struct tipc_chan *chan)` | `0xfebab79c` | `0xfebab79c` |
| `tipc_chan_get_txbuf_timeout` | `EXPORT_SYMBOL` | `0xc48074f4` | *none in 471-module stock scan* | `struct tipc_msg_buf *tipc_chan_get_txbuf_timeout(struct tipc_chan *chan, long timeout)` | `0xc48074f4` | `0xc48074f4` |
| `tipc_chan_put_rxbuf` | `EXPORT_SYMBOL` | `0x5c7af968` | *none in 471-module stock scan* | `void tipc_chan_put_rxbuf(struct tipc_chan *chan, struct tipc_msg_buf *mb)` | `0x5c7af968` | `0x5c7af968` |
| `tipc_chan_put_txbuf` | `EXPORT_SYMBOL` | `0x2f69387a` | *none in 471-module stock scan* | `void tipc_chan_put_txbuf(struct tipc_chan *chan, struct tipc_msg_buf *mb)` | `0x2f69387a` | `0x2f69387a` |
| `tipc_chan_queue_msg` | `EXPORT_SYMBOL` | `0x46a855ed` | *none in 471-module stock scan* | `int tipc_chan_queue_msg(struct tipc_chan *chan, struct tipc_msg_buf *mb)` | `0x46a855ed` | `0x46a855ed` |
| `tipc_chan_shutdown` | `EXPORT_SYMBOL` | `0xc2324a0d` | *none in 471-module stock scan* | `int tipc_chan_shutdown(struct tipc_chan *chan)` | `0xc2324a0d` | `0xc2324a0d` |
| `tipc_create_channel` | `EXPORT_SYMBOL` | `0x339dd60c` | *none in 471-module stock scan* | `struct tipc_chan *tipc_create_channel(struct device *dev, const struct tipc_chan_ops *ops, void *cb_arg)` | `0x339dd60c` | `0x339dd60c` |
| `tipc_k_connect` | `EXPORT_SYMBOL` | `0x6d3e778c` | `gz_tz_system.ko` `0x6d3e778c` | `int tipc_k_connect(struct tipc_k_handle *h, const char *port)` | `0x6d3e778c` | `0x6d3e778c` |
| `tipc_k_disconnect` | `EXPORT_SYMBOL` | `0x389e0025` | `gz_tz_system.ko` `0x389e0025` | `int tipc_k_disconnect(struct tipc_k_handle *h)` | `0x389e0025` | `0x389e0025` |
| `tipc_k_read` | `EXPORT_SYMBOL` | `0xe9bc90dd` | `gz_tz_system.ko` `0xe9bc90dd` | `ssize_t tipc_k_read(struct tipc_k_handle *h, void *buf, size_t buf_len, unsigned int flags)` | `0xe9bc90dd` | `0xe9bc90dd` |
| `tipc_k_write` | `EXPORT_SYMBOL` | `0xd5b2fc22` | `gz_tz_system.ko` `0xd5b2fc22` | `ssize_t tipc_k_write(struct tipc_k_handle *h, void *buf, size_t len, unsigned int flags)` | `0xd5b2fc22` | `0xd5b2fc22` |
| `tipc_set_default_cpumask` | `EXPORT_SYMBOL` | `0xdabdc7b5` | `gz_main_mod.ko` `0xdabdc7b5` | `int tipc_set_default_cpumask(uint32_t cpumask)` | `0xdabdc7b5` | `0xdabdc7b5` |

- direct consumers: **2**
- consumer edges: **6**
- consumed exports: **15/15**
- broken edges after source build: **0**

Machine evidence:
- `phase4-gz-ipc-mod-consumer-edges.tsv` (stock scan)
- `phase4-gz-transport-consumer-acceptance.tsv` (natural rebuilt acceptance)
- `phase4-gz-ipc-mod-exports.tsv` (export class/CRC)
