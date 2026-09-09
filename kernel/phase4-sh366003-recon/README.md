# SH366003 reconstruction

Target: Linux 6.1.115-android14-11, `//common:kernel_aarch64`.

Default build is development-safe:

```text
SH366003_ALLOW_AFI_PROGRAMMING=0
```

The embedded stock AFI algorithm and byte-exact profile compile into the module, but all unseal/data-flash/manufacture-date entry points fail closed before any programming transaction. Ordinary read-only gauge behavior is unchanged.

An oracle-parity static build can be requested with `SH366003_ALLOW_AFI_PROGRAMMING=1`; never load that build on development hardware. This project performs static build/disassembly only.

The three YFT symbols are resolved through exact stock CRCs in `stock-yft-devinfo.symvers`. Do not substitute the incomplete reconstructed YFT provider, patch `__versions`, or edit the ELF.
