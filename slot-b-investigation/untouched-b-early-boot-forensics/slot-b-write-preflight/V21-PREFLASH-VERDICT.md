# V21 pre-flash verdict

## Question

Does adding one otherwise-unused vendor SELinux type preserve every existing
V17 type ordinal when the new type is appended after the actual final V17
type source declaration?

## V17

- type count: 181
- known-good control
- final type: `vendor_fm_radio_app_prop`
- ordinal: 181
- corrected source:
  `device/lineage/sepolicy/common/vendor/property.te:11`
- source mechanism:
  `vendor_public_prop(vendor_fm_radio_app_prop);`

## V20

- type count: 182
- dummy ordinal: 155
- 27 existing types shifted
- reproduced the pre-early-init failure

## V21

```
ENVSETUP_RC=0
LUNCH_CHOICE=lineage_armol-bp1a-user
LUNCH_RC=0
BUILD_TARGET=vendor_sepolicy.cil
BUILD_RC=0

V17_TYPE_COUNT=181
V21_TYPE_COUNT=182

ONLY_V17_TYPE_COUNT=0
ONLY_V21_TYPE_COUNT=1
ONLY_V21_TYPE=lieppos_v21_dummy_type

V20_DUMMY_PRESENT=0
DUMMY_TYPE_ORDINAL=182

SHIFTED_COMMON_TYPE_COUNT=0
ORDINALS_1_TO_181_IDENTICAL=1

V21_CIL_REFERENCE_COUNT=2
V21_UNEXPECTED_REFERENCE_COUNT=0

AUDIT_RC=0
SEMANTIC_AUDIT_RC=0

V21_FLASH_GATE=PASS
SOURCE_LEFT_AS_V21=1
PHONE_MODIFIED=0
```

## Interpretation after eventual Slot-B test

If V21 boots while V20 fails, the isolated evidence points toward the V20
renumbering of existing vendor SELinux types being required for that failure.

If V21 reproduces the same pre-early-init failure while V17 ordinals 1..181
remain identical, existing-type renumbering is not required. Investigation
should move toward type-table growth, policy serialization/layout, or another
correlated structural policy property.

If V21 behaves differently from both controls, preserve the state and compare
the generated and binary policy artifacts before drawing a conclusion.
