# Follow-up TODO

- [ ] Back up runtime `/mnt/vendor/nvcfg/infiray` if present and read-only module files before ROM modification.
- [ ] With stock app only, capture USB descriptors and one unmodified frame; do not issue undocumented controls.
- [ ] Confirm installed detector geometry/model against descriptor, frame length and module label.
- [ ] Map safe UI actions to usbmon captures one at a time.
- [ ] Decompile named radiometry exports with Ghidra/rizin to recover fixed-point scales/constants.
- [ ] Validate stock versus LieppOS temperatures against controlled references across gain/FFC transitions.
- [ ] Keep firmware, flash, calibration writes and ROM-entry disabled absent explicit authorization.
