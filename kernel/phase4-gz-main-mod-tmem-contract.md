# gz_main_mod — tmem_ffa contract

## 1. Imported tmem_ffa symbols — exactly two

Independently re-derived from the stock ELF against the 15-symbol `tmem_ffa`
export table. The previously recorded count of 2 is confirmed, and the exact
symbols are:

| symbol | stock CRC | source-built tmem_ffa CRC | call sites | status |
|---|---|---|---:|---|
| `ssmr_offline` | `0x6ce41c25` | `0x6ce41c25` | 1 | NATURAL_OK |
| `ssmr_online` | `0xb8313cbf` | `0xb8313cbf` | 1 | NATURAL_OK |

Provider: the REAL source-built `//lieppos/tmem-ffa-gzaccept:tmem_ffa_gzaccept`
(`SOURCE_NOW / FROZEN FOR RE`, the variant built against source gz_tz_system).
No witness.

## 2. Prototypes

From `drivers/misc/mediatek/trusted_mem/ssmr/memory_ssmr.h` at the pinned
revision:

```c
int ssmr_offline(phys_addr_t *pa, unsigned long *size, bool is_64bit,
                 unsigned int feat);
int ssmr_online(unsigned int feat);
```

`ssmr` = Secure/Silent Memory Reservation. `ssmr_offline()` takes a reserved
region *offline* from Linux (making it available to the secure world) and
returns its physical address and size; `ssmr_online()` gives it back.

## 3. Call sites — both in the chunk-memory unit test

Both live in `mtee_ut/gz_chmem_ut.o`, inside `gz_test_chm_main`
(`.text+0x3988`, 1576 bytes):

| offset | symbol | role |
|---|---|---:|
| `.text+0x39f0` | `ssmr_offline` | take the feature region offline before the chunk-memory test |
| `.text+0x3ef4` | `ssmr_online` | return it to Linux at the end of the test |

The surrounding stock strings make the bracketing explicit:

```
[Chmem UT][%s]ssmr offline passed! feat:%d, pa: 0x%llx, sz: 0x%x
[Chmem UT][ERR][%s]ssmr offline failed (feat:%d)!
[Chmem UT][%s]ssmr online passed!
[Chmem UT][ERR][%s]ssmr online failed (feat:%d)!
[Chmem UT][ERR][%s]ssmr pa(0x%llx) & size(0x%x) is invalid
ssmr_get chmem
ssmr_put chmem
```

## 4. Reachability

Neither symbol is reachable from any ioctl. The only path is:

```
write '4' > /sys/devices/virtual/misc/gz_kree/gz_test
   -> kthread "test_chm" -> gz_test_chm()
        -> mutex_lock(&chmem_ut_mutex)
        -> gz_test_chm_main(SSMR_FEAT_PROT_REGION, MTEE_MCHUNKS_PROT)
             -> ssmr_offline(...) ... KREE_* chunk-memory ops ... ssmr_online(...)
        -> mutex_unlock(&chmem_ut_mutex)
```

`gz_test_chm_main` is called exactly once, and the whole sequence is
serialised by `chmem_ut_mutex`.

The `SSMR_FEAT_PROT_REGION` / `MTEE_MCHUNKS_PROT` argument pair is selected by
`CONFIG_MTK_PROT_MEM_SUPPORT`, which the config contract proves is ON.

## 5. Ownership, lifetime, error behaviour

| aspect | behaviour |
|---|---|
| ownership | the SSMR region is owned by `tmem_ffa`; `gz_main_mod` only borrows it for the duration of the test |
| lifetime | strictly bracketed — `ssmr_online` returns the region in the same function |
| pa/size validation | the returned `pa` and `size` are checked and rejected as "invalid" if inconsistent |
| error behaviour | a failed `ssmr_offline` aborts the test and logs; it does not attempt the chunk-memory operations |
| concurrency | `chmem_ut_mutex` prevents two concurrent sysfs-triggered tests |

## 6. Effect on tmem_ffa

None. `gz_main_mod` is a pure consumer and defines nothing that `tmem_ffa`
imports. `tmem_ffa` remains `SOURCE_NOW / FROZEN FOR RE` with all 15 exports
natural and its 76/76 verifier unchanged.

No SSMR region was taken offline and no secure memory was allocated during
this analysis.
