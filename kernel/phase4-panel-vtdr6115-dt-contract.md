# Phase 4 — VTDR6115 DT contract

Oracle: the already-captured, read-only merged stock tree in `workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649/devicetree.tar`. No device operation was performed during this reconstruction.

```dts
/soc/dsi0@1401a000 {
    status = "okay";
    switch-fps = <120>;

    panel1@0 {
        compatible = "hx,vtdr6115,cmd,120hz,ky";
        reg = <0>;
        vci-gpios     = <&gpio 39  0>;
        dvdd-gpios    = <&gpio 38  0>;
        powerdm-gpios = <&gpio 194 0>;
        reset-gpios   = <&gpio 90  0>;
        gate-ic = <0>;
        pinctrl-names = "default";
        port { endpoint { /* remote DSI endpoint */ }; };
    };
};
```

Raw property cells are preserved in the tar: GPIO controller phandle `0x89`, line cells `0x27`, `0x26`, `0xc2`, `0x5a`, flags 0.

## Consumed by stock module

- `compatible`, `reg`, DSI graph endpoint/remote parent
- `reset-gpios`, `vci-gpios`, `dvdd-gpios`
- optional `backlight` phandle
- optional `rc-enable`
- optional `lcm-degree`
- parent-presence property `init-panel-off`

## Present/absent on this device

Present: compatible/reg, three used GPIOs, `powerdm-gpios`, gate-ic, default pinctrl, endpoint, parent `switch-fps=120`.

Absent: panel backlight phandle, regulator supplies, `rc-enable`, `lcm-degree`, and parent `init-panel-off`. Consequently round-corner and degree remain zero/default; the driver assumes bootloader-prepared/enabled state until normal lifecycle transitions.

`powerdm-gpios` is present but **unused** by this module: there is no matching string, relocation, GPIO request, or field access in the stock ELF. It must not be invented into the replacement sequence.
