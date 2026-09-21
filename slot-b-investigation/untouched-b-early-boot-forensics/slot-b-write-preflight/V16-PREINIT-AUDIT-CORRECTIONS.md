# V16 pre-init audit corrections

## Precompiled-policy handshake

The V16 vendor hash sidecars matched all extracted counterpart files.

The later summary printed `MATCH=0` because it emitted the raw exit status
from `cmp -s`. For `cmp`, exit status 0 means the files are identical.

Therefore:

- plat handshake: match
- system_ext handshake: match
- product handshake: match

V15 and V16 also contain identical three handshake hash values.

## Stale logical system dump

`slot-b-investigation/current-b-logical-dumps/system_b.img` hashes to:

    4a0bb9f615e1d2de9c05a2ebb770beda2c9b4e1dc9466dfd6ed6c3a6dd94a8d5

This is not the live frozen V12 Slot-B system image.

The live Slot-B mapping was verified immediately after the V16 experiment as:

    1a1e7468a62c5129c579df1d050565badaa81c183b0d4df65b54910df5ef6c5b

Therefore the old logical dump must not be used as authoritative V12 image
evidence.

The V16 precompiled-policy handshake mismatch theory is not supported by
the current evidence.

PHONE_MODIFIED=0
