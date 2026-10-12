# Hardware and runtime contract

All findings are static/offline. No phone, reboot register, GPU test, DMA allocation or kernel module was operated.

## reboot-mode framework and syscon driver

The stock merged DT places this child below the syscon at `0x1c00a000`:

```dts
reboot-mode {
    compatible = "syscon-reboot-mode";
    offset = <0x24>;
    mask = <0x0f>;
    mode-charger = <0x01>;
    mode-recovery = <0x02>;
    mode-bootloader = <0x03>;
    mode-dm-verity-dev-corrupt = <0x04>;
    mode-kpoc = <0x05>;
    mode-ddr-reserve = <0x06>;
    mode-meta = <0x07>;
    mode-rpmbpk = <0x08>;
};
```

`reboot-mode.ko` parses every DT property prefixed `mode-`, exports the register/unregister and devm variants of
the framework, and registers a reboot notifier. When a real reboot command matches a mode, the notifier calls the
provider's write callback. `syscon-reboot-mode.ko` obtains the parent syscon regmap and its `offset`/`mask`, then
uses `regmap_update_bits(map, 0x24, 0x0f, magic)`.

This report preserves the actual mode values but **does not** claim they were exercised. No register write or reboot
was performed. Stock load order is reboot-mode 250, syscon-reboot-mode 251; the latter has `depends=reboot-mode` and
imports `reboot_mode_register` with matching CRC.

## hbt

The exact Android-U driver registers two world-writable misc devices, `/dev/hbt` and `/dev/vhbt` (mode 0666), ABI
major/minor 2.0. Its ioctls support version query, selected `mm_struct` compatibility fields, mmap base, proxy
`security_file_ioctl`, compatibility robust-list access, getdents64 and lseek. It is a userspace compatibility
bridge, not a hardware device driver; there is no DT binding. Stock loads it second-stage at sequence 424.

The source manipulates only the calling process and caller-supplied file descriptors under normal kernel locks and
security checks. Matching source does not endorse exposing these ioctls to arbitrary policy domains; SELinux/device
permissions remain separate userspace policy.

## scheduler_ext

`scheduler_ext.ko` is a two-function inert external module: init returns 0 and exit is empty. It exports nothing,
imports only `__stack_chk_fail`, has no DT node and was never loaded in the saved capture. It is distinct from the
certified MediaTek `scheduler.ko` and does not implement a scheduling policy.

## Mali DMA-BUF test exporter

`mali_dmabuf_test_mt6878_r44.ko` is ARM's standalone diagnostic DMA-BUF exporter (`/dev/dma_buf_te`, ABI 1.0). Its
ioctls can create contiguous/non-contiguous test DMA-BUFs, query them, inject attach/map/mmap failures, and fill test
buffers; the implementation supports attach/detach, DMA/CPU mapping and synchronization. It imports namespace
`DMA_BUF` and exports no symbols.

It is **not** `mali_kbase_mt6878_r44`, not required evidence for GPU runtime correctness, and contains no GPU
firmware. Although present and listed at stock load sequence 305, no GPU or DMA-BUF test was run here.

## Load and dependency order

- built-in GKI providers precede all modules;
- `reboot-mode` 250 precedes `syscon-reboot-mode` 251;
- Mali test exporter 305;
- hbt 424;
- scheduler_ext: not in either modules.load path / never loaded.

The 107-edge dependency graph has 106 GKI imports and one intra-batch import; every CRC, licence and namespace is
consistent and none is unresolved.
