# Root vbmeta_b hash scopes

Two previously recorded SHA256 values refer to different byte ranges:

- full 8 MiB vbmeta_b partition: e14e11e184950d487b31def17a349f4f161e34988825bf35d85fc9bd6c3bde93
- first 8192 bytes only: bb2c7cb52dd15ee636cdb27b60f3fa5ed8fd6f774fe4acfc0a77301cbb4b17fb

They must not be compared as though they hash the same object.

V9 leaves root vbmeta_b unchanged and will update only system_b plus
vbmeta_system_b.

PHONE_MODIFIED=0
