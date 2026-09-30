# Fastbootd logical-partition open failure isolation

Late-started TCP fastbootd has proven working BootControl:

- is-userspace=yes
- current-slot=a
- slot-count=2

It also reads super metadata sufficiently to identify system_b,
system_ext_b and product_b as logical partitions.

However partition-size on those logical partitions fails with:

    Could not open partition

AOSP fastbootd resolves partition-size by creating a writable dm-linear
logical-partition mapping and then opening that mapped block device.

This audit checks:

- whether the logical dm names already exist before fastbootd
- active and inactive slot mapper state
- mapper read-only status and tables
- physical super accessibility
- exact fastbootd/libdm error messages during OpenLogicalPartition

No mapper is deleted, created manually, changed, suspended, resumed, or
made writable by this audit. No partition write occurs.
