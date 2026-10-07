# SYSTEM-DLKM — closure (2026-10-07, static)

Workspace component `Reverse Engineer - PARTIAL/SYSTEM-DLKM` → **DONE**.

## Scope

The stock `system_dlkm` partition holds 60 GKI `.ko` files plus the
`modules.{load,dep,softdep,alias}` metadata. This closure covers their
source/artifact parity with the public GKI build android14-6.1 /
`ab12901745` (common @ `6b18f0b574ab`), and their layout and loading
relationship to `vendor_boot`/`vendor_dlkm`.

## Result

**All 60 modules are byte-identical to stock ELF bodies, including the
GNU build-id.** Only the appended module signature differs. Stock is signed
with Google's GKI release key; the rebuild uses Kleaf's ephemeral build key.
* Source: `scripts/system_dlkm_parity.py`, against the stamped build from
  `scripts/build_gki_stamped.sh`.
* Results: `parity/system-dlkm-parity-B1.txt` and `-B2.txt`.
* B1 and B2 come from a `bazel clean` in between, and give identical bodies
  (`parity/b1-b2.txt`).

Three things were needed for parity:
1. **Stamping.** Use `BUILD_NUMBER=12901745 --config=stamp`. This makes
   `vermagic` `6.1.115-android14-11-g6b18f0b574ab-ab12901745`, adds the
   `.modinfo` `intree=Y` + `scmversion=g6b18f0b574ab` fields, and stabilises
   the `__UNIQUE_ID` counters. Without it you get `…-maybe-dirty`.
2. **`-faddrsig`.** Stock modules carry `.llvm_addrsig`, but this host's
   prebuilt-clang invocation emitted none (Gentoo host). Adding `-faddrsig`
   to `KCFLAGS` restores it; this is the same flag the vendor-module
   reconstructions use.
3. **A clean release string.** The flag is injected through
   `build.config.common` with `git update-index --assume-unchanged`, so
   `setlocalversion` does not append `-dirty`.

Signature consequence: these modules cannot be re-signed as stock. A
LieppOS `system_dlkm` must either ship the stock signed `.ko` files (they are
the same code) or run with the GKI signature-enforcement policy of its own
boot image. The stock GKI boot image enforces `CONFIG_MODULE_SIG_PROTECT`
only for protected symbols. This is an integration choice.

## Layout (unchanged, see `notes/module-map.md`)

* `system_dlkm` holds only GKI-built protocol and USB-network extras
  (6LoWPAN/802.15.4, CAN, PPP/L2TP/PPTP, BT core + rfcomm/hidp, USB
  serial/net, `zram`/`zsmalloc`, `gzvm`, `kheaders`, `wwan`, `tipc`, `nfc`).
  There are no MTK modules.
* `modules.load` lists all 60. Vendor modules are loaded from
  `vendor_boot` / `vendor_dlkm` (MTK-MODULE-LOADER, DONE).
