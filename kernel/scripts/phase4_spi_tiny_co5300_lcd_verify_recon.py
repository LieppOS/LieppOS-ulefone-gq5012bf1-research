#!/usr/bin/env python3
"""Fail-closed static verifier for the GQ5012BF1 CO5300 reconstruction."""
from pathlib import Path
import csv
import hashlib
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "workspace/phase4-spi-tiny-co5300-lcd"
K = ROOT / "kernel"
FINAL = Path("/home/armol/kernel-work/gki-12901745-workspace/lieppos/spi-tiny-co5300-lcd-recon/spi_tiny_co5300_lcd.ko")
checks = []


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ok(name, condition, detail=""):
    if not condition:
        raise AssertionError(f"FAIL {name}: {detail}")
    checks.append(name)


def tsv(path, key):
    with open(path, newline="") as f:
        return {row[key]: row for row in csv.DictReader(f, delimiter="\t")}


def modversions(path):
    out = subprocess.check_output(
        ["modprobe", "--dump-modversions", str(path)], text=True
    )
    result = {}
    for line in out.splitlines():
        if "\t" in line:
            crc, symbol = line.split("\t", 1)
            result[symbol] = crc.lower()
    return result


def main():
    stock = P / "oracle/spi_tiny_co5300_lcd.stock.ko"
    rebuild = P / "rebuild/spi_tiny_co5300_lcd.ko"
    source = P / "reconstruction-source/spi_tiny_co5300_lcd.c"

    ok("frozen stock SHA", sha(stock) == "39eecad8254c2fc69f9c8d52902b443b3adc64c79c4c6a529af19b4b1f2a9742")
    ok("reconstruction source SHA", sha(source) == "863fabcffc50d212273d4c8189b3b20188373b2f7b7e620cabff8007c9fd49aa")
    ok("rebuild SHA", sha(rebuild) == "9149da0533d4d8327518d22762964c2e656f4aeb95fdd8a88280c109555dbfe2")
    ok("required final artifact", FINAL.is_file() and sha(FINAL) == sha(rebuild))

    stock_functions = tsv(K / "phase4-spi-tiny-co5300-lcd-functions.tsv", "function")
    rebuild_functions = tsv(P / "rebuild/rebuild-spi-tiny-co5300-lcd-functions.tsv", "function")
    ok("25-function count", len(stock_functions) == len(rebuild_functions) == 25)
    ok("exact function-name set", set(stock_functions) == set(rebuild_functions))
    direct_helpers = {
        "spidev_sync_read_data",
        "spidev_sync_write_cmd",
        "spidev_sync_write_data",
        "spidev_sync_write_multi_data",
        "tiny_lcd_power_enable_func",
    }
    ok(
        "address-taken KCFI parity",
        all(
            stock_functions[name]["kcfi_id"] == rebuild_functions[name]["kcfi_id"]
            for name in stock_functions
            if name not in direct_helpers
        ),
    )

    stock_imports = tsv(K / "phase4-spi-tiny-co5300-lcd-imports.tsv", "symbol")
    rebuild_imports = tsv(P / "rebuild/rebuild-spi-tiny-co5300-lcd-imports.tsv", "symbol")
    ok("58-MODVERSION count", len(stock_imports) == len(rebuild_imports) == 58)
    ok("exact import set", set(stock_imports) == set(rebuild_imports))
    ok(
        "exact import CRC map",
        all(
            stock_imports[name]["crc"].lower()
            == rebuild_imports[name]["crc"].lower()
            for name in stock_imports
        ),
    )
    providers = {
        "tiny_tp_gesture_contorl": "0x4e4b7919",
        "tiny_tp_power_contorl": "0xfcc94fc7",
        "yft_tinylcd_device_add": "0x9c6d85d0",
        "yft_set_tinylcd_device_used": "0x25e94db4",
    }
    ok(
        "four vendor provider edges",
        all(rebuild_imports[name]["crc"].lower() == crc for name, crc in providers.items()),
    )
    ok("loader MODVERSION view", all(modversions(rebuild).get(name) == row["crc"].lower() for name, row in rebuild_imports.items()))
    rebuild_exports = tsv(P / "rebuild/rebuild-spi-tiny-co5300-lcd-exports.tsv", "symbol")
    ok("leaf module has no exports", not rebuild_exports)

    stock_objects = tsv(K / "phase4-spi-tiny-co5300-lcd-objects.tsv", "object")
    rebuild_objects = tsv(P / "rebuild/rebuild-spi-tiny-co5300-lcd-objects.tsv", "object")
    exact_objects = {
        "gImage_logo": (231200, "c1a917c583dd698be389e7bf7bbc638dafc58fbdb0e04dd44644a459b37761cf"),
        "init_setting": (1232, "908e91b61b0e1e5cdb1f618bc3f605bb08ec39608902de27f7aa6a5fb23fd0ff"),
        "spi_tiny_lcd_driver": (216, "a5645e7a3fa0866cde8842c4dab96567507c3d1a3c028b816bc63f6966367b70"),
        "tiny_lcd_miscdev": (80, "72de9e04f5062b5c6c5af8e48c07bc745cf715eea93ed719f6e370febde041a9"),
        "tiny_lcd_fops": (272, "e4d879a3407de578f579dfab4366fcea75a6649c683d9efe4f056f6505437574"),
        "framesize": (8, "d2711e7cf64ddc150f8cdaea83190a396d35917fa1f709fd78d707dbbbb35f3b"),
        "write_frame_status": (8, "7c9fa136d4413fa6173637e883b6998d32e1d675f88cddff9dcbcf331820f4b8"),
    }
    ok(
        "exact critical object bytes",
        all(
            int(stock_objects[name]["size"]) == int(rebuild_objects[name]["size"]) == size
            and stock_objects[name]["sha256"] == rebuild_objects[name]["sha256"] == digest
            for name, (size, digest) in exact_objects.items()
        ),
    )
    attributes = [
        "driver_attr_tiny_lcd_power_enable",
        "driver_attr_tiny_lcd_bl_enable",
        "driver_attr_tiny_lcd_backlight_control",
        "driver_attr_tiny_lcd_write_frame",
        "driver_attr_tiny_lcd_tp_control",
    ]
    ok("five exact driver attributes", all(stock_objects[name]["sha256"] == rebuild_objects[name]["sha256"] for name in attributes))

    text = source.read_text()
    ok("module identity", all(value in text for value in [
        'TINY_LCD_NAME              "spi_tiny_lcd_co5300"',
        'TINY_LCD_MISC_NAME         "tiny_lcd_miscdev"',
        'MODULE_VERSION("v0.01")',
        'MODULE_LICENSE("GPL v2")',
    ]))
    ok("OF compatible", '"hxytech, spi_tiny_lcd"' in text)
    ok("exact SPI rates", "TINY_LCD_SPI_HZ            52000000U" in text and "TINY_LCD_READ_HZ           1000000U" in text)
    ok("exact RGB565 frame sizes", all(value in text for value in [
        "TINY_LCD_FULL_FRAME        (340U * 340U * 2U)",
        "TINY_LCD_CROP_FRAME        (320U * 320U * 2U)",
        "first = 10;", "last = 329;", "last = 339;",
    ]))
    ok("controller ID gate", all(value in text for value in [
        "spidev_sync_read_data(0xda)", "spidev_sync_read_data(0xdb)",
        "id0 != 0x33", "id1 == 0x11", "id1 == 0x10",
    ]))
    ioctl_values = ["0x00006b37U", "0x00006b38U", "0x00006b39U", "0x00006b3aU",
                    "0x40086b3bU", "0x40086b3cU", "0xc0086b3dU", "0x00006b3eU",
                    "0x00006b3fU", "0x00006b40U", "0x40086b41U"]
    ok("complete ioctl ABI", all(value in text for value in ioctl_values))
    ok("TE delayed-work path", all(value in text for value in [
        "IRQF_TRIGGER_FALLING", "queue_delayed_work_on(WORK_CPU_UNBOUND",
        "write_frame_status != 3", "write_frame_status = 1",
    ]))
    ok("power sequencing", all(value in text for value in [
        "spidev_sync_write_cmd(0x28)", "spidev_sync_write_cmd(0x10)",
        "mdelay(220)", "mdelay(15)", "mdelay(30)", "mdelay(120)",
        "disable_irq", "enable_irq",
    ]))
    ok("YFT and Hynitron calls", all(value in text for value in [
        "yft_tinylcd_device_add(&spi_tiny_lcd_driver, 0)",
        "yft_set_tinylcd_device_used(TINY_LCD_NAME, 1)",
        "tiny_tp_power_contorl", "tiny_tp_gesture_contorl",
    ]))
    ok("boot-mode gate", all(value in text for value in [
        'of_find_node_by_path("/chosen@0")', '"atag,boot"',
        "mode == 1", "mode == 5", "mode == 6", "mode == 8", "mode == 9",
    ]))

    yft_symvers = (P / "oracle/stock-yft-devinfo.symvers").read_text()
    hyn_symvers = (P / "oracle/hynitron-rebuilt.Module.symvers").read_text()
    ok("stock YFT witness", all(name in yft_symvers and crc in yft_symvers for name, crc in providers.items() if name.startswith("yft_")))
    ok("source-built Hynitron witness", all(name in hyn_symvers and crc in hyn_symvers for name, crc in providers.items() if name.startswith("tiny_tp_")))
    makefile = (P / "reconstruction-source/Makefile").read_text()
    ok("provider symvers build inputs", "hynitron-rebuilt.Module.symvers" in makefile and "stock-yft-devinfo.symvers" in makefile)
    combined = text + makefile
    ok("no prohibited ABI fabrication", not any(token in combined for token in [
        "KBUILD_MODPOST_WARN", "__versions[]", "__crc_", "objcopy --update-section",
    ]))

    log = (P / "rebuild/build.log").read_text(errors="replace")
    ok("clean exact-GKI build", "Build completed successfully" in log and not re.search(r"(^|\s)warning:", log, re.I | re.M))
    print(f"{len(checks)}/{len(checks)} CHECKS PASSED")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
