# SDK36 userspace pivot feasibility

Live testing proved that the coherent vanilla Slot-B product removes the two
previous Google PackageManager blockers.

The next hard blocker is not GApps:

`LineageSettingsProvider` from the older B userspace attempts to open shared
Lineage settings state created by the newer A userspace and aborts with:

`Can't downgrade database from version 24 to 21`

Slot A is Lineage 23.2 / SDK 36.

Slot B remains an SDK 35 generation userspace despite release-property parity
changes.

This investigation compares the actual A/B LineageSettings providers,
system/system_ext layouts, logical partition sizes, and local Lineage SDK
source before selecting the next candidate.

No userdata or partition contents are modified.

## Selected path

Neither `feasibility.txt` option was taken yet. A third, smaller option was
built and verified offline first: keep Slot B at SDK 35 but rebuild its
`LineageSettingsProvider` with `DATABASE_VERSION = 24`, which upstream proves to
be a constant-only change because the 21->24 upgrade path contains no schema or
table-level SQL. That candidate and its verification gates are recorded in
`../vanillaization/lineage-settings-db-mismatch/db24-candidate/`. The full
SDK 36 / Lineage 23.2 userspace pivot remains the fallback if the DB-24 provider
candidate still fails to boot.

The shared Slot-A schema-24 database is never downgraded or deleted.
