# GQ5012BF1 GenieZone transport DT/platform contract

## Stock evidence

Authoritative decompile: `workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dts`, backed by committed vendor-boot DTB and live-stock devicetree snapshots. No DT was edited.

## Root provider nodes

```dts
trusty {
    compatible = "android,trusty-smc-v1";
    ranges;
    #address-cells = <2>;
    #size-cells = <2>;
    tee-id = <0>;
    tee-name = "trusty";

    trusty-virtio { compatible = "android,trusty-virtio-v1"; };
    trusty-irq {
        compatible = "android,trusty-irq-v1";
        ppi-interrupt-parent = <0x01>;
    };
    tz-system {
        compatible = "mediatek,trusty-tz";
        virtio-supply = <&trusty_virtio>; /* stock phandle 0xb3 */
        irq-supply = <&trusty_irq>;       /* stock phandle 0x15a */
    };
    mtee {
        compatible = "mediatek,trusty-mtee-v1";
        tz-supply = <&tz_system>;         /* stock phandle 0x15b */
    };
    trusty-gz-log { compatible = "android,trusty-gz-log-v1"; };
    trusty-sapu { compatible = "mediatek,trusty-sapu"; ... };
};

nebula {
    compatible = "android,nebula-smc-v1";
    ranges;
    #address-cells = <2>;
    #size-cells = <2>;
    tee-id = <1>;
    tee-name = "nebula";

    nebula-virtio { compatible = "android,nebula-virtio-v1"; };
    nebula-irq {
        compatible = "android,nebula-irq-v1";
        ppi-interrupt-parent = <0x01>;
    };
    nebula-gz-log { compatible = "android,nebula-gz-log-v1"; };
};
```

Exact root phandles are Trusty `0x2c7` and Nebula `0x2c8` in the frozen decompile.

## Driver binding

`gz_trusty_mod` registers two platform drivers:

- `android,trusty-smc-v1` → driver name `trusty`, reads `tee-id=0`;
- `android,nebula-smc-v1` → driver name `nebula`, reads `tee-id=1`.

Probe rejects a missing OF node. It reads `tee-id`, establishes platform drvdata, initializes Linux Trusty state, and calls `of_platform_populate` so virtio/IRQ/tz-system/log/SAPU child drivers probe beneath the correct TEE parent. Remove unregisters those child platform devices.

`gz_ipc_mod` is a virtio driver and has no direct OF match table. It binds the TIPC virtio device created by the child virtio stack, uses the TEE-specific parent chain, and obtains its cdev/message configuration from virtio config rather than DT properties.

## IRQ, memory, mailbox, and shared memory

The Trusty/Nebula SMC parent nodes contain no direct `interrupts`, `reg`, reserved-memory, or mailbox property. IRQ routing belongs to the child `*-irq` nodes (`ppi-interrupt-parent`). TIPC buffers are dynamically allocated shareable pages and passed through virtqueues; no dedicated TIPC reserved-memory or mailbox DT property is stock-visible. `tz-system` links to the Trusty virtio and IRQ child through `virtio-supply`/`irq-supply` phandles.

## Ordering

Normal vendor module order is:

1. `gz_trusty_mod.ko` — index 145 (one-based)
2. `gz_ipc_mod.ko` — index 146
3. `gz_tz_system.ko` — index 149

`modules.dep` requires `gz_ipc_mod → gz_trusty_mod` and `gz_tz_system → gz_ipc_mod,gz_trusty_mod`. Within device probing, Trusty parent state must exist before its populated child devices, and the TIPC virtio device must exist before kernel clients can connect. A missing TIPC virtio device produces `-ENOENT`/`-ENODEV`; it is not hidden by a synthetic fallback.
