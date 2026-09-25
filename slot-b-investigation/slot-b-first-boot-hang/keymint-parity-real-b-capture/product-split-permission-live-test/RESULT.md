# Slot-B product split-permission controlled test

## Diagnostic delta

Only the following product path was removed:

etc/permissions/split-permissions-google.xml

## Candidate product

SHA256:

a0a7eb7692dfc27e261d17eef366cd43beff351f5e67979ae35aa1d2e17d329d

## Candidate root vbmeta

SHA256 first/complete 8192-byte AVB image:

41afac0837a1d4d6d012fe745160a2cadf8463f55e3f3ff737b7f97f99e10844

## Runtime result

Authorized real Slot-B ADB acquired.

sys.boot_completed:

0

Previous split-permission fatal still present:

0

## Shared metadata key

Before:

1eac61edfe777d0c6fa2f2d4f62ec892b6a031b90cb7064e4d6581c0a944fbca

After:

1eac61edfe777d0c6fa2f2d4f62ec892b6a031b90cb7064e4d6581c0a944fbca

Expected:

1eac61edfe777d0c6fa2f2d4f62ec892b6a031b90cb7064e4d6581c0a944fbca

Unchanged:

YES

## Final state

Phone returned to fully booted Slot A.

Slot-B diagnostic product pair remains installed:

product_b=a0a7eb7692dfc27e261d17eef366cd43beff351f5e67979ae35aa1d2e17d329d

vbmeta_b-first8192=41afac0837a1d4d6d012fe745160a2cadf8463f55e3f3ff737b7f97f99e10844

No factory reset was performed.

userdata and metadata were not formatted.

super metadata was not resized.
