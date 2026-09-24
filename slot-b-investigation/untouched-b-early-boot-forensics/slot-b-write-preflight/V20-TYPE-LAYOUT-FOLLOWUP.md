# V20 type-layout follow-up

V20 decisively reproduced the pre-early-init failure.

The V20 control added only one unused bare vendor SELinux type relative
to the historical V17 vendor policy artifact.

The next question is whether the failure comes from:

1. merely increasing the vendor policy type count, or
2. shifting the ordinal / binary type IDs of existing policy types.

This audit compares the order of every `(type NAME)` declaration in the
V17 and V20 generated vendor CIL.

If many existing types after the dummy move by +1, the next control should
place an unused dummy type at the absolute tail of the vendor policy so
existing type order remains unchanged.

If existing common types do not shift, the investigation should instead
focus directly on total type-count / precompiled binary policy compatibility
and first-stage SELinux loading.

PHONE_MODIFIED=0
