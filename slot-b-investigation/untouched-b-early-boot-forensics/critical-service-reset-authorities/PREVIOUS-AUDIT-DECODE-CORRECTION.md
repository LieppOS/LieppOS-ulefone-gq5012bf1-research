# Critical-service audit continuation correction

The preceding critical-service audit did not alter phone state.

It failed during the repository-wide evidence-search stage because Python
`subprocess.run(..., text=True)` attempted strict UTF-8 decoding on output
containing non-UTF-8 bytes.

The failure occurred after:

- safety preflight;
- current-B service-definition inventory;
- Android init critical-crash source extraction;
- current-B service-start chronology;
- working-A control collection;
- Tier3 non-fallback search.

The Tier3 non-fallback search returned no critical-service evidence before the
decode exception occurred.

The run failed before its selective repository commit.

This continuation uses byte-mode subprocess output and explicitly decodes with
`errors="replace"`.

No previous evidence is discarded.
