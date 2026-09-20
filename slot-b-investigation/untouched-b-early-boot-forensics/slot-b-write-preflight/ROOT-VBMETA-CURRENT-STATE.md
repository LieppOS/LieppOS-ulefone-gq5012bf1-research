# Current Slot-B root vbmeta audit

Read-only audit. No flash, reboot, or slot change occurred.

## Expected staged root

Size:

`8192`

Full SHA256:

`bb2c7cb52dd15ee636cdb27b60f3fa5ed8fd6f774fe4acfc0a77301cbb4b17fb`

First-4096 SHA256:

`768e992decaf8ea13235f6ef9e5c675e8263f061b16326b3568d65c5c5ba4e4d`

## Current on-device vbmeta_b

Exactly `8192` bytes were read from the start of vbmeta_b.

Full SHA256:

`bb2c7cb52dd15ee636cdb27b60f3fa5ed8fd6f774fe4acfc0a77301cbb4b17fb`

First-4096 SHA256:

`768e992decaf8ea13235f6ef9e5c675e8263f061b16326b3568d65c5c5ba4e4d`

`ROOT_BYTE_IDENTICAL=1`

`ROOT_AVB_INFO_IDENTICAL=1`

## vbmeta_vendor chain trust

Expected chain key:

`UNKNOWN`

Live chain key:

`UNKNOWN`

`VENDOR_CHAIN_KEY_IDENTICAL=0`

## Historical artifact search

`LIVE_ROOT_KNOWN_ARTIFACT=1`

See:
- live-vbmeta-b-hash-research-hits.txt
- live-vbmeta-b-tier3-image-matches.txt

## Snapshot state

`LPDUMP_UPDATE_STATE=none`

`LPDUMP_CURRENT_SLOT=_a`

## Classification

`ROOT_STATE=EXACT_EXPECTED_ROOT`

`SNAPSHOT_GATE=1`
