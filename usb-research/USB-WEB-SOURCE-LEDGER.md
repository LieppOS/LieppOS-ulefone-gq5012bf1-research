# USB web-source ledger

Accessed 2026-09-23. Web claims remain lower confidence than exact stock DT/runtime/module evidence unless identified as official.

| Source | Type | Relevant evidence | Limits |
|---|---|---|---|
| <https://www.ulefone.com/pages/armor-29-pro-thermal-version-spec> | official product page | USB Type-C, 120 W charging, 10 W wired reverse charging, supplied Type-C data cable, IP68/IP69K, non-removable battery | No USB data-generation or lane-routing statement |
| <https://www.mediatek.com/products/smartphones/mediatek-dimensity-7300> | official SoC product page | confirms public Dimensity family capabilities | No USB controller/PHY/version data published |
| <https://www.mediatek.com/hubfs/Dimensity%207400_Infographic.pdf> | official SoC infographic | confirms Dimensity 7400 product family | No usable USB controller/PHY/version statement found |
| <https://github.com/NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878> | OEM-published kernel source | exact MT6878 USB/PHY architecture; frozen at commit `957dac185efe46cbf6336b0fff9516d84c8cd78f` | Kernel implementation, not package ball map or silicon datasheet |
| <https://buy2fix.co.uk/products/for-ulefone-armor-29-pro-charging-port-board> | replacement-part listing | dedicated Armor 29 Pro charging-port board, SKU `EDA006599748`; product image | Third-party listing; not a schematic; title does not separately say Thermal variant |
| <https://www.bobshop.co.za/for-ulefone-armor-29-pro-charging-port-board/p/679058920> | listing mirror | independently repeats SKU `EDA006599748` and original image URL | Marketplace source |
| <https://img.myipadbox.com/sec/product_raw/EDA006599748.jpg> | listing source image | top side of `BM65_SUB_V1.2` daughterboard: USB-C receptacle, board-to-board connector and components | One side only; no net labels, underside, X-ray or continuity data |
| <https://fccid.io/2AOWK-5012> | FCC filing index | FCC family `2AOWK-5012`, Shenzhen Gotron model 5012; internal-photo exhibit 8392091 is listed | Cloudflare blocked direct exhibit retrieval in this session |
| <https://device.report/shenzhen-gotron-electronic/5012> | FCC mirror/index | identifies 12-page internal-photo exhibit, approximately 3.7 MB | Mirror also blocked direct retrieval |
| PhoneDB MT6878 processor entry | secondary database | claims USB 3.0 / 5 Gbit/s for MT6878 | marked preliminary; no cited primary MediaTek source; conflicts with OEM-published MT6878 kernel topology |

Locally frozen visual evidence:

- `evidence/EDA006599748-armor29pro-charging-board.jpg`, SHA-256 `6930efc7c12ce05f97e2f8ccfaefbc98fa3f2b7d5650b32b0f2d20aee5d1b420`.

The FCC internal-photo exhibit is the best known public next source. Its existence is verified, but no visual conclusion from it is claimed until the actual pages can be obtained and archived.
