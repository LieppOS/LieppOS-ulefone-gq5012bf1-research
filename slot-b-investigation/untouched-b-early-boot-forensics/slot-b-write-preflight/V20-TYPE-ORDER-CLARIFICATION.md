# V20 type-order clarification

V20 decisively reproduced the pre-early-init failure, but its generated
vendor policy changed in two separable ways relative to the historical V17 policy artifact:

- vendor type count increased from 181 to 182;
- the V20 dummy type was inserted at ordinal 155;
- 27 existing types moved by +1;
- the shifted range begins with proc_deny_new_usb at 155 -> 156;
- the shifted range ends with vendor_fm_radio_app_prop at 181 -> 182.

Therefore V20 proves that adding the otherwise-unused type at that position
is sufficient to reproduce the failure, but it does not distinguish between:

1. failure caused by increasing/changing the total compiled vendor policy;
2. failure caused by changing the numeric/ordinal IDs of existing types.

The next useful control is V21: add one unused vendor type only after all
181 V17 types, producing dummy ordinal 182 while preserving every existing
V17 type ordinal exactly.

V21 must be audited before flashing. Required generated-policy properties:

    V21_TYPE_COUNT=182
    DUMMY_TYPE_ORDINAL=182
    SHIFTED_COMMON_TYPE_COUNT=0
    ONLY_V21_TYPE=one dummy type

The exact policy-directory ordering should be established before constructing
V21 rather than assuming that lexical .te filenames determine final CIL order.

PHONE_MODIFIED=0
