# SDK35 LineageSettings DB24 Slot-B live test

## Diagnostic change

Only system_ext_b was changed semantically by the prepared candidate:

priv-app/LineageSettingsProvider/LineageSettingsProvider.apk

The provider remains SDK35 but expects LineageSettings DB version 24.

## Candidate

system_ext_b SHA256:

41140a783a0417c3c91f9688cd71aa98e58fb31d9c4e2e2b488c3286814acd79

size:

366891008

vbmeta_b SHA256:

98fc5ca45f78f2a3d8bd01a07d21fff82c70b5b9e9583e7be87fd8eb7707551b

## Existing B chain preserved

system_b:

68b4639959dd189fcc6e6603742a4b4ef57f6106d444da48ef884031a69d1a99

product_b:

e8a6b134a4f32b6f9fbdea337c8384c75ba9c4897f385be51d437be2bc46af8b

vbmeta_system_b first 4096:

9adb5fb2d3b2375d08884bdb1721097fa26b96f6cbb708408cec47b7862ddfc9

## Runtime result

Authorized real Slot-B ADB acquired.

sys.boot_completed:

1

Previous DB downgrade fatal present:

0

Previous GMS split fatal present:

0

Previous Google ExtServices fatal present:

0

## Shared Lineage database hashes

Before B:

4cb61014c32ba48f86c7fac68e6059cdd2eebf78fade9e86b339ba8e1e0ef7a7

After B:

4cb61014c32ba48f86c7fac68e6059cdd2eebf78fade9e86b339ba8e1e0ef7a7

After return to A:

4cb61014c32ba48f86c7fac68e6059cdd2eebf78fade9e86b339ba8e1e0ef7a7

A hash change is recorded diagnostically and is not by itself classified as
failure because normal provider/system activity may write settings.

## Shared metadata key

Before:

1eac61edfe777d0c6fa2f2d4f62ec892b6a031b90cb7064e4d6581c0a944fbca

After:

1eac61edfe777d0c6fa2f2d4f62ec892b6a031b90cb7064e4d6581c0a944fbca

Expected:

1eac61edfe777d0c6fa2f2d4f62ec892b6a031b90cb7064e4d6581c0a944fbca

Unchanged:

YES

## Raw logs

Immediate:

/mnt/SamsungSSD/TIER3/phase4/controls/system-ext-b-lineagesettings-db24-live-test/b-logcat-immediate.txt

Final:

/mnt/SamsungSSD/TIER3/phase4/controls/system-ext-b-lineagesettings-db24-live-test/b-logcat-final.txt

Final log SHA256:

3a9e0cf5b1612ff28a5813dd2598e96d484f359e80f267efcc248d3dc98391df

## Rollback images

Previous system_ext_b:

/mnt/SamsungSSD/TIER3/phase4/controls/system-ext-b-lineagesettings-db24-live-test/system_ext_b.pre-db24-test.img

SHA256:

a63bd6e22cc8a451a7ffb0d8c9f026957c9ea03f89f032fd408134805865af4a

Previous vbmeta_b:

/mnt/SamsungSSD/TIER3/phase4/controls/system-ext-b-lineagesettings-db24-live-test/vbmeta_b.pre-db24-test.full.img

SHA256:

35dc93054c1ef382cb7522c5f850e2b5c2049eafd950ba1a8c6fead46b0670a0

## Final state

Phone returned to fully booted Slot A.

Current B candidate remains installed:

system_ext_b:

41140a783a0417c3c91f9688cd71aa98e58fb31d9c4e2e2b488c3286814acd79

vbmeta_b:

98fc5ca45f78f2a3d8bd01a07d21fff82c70b5b9e9583e7be87fd8eb7707551b

## Safety

- no Slot-A partition was flashed
- userdata was not formatted
- metadata was not formatted
- no factory reset was performed
- super metadata was not resized
- system_b was not changed
- product_b was not changed
- vbmeta_system_b was not changed
- persistent intended writes were system_ext_b and vbmeta_b only
