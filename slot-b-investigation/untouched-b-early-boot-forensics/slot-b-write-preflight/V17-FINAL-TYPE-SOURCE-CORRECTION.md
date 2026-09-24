# V17 final SELinux type source correction

Earlier source mapping identified the correct source file but reported:

```
V17_LAST_TYPE_SOURCE=device/lineage/sepolicy/common/vendor/property.te:61
```

Direct inspection establishes the actual declaration mechanism as:

```
device/lineage/sepolicy/common/vendor/property.te:11

vendor_public_prop(vendor_fm_radio_app_prop);
```

The generated vendor CIL still confirms that
`vendor_fm_radio_app_prop` is the final V17 type at ordinal 181.

Therefore the previous `:61` value must not be treated as the literal
source-file line number.

V21 is anchored after the actual macro invocation above.

PHONE_MODIFIED=0
