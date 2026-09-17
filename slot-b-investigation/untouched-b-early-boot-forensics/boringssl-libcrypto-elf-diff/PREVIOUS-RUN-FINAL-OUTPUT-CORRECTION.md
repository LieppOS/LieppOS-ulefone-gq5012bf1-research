# Previous Conscrypt isolation run — final-output correction

Commit `1f5295b` completed before the terminal exception.

The final terminal footer from that run was invalid because the extracted
Conscrypt paths lived under Python `TemporaryDirectory()` and the footer
re-hashed those paths only after the temporary directory had been deleted.

Consequently:

`SELFTEST_BINARY_IDENTICAL=0`

from that footer must not be treated as evidence.

Likewise, the subsequent `NoneType` concatenation exception was a reporting
bug rather than an investigation failure.

The summary generated while the extracted files still existed reports:

- self-test binary identical:
  `True`
- libcrypto identical:
  `False`
- B Conscrypt self-test SHA256:
  `1945ec6d1001495bffc11dae26adb3db8462fcfac3c146697f5cc21676c93cc4`
- B platform self-test SHA256:
  `1945ec6d1001495bffc11dae26adb3db8462fcfac3c146697f5cc21676c93cc4`

This correction does not alter any phone state.
