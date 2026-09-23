# V20 installation provenance correction

The first V20 install retry succeeded.

Successful install research commit:

    be6c091

It wrote and verified:

VENDOR_B_SHA256=ac3a557e1b0e92ea8b9138a7de1429fd3eb892112e4499b4e9f6b3302712731d
VBMETA_VENDOR_B_FIRST4096_SHA256=93bfd8880742d46385b0cc5ef3d4005bc665852ae827e80256410fad6a60d9c7

and ended with:

    WRITE_DONE=1
    V20_INSTALL_OK=1
    CURRENT=0
    ACTIVE=0
    PHONE_MODIFIED=1

The install block was then accidentally executed a second time.

That second execution saw V20 already installed, while its pre-write gate
still expected V19. It therefore stopped with:

    PREWRITE_STATE_OK=0
    WRITE_DONE=0
    V20_INSTALL_OK=0
    PHONE_MODIFIED=0

Commit e835349 records that second no-op execution and must not be
interpreted as failure of the actual V20 installation.

Fresh live verification after both executions:

VENDOR_B_SHA256=ac3a557e1b0e92ea8b9138a7de1429fd3eb892112e4499b4e9f6b3302712731d
VBMETA_VENDOR_B_FIRST4096_SHA256=93bfd8880742d46385b0cc5ef3d4005bc665852ae827e80256410fad6a60d9c7
SYSTEM_B_SHA256=1a1e7468a62c5129c579df1d050565badaa81c183b0d4df65b54910df5ef6c5b
VBMETA_SYSTEM_B_FIRST4096_SHA256=d7ec0fec34494a10eef5ba758e83fbc1f5034fbe051201c2756bdfe3cc96aa74
ROOT_VBMETA_B_SHA256=e14e11e184950d487b31def17a349f4f161e34988825bf35d85fc9bd6c3bde93

V20_CURRENT_OK=1

PHONE_MODIFIED_BY_THIS_CAPTURE=0
