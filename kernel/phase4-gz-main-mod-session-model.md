# gz_main_mod — client session model

## 1. The four distinct identifiers

These are routinely conflated; the module keeps them strictly separate.

| identifier | type | scope | owner |
|---|---|---|---|
| Linux file descriptor | `int` | per `open("/dev/gz_kree")` | VFS |
| slot index in the session table | `int` (0..handle_num-1) | per open file | `gz_main_mod` |
| `KREE_SESSION_HANDLE` | `int32` | per KREE session | `gz_tz_system` |
| secure-world session id | opaque | GZ/Trusty internal | secure world, never seen by Linux |
| TIPC channel | `tipc_k_*` channel | per KREE session, inside gz_tz_system | `gz_ipc_mod` |

`gz_main_mod` only ever manipulates the first three. It never touches a TIPC
channel directly and never learns the secure-world session id; its single
`gz_ipc_mod` edge is `tipc_set_default_cpumask`, a global tuning knob, not a
per-session operation.

## 2. Per-open state

```c
struct session_info {
        int handle_num;              /* current capacity        */
        KREE_SESSION_HANDLE *handles;/* array of session handles*/
        struct mutex mux;            /* protects both fields    */
};
```

Stored in `struct file::private_data`. There is **no global session registry**
and no per-process state: two `open()` calls from the same process get two
independent tables.

Constants:

| name | value | meaning |
|---|---|---|
| `queue_SessionNum` | 32 | initial table capacity |
| `non_SessionID` | `0xffffffff` | empty-slot sentinel |
| `KREE_SESSION_HANDLE_MAX_SIZE` | 512 | max TA name length copied from user |

## 3. Lifecycle

### open — `gz_dev_open` → `_init_session_info`
1. `kmalloc(sizeof(struct session_info))`.
2. `kmalloc_array(32, sizeof(KREE_SESSION_HANDLE))`.
3. Every slot initialised to `non_SessionID`.
4. `mutex_init(&info->mux)` — the lock's lockdep key is the static
   `_init_session_info.__key` object visible in stock.
5. `fp->private_data = info`.

On the `handles` allocation failing, the `info` allocation is freed and
`TZ_RESULT_ERROR_GENERIC` is returned — no leak.

### open session — `MTEE_CMD_OPEN_SESSION`
1. `KREE_CreateSession(name, &handle)` (gz_tz_system).
2. `_register_session_info(fp, handle)`:
   * takes `info->mux`;
   * linear scan for the first `non_SessionID` slot;
   * **if the table is full it doubles**: `krealloc` to `num * 2`, then
     `memset` the new tail to the sentinel, `handle_num = nspace`;
   * stores the handle, releases the mutex.
3. A `handle < 0` is rejected up front with
   `TZ_RESULT_ERROR_BAD_PARAMETERS`.

If `krealloc` fails the mutex is released before returning
`TZ_RESULT_ERROR_GENERIC` — no lock leak on the error path.

### service call — `MTEE_CMD_TEE_SERVICE`
Stateless with respect to the table: the handle travels in the ioctl argument
and is passed straight to `KREE_TeeServiceCallPlus`. The session table is not
consulted, so a caller may legitimately invoke a handle it obtained on the
same fd; there is no per-call ownership re-validation in Linux.

### close session — `MTEE_CMD_CLOSE_SESSION`
`KREE_CloseSession(handle)` then the slot is reset to `non_SessionID`.

### release — `gz_dev_release` → `_free_session_info`
1. Takes `info->mux`.
2. Walks all `handle_num` slots and calls `KREE_CloseSession()` on every slot
   that is not `non_SessionID`, resetting each to the sentinel.
3. Clears `fp->private_data`, releases the mutex.
4. `kfree(info->handles)`, `kfree(info)`.

**This is the process-exit guarantee.** Because `release` runs when the last
reference to the file drops, an abnormally terminated client cannot leak
secure-world sessions: every session opened through that fd is closed by the
kernel.

## 4. Locking and concurrency

| lock | protects | notes |
|---|---|---|
| `info->mux` (per open) | the session handle array and its capacity | held across `krealloc`, released on every error path |
| `ut_mutex`, `simple_ut_mutex`, `chmem_ut_mutex`, `shmem_ut_mutex`, `vreg_ut_mutex` | the five sysfs-triggered unit-test paths | each serialises its own test so concurrent `gz_test` writes cannot interleave |
| `ffa_mem_lock` (spinlock, gz_ffa.c) | the FF-A memory record list | separate subsystem |

The session mutex is **not** held across `KREE_CreateSession`, only across the
table update. `_free_session_info` does hold it across the `KREE_CloseSession`
loop.

## 5. TEE selection (Trusty vs Nebula)

`gz_main_mod` does not select a TEE. It binds only the `mediatek,trusty-mtee-v1`
node, which lives under the `trusty` root (`tee-id = <0>`). TEE routing is
resolved below it: `gz_tz_system` holds `tz_system_dev` and `get_smcnr_dev`
maps a device to its SMC number space. The `nebula` root (`tee-id = <1>`) has
no `mtee` child that this driver matches, so no Nebula path is reachable from
this module.

## 6. Reference counting

* `/dev/gz_kree` sets `.owner = THIS_MODULE`, so the module cannot be unloaded
  while a client holds the node open.
* `/dev/gz_ffa_dev` does **not** set `.owner` — an open FF-A fd does not pin
  the module.
* Session handles are not reference counted in Linux; the table holds exactly
  one entry per successfully created session.

## 7. Error unwinding summary

| failure | unwind |
|---|---|
| `copy_from_user` in any ioctl | return `-EFAULT`, nothing allocated |
| `KREE_CreateSession` fails | no table slot consumed |
| table full and `krealloc` fails | mutex released, `TZ_RESULT_ERROR_GENERIC` |
| GP param bounce alloc fails mid-walk | `error:` label frees every buffer allocated so far |
| client crashes / fd closed | `release` closes all live sessions |
