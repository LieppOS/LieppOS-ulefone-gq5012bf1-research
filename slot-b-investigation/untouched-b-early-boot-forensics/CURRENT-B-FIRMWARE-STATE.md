# Current Slot-B firmware state

## Result

Read-only live verification from healthy slot A proves the repaired TIER3
slot-B MediaTek firmware state is still intact.

Current A preflight:

- slot suffix: `_a`
- boot completed: `1`
- bootctl current slot: `0`
- snapshot merge state: `none`

`lk_b`:

- size: 16,777,216 bytes
- SHA256: `ee0303f531e204f639a9e2f4f058ffd1ae159b02804c402282a9def15d250461`
- result: exact match to the final TIER3 same-device working-A-derived candidate

Seventeen subordinate B firmware partitions were compared against the exact
TIER3 `writes.tsv` manifest:

- checked: 17
- pass: 17
- fail: 0
- error: 0

The verified partitions are:

`logo_b`, `gz_b`, `tee_b`, `sspm_b`, `pi_img_b`, `mcupm_b`, `scp_b`,
`ccu_b`, `spmfw_b`, `apusys_b`, `dpm_b`, `modem_b`, `gpueb_b`, `vcp_b`,
`connsys_bt_b`, `connsys_gnss_b`, and `connsys_wifi_b`.

Therefore 18/18 checked slot-B selector/firmware components remain exactly in
the repaired August TIER3 state.

## Consequence

The September untouched-B boot failure cannot be explained by regression or
loss of the repaired `lk_b` or subordinate MediaTek B firmware chain.

The next investigation boundary is the Android boot-image delta between:

1. the untouched current B baseline; and
2. the August post-firmware diagnostic configuration that reached MediaTek USB
   PID `0e8d:201c`, proving Linux and Android-init USB progress.

No new B boot, setter, flash, wipe, or partition modification is authorized by
this result.
