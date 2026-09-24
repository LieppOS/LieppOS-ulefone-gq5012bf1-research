# V17 boot-status correction

V17 was previously described in research notes as a known-good boot baseline.

That is incorrect.

The device owner confirms that V17 never successfully booted.

Therefore:

- V17 must NOT be treated as a known-good runtime baseline.
- V17 is only a historical SELinux/vendor artifact baseline.
- Reproducing V17 CIL and precompiled_sepolicy hashes proves artifact reproducibility,
  not bootability.
- Any prior inference based on "V17 boots while V20/V21 fail" is invalid.
- V20 and V21 are both observed to hang on the boot logo without reaching ADB.
- The current investigation must determine what configuration actually last booted,
  rather than assuming V17 was that configuration.

PHONE_MODIFIED=0
