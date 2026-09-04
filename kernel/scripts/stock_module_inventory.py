#!/usr/bin/env python3

import argparse
import csv
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path


PARTITIONS = ("vendor_dlkm", "system_dlkm", "odm_dlkm")

CSV_FIELDS = [
    "partition",
    "filename",
    "relative_path",
    "sha256",
    "size_bytes",
    "module_name",
    "vermagic",
    "depends",
    "aliases",
    "softdeps",
    "license",
    "description",
    "srcversion",
    "retpoline",
    "elf_machine",
    "imported_symbol_count",
    "exported_symbol_count",
    "has___versions",
]


def run(cmd, *, check=True):
    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        errors="replace",
    )

    if check and proc.returncode != 0:
        raise RuntimeError(
            f"command failed ({proc.returncode}): {' '.join(map(str, cmd))}\n"
            f"stderr: {proc.stderr.strip()}"
        )

    return proc.stdout


def find_tool(name, fallback=None):
    found = shutil.which(name)
    if found:
        return found

    if fallback:
        found = shutil.which(fallback)
        if found:
            return found

    raise RuntimeError(f"required tool not found in PATH: {name}")


def discover_modules(partitions_root):
    modules = []
    counts = Counter({p: 0 for p in PARTITIONS})

    for partition in PARTITIONS:
        root = partitions_root / partition

        if not root.is_dir():
            continue

        found = sorted(
            p for p in root.rglob("*.ko")
            if p.is_file()
        )

        counts[partition] = len(found)
        modules.extend(found)

    modules.sort(
        key=lambda p: p.relative_to(partitions_root).as_posix()
    )

    return modules, counts


def validate_counts(counts, expected, expected_total):
    errors = []

    for partition in PARTITIONS:
        actual = counts.get(partition, 0)
        wanted = expected.get(partition, 0)

        if actual != wanted:
            errors.append(
                f"{partition} expected {wanted}, found {actual}"
            )

    total = sum(counts.get(p, 0) for p in PARTITIONS)

    if total != expected_total:
        errors.append(
            f"total expected {expected_total}, found {total}"
        )

    if errors:
        raise ValueError("; ".join(errors))


def sha256_file(path):
    digest = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def modinfo_field(modinfo, path, field):
    out = run(
        [modinfo, "-F", field, str(path)],
        check=False,
    )

    values = [
        line.strip()
        for line in out.splitlines()
        if line.strip()
    ]

    return ";".join(values)


def get_elf_machine(readelf, path):
    out = run([readelf, "-h", str(path)])

    for line in out.splitlines():
        if "Machine:" in line:
            return line.split("Machine:", 1)[1].strip()

    return ""


def has_versions_section(readelf, path):
    out = run([
        readelf,
        "-S",
        "--wide",
        str(path),
    ])

    return "yes" if "__versions" in out else "no"


def get_symbol_counts(nm, path):
    undefined = run(
        [nm, "-u", str(path)],
        check=False,
    )

    imports = {
        line.split()[-1]
        for line in undefined.splitlines()
        if line.strip() and line.split()
    }

    defined = run(
        [nm, "--defined-only", str(path)],
        check=False,
    )

    exports = set()

    for line in defined.splitlines():
        parts = line.split()

        if not parts:
            continue

        name = parts[-1]

        if name.startswith("__ksymtab_"):
            exports.add(
                name.removeprefix("__ksymtab_")
            )

    return len(imports), len(exports)


def collect_row(path, partitions_root, tools):
    relative = path.relative_to(partitions_root)
    partition = relative.parts[0]

    imports, exports = get_symbol_counts(
        tools["nm"],
        path,
    )

    return {
        "partition": partition,
        "filename": path.name,
        "relative_path": relative.as_posix(),
        "sha256": sha256_file(path),
        "size_bytes": str(path.stat().st_size),

        "module_name": modinfo_field(
            tools["modinfo"], path, "name"
        ),
        "vermagic": modinfo_field(
            tools["modinfo"], path, "vermagic"
        ),
        "depends": modinfo_field(
            tools["modinfo"], path, "depends"
        ),
        "aliases": modinfo_field(
            tools["modinfo"], path, "alias"
        ),
        "softdeps": modinfo_field(
            tools["modinfo"], path, "softdep"
        ),
        "license": modinfo_field(
            tools["modinfo"], path, "license"
        ),
        "description": modinfo_field(
            tools["modinfo"], path, "description"
        ),
        "srcversion": modinfo_field(
            tools["modinfo"], path, "srcversion"
        ),
        "retpoline": modinfo_field(
            tools["modinfo"], path, "retpoline"
        ),

        "elf_machine": get_elf_machine(
            tools["readelf"], path
        ),
        "imported_symbol_count": str(imports),
        "exported_symbol_count": str(exports),
        "has___versions": has_versions_section(
            tools["readelf"], path
        ),
    }


def write_csv_atomic(output, rows):
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{output.name}.",
        suffix=".tmp",
        dir=str(output.parent),
    )

    os.close(fd)

    temporary = Path(temporary_name)

    try:
        with temporary.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as f:
            writer = csv.DictWriter(
                f,
                fieldnames=CSV_FIELDS,
                extrasaction="raise",
            )

            writer.writeheader()
            writer.writerows(rows)

        temporary.replace(output)

    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def parse_args():
    script = Path(__file__).resolve()
    repo_root = script.parents[2]

    parser = argparse.ArgumentParser(
        description=(
            "Inventory canonical GQ5012BF1 "
            "stock kernel modules."
        )
    )

    parser.add_argument(
        "--partitions-root",
        type=Path,
        default=(
            repo_root
            / "workspace/gq5012bf1/stock/partitions"
        ),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=(
            repo_root
            / "kernel/stock-module-inventory.csv"
        ),
    )

    parser.add_argument(
        "--expect-vendor",
        type=int,
        default=215,
    )

    parser.add_argument(
        "--expect-system",
        type=int,
        default=60,
    )

    parser.add_argument(
        "--expect-odm",
        type=int,
        default=0,
    )

    parser.add_argument(
        "--expect-total",
        type=int,
        default=275,
    )

    return parser.parse_args()


def main():
    args = parse_args()

    partitions_root = (
        args.partitions_root.resolve()
    )

    if not partitions_root.is_dir():
        raise SystemExit(
            "partitions root not found: "
            f"{partitions_root}"
        )

    expected = {
        "vendor_dlkm": args.expect_vendor,
        "system_dlkm": args.expect_system,
        "odm_dlkm": args.expect_odm,
    }

    modules, counts = discover_modules(
        partitions_root
    )

    validate_counts(
        counts,
        expected,
        args.expect_total,
    )

    tools = {
        "modinfo": find_tool("modinfo"),
        "readelf": find_tool(
            "readelf",
            "llvm-readelf",
        ),
        "nm": find_tool(
            "llvm-nm",
            "nm",
        ),
    }

    rows = []
    total = len(modules)

    for index, path in enumerate(
        modules,
        start=1,
    ):
        rows.append(
            collect_row(
                path,
                partitions_root,
                tools,
            )
        )

        if (
            index == 1
            or index % 25 == 0
            or index == total
        ):
            print(
                f"[{index:3d}/{total}] "
                f"{path.relative_to(partitions_root)}",
                file=sys.stderr,
            )

    if len(rows) != args.expect_total:
        raise SystemExit(
            "internal inventory mismatch: "
            f"expected {args.expect_total} rows, "
            f"got {len(rows)}"
        )

    output = args.output.resolve()

    write_csv_atomic(
        output,
        rows,
    )

    print(
        f"wrote {len(rows)} rows: {output}"
    )

    print(
        "counts: "
        + ", ".join(
            f"{partition}="
            f"{counts.get(partition, 0)}"
            for partition in PARTITIONS
        )
    )


if __name__ == "__main__":
    main()
