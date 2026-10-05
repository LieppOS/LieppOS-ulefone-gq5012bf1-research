# Build configuration for the exact USB rebuilds

- **Kernel object tree.** GKI `kout` for ACK `6b18f0b574ab` (android14-6.1-2024-12_r4), shared with the storage work. Flags: `KCFLAGS=-faddrsig`, `-fmacro-prefix-map=<tree>/=../kernel_device_modules-6.1/`, clang-r487747c.
- **Vendor source.** MTK ALPS `5e415e059253` (`git archive`), plus [`../kdm-patches/`](../kdm-patches/).
- **Build method.** Each module is built in isolation with `M=` (`../../scripts/sb.sh <tree> <mod> <dir> "<objs>" <tag>`); `../../scripts/build-all.sh <tree> <tag>` builds all 13. Vendor provider CRCs come from the stock-harvested `stock-all.symvers` (the storage workspace).
- **Per-module extra flags** (`XCCFLAGS`):
  - `xhci-mtk-hcd-v2`, `usb_logger`: `-I<module src dir>`, because the tracepoint header is included as `./xhci-trace.h` / `./u_logger_trace.h`.
  - `rt_pd_manager`, `tcpci_late_sync`: `-DCONFIG_MTK_TYPEC_WATER_DETECT=1`. Stock `struct tcpc_device` has the water-detect members (for example `bootmode` at 0x3550). This is the same requirement DONE/TCPC-CLASS found for `tcpc_class.ko`.
- **Stripping.** Both stock and B are compared after `llvm-strip --strip-debug`. Stock modules ship debug-stripped with a build-id note.
- **srcversion.** `scripts/tools/sumversion-harness.c` (linked against the real `scripts/mod/sumversion.c`) plus `svtext.py` compute `srcversion` for candidate source texts. This is how the `rt_pd_manager` residual was characterised.
