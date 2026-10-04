# Reconstructed Hynitron V2.1 source

This is the GQ5012BF1 stock `hynitron.ko` source reconstruction. It combines
the nearest public Hynitron multi-file lineage with binary-proven Ulefone/YFT
deltas. All 65 functions compile byte-identically to stock under the recorded
CI-12901745 toolchain. Forty-one `#line` anchors preserve the stock
`HYN_FUNC_EXIT()` `__LINE__` immediates; do not remove them as cosmetic.

The proprietary CST controller images are not committed. Kbuild cannot accept
an `M=` path containing spaces, so copy this directory to a no-space scratch
path before reproducing:

```sh
cp -a source /tmp/hynitron-v21
cd /tmp/hynitron-v21
./extract-firmware.py /path/to/stock/hynitron.ko
export GKI_ROOT=/path/to/gki-12901745-workspace
export KOUT="$GKI_ROOT/lieppos/nfc/kout"   # configured CONFIG_LTO_NONE tree
./build.sh
```

`KCFLAGS=-faddrsig` must be global because the stock `.llvm_addrsig` includes
both driver objects and generated `hynitron.mod.o`. Without it all executable
behavior remains equal, but the section does not match. The only remaining
stock-file difference after stripping DWARF is `.note.gnu.build-id`, which
hashes original, unavailable build-path/DWARF provenance.

See `../build-config.md`, `../phase4-hynitron-v21-RED.md`, and `../parity/`.
