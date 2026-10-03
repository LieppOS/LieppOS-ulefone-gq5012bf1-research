# Exact-source provenance (connectivity)

The source is public MediaTek code, so this directory records **which exact tree** reproduces
stock, using git tree object ids, instead of copying ~75 MB of source. Only the deltas against
the public trees are stored here (`*.patch`).

## vendor/mediatek/kernel_modules/connectivity

Upstream: `https://github.com/NothingOSS/android_kernel_modules_nothing_mt6878`, fetched blobless
into `/home/armol/kernel-work/public-mtk/nkm.git` (87 commits, 7 branches).
Research build tree: `$G/vendor/mediatek/kernel_modules/connectivity` (git, HEAD `7de5e1c`). It
**must** sit at `../vendor/mediatek/kernel_modules/connectivity` relative to `common/`, because
`__FILE__` strings are part of the parity.

| dir | research tree id | upstream 2115d27 tree id | delta |
|---|---|---|---|
| `conninfra` | `0d4be133360857c7c39431080d398a4f3335f889` | same | none |
| `connfem` | `8a2836446ac9d96479e0bbd373e1ef628636a224` | same | none |
| `fmradio` | `503f61f0953e0a6f26c520176d1697c5987f2d8c` | same | none |
| `gps` | `ce5f4c68db0845358285ff0714210efc42e1726b` | same | none |
| `bt/mt66xx` | `82349046f0d0efb589a9c1326fd81b1119a8a43c` | same | none |
| `wlan/adaptor` | `9e78ca8e77855d14f6d66688a6d7005d60b6f17d` | same | none |
| `wlan/core/gen4m` | `08cbfd2b3d94037ebfa672344d82d923d05d26c8` | `5a9b91b828d8e957da99e8033e8edfa47ae9fa1c` | `wlan-gen4m-6878-alps-v11.24-backports.patch` (13 hunks from c3d070e) |

Research tree commits: `47ff776` (5f75a3b snapshot baseline) → `25a040e` (conninfra @2115d27)
→ `68cde6d` (full tree @2115d27) → `7de5e1c` (wlan backports).

## kernel_device_modules-6.1 (shared research KDM tree)

Upstream: `https://github.com/NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878`
(`/home/armol/kernel-work/public-mtk/nt6878.git`).

| dir | research tree id | upstream id | research commit |
|---|---|---|---|
| `drivers/misc/mediatek/connectivity` | `f3ebcea5…` | 6df320423600 same | `e4b5575` |
| `drivers/misc/mediatek/conn_scp` | `3b0bd05c…` | 6df320423600 same | `e4b5575` |
| `drivers/misc/mediatek/clkbuf` | `4b691346…` | 6df320423600 same | `e4b5575` |
| `drivers/thermal/mediatek/wifi_cooling.c` | - | 6df320423600 | `e4b5575` |
| `drivers/misc/mediatek/power_throttling` | `d765f3e4…` | 6df320423600 same | `05f8044` |
| `drivers/misc/mediatek/uarthub` | `7390cbaa…` | 957dac1 = 6df320423600 | baseline `0579490` |
| `drivers/misc/mediatek/mddp`, `drivers/mfd/mt6685-core.c` | - | 957dac1 | baseline `0579490` |
| `sound/soc/mediatek/common/mtk-btcvsd.c` | - | e38092245fb4 | audio `27f8383` |

## GKI common

`cfg80211`, `mac80211`, `bluetooth`: `$G/common` (6.1.115 android14-11), built with
`M=net/<dir>`. Then `scripts/intree_relink.sh` re-emits the `intree`/`scmversion=g945dff7bc1bf`
modinfo that the vendor's in-tree build produced. Code and data were never touched.
