# V19 pre-existing Slot-B state correction

The attempted V19 install was stopped by its pre-write gate.

The script expected Slot B to still contain V18, but fresh pre-write reads
already showed the exact V19 vendor and vbmeta_vendor hashes:

LIVE_VENDOR_B_SHA256=c7cdc8fde5415f81f1813c24a58cf45e31db3660f9726eb7506d0636d19cf298
LIVE_VBMETA_VENDOR_B_FIRST4096_SHA256=a4cc9fe8aa173ec1d796d6268ca1bd1af7473c3956956108cc9c536a885ffa61

Frozen companion state:

LIVE_SYSTEM_B_SHA256=1a1e7468a62c5129c579df1d050565badaa81c183b0d4df65b54910df5ef6c5b
LIVE_VBMETA_SYSTEM_B_FIRST4096_SHA256=d7ec0fec34494a10eef5ba758e83fbc1f5034fbe051201c2756bdfe3cc96aa74
LIVE_ROOT_VBMETA_B_SHA256=e14e11e184950d487b31def17a349f4f161e34988825bf35d85fc9bd6c3bde93

V19_ALREADY_INSTALLED=1

The failed install attempt had:

    PREWRITE_STATE_OK=0
    WRITE_DONE=0

Therefore that attempt itself performed no Slot-B write.

The POST_* values printed by that run are not considered evidence because
their variables were not initialized before the conditional post-write
branch. In an interactive shell they could contain stale values from an
earlier command.

PHONE_MODIFIED_BY_FAILED_INSTALL_ATTEMPT=0
