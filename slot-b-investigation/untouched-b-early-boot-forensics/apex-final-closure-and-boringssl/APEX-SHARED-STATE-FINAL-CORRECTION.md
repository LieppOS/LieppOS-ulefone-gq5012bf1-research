# Slot-B shared APEX state — final correction

## Result

`SHARED_APEX_UPDATE_STATE_CLOSED`

The preceding audit correctly established:

- `/data/apex/active` contains zero active APEX/CAPEX files;
- `/data/apex/sessions` is absent;
- `/data/apex/ota_reserved` is empty;
- no active data APEX key comparison is therefore required.

The previous value:

`SESSION_OR_METADATA_ENTRY_COUNT=4`

was not a count of four staged APEX sessions.

It counted ordinary paths below `/metadata/apex`, including the framework
directories:

- `config`
- `images`
- `images/active`
- `sessions`

Directory existence alone is not staged-session evidence.

The corrected exact child counts are:

- active data APEX packages: `0`
- entries under `/data/apex/sessions`: `0`
- entries under `/metadata/apex/sessions`: `0`
- children under `/metadata/apex/images/active`: `0`

The populated `/data/apex/decompressed` directory is not treated as an
active data-APEX replacement set.

Earlier source analysis established that compressed-APEX decompression caches
are validated against package/version/key/root-digest identity before reuse;
a stale Slot-A decompressed copy cannot silently substitute for an
incompatible Slot-B original APEX.

Therefore, if all four corrected active/session counts are zero, shared APEX
update/session state is closed as an explanation for the historical Slot-B
failure.

No device state was modified.
