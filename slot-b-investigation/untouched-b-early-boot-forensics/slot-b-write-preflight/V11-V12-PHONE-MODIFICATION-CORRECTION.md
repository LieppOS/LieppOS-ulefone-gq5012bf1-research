# V11/V12 phone-modification accounting correction

Some historical runtime capture output used `PHONE_MODIFIED=0` to describe
the read-only post-return capture step.

For clarity:

- V11 runtime experiment: PHONE_MODIFIED=1
  - marker seeding modified /metadata
  - Slot B was activated

- V11 post-return capture itself: CAPTURE_PHONE_MODIFIED=0

- V12 vendor/system preparation and pair write steps that wrote Slot B:
  PHONE_MODIFIED=1

- V12 runtime experiment: PHONE_MODIFIED=1
  - marker seeding modified /metadata
  - Slot B was activated

- V12 post-return capture itself: CAPTURE_PHONE_MODIFIED=0

Raw historical evidence is preserved unchanged. This document only corrects
the experiment-level accounting terminology.
