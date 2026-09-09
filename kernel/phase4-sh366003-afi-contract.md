# SH366003 AFI / firmware update contract

## Nature of the image

Stock names the operation “AFI firmware update,” but the embedded 2,142-byte object is a scripted data-flash/profile program, not host executable firmware. It programs monotonic gauge data-flash addresses 0x4000 through 0x47b8 and supplies precomputed checksum/length commits. No external file is loaded.

## Trigger and version gate

1. Probe reads MAC 0x0046 (current AFI) and 0x004d (profile/date), with up to five attempts while both are zero.
2. Automatic update is required when 0x004d differs from **0x5a93** or FCC is <= **3,500 mAh**. Both-zero read failure records `-1` and suppresses an automatic attempt.
3. Manual class `force_upgrade` supplies a second trigger.
4. Update work is queued once at **3,000 jiffies = 12 seconds** after probe.
5. It refuses to program when `primary_chg` is online (adapter state 2), SOC is below **11%**, boot mode is 8/9, or no automatic/manual trigger is active.
6. Before entering the engine it snapshots SOC/voltage/current/temperature into the fallback quartet and selects those caches so readers never observe an in-progress invalid value.

## Unlock and access state

`fg_gauge_unseal` writes, in order, four 16-bit words to SBS command 0x00:

`0x5678`, `0x1234`, `0xcdef`, `0x90ab`

with 3 ms after each. It reads MAC 0x0054 and requires bits 0x0300 to be clear. `file_decode_process` calls this routine twice before programming. This is the full-access sequence recovered from stock.

No separate ROM/bootloader address, erase opcode, or firmware-download-mode transition appears. There is no explicit erase phase in the stream; unsupported claims of one are omitted.

## Exact interpreter

The full stream has 209 records and no terminator record; end offset is 0x85e.

| Type | Count | Semantics |
|---:|---:|---|
| 1 | 0 | legacy raw read supported by interpreter; record size 4 |
| 2 | 104 | raw write to 7-bit address `(addr8 >> 1)`; wire buffer is register byte plus `len` payload bytes |
| 3 | 1 | raw register write + read + exact byte compare |
| 4 | 104 | big-endian 16-bit millisecond sleep |

Write distribution:

- 51 data-flash writes through register 0x3e, addresses 0x4000..0x47b8, strictly increasing, payloads 1..32 bytes;
- 51 precomputed checksum/length commits through register 0x60;
- control write `45 00` through register 0x00;
- final MAC selector `46 00` through register 0x3e.

Wait distribution: 51×2 ms, 51×5 ms, 2×1,500 ms; encoded total 3,357 ms.

Every raw transfer is serialized by the global I2C mutex. Transfer failures get one retry after 50 ms. Compare failure is fatal. The driver computes no checksum or CRC: all 0x60 values are embedded and must remain byte-identical.

## Verification and restart

The final records are:

1. write control bytes `45 00` to register 0x00;
2. wait 1,500 ms;
3. write MAC selector `46 00` to register 0x3e;
4. wait 1,500 ms;
5. read four bytes starting at 0x3e and require `46 00 d3 8c`.

This verifies target AFI value **0x8cd3**. The semantic name of control subcommand 0x0045 is not published; stock uses it as the profile activation/restart step.

After a successful interpreter run, update work waits 1,000 ms, retries ordinary telemetry, inspects MAC 0x00c1 run-state flags, and conditionally sends:

- MAC 0x0041 for reset/recovery when stock's voltage/current consistency test fails;
- MAC 0x0021 when bit 14 is absent;
- MAC 0x0067 when bit 15 is absent.

It reads post-update MAC block 0x00c5, clears the fallback selector, clears manual trigger to -1, and logs completion. Failures also restore ordinary-cache selection and preserve a documented error result; no alternate rollback image exists.

## Seal behavior

`fg_gauge_seal` writes MAC 0x0030 and checks operation status. It exists and is called by parser error/exit paths in stock. The reconstruction keeps this exact routine inside the guarded programming engine.

## Completeness and safety

The trigger, source, unlock, record format, address progression, packet sizes, embedded checksums, waits, retry count, final compare, activation command and post-update recovery are statically accounted for. Names of undocumented 0x0045/0x0067 silicon commands remain semantic labels only; their exact values/order are known.

All programming code is `DO_NOT_RUNTIME_TEST`. Development-safe builds set `SH366003_ALLOW_AFI_PROGRAMMING=0`; oracle-parity builds require an explicit opt-in. No live update, register write, reset, bind/unbind, module load, flash, reboot or slot switch was performed.
