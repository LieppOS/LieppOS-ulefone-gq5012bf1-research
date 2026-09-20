# Temporary vendor_b RW alias test

This test created, inspected, hashed, and removed a transient device-mapper
alias over exactly the existing inactive vendor_b extent:

`0 1594432 linear /dev/block/by-name/super 17098384`

No partition payload was written.

Expected size:

`816349184`

Expected rollback SHA256:

`9f3dfe3fe5ef025b667b8181bddfedaf6b08dace4b7cd6c4e05a4fde0d16aa98`

Raw output:

`vendor-b-rw-alias-test.txt`
