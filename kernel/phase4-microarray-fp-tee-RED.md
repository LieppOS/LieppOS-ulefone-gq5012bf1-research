# MicroArray fingerprint TEE mandatory RED

## RED classification

**EMPTY-SOURCE RED**.

No plausible donor source survived the exact-identity gate. Therefore there is
no unchanged donor body that can honestly be built and compared. The RED input
set is empty by design, not a skipped build.

The structural references fail before behavioral edits on compatible, platform,
device-tree ownership, character-device ABI, ioctl set, provider graph, SPI
security architecture, TrustKernel boundary, PM, probe, and teardown. Build or
include changes cannot turn those sources into this stock module.

## Baseline

The only authoritative RED baseline is the frozen stock ELF:

- SHA256 `8e1449cea5d07ef663d368ce5eea27e8c879a9cd70d39f8fc2b5b25445c2cf33`
- 27 defined functions
- 66 imported MODVERSION entries excluding `module_layout` (59 GKI + 7
  intermodule), 0 exports
- compatible `mediatek,madev_finger`
- `/dev/madev0`
- hybrid direct-Linux SPI data transfers plus five bounded
  `tee_spi_transfer()` calls during probe-time chip identification

The reconstruction is consequently clean-room and evidence-driven.
