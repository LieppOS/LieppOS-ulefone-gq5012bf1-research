# Coherent vanilla Slot-B live boot test

## Candidate

product_b:

/mnt/SamsungSSD/TIER3/phase4/controls/slot-b-vanilla-product-debug/product-b-vanilla-debug.img

SHA256:

e8a6b134a4f32b6f9fbdea337c8384c75ba9c4897f385be51d437be2bc46af8b

Size:

337686528

vbmeta_b:

/mnt/SamsungSSD/TIER3/phase4/controls/slot-b-vanilla-product-debug/vbmeta_b.vanilla-debug.img

SHA256:

39ab5e9e6eabc2fa33e9a8e0aec842fc650828f5f8cb505f9e2ea655fab7c917

## Existing debug system preserved

system_b:

68b4639959dd189fcc6e6603742a4b4ef57f6106d444da48ef884031a69d1a99

vbmeta_system_b first 4096:

9adb5fb2d3b2375d08884bdb1721097fa26b96f6cbb708408cec47b7862ddfc9

## Runtime

Authorized real Slot-B ADB acquired.

sys.boot_completed:

0

Previous GMS split-permission fatal present:

0

Previous Google ExtServices fatal present:

0

## Full raw logcat

Immediate:

/mnt/SamsungSSD/TIER3/phase4/controls/slot-b-vanilla-live-test/b-logcat-immediate.txt

Final:

/mnt/SamsungSSD/TIER3/phase4/controls/slot-b-vanilla-live-test/b-logcat-final.txt

Final SHA256:

b9fcf8940b2655ccba913654df47c942f843f7e2321ac86730d9e6259a8d618d

## Shared metadata key

Before:

1eac61edfe777d0c6fa2f2d4f62ec892b6a031b90cb7064e4d6581c0a944fbca

After:

1eac61edfe777d0c6fa2f2d4f62ec892b6a031b90cb7064e4d6581c0a944fbca

Expected:

1eac61edfe777d0c6fa2f2d4f62ec892b6a031b90cb7064e4d6581c0a944fbca

Unchanged:

YES

## Rollback evidence

Previous product image:

/mnt/SamsungSSD/TIER3/phase4/controls/slot-b-vanilla-live-test/product_b.pre-vanilla-test.img

SHA256:

a0a7eb7692dfc27e261d17eef366cd43beff351f5e67979ae35aa1d2e17d329d

Previous full vbmeta_b:

/mnt/SamsungSSD/TIER3/phase4/controls/slot-b-vanilla-live-test/vbmeta_b.pre-vanilla-test.full.img

SHA256:

076c5ce1ee8f9aa397ce577171ac5d282f047d6ca07c3f9ecdfb7e772b7b1e67

## Final state

Phone returned to fully booted Slot A.

Installed B product:

e8a6b134a4f32b6f9fbdea337c8384c75ba9c4897f385be51d437be2bc46af8b

Installed B vbmeta first 8192:

39ab5e9e6eabc2fa33e9a8e0aec842fc650828f5f8cb505f9e2ea655fab7c917

Installed B system:

68b4639959dd189fcc6e6603742a4b4ef57f6106d444da48ef884031a69d1a99

Installed B vbmeta_system first 4096:

9adb5fb2d3b2375d08884bdb1721097fa26b96f6cbb708408cec47b7862ddfc9

## Safety

- No Slot-A partition was flashed.
- userdata was not formatted.
- metadata was not formatted.
- no factory reset was performed.
- super metadata was not resized.
- system_b was not modified.
- system_ext_b was not modified.
- persistent intended writes were product_b and vbmeta_b only.
