#!/usr/bin/env python3

import argparse
import csv
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("build_info")
    ap.add_argument("output")
    args = ap.parse_args()

    manifest_path = Path(args.manifest)
    build_info_path = Path(args.build_info)
    output_path = Path(args.output)

    with build_info_path.open(encoding="utf-8") as f:
        info = json.load(f)

    sha_by_name = {}
    sha_sources = {}

    def add_pin(name, sha, source):
        if not isinstance(name, str):
            return
        if not isinstance(sha, str) or not SHA_RE.fullmatch(sha):
            return

        old = sha_by_name.get(name)
        if old is not None and old != sha:
            raise RuntimeError(
                f"conflicting SHA for project {name!r}: "
                f"{old} ({sha_sources[name]}) vs {sha} ({source})"
            )

        sha_by_name[name] = sha
        sha_sources[name] = source

    def walk(obj, where="$"):
        if isinstance(obj, dict):
            # BUILD_INFO project records commonly look like:
            # {"name": "kernel/common", ..., "revision": "<40-char SHA>"}
            name = obj.get("name")
            revision = obj.get("revision")

            if (
                isinstance(name, str)
                and isinstance(revision, str)
                and SHA_RE.fullmatch(revision)
            ):
                add_pin(name, revision, f"{where}:project-record")

            # BUILD_INFO also contains project-name -> SHA maps.
            # Only accept keys that look like actual project names.
            for key, value in obj.items():
                if (
                    isinstance(key, str)
                    and "/" in key
                    and isinstance(value, str)
                    and SHA_RE.fullmatch(value)
                ):
                    add_pin(key, value, f"{where}:project-map")

                walk(value, f"{where}.{key}")

        elif isinstance(obj, list):
            for i, value in enumerate(obj):
                walk(value, f"{where}[{i}]")

    walk(info)

    root = ET.parse(manifest_path).getroot()
    default = root.find("default")

    default_revision = (
        default.get("revision", "") if default is not None else ""
    )
    default_remote = (
        default.get("remote", "") if default is not None else ""
    )

    rows = []

    for project in root.findall("project"):
        name = project.get("name", "")
        path = project.get("path", name)
        explicit_revision = project.get("revision", "")
        effective_revision = explicit_revision or default_revision
        remote = project.get("remote", default_remote)

        rows.append({
            "name": name,
            "path": path,
            "manifest_revision": effective_revision or "-",
            "ci_sha": sha_by_name.get(name, "-"),
            "ci_pin_source": sha_sources.get(name, "-"),
            "remote": remote or "-",
        })

    # Atomic output: don't destroy the existing file if parsing fails.
    tmp = output_path.with_suffix(output_path.suffix + ".tmp")

    with tmp.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "name",
                "path",
                "manifest_revision",
                "ci_sha",
                "ci_pin_source",
                "remote",
            ],
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerows(rows)

    tmp.replace(output_path)

    print(f"manifest projects: {len(rows)}")
    print(f"BUILD_INFO project SHAs discovered: {len(sha_by_name)}")
    print(f"manifest projects with CI SHA: {sum(r['ci_sha'] != '-' for r in rows)}")
    print(f"output: {output_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise
