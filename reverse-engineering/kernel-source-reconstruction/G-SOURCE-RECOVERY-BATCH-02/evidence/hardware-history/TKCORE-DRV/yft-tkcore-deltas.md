# Ulefone / YFT deltas in tkcore_drv

**None identified.** Every difference between the stock module and the public donor is a
TrustKernel release difference (stock = older 6:1.1-era backend, donor = 7:2.2), listed in
`source-lineage.md`. The stock binary contains no YFT/Ulefone strings, symbols, DT properties
or configuration beyond the generic MediaTek integration.

| area | donor behaviour (7:2.2) | GQ5012BF1 behaviour | evidence | classification |
|---|---|---|---|---|
| dispatcher | workqueue | per-CPU kthreads | byte-exact rebuild | TrustKernel release delta |
| RPC features | log flush, named shm | absent | byte-exact rebuild | TrustKernel release delta |
| transport selection | FF-A + SMC registered | same; SMC dormant because the board DT has no `trustkernel,tzdrv` node | DT | MediaTek platform integration (FF-A SPMC in `tee.img`) |
| reserved memory | `trustkernel,shared_mem` | 32 MiB dynamic, 1–3 GiB, `no-map` | DT | MediaTek platform DT |
| log IRQ | `trustkernel,tkcore` node | absent (irq 0) | DT | MediaTek platform DT |
| Kconfig | RPMB default y, FP optional | RPMB=y, FP=y | code present | MediaTek/TrustKernel config |
| init quirks | init returns `ffa_rc && smc_rc`; exit unregisters only failed drivers | identical | both sources | upstream TrustKernel (not YFT) |
