# Exact-GKI build: `spi_tiny_co5300_lcd`

## Workspace and target

```text
workspace: /home/armol/kernel-work/gki-12901745-workspace
target:    //lieppos/spi-tiny-co5300-lcd-recon:spi_tiny_co5300_lcd_recon
output:    /home/armol/kernel-work/gki-12901745-workspace/lieppos/spi-tiny-co5300-lcd-recon/spi_tiny_co5300_lcd.ko
```

Build command:

```sh
cd /home/armol/kernel-work/gki-12901745-workspace
tools/bazel build \
  //lieppos/spi-tiny-co5300-lcd-recon:spi_tiny_co5300_lcd_recon \
  --noshow_progress
```

The frozen successful log is
`workspace/phase4-spi-tiny-co5300-lcd/rebuild/build.log`. It contains no
compiler or modpost warning and ends in `Build completed successfully`.

## Artifact

```text
SHA256: 9149da0533d4d8327518d22762964c2e656f4aeb95fdd8a88280c109555dbfe2
name: spi_tiny_co5300_lcd
version: v0.01
depends: yft_devinfo,hynitron
exports: 0
undefined ELF symbols: 57
MODVERSION entries: 58 (including module_layout)
```

The stock and rebuild import sets and all CRC values are exactly equal. The
rebuilt module naturally carries exact CRCs for the 54 GKI/module-layout edges,
two rebuilt-Hynitron edges, and two stock-YFT edges.

The generated `-maybe-dirty` local-release provenance differs from the stock
commit-tag release text. The kernel ABI is exact: all 58 MODVERSION entries
match stock, and generated module layout metadata comes from the pinned build.
No binary patching is involved.
