# GQ5012BF1 `spi-mt65xx` source candidates

## Search keys

`spi-mt65xx`, `spi_mt65xx`, `mt_spi_enable_master_clk`,
`mt_spi_disable_master_clk`, `mtk_spi_set_autosuspend_delay`, `mtk_spi`,
`mt65xx_spi`, `mtk_spi_probe`, `mediatek,spi`, the stock author/description,
all stock OF aliases, and vendor-only strings including `tee-only`,
`mediatek,autosuspend-delay`, `spi_log`, and `enhance_packet_len`.

Local searches covered the pinned Nothing MT6878 `device_modules`, `kernel`,
and `kernel_modules` repositories, exact Android Common/GKI, and the existing
project indices built from MediaTek/MiCode/vendor-reference searches. A web
exact-identifier search was attempted; the available anonymous search backend
returned only generic upstream/common copies and no candidate stronger than the
pinned local Nothing source. Exact local evidence is sufficient and stronger.

## Candidates

| candidate | frozen revision | path / SHA256 | classification | reason |
|---|---|---|---|---|
| Nothing MT6878 `device_modules` | `957dac185efe46cbf6336b0fff9516d84c8cd78f` | `drivers/spi/spi-mt65xx.c`; `339e05e55161aa35696fa84fc6a0426e0d72b4a45e471f589e94e5cfe2e45669` | **EXACT_SOURCE** | Correct module target/name; all 31 built function symbols, offsets, sizes, and KCFI IDs match stock; all 65 imports/66 MODVERSION records/3 exports match; all three export CRCs regenerate naturally; all function bytes match. |
| Nothing MT6878 vendor header | same | `include/linux/platform_data/spi-mt65xx.h`; `8971388cc7e30c6eaaae662c8eb7aaef67ecf89d7ebd76810f7bbbbba156ea16` | **EXACT_SOURCE** | Required private `struct mtk_chip_config` shape; the driver dereferences three fields absent from GKI Common's copy. |
| Nothing MT6878 `kernel` | pinned local tree | `drivers/spi/spi-mt65xx.c`; `5e29d6bd749fd44274f6d6aa6592c84306b555fe2bd74c21786d2ef97b70f53c` | STRUCTURAL_DONOR_ONLY | Upstream-style core, 1423 lines/38248 bytes; lacks all three vendor exports and the GQ5012BF1 MT6989/TEE/autosuspend/debug deltas. |
| exact GKI Android Common | `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09` | `common/drivers/spi/spi-mt65xx.c`; `9a900eabad47db5ed1f484113cf005fcdd8916559b553083ffc1ad76c2d9fec2` | STRUCTURAL_DONOR_ONLY | Same upstream lineage; 1425 lines/38286 bytes; no vendor exports. Its platform-data header also lacks three fields used by exact vendor source. |
| generic upstream / stable / other vendor mirrors | searched by exact file/symbol/compatible strings | various | STRUCTURAL_DONOR_ONLY or NO_USEFUL_SOURCE | Establish lineage only; none supersedes the pinned exact MT6878 source/build proof. |

## Frozen source objects

At `device_modules@957dac185efe46cbf6336b0fff9516d84c8cd78f`:

| path | git blob | SHA256 |
|---|---|---|
| `drivers/spi/spi-mt65xx.c` | `ed36da2b3ba725024f3478c50941526d355b1a9d` | `339e05e55161aa35696fa84fc6a0426e0d72b4a45e471f589e94e5cfe2e45669` |
| `include/linux/platform_data/spi-mt65xx.h` | `bdb1b5026c6ba56bd79bd3dfe1891ae88b28cb4b` | `8971388cc7e30c6eaaae662c8eb7aaef67ecf89d7ebd76810f7bbbbba156ea16` |
| `drivers/spi/Kconfig` | `c98523cf109e0eaecaca3beb7ea4062b7aaacb61` | `25830e7dab55a9d1b05e05110c58940183ed80454f0224b2c37b75a4b1cd730a` |
| `drivers/spi/Makefile` | `4e0bba2d3c9316d609e4db6d24d4762f90ede388` | `ef77fe29acebb90eebbde6cb9ea5f45b4ccb60a8510389f461e71a1f9b7cbc28` |

## Conclusion

No reverse engineering or behavioral delta is required. The correct source is
the pinned Nothing MT6878 MediaTek `device_modules` variant, not upstream
`common/drivers/spi/spi-mt65xx.c`.
