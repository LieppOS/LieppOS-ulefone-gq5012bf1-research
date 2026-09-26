# LineageSettings shared-database schema mismatch

The coherent vanilla Slot-B boot removed both previously identified Google
PackageManager blockers.

The next hard failure is:

`android.database.sqlite.SQLiteException:
Can't downgrade database from version 24 to 21`

raised by:

`org.lineageos.lineagesettings.LineageSettingsProvider`

during `system_server` provider installation.

This demonstrates that Slot B has progressed past the Google configuration
failures and now conflicts with newer Lineage settings state already present
on the shared userdata partition.

The existing database must not be downgraded or deleted while Slot A remains
the known-good daily boot.

`provenance.txt` records a read-only investigation of the database location,
schema version, A-side provider and B-side provider.

No partition or userdata content is modified by this investigation.
