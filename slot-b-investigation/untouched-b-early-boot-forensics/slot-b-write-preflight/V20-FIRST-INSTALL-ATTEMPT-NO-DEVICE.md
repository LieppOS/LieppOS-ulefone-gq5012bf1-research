# V20 first install attempt: no device

The first V20 install attempt did not reach any phone write.

Observed:

ADB was unavailable at the initial Slot-A safety gate.

A_SAFETY_OK=0
PREWRITE_STATE_OK=0
WRITE_DONE=0
V20_INSTALL_OK=0
PHONE_MODIFIED=0

Therefore commit 6cc0dbd records a failed/no-op installation attempt and
must not be interpreted as evidence that V20 was installed.

After recovery:

A_SAFETY_OK=1
V19_STILL_INSTALLED=1

LIVE_VENDOR_B_SHA256=c7cdc8fde5415f81f1813c24a58cf45e31db3660f9726eb7506d0636d19cf298
LIVE_VBMETA_VENDOR_B_FIRST4096_SHA256=a4cc9fe8aa173ec1d796d6268ca1bd1af7473c3956956108cc9c536a885ffa61
LIVE_SYSTEM_B_SHA256=1a1e7468a62c5129c579df1d050565badaa81c183b0d4df65b54910df5ef6c5b
LIVE_VBMETA_SYSTEM_B_FIRST4096_SHA256=d7ec0fec34494a10eef5ba758e83fbc1f5034fbe051201c2756bdfe3cc96aa74
LIVE_ROOT_VBMETA_B_SHA256=e14e11e184950d487b31def17a349f4f161e34988825bf35d85fc9bd6c3bde93

PHONE_MODIFIED=0
