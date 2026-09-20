# Corrected temporary vendor_b RW alias test

The first alias command used the dmctl target arguments in the wrong order and
failed before creating a mapper.

Correct dmctl target syntax is:

`linear 0 1594432 /dev/block/by-name/super 17098384`

This transient alias covers exactly the existing inactive vendor_b extent.

No partition payload write was performed.
