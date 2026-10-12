# TrustKernel ABI boundary: tmem_ffa (C) and tkcore (C)

## Facts (stock read-only)

| Symbol | stock tmem_ffa `__versions` import CRC | stock tkcore.ko export CRC | natural rebuild CRC (public TrustKernel 7:2.2 header) |
|---|---|---|---|
| TEEC_InitializeContext | 0x89b94f9a | 0x89b94f9a | 0x594d83c6 |
| TEEC_RegisterSharedMemory | 0xa7bb0a46 | 0xa7bb0a46 | 0x0dd35280 |
| TEEC_OpenSession | 0xe821e2a3 | 0xe821e2a3 | 0x131b2048 |
| TEEC_FinalizeContext | 0x7b3bc43f | 0x7b3bc43f | 0x37f5725e |

- **What matches:** stock tmem_ffa imports exactly the CRCs that stock tkcore exports, so the device is
  self-consistent. In the rebuild, 141/141 functions, all non-version data, KCFI and 2,208 relocations are exact.
- **Cause:** a genksyms CRC hashes the full type graph of each prototype (`TEEC_Context`, `TEEC_SharedMemory`,
  `TEEC_Session`, …). The public TrustKernel 7:2.2 headers produce different CRCs from the shipped 6:1.1-era
  declarations. Codex recovered the older namespace (the `tkcore_TEEC_*` → `TEEC_*` export-name delta), but the
  private struct/type declarations behind these four CRCs are not public.
- **No workaround used:** no CRC was hardcoded, no `__versions` or symvers entry was copied from stock, and no
  waiver was added.

## Classification

- `tmem_ffa.ko` → **C** (`FOUR_NATURAL_IMPORT_CRCS_NOT_WAIVED`). Its source is complete and compiled, but strict
  whole-file parity fails on exactly the four import CRCs.
- `tkcore.ko` stays **C** (FINISH:TRUSTKERNEL-SOURCE-ABI) and `tkcore_drv.ko` stays **G**; neither was changed by
  this integration.

## Shared future investigation (not started here)

Both rows close with the same input: the authentic TrustKernel `tee_client_api` / TEEC context header set matching
the 6:1.1 ABI that tkcore.ko exports. Once recovered, rebuild tkcore and tmem_ffa together and require natural CRCs
equal to the four stock values above. No TrustKernel/TEE command or device access is involved.
