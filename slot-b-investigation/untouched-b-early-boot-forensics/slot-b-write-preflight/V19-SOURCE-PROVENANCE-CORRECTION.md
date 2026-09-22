# V19 source provenance correction

The original V19 staging command explicitly supplied the deleted path:

    sepolicy/vendor/property_contexts

to git add, which produced a pathspec error.

The V19 build itself remained valid and passed its generated-artifact gates.

Source provenance was subsequently normalized with:

    git add -A -- BoardConfig.mk sepolicy/vendor

Final source gates:

BOARD_POLICY_INCLUDE_COUNT=1
MTK_PROPERTY_TYPE_DECL_COUNT=1
PROPERTY_CONTEXT_SOURCE_PRESENT=0
INSMOD_TYPE_SOURCE_HITS=0
V19_SOURCE_PROVENANCE_OK=1

DEVICE_HEAD=5adf68c

PHONE_MODIFIED=0
