# ffa_v10 type graph

Every type feeding a natural export CRC is public upstream UAPI-adjacent
kernel API (`include/linux/arm_ffa.h`, GPL, unchanged by MediaTek), not a
private vendor type - which is exactly why all five CRCs regenerate
naturally with zero blocked edges, unlike tkcore's private `struct tee`.

## `struct ffa_driver` (consumer-facing, drives `ffa_driver_register` CRC)

```c
struct ffa_driver {
	const char *name;
	int (*probe)(struct ffa_device *ffa_dev);
	void (*remove)(struct ffa_device *ffa_dev);
	void (*shutdown)(struct ffa_device *ffa_dev);
	const struct ffa_device_id *id_table;
	struct device_driver driver;
};
```
member order/types: verified against `include/linux/arm_ffa.h` at the pinned
common commit; `sizeof`/alignment inherited from `struct device_driver`
(opaque to this driver). tkcore_drv's own copy of this struct
(`tkcore_ffa_driver`) was already proven byte-compatible in the tkcore_drv
closure (kCFI `0xd353e493`/`0xa30d19cc` on its probe/remove pair matched
stock).

## `struct ffa_device`

```c
struct ffa_device {
	int vm_id;
	bool mode_32bit;
	uuid_t uuid;
	struct device dev;
	const struct ffa_ops *ops;
};
```
Drives `ffa_device_register`'s return type and `ffa_device_unregister`'s
argument. `mode_32bit` is the field `ffa_mode_32bit_set()` writes (see
bus-contract / message-contract docs).

## `struct ffa_device_id`

```c
struct ffa_device_id {
	uuid_t uuid;
};
```
Used for `MODULE_DEVICE_TABLE`-style matching in `ffa_device_match_uuid()`.

## `struct ffa_ops` / message / memory / info ops

```c
struct ffa_info_ops {
	u32 (*api_version_get)(void);
	int (*partition_info_get)(const char *uuid_str,
				  struct ffa_partition_info *buffer);
};
struct ffa_msg_ops {
	void (*mode_32bit_set)(struct ffa_device *dev);
	int (*sync_send_receive)(struct ffa_device *dev,
				 struct ffa_send_direct_data *data);
};
struct ffa_mem_ops {
	int (*memory_reclaim)(u64 g_handle, u32 flags);
	int (*memory_share)(struct ffa_mem_ops_args *args);
	int (*memory_lend)(struct ffa_mem_ops_args *args);
};
struct ffa_ops {
	const struct ffa_info_ops *info_ops;
	const struct ffa_msg_ops *msg_ops;
	const struct ffa_mem_ops *mem_ops;
};
```
None of these three ops tables is itself exported (only pointed to via the
`ffa_device`'s `ops` field, set once at registration time in `driver.c`), so
they do not carry their own export CRC; their exact member layout is however
provable independently via kCFI on the callback functions themselves (see
message-contract and memory-contract docs), and all three tables are
byte-identical between stock and rebuild (part of the 28/28 object parity).

## Partition-info / direct-message / UUID types

```c
struct ffa_partition_info {
	u16 id;
	u16 exec_ctxt;
	u32 properties;   /* FFA_PARTITION_* flags */
};

struct ffa_send_direct_data {
	unsigned long data0;   /* w3/x3 */
	unsigned long data1;   /* w4/x4 */
	unsigned long data2;   /* w5/x5 */
	unsigned long data3;   /* w6/x6 */
	unsigned long data4;   /* w7/x7 */
};

struct ffa_mem_ops_args {
	bool use_txbuf;
	u32 nattrs;
	u32 flags;
	u64 tag;
	u32 g_handle;
	struct ffa_mem_region_attributes *attrs;
	union {
		struct scatterlist *sg;    /* !use_txbuf */
		void *buf;                 /*  use_txbuf */
	};
};

typedef struct arm_smccc_1_2_regs ffa_value_t;   /* common.h */
```
`uuid_t` is the generic kernel type (`include/linux/uuid.h`), untouched.

## Function-pointer prototypes (kCFI-pinned independently of genksyms)

kCFI type ids confirm every callback prototype byte-for-byte against stock
without relying on genksyms at all - a second, independent proof path:

| callback | prototype | stock kCFI | rebuild kCFI |
|---|---|---|---|
| `ffa_device_match` | `int (struct device *, struct device_driver *)` | `0xc8e784f6` | `0xc8e784f6` |
| `ffa_device_probe` | `int (struct device *)` | `0x3f45655f` | `0x3f45655f` |
| `ffa_device_remove` / `ffa_release_device` | `void (struct device *)` | `0x94ee7df3` | `0x94ee7df3` |
| `ffa_device_uevent` | `int (struct device *, struct kobj_uevent_env *)` | `0x46eb5118` | `0x46eb5118` |
| `arm_ffa_bus_init` | `int (void)` | `0x36b1c5a6` | `0x36b1c5a6` |
| `arm_ffa_bus_exit` | `void (void)` | `0xa540670c` | `0xa540670c` |

(all 34 functions match; see `kernel/phase4-ffa-v10-function-parity.tsv` for
the complete table.)
