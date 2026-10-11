# Offline phone-specific diagnostics/instrumentation contract

No device accessed. Labels distinguish shipping/build behavior from DT-enabled nodes and genuine source-only generic support. Exact module identities/runtime status originate from saved boot/module-loading/module-classification.tsv and unchanged stock inventory; DT declarations from saved coverage-audit/device-tree.tsv (580 compatibility records). Coverage letters in that DT table describe component research, **not kernel source classifications**.

## Recorded phone evidence

All12 diagnostics modules: **PROVEN_RUNTIME** saved captured load presence only; probe/register success is not implied. Selected MET modules are **UNKNOWN** runtime (not observed in the saved module capture, no module-load contract); shipping is STOCK_BINARY_IMPLEMENTATION, not runtime necessity.

**ENABLED_IN_STOCK_DT** declarations matching actual source compatible tables:

| Module | Compatible | Saved stock node | Register base evidenced |
|---|---|---|---|
|atf_logger (tfa_debug composite)|mediatek,tfa_debug|/atf-logger|UNKNOWN in coverage summary|
|bus-parity|mediatek,bus-parity|/bus-parity@c538800|0x0c538800|
|cache-parity|mediatek,mt6873-cache-parity|/cache-parity|UNKNOWN in coverage summary|
|dbg_error_flag|mediatek,dbg-error-flag|/dbg-error-flag|UNKNOWN in coverage summary|
|dbgtop-drm|mediatek,dbgtop-drm|/soc/drm@1000d000|0x1000d000|
|last_bus|mediatek,lastbus|/lastbus|UNKNOWN in coverage summary|

Don't claim source-compatible variants mt6785/mt6985/mt6885 are enabled solely because they occur in unchanged source. The separate DT 'mediatek, soc-dbg-error-flag' node at0x0d01a000 is not the selected driver's exact match string; generic coverage's candidate naming isn't proof of a bind. Likewise cache-parity's generic claim on CCCI reserved-memory or atf_logger's APUSYS/USB logger candidate tags must not be treated as actual ownership. This source+stock check resolves compatible matching, not a new observed probe.

bootprof/log_store/monitor_hang/mtk_printk_ctrl/pidmap/trace_mmstat are source-backed proc/trace/software diagnostics and may find DT resources indirectly; don't invent a platform node for a module with no own of_device_id. log_store imports natural dbgtop_drm functions; bus/last-bus register dbg_error_flag notifiers. AEE warnings/unwinding and GPU metrics consume previously maintained source ABI providers.

## Stock-binary/source implementation only

Complete source corresponds to accepted stock bytes in development, so actual implemented MMIO/IRQ/resource parsing, logging/cache/bus exception behavior and metadata are **STOCK_BINARY_IMPLEMENTATION**. Source calls of_irq/resource/ioremap APIs according to its unchanged C: DT register sizes/interrupt cells/clock inputs/power-domain IDs/regulator/pinctrl/DMA configuration not present in the saved summary remain **UNKNOWN** until matched against complete original node data. Do not infer physical resources from a generic MediaTek board .dtsi. No MMIO/secure-world/interrupt trigger is performed.

MET core and nine wrappers: software instrumentation interfaces, memory/counter/GPU/TinySys/SSPM/MCUPM/GPUEB/scmi callback APIs and fixed source-provided logging/trace definitions. **PUBLIC_SOURCE_ONLY** feature support becomes **STOCK_BINARY_IMPLEMENTATION** when strict stock parity passes, not proof that measurement runs on this phone. Source-defined shared-memory/reserved-mem/message types compile naturally; no DSP/TinySys firmware algorithm is reconstructed. Source witnesses do not certify those external providers anew. met_backlight_api remains reserved/excluded, and no camera/display/power calibration ownership is inferred.

Firmware interfaces/physical registers/IRQs/clocks/power/regulators/GPIO/DMA for optional MET operation are **UNKNOWN** in saved runtime evidence; keep that boundary rather than fabricate values. Existing stock ABI/module-loading graph is preserved. No boot/recovery/OS deployment action follows from source acceptance.
