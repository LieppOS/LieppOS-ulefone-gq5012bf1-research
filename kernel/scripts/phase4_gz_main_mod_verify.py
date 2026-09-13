#!/usr/bin/env python3
"""Fail-closed verifier for the GQ5012BF1 gz_main_mod source closure.

Every check must pass. Any missing artifact, changed hash, weakened provider
edge, altered userspace ABI or forbidden build technique fails the run.

Read-only. Nothing is loaded, flashed or invoked.
"""
from __future__ import annotations

import csv
import hashlib
import json
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
WS = pathlib.Path("/home/armol/kernel-work/gki-12901745-workspace")
PKG = WS / "kernel_device_modules-6.1/drivers/misc/mediatek/geniezone"
ART = REPO / "workspace/phase4-gz-main-mod"

STOCK_SHA = "398ce0058798adf1d919dbd60856ed7b83e956f5d778ff6d3116e27468916fc7"
STOCK_SIZE = 159400
BUILD_ID = "3f40ddec521d65a7dce6f240fa306e8f8da1057d"
VERMAGIC = ("6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload "
            "modversions aarch64")
REVISION = "957dac185efe46cbf6336b0fff9516d84c8cd78f"
REBUILT_SHA = "7b7cb36b03d7749e5f7b3d53c8b0207bfc7f7e6b4bf2819c501b42d42cb5df51"

PASS: list[str] = []
FAIL: list[str] = []


def check(cond: bool, label: str) -> bool:
    (PASS if cond else FAIL).append(label)
    return bool(cond)


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tsv(path: pathlib.Path) -> list[dict]:
    with open(path, newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def tool(*args: str) -> str:
    return subprocess.run(args, capture_output=True, text=True).stdout


def code_only(text: str) -> str:
    """Strip '#' comments so forbidden-technique checks test real directives.

    Both Makefile and Starlark use '#' to end-of-line. Documentation that
    merely *names* a forbidden technique must not trip the check; an actual
    directive must.
    """
    out = []
    for line in text.splitlines():
        stripped = line.split("#", 1)[0]
        if stripped.strip():
            out.append(stripped)
    return "\n".join(out)


# ---------------------------------------------------------------- oracle ---
def verify_oracle() -> None:
    stock = ART / "oracle/gz_main_mod.stock.ko"
    if not check(stock.is_file(), "stock oracle present"):
        return
    check(sha256(stock) == STOCK_SHA, "stock SHA256 unchanged")
    check(stock.stat().st_size == STOCK_SIZE, "stock size 159400")

    canonical = (REPO / "workspace/gq5012bf1/stock/partitions/vendor_dlkm/"
                 "lib/modules/gz_main_mod.ko")
    check(canonical.is_file() and sha256(canonical) == STOCK_SHA,
          "oracle matches the canonical stock placement byte-for-byte")

    notes = tool("llvm-readelf", "-n", str(stock))
    check(BUILD_ID in notes, "stock Build ID unchanged")

    info = tool("modinfo", str(stock))
    check(f"vermagic:       {VERMAGIC}" in info or VERMAGIC in info,
          "stock vermagic unchanged")
    check("name:           gz_main_mod" in info, "module name gz_main_mod")
    check("import_ns:      DMA_BUF" in info, "import namespace DMA_BUF")
    check("parm" not in info, "stock declares no module parameters")
    for alias in ("of:N*T*Cmediatek,trusty-mtee-v1",
                  "of:N*T*Cmediatek,trusty-mtee-v1C*"):
        check(alias in info, f"stock alias {alias}")
    for dep in ("gz_tz_system", "gz_trusty_mod", "gz_ipc_mod", "ffa_v10",
                "mtk_sec_heap", "tmem_ffa"):
        check(re.search(rf"depends:.*\b{re.escape(dep)}\b", info) is not None,
              f"stock depends lists {dep}")

    comment = tool("llvm-readelf", "-p", ".comment", str(stock))
    check("clang version 17.0.2" in comment, "stock compiler clang 17.0.2")

    mods = (REPO / "workspace/gq5012bf1/stock/partitions/vendor_dlkm/"
            "lib/modules/modules.load").read_text().splitlines()
    check(mods.index("gz_main_mod.ko") == 149,
          "modules.load index 149 zero-based (150 one-based)")

    dep_file = (REPO / "workspace/gq5012bf1/stock/partitions/vendor_dlkm/"
                "lib/modules/modules.dep").read_text().splitlines()
    lhs = [ln for ln in dep_file if ln.startswith(
        "/vendor_dlkm/lib/modules/gz_main_mod.ko:")]
    check(len(lhs) == 1, "exactly one modules.dep entry for gz_main_mod")
    check(all("gz_main_mod.ko" not in ln.split(":", 1)[1] for ln in dep_file),
          "no stock module depends on gz_main_mod (proven leaf)")

    copies = [p for p in (REPO / "workspace/gq5012bf1/stock").rglob("*.ko")
              if p.name in ("gz_main_mod.ko", "gz-main-mod.ko")]
    check(len(copies) == 1, "exactly one stock placement, no duplicates")
    check(not any("recovery" in str(p).lower() for p in copies),
          "absent from recovery")


# ---------------------------------------------------------------- source ---
def verify_source() -> None:
    hashes = ART.parent.parent / "kernel/phase4-gz-main-mod-source-hashes.tsv"
    rows = tsv(REPO / "kernel/phase4-gz-main-mod-source-hashes.tsv") \
        if hashes else []
    check(len(rows) == 16, "16 source/header hash rows recorded")
    for row in rows:
        path = WS / "kernel_device_modules-6.1" / row["path"]
        check(path.is_file() and sha256(path) == row["sha256"],
              f"source unchanged: {row['path']}")

    donor = pathlib.Path("/home/armol/androido_dalykai/LieppOS custom ROM/"
                         "kernel-research/nothing-mt6878/device_modules")
    head = subprocess.run(["git", "-C", str(donor), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    check(head == REVISION, f"pinned donor revision {REVISION}")

    for name in ("Makefile", "BUILD.bazel", "Makefile.vendor", "Kconfig",
                 "stock-provider.symvers", "stock-provider.provenance.json"):
        check((PKG / name).is_file(), f"build plumbing present: {name}")

    # vendor object list reproduced exactly
    vendor = (PKG / "Makefile.vendor").read_text()
    check("gz_main_mod-objs += gz_main.o" in vendor,
          "vendor Makefile preserved verbatim")
    mk = (PKG / "Makefile").read_text()
    for obj in ("gz_main.o", "mtee_ut/gz_ut.o", "mtee_ut/gz_chmem_ut.o",
                "mtee_ut/gz_shmem_ut.o", "mtee_ut/gz_vreg_ut.o", "gz_ffa.o"):
        check(f"gz_main_mod-y += {obj}" in mk, f"object in build: {obj}")

    # __FILE__ parity: the module must be built at the vendor path
    check(PKG.as_posix().endswith(
        "kernel_device_modules-6.1/drivers/misc/mediatek/geniezone"),
        "built in the vendor directory layout (__FILE__ parity)")


# ---------------------------------------------------------------- config ---
def verify_config() -> None:
    mk = (PKG / "Makefile").read_text()
    for sym in ("CONFIG_MTK_GZ_MAIN_MODULE", "CONFIG_MTK_ENABLE_GENIEZONE",
                "CONFIG_MTK_GZ_KREE", "CONFIG_MTK_PROT_MEM_SUPPORT",
                "CONFIG_ARM_FFA_TRANSPORT"):
        check(f"-D{sym}=1" in mk, f"config ON: {sym}")
    check("-faddrsig" in mk, "-faddrsig (stock carries .llvm_addrsig)")
    check(not re.search(r"^\s*ccflags-y \+= -DCONFIG_MTK_GZ_SUPPORT_SDSP",
                        mk, re.M),
          "CONFIG_MTK_GZ_SUPPORT_SDSP deliberately undefined")

    strings = {r["string"] for r in
               tsv(REPO / "kernel/phase4-gz-main-mod-strings.tsv")}
    check(any("MTEE_CMD_FOD_TEE_SHM_ON" in s for s in strings),
          "SDSP-off evidence: FOD_TEE_SHM_ON case compiled in")
    check(not any("CONFIG_MTK_PROT_MEM_SUPPORT disabled" in s
                  for s in strings),
          "PROT_MEM-on evidence: no 'disabled' string")


# -------------------------------------------------------------- provider ---
def verify_providers() -> None:
    rows = tsv(REPO / "kernel/phase4-gz-main-mod-provider-map.tsv")
    check(len(rows) == 76, "provider map covers all 76 imports")
    check(all(r["status"] == "EXACT" for r in rows),
          "every provider edge CRC is EXACT")
    check(not any(r["class"] == "UNKNOWN" for r in rows),
          "UNKNOWN provider count is 0")

    by_class: dict[str, int] = {}
    for row in rows:
        by_class[row["class"]] = by_class.get(row["class"], 0) + 1

    expected = {
        "GKI_NATURAL": 51,
        "GZ_TZ_SYSTEM_NATURAL": 15,
        "GZ_TRUSTY_NATURAL": 5,
        "GZ_IPC_NATURAL": 1,
        "FFA_V10_NATURAL": 1,
        "TMEM_FFA_NATURAL": 2,
        "STOCK_RUNTIME_PROVIDER": 1,
    }
    for cls, n in expected.items():
        check(by_class.get(cls) == n, f"{cls} == {n}")

    stock_edges = [r for r in rows if r["class"] == "STOCK_RUNTIME_PROVIDER"]
    check([r["symbol"] for r in stock_edges] == ["dmabuf_to_secure_handle"],
          "the only stock runtime edge is dmabuf_to_secure_handle")
    check(all("mtk_sec_heap" in r["provider"] for r in stock_edges),
          "that edge is declared as mtk_sec_heap")

    prov = json.loads((PKG / "stock-provider.provenance.json").read_text())
    check("NOT reconstructed" in prov["note"],
          "stock provider is declared, never described as reconstructed")

    natural = [r for r in rows if r["class"].endswith("_NATURAL")]
    check(len(natural) == 75, "75 of 76 imports are natural")

    prov_tsv = tsv(REPO / "kernel/phase4-gz-main-mod-provider-provenance.tsv")
    check(len(prov_tsv) == 76, "provider provenance table has 76 rows")


# ---------------------------------------------------------------- parity ---
def verify_parity() -> None:
    fp = tsv(REPO / "kernel/phase4-gz-main-mod-function-parity.tsv")
    check(len(fp) == 42, "42 functions in the parity table")
    check(all(r["size_status"] == "EXACT" for r in fp), "42/42 size-identical")
    check(all(r["byte_status"] == "EXACT" for r in fp), "42/42 byte-identical")
    check(all(r["kcfi_status"] == "EXACT" for r in fp), "42/42 KCFI exact")

    op = tsv(REPO / "kernel/phase4-gz-main-mod-object-parity.tsv")
    check(len(op) == 45, "45 objects in the parity table")
    diff = [r for r in op if r["size_status"] != "EXACT"]
    check([r["object"] for r in diff] == ["__UNIQUE_ID_vermagic333"],
          "the only object difference is the vermagic string length")

    check(len(tsv(REPO / "kernel/phase4-gz-main-mod-imports.tsv")) == 76,
          "76 imports")
    check(len(tsv(REPO / "kernel/phase4-gz-main-mod-modversions.tsv")) == 77,
          "77 MODVERSION records")
    check(len(tsv(REPO / "kernel/phase4-gz-main-mod-relocations.tsv")) == 2817,
          "2817 relocations")
    check(len(tsv(REPO / "kernel/phase4-gz-main-mod-exports.tsv")) == 0,
          "0 exports")

    rebuilt = ART / "build/gz_main_mod.rebuilt.ko"
    if not check(rebuilt.is_file(), "rebuilt module present"):
        return
    check(sha256(rebuilt) == REBUILT_SHA, "rebuilt SHA256 unchanged")

    red = ART / "red/gz_main_mod.red.ko"
    check(red.is_file() and sha256(red) == REBUILT_SHA,
          "RED build is byte-identical to final (zero source delta)")

    # rebuilt inventory must still match stock
    stock = ART / "oracle/gz_main_mod.stock.ko"
    s_imports = sorted(re.findall(r"\S+$", tool("llvm-nm", "-u", str(stock)),
                                  re.M))
    r_imports = sorted(re.findall(r"\S+$", tool("llvm-nm", "-u", str(rebuilt)),
                                  re.M))
    check(s_imports == r_imports, "rebuilt import set identical to stock")
    check(len(r_imports) == 76, "rebuilt has exactly 76 undefined symbols")

    s_ver = sorted(tool("modprobe", "--dump-modversions",
                        str(stock)).splitlines())
    r_ver = sorted(tool("modprobe", "--dump-modversions",
                        str(rebuilt)).splitlines())
    check(s_ver == r_ver, "rebuilt MODVERSION CRCs identical to stock")

    unresolved = [s for s in r_imports
                  if not any(s == v.split()[-1] for v in r_ver)]
    check(not unresolved, "0 unresolved symbols")

    symvers = ART / "build/Module.symvers"
    check(symvers.is_file() and symvers.stat().st_size == 0,
          "rebuilt Module.symvers is empty (module exports nothing)")


# ----------------------------------------------------------------- build ---
def verify_build() -> None:
    log = ART / "build/logs/gz-main-mod-final-build.log"
    if not check(log.is_file(), "final build log present"):
        return
    text = log.read_text(errors="replace")
    check("BUILD_RC=0" in text, "BUILD_RC=0")
    check("Build completed successfully" in text, "bazel reported success")

    noisy = [ln for ln in text.splitlines()
             if re.search(r"warning", ln, re.I)
             and "SSL error" not in ln and "signing_key" not in ln]
    check(not noisy, "0 compiler warnings")
    check(not re.search(r"modpost", text, re.I), "0 modpost warnings")
    check(not re.search(r"no symbol version|undefined!", text, re.I),
          "no missing symbol versions")


# ------------------------------------------------------- forbidden things ---
def verify_no_forbidden_techniques() -> None:
    mk_raw = (PKG / "Makefile").read_text()
    bz_raw = (PKG / "BUILD.bazel").read_text()
    mk = code_only(mk_raw)
    bz = code_only(bz_raw)
    check(not re.search(r"KBUILD_MODPOST_WARN", mk),
          "no KBUILD_MODPOST_WARN directive in the module Makefile")
    check("KBUILD_MODPOST_WARN" not in bz,
          "no KBUILD_MODPOST_WARN directive in BUILD.bazel")
    check("objcopy" not in mk and "elfedit" not in mk,
          "no ELF patching in the build")
    check("__versions" not in mk, "no __versions editing")
    check("__kcrctab" not in mk, "no kcrctab editing")
    check("__crc_" not in mk, "no CRC symbol injection")

    # exactly one witness file, exactly one symbol in it
    sv = (PKG / "stock-provider.symvers").read_text().strip().splitlines()
    check(len(sv) == 1, "stock provider record contains exactly one symbol")
    check(sv[0].split("\t")[1] == "dmabuf_to_secure_handle",
          "the witness symbol is dmabuf_to_secure_handle")
    check(sv[0].split("\t")[2] == "mtk_sec_heap",
          "the witness names mtk_sec_heap as provider")

    # no witness may exist for any source-closed provider
    banned = ("KREE_", "tipc_", "trusty_", "ffa_driver_register",
              "ssmr_online", "ssmr_offline", "tz_system_dev",
              "get_smcnr_dev", "_map_user_pages")
    body = (PKG / "stock-provider.symvers").read_text()
    for token in banned:
        check(token not in body,

              f"no witness record for source-built provider symbol {token}")

    # the build must depend on the witness-free gz_tz_system acceptance target
    check("gz-tz-system-accept" in bz_raw,
          "depends on the witness-free gz_tz_system acceptance build")
    for dep in ("gz-trusty:gz_transport", "ffa-v10:ffa_v10",
                "tmem-ffa-gzaccept"):
        check(dep in bz_raw, f"depends on real source-built provider: {dep}")


# ------------------------------------------------------- userspace / ABI ---
def verify_userspace_abi() -> None:
    strings = {r["string"] for r in
               tsv(REPO / "kernel/phase4-gz-main-mod-strings.tsv")}
    check("gz_kree" in strings, "misc device name gz_kree present in stock")
    check("gz_ffa_dev" in strings, "chardev name gz_ffa_dev present in stock")

    funcs = {r["name"]: r for r in
             tsv(REPO / "kernel/phase4-gz-main-mod-functions.tsv")}
    for fn in ("gz_dev_open", "gz_dev_release", "gz_ioctl", "gz_compat_ioctl",
               "_gz_ioctl", "ff_a_gz_ioctl", "gz_main_probe", "gz_main_remove",
               "gz_test_show", "gz_test_store"):
        check(fn in funcs, f"file_operations/sysfs handler present: {fn}")

    # compat entry point must exist and share the ioctl KCFI signature
    check(funcs["gz_compat_ioctl"]["kcfi_type_id"] ==
          funcs["gz_ioctl"]["kcfi_type_id"] ==
          funcs["ff_a_gz_ioctl"]["kcfi_type_id"],
          "all three ioctl entry points share the ioctl KCFI signature")

    # the 9 gz_kree ioctl comparands must be present in stock _gz_ioctl
    dump = ART / "oracle/gz_main_mod.stock.text.objdump.txt"
    if check(dump.is_file(), "stock .text disassembly present"):
        start = int(funcs["_gz_ioctl"]["offset"], 16)
        size = int(funcs["_gz_ioctl"]["size"])
        body = []
        for line in dump.read_text(errors="replace").splitlines():
            m = re.match(r"^\s*([0-9a-f]+):", line)
            if m and start <= int(m.group(1), 16) < start + size:
                body.append(line)
        blob = "\n".join(body)
        for imm in ("0x5401", "0x5402", "0x5403", "0x5404", "0x5410",
                    "0x5411", "0x5415", "0x5416", "0x5417"):
            check(imm in blob, f"ioctl comparand {imm} in stock _gz_ioctl")
        for imm in ("0xc010", "0xc020", "0xc008", "0x4008", "0x4004"):
            check(imm in blob, f"ioctl dir/size half {imm} in stock _gz_ioctl")

    objs = {r["name"] for r in
            tsv(REPO / "kernel/phase4-gz-main-mod-objects.tsv")}
    for obj in ("fops", "gz_device", "gz_main_driver", "gz_main_of_match",
                "gz_ffa_driver", "gz_ffa_device_id", "dev_attr_gz_test"):
        check(obj in objs, f"ABI object present: {obj}")

    # session / memory model markers
    for fn in ("_register_session_info", "_reg_shmem_from_userspace",
               "tz_client_open_session", "tz_client_close_session",
               "tz_client_tee_service", "DMAFd2MemHandle"):
        check(fn in funcs, f"session/memory handler present: {fn}")


# ---------------------------------------------------------------- android ---
def verify_android_contract() -> None:
    part = REPO / "workspace/gq5012bf1/stock/partitions"
    rc = (part / "vendor/etc/init/hw/init.mt6878.rc").read_text(
        errors="replace")
    check("chmod 0660 /dev/gz_kree" in rc, "init: /dev/gz_kree mode 0660")
    check("chown system system /dev/gz_kree" in rc,
          "init: /dev/gz_kree owned system:system")
    check("chmod 0660 /dev/gz_ffa_dev" in rc, "init: /dev/gz_ffa_dev 0660")

    fc = (part / "vendor/etc/selinux/vendor_file_contexts").read_text(
        errors="replace")
    check("/dev/gz_kree(/.*)?" in fc and "u:object_r:gz_device:s0" in fc,
          "file_contexts labels /dev/gz_kree as gz_device")

    cil = (part / "vendor/etc/selinux/vendor_sepolicy.cil").read_text(
        errors="replace")
    check("(type gz_device)" in cil, "sepolicy declares type gz_device")
    check("(allow mtk_hal_camera gz_device" in cil,
          "sepolicy allows mtk_hal_camera -> gz_device")
    check("(allow vpud_native gz_device" in cil,
          "sepolicy allows vpud_native -> gz_device")


# ---------------------------------------------------------------- reports ---
def verify_reports() -> None:
    required = [
        "phase4-gz-main-mod-stock-oracle.txt",
        "phase4-gz-main-mod-functions.tsv",
        "phase4-gz-main-mod-objects.tsv",
        "phase4-gz-main-mod-imports.tsv",
        "phase4-gz-main-mod-modversions.tsv",
        "phase4-gz-main-mod-exports.tsv",
        "phase4-gz-main-mod-relocations.tsv",
        "phase4-gz-main-mod-strings.tsv",
        "phase4-gz-main-mod-provider-map.tsv",
        "phase4-gz-main-mod-provider-provenance.tsv",
        "phase4-gz-main-mod-source-candidates.md",
        "phase4-gz-main-mod-lineage.md",
        "phase4-gz-main-mod-source-hashes.tsv",
        "phase4-gz-main-mod-config-contract.md",
        "phase4-gz-main-mod-consumer-abi.md",
        "phase4-gz-main-mod-RED.md",
        "phase4-gz-main-mod-delta-ledger.tsv",
        "phase4-gz-main-mod-userspace-abi.md",
        "phase4-gz-main-mod-ioctl-contract.md",
        "phase4-gz-main-mod-session-model.md",
        "phase4-gz-main-mod-memory-contract.md",
        "phase4-gz-main-mod-gz-tz-system-acceptance.md",
        "phase4-gz-main-mod-transport-acceptance.md",
        "phase4-gz-main-mod-ffa-contract.md",
        "phase4-gz-main-mod-tmem-contract.md",
        "phase4-gz-main-mod-dt-contract.md",
        "phase4-gz-main-mod-type-contract.md",
        "phase4-gz-main-mod-object-contract.md",
        "phase4-gz-main-mod-android-contract.md",
        "phase4-gz-main-mod-function-parity.tsv",
        "phase4-gz-main-mod-object-parity.tsv",
        "phase4-gz-main-mod-reconstruction.md",
        "phase4-geniezone-main-stack-acceptance.md",
    ]
    for name in required:
        path = REPO / "kernel" / name
        check(path.is_file() and path.stat().st_size > 0,
              f"report present and non-empty: {name}")


def main() -> int:
    verify_oracle()
    verify_source()
    verify_config()
    verify_providers()
    verify_parity()
    verify_build()
    verify_no_forbidden_techniques()
    verify_userspace_abi()
    verify_android_contract()
    verify_reports()

    total = len(PASS) + len(FAIL)
    for label in FAIL:
        print(f"[FAIL] {label}")
    if FAIL:
        print(f"\n{len(PASS)}/{total} CHECKS PASSED - {len(FAIL)} FAILED")
        return 1
    for label in PASS:
        print(f"[PASS] {label}")
    print(f"\n{total}/{total} CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
