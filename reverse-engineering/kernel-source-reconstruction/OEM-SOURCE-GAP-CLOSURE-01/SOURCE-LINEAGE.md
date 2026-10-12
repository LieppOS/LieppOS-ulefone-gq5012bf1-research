# tmem_ffa source lineage

| Layer | Source | Commit |
|---|---|---|
| tmem_ffa C/H/Kbuild | MediaTek ALPS `drivers/misc/mediatek/trusted_mem`, plus the secure_transport 0001 release delta (Codex, unchanged) | ALPS `5e415e05` |
| Recipe and engine | `android_kernel_modules_secure_transport_ulefone_gq5012bf1` (Codex batch-01) | `009294902944237123e5561bd0361167692a9a02` |
| TrustKernel provider witness | public anvil-kernel 7:2.2 (`tkcore-public` pin `ff290548`) + **`patches/source/0002`** (stock-evidenced 6:1.1 no-named-shm declaration delta, using authentic 4.0p0 text for `tee_shm_alloc_from_rpc`/`tee_rpc_alloc`) | fork `15e7e8d8d4f9cbf56982791b2fac0e54087d0f49` |
| Environment | GKI `6b18f0b5` / build 12901745, clang r487747c `7775eb11`, NothingOSS config `957dac18` | unchanged pins |

- **Fork:** `android_kernel_modules_trustkernel_abi_ulefone_gq5012bf1` keeps the full upstream history: 0092949
  → 9ee50d3 (patch) → 15e7e8d (ownership/plan/wrapper/README).
- **tmem_ffa's own source** is byte-for-byte the upstream recipe's. Only the provider witness that supplies its
  four `TEEC_*` import CRCs changed.
