# ffa_v10 memory-ops ABI

Present in stock (`ffa_memory_ops`, `ffa_memory_share`, `ffa_memory_lend`,
`ffa_memory_reclaim`, `ffa_transmit_fragment`, `ffa_set_up_mem_ops_native_flag`
are all in the stock function set). **No consumer on this device calls any of
it** - tkcore_drv builds its own SHM window via SMC fast-call `0xf2005704`,
not via FF-A memory-share. Documented for completeness because it is present
in the binary, not because anything invokes it.

## Share / lend

```c
static int ffa_memory_share(struct ffa_mem_ops_args *args)
{ return ffa_memory_ops(native_mem_share ? FFA_FN_NATIVE(MEM_SHARE) : FFA_MEM_SHARE, args); }

static int ffa_memory_lend(struct ffa_mem_ops_args *args)
{ return ffa_memory_ops(native_mem_lend ? FFA_FN_NATIVE(MEM_LEND) : FFA_MEM_LEND, args); }

static int ffa_memory_ops(u32 func_id, struct ffa_mem_ops_args *args)
{
	rc = ffa_setup_and_transmit(func_id, buf, RXTX_BUFFER_SIZE, args);
	...
	invoke_ffa_fn((ffa_value_t){ .a0 = func_id, .a1 = total_len, .a2 = frag_len }, &ret);
	if (ret.a0 == FFA_MEM_FRAG_RX) ... /* multi-fragment path via ffa_transmit_fragment */
	if (ret.a0 == FFA_SUCCESS) args->g_handle = PACK_HANDLE(ret.a2, ret.a3);
}
```

## Reclaim

```c
static int ffa_memory_reclaim(u64 g_handle, u32 flags)
{
	invoke_ffa_fn((ffa_value_t){ .a0 = FFA_MEM_RECLAIM,
				     .a1 = HANDLE_LOW(g_handle),
				     .a2 = HANDLE_HIGH(g_handle),
				     .a3 = flags }, &ret);
	return ret.a0 == FFA_ERROR ? ffa_to_linux_errno(ret.a2) : 0;
}
```

## Descriptor / scatter-gather layout

`ffa_setup_and_transmit()` builds a `struct ffa_mem_region` +
`ffa_composite_mem_region` + `ffa_mem_region_addr_range[]` chain directly in
the TX buffer (`RXTX_BUFFER_SIZE` = `PAGE_SIZE`, `FFA_PAGE_SIZE` = 4096),
walking the caller's `scatterlist` (`ffa_get_num_pages_sg` counts 4 KiB pages
per SG entry) or a flat `buf` if `args->use_txbuf`.

* `handle` width: 64-bit (`u64 g_handle`, packed/unpacked via
  `PACK_HANDLE`/`HANDLE_LOW`/`HANDLE_HIGH` across two 32-bit registers).
* page counts: `ffa_get_num_pages_sg()`, one 4 KiB `FFA_PAGE_SIZE` unit per
  descriptor entry.
* alignment: no explicit extra alignment beyond page granularity.
* fragmentation: `ffa_transmit_fragment()` handles the `FFA_MEM_FRAG_TX`/
  `FFA_MEM_FRAG_RX` continuation protocol when a region does not fit one
  `RXTX_BUFFER_SIZE` TX buffer.
* attributes byte: **stock always writes `0x2f`**
  (`FFA_MEM_NORMAL | FFA_MEM_WRITE_BACK | FFA_MEM_INNER_SHAREABLE`) even for
  `MEM_LEND`, per the pre-`e578a26084eb` vendor snapshot - see lineage.md.
  This is reproduced exactly, not "corrected".

## Error handling

Same `ffa_to_linux_errno()` translation table as the message path.

## Native (SMC64) flag

`ffa_set_up_mem_ops_native_flag()` probes `FFA_FEATURES(FFA_FN_NATIVE(MEM_LEND))`
/`(MEM_SHARE)` once at init and sets `native_mem_lend`/`native_mem_share`
booleans so later calls use the 64-bit SMC encoding when the firmware
advertises it - present in stock, kCFI `0x94000000` group (internal, no
external prototype to pin).
