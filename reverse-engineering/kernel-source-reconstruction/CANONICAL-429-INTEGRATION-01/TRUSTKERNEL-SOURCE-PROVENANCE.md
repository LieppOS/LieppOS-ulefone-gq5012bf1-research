# TrustKernel provenance (tmem_ffa)

## The change

- **Text kept:** `tmem_ffa`'s own C/H/Kbuild is the unchanged ALPS 5e415e05 source with Codex's secure_transport
  0001 release delta.
- **What changed:** only the TrustKernel provider *witness*. This is the source-built `tkcore` core whose
  modpost supplies `tmem_ffa`'s seven `TEEC_*` import CRCs.
- **The patch:** the witness is public TrustKernel 7:2.2 (anvil-kernel `8e1a0f39478f`, pin `ff290548`) plus
  `patches/source/0002-trustkernel-6.1.1-stock-evidenced-no-named-shm.patch`. The patch:
  - removes `uint16_t shm_name` from `struct tee_shm`;
  - removes `uint16_t named_shm` from `struct tee_rpc_alloc`;
  - restores the authentic TrustKernel 4.0p0 text for `tee_shm_alloc_from_rpc(tee, size, extra_flags)`;
  - drops the named-shm lookup paths.

## Evidence

- **Stock code:**
  - stock `tkcore.ko` has no 16-bit access at `tee_shm+0x3c`, while the 7:2.2 build has four;
  - the stock `tee_shm_alloc_from_rpc` takes three arguments;
  - the stock caller zeroes a 0x18-byte `tee_rpc_alloc`.
- **Effect:** the export CRCs reproduced naturally go from 14/25 to 25/25.

## Classification of the text

- This is a **reconstruction proven by stock evidence**. The original TrustKernel 6:1.1 header text was **not**
  recovered.
- No CRC, symvers line or stock byte is a build input.

## Ownership decision

- **tmem_ffa:** `android_kernel_modules_trustkernel_abi_ulefone_gq5012bf1` @ `15e7e8d8` is authoritative. It is a
  history-preserving fork: 0092949 → 9ee50d3 → 15e7e8d.
- **The eight GZ/FF-A A rows:** they stay with Codex's `android_kernel_modules_secure_transport_ulefone_gq5012bf1`
  @ `00929490` (unchanged; neither history was rewritten). The fork rebuilds them only as regression controls.
- **Why not fast-forward secure_transport:** the fork's `15e7e8d` re-scopes OWNERSHIP.json and the acceptance plan
  to tmem_ffa, which would be wrong for Codex's repository.
- **Superseded expectation:** secure_transport's committed `acceptance-plan.json`/OWNERSHIP still describe
  tmem_ffa as an expected C reject. That historical expectation is superseded by the canonical audit row; it is
  not a second owner.

## Not inferred

- **tkcore.ko stays C:** 25/25 exports match, but 19/122 functions differ.
- **tkcore_drv.ko is C** under Codex batch-02.
