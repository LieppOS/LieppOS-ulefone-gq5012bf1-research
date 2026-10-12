# Remaining Category D after this batch (projected 8) and recommended next work

| Group | Modules | Source | Note |
|---|---|---|---|
| **In-tree reboot pair**, recommended next | reboot-mode, syscon-reboot-mode | GKI-tree `drivers/power/reset` | 2 occurrences each (vendor_boot + vendor_dlkm). Uses the native/split-BTF stage of the boot-dependencies engine (OEM BTF base recipe). A small, coherent, likely PUBLIC_EXACT pair |
| Nothing `kernel_modules/*_cus` (pure source) | hbt, scheduler_ext | Nothing kernel_modules 5f75a3b (`hbt_driver_cus`, `sched_cus`) | Needs a second external-module root in the engine. scheduler_ext has no modules.load entry |
| Nothing `kernel_modules/*_cus` (shipped objects) | fpsgo, msync2_frd | `fpsgo_cus`, `msync2_frd_cus` | Kbuild links MediaTek `*_shipped` prebuilt objects. **Needs an explicit project decision**; these cannot be certified as source |
| Mali diagnostic | mali_dmabuf_test_mt6878_r44 | Mali r44p1 `dma_buf_test_exporter` | GPU repo family |
| Blocked OEM variant | flashlight | ODM `flashlight-core.c` | Needs the OEM source (GPL request); see BLOCKERS.tsv |

Integrating this batch and Codex's G work must be reconciled by exact identity before counting.
