# GQ5012BF1 tkcore ioctl UAPI

Authoritative source: stock GQ5012BF1 `tkcore.ko` relocation-aware disassembly. Donor names are used only where the numeric stock encoding confirms them.

## Encoding

All accepted commands use ioctl type `'t'` (`0x74`). Explicit 64-bit padding in every pointer-bearing ABI structure keeps native and compat command numbers identical.

| Command | Encoding | Macro shape | Native / compat size | Direction | Handler | Node(s) / fd | Copy and return contract |
|---|---:|---|---:|---|---|---|---|
| `TEE_OPEN_SESSION_IOC` | `0xc03074a1` | `_IOWR('t',161,struct tee_cmd_io)` | 48 / 48 | in+out | `tee_internal_ioctl` | `tkcore_client`, `tkcore_fp`, technically admin; success creates anonymous session fd | copies all 48 in; validates; writes `err`+`origin` even on backend failure and `fd_sess` only after successful creation; returns Linux status |
| `TEE_INVOKE_COMMAND_IOC` | `0xc03074a3` | `_IOWR('t',163,struct tee_cmd_io)` | 48 / 48 | in+out | `tee_session_internal_ioctl` | anonymous session fd | copies 48 in via `tee_copy_from_user`; writes `err`+`origin`; backend return is Linux return |
| `TEE_REQUEST_CANCELLATION_IOC` | `0xc03074a4` | `_IOWR('t',164,struct tee_cmd_io)` | 48 / 48 | in+out | `tee_session_internal_ioctl` | anonymous session fd | copies 48 in; writes `err`+`origin` only on successful cancel backend path; returns backend/Linux status |
| `TEE_ALLOC_SHM_IOC` | `0xc01874a5` | `_IOWR('t',165,struct tee_shm_io)` | 24 / 24 | in+out | `tee_internal_ioctl` | all three misc nodes | copies 24 in; on success writes only `fd_shm` and `flags`; returns allocator status |
| `TEE_GET_FD_FOR_RPC_SHM_IOC` | `0xc01874a7` | `_IOWR('t',167,struct tee_shm_io)` | 24 / 24 | in+out | `tee_internal_ioctl` | **admin descriptor only** (`ctx_priv->supplicant != 0`) | copies 24 in after descriptor gate; on success writes only `fd_shm`; returns conversion/backend status |
| feature-flags query (stock symbol `nsdrv_feature_flags`; historical macro spelling unavailable) | `0x800474b7` | `_IOR('t',183,u32)` | 4 / 4 | out | `tee_internal_ioctl` | all misc nodes | copies the 4-byte static-zero stock object to userspace; 0 or `-EFAULT`; NULL gives `-EINVAL` |

Accepted native ioctl command count: **6**. Accepted compat ioctl command count: **6**.

## Compat pre-conversion table

| Encoding | Conversion | Native result |
|---:|---|---|
| `0xc03074a1` | `convert_compat_tee_cmd` | open-session dispatch |
| `0xc03074a3` | `convert_compat_tee_cmd` | invoke dispatch |
| `0xc03074a4` | `convert_compat_tee_cmd` | cancellation dispatch |
| `0xc01874a5` | `convert_compat_tee_shm_io` | alloc-SHM dispatch |
| `0xc01874a7` | `convert_compat_tee_shm_io` | RPC-SHM-fd dispatch |
| `0x800474b7` | none | native feature query |

Stock `tee_compat_ioctl` also recognises `0xc01874ae` (type `'t'`, nr 174, 24-byte in/out) and runs `convert_compat_tee_spta_inst`, but `tee_internal_ioctl` has **no handler for it** and returns `-EINVAL` as unknown. This is a proven, internally inconsistent stock path, not a supported seventh command. The conversion can fail first with `-EFAULT`. Literal `0xc01874ad` appears only as a comparison boundary; it is neither converted nor accepted.

## Structures

### `struct tee_cmd_io` — 48 bytes

| Field | Offset | Width |
|---|---:|---:|
| `err` | 0x00 | 4 |
| `origin` | 0x04 | 4 |
| `cmd` | 0x08 | 4 |
| `fd_sess` | 0x0c | 4 |
| `uuid` / fixed ABI slot | 0x10 | 8 |
| `data` / fixed ABI slot | 0x18 | 8 |
| `op` / fixed ABI slot | 0x20 | 8 |
| `data_size` | 0x28 | 4 |
| reserved | 0x2c | 4 |

### `struct tee_shm_io` — 24 bytes

| Field | Offset | Width |
|---|---:|---:|
| `buffer` / fixed ABI slot | 0x00 | 8 |
| `size` | 0x08 | 4 |
| `flags` | 0x0c | 4 |
| `fd_shm` | 0x10 | 4 |
| `registered` | 0x14 | 4 |

Compat uses a 32-bit pointer in the low word of each 8-byte pointer slot. The converter zeroes the high word in place before native code consumes it.

## Validation and errno mapping

- Unknown core or session command: stock returns **`-EINVAL`**, not `-ENOSYS`/`-ENOIOCTLCMD`; core also prints `internal_ioctl: Unknown command: %u`.
- User-access or converter failure: normally `-EFAULT`; the larger native handlers retain `-EINVAL` on their initial copy-in failure, exactly as stock does.
- Open: `fd_sess >= 1` invalid; `op` and `uuid` required; data pointer and size must either both be zero or both nonzero.
- Invoke/cancel: `op` required; `uuid`, `data`, `data_size` must all be zero.
- Allocate: `buffer==NULL`, `fd_shm==0`, at least one provider-supported flag, `registered==0`.
- RPC fd: admin/supplicant descriptor required; `buffer!=NULL`, `size!=0`, `fd_shm==0`, flags are a nonempty subset of provider flags, `registered==0`.
- No `capable()` or credential test occurs in stock. Admin exclusivity is enforced at open by `tee_supp_open`, not by ioctl dispatch.
