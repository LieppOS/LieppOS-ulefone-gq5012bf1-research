#!/usr/bin/env python3
"""Fail-closed consistency checks for the GQ5012BF1 USB research set."""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

REQUIRED_REPORTS = [
    "README.md",
    "FINAL-USB-REPORT.md",
    "USB-EVIDENCE-MATRIX.md",
    "USB-ARCHITECTURE.md",
    "USB-DEVICE-TREE.md",
    "USB-CONTROLLER.md",
    "USB-PHY.md",
    "USB-TYPEC-PD.md",
    "USB-CHARGING-INTEGRATION.md",
    "USB-INTERNAL-THERMAL-CAMERA.md",
    "USB-STOCK-RUNTIME.md",
    "USB-KERNEL-DRIVERS.md",
    "USB-ANDROID-STACK.md",
    "USB3-HARDWARE-ROUTING.md",
    "USB3-FEASIBILITY.md",
    "MT6878-DONOR-COMPARISON.md",
    "CUSTOM-KERNEL-USB-PLAN.md",
    "USB-WEB-SOURCE-LEDGER.md",
]

REQUIRED_EVIDENCE = [
    "stock-safe-state.txt",
    "stock-usb-dt-nodes.txt",
    "live-usb-dt-nodes.txt",
    "stock-module-metadata.txt",
    "stock-module-symbols.tsv",
    "stock-android-usb-services.txt",
    "stock-udc-gadget.txt",
    "stock-platform-bindings.txt",
    "stock-usb-device-topology-idle.txt",
    "stock-typec-state.txt",
    "stock-power-usb-state.txt",
    "stock-usb-modules.txt",
    "stock-usb-dmesg-filtered.txt",
    "stock-runtime-lowlevel.txt",
    "host-external-usb-enumeration.txt",
    "host-external-usb-descriptor.txt",
    "thermal-camera-enumeration-log.txt",
    "thermal-camera-active-sysfs.txt",
    "thermal-camera-transition-sysfs.txt",
    "thermal-camera-capture-manifest.txt",
    "nothing-mt6878-usb-nodes.txt",
    "EDA006599748-armor29pro-charging-board.jpg",
]


def require_text(path: pathlib.Path, fragments: list[str]) -> None:
    text = path.read_text(errors="strict")
    for fragment in fragments:
        if fragment not in text:
            raise AssertionError(f"{path.relative_to(ROOT)} lacks {fragment!r}")


def main() -> int:
    for name in REQUIRED_REPORTS:
        path = ROOT / name
        if not path.is_file() or path.stat().st_size == 0:
            raise AssertionError(f"missing/empty report: {name}")

    evidence = ROOT / "evidence"
    for name in REQUIRED_EVIDENCE:
        path = evidence / name
        if not path.is_file() or path.stat().st_size == 0:
            raise AssertionError(f"missing/empty evidence: {name}")
        if path.stat().st_size > 1_000_000:
            raise AssertionError(f"unexpected giant evidence artifact: {name}")

    require_text(evidence / "stock-safe-state.txt", ["_a", "1"])
    require_text(evidence / "stock-usb-dt-nodes.txt", [
        'compatible = "mediatek,mtu3"',
        'maximum-speed = "high-speed"',
        'compatible = "mediatek,xsphy", "mediatek,mt6878-xsphy"',
        'usb2-phy0@11f40000',
        'compatible = "mediatek,fpga-u3phy"',
        'status = "disabled"',
        'uvc_switch_gpio = <0x89 0x37 0x00>',
        'uvc_vbus_gpio = <0x89 0x98 0x00>',
    ])
    require_text(evidence / "stock-udc-gadget.txt", [
        "11201000.usb0", "current_speed=high-speed",
        "maximum_speed=high-speed", "state=configured",
    ])
    require_text(evidence / "host-external-usb-enumeration.txt", ["480M", "GQ5012BF1"])
    require_text(evidence / "host-external-usb-descriptor.txt", [
        "0x0e8d", "0x201c", "bcdUSB               2.00",
    ])
    require_text(evidence / "thermal-camera-active-sysfs.txt", [
        "speed=480", "idVendor=3474", "idProduct=4321",
        "manufacturer=Thermal Cam Co.,Ltd", "serial=11200000.xhci0",
        "11200000.xhci0 driver=xhci-mtk",
    ])
    require_text(evidence / "thermal-camera-enumeration-log.txt", [
        "new high-speed USB device", "Found UVC 1.10 device Camera (3474:4321)",
    ])
    require_text(evidence / "nothing-mt6878-usb-nodes.txt", [
        'maximum-speed = "high-speed"', "PHY_TYPE_USB2", "status = \"disabled\"",
    ])
    require_text(ROOT / "USB3-FEASIBILITY.md", [
        "UNKNOWN — NEED PCB EVIDENCE", "Single highest-value next experiment",
    ])
    require_text(ROOT / "FINAL-USB-REPORT.md", [
        "1. **Exact identity", "25. **Single highest-value next experiment",
    ])

    print(f"PASS: {len(REQUIRED_REPORTS)} reports and {len(REQUIRED_EVIDENCE)} evidence artifacts")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, OSError, UnicodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
