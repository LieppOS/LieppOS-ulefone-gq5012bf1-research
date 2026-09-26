# AVB chain for the vanilla Product-B candidate

## Descriptor ownership

Ownership was parsed again from the exact current diagnostic vbmeta images.

| Partition | Descriptor owner |
|---|---|
| `product` | root `vbmeta_b` |
| `system_ext` | root `vbmeta_b` |
| `system` | `vbmeta_system_b` |
| `vendor` | `vbmeta_vendor_b` |
| `vendor_dlkm` | root `vbmeta_b` |
| `system_dlkm` | root `vbmeta_b` |
| `odm_dlkm` | root `vbmeta_b` |

The complete mapping is in [`AVB-OWNERSHIP.tsv`](AVB-OWNERSHIP.tsv).

Only `product` changed. Therefore only root `vbmeta_b` required regeneration.
`vbmeta_system_b`, `vbmeta_vendor_b`, and every unchanged partition descriptor
remain unchanged.

## Product descriptor

| Field | Current diagnostic product | Vanilla product |
|---|---|---|
| image size | `331276288` | `331276288` |
| tree offset | `331276288` | `331276288` |
| tree size | `2613248` | `2613248` |
| hash algorithm | SHA-1 | SHA-1 |
| salt | `b6497d667c35b54999e4eee6d8c57a3e606fe5bf5d1c2e4919e201e5fb624aa6` | same |
| FEC roots | 2 | 2 |
| FEC offset | `333889536` | `333889536` |
| FEC size | `2646016` | `2646016` |
| flags | 0 | 0 |
| root digest | `2cee01617463eb37655a0913b6c695da5b7e52f7` | `1dbbbb4ed375f4c52921a5dfbe69cbd9cea7c345` |

The embedded product descriptor and the product descriptor in the new root
vbmeta are byte-identical. Product hashtree verification passes.

## Root vbmeta

Candidate:

`/mnt/SamsungSSD/TIER3/phase4/controls/slot-b-vanilla-product-debug/vbmeta_b.vanilla-debug.img`

- exact size: `8192` bytes
- SHA-256: `39ab5e9e6eabc2fa33e9a8e0aec842fc650828f5f8cb505f9e2ea655fab7c917`
- algorithm: `SHA256_RSA2048`
- rollback index: `0`
- rollback-index location: `0`
- flags: `3`, exactly preserving the current working diagnostic root
- embedded public-key SHA-256:
  `2540a16cdbdafe1a3fc08fbef83b5dc876099b881e174b63a895b6def8798d50`
- signature: valid
- descriptor count before/after: `28` / `28`

No AVB setting was weakened further. The existing diagnostic root flags were
preserved rather than changed during this product-only experiment.

The root chain descriptors remain byte-identical:

- `boot`, rollback location 3
- `vbmeta_system`, rollback location 2
- `vbmeta_vendor`, rollback location 4

All 27 non-product descriptors are byte-identical. The product descriptor has
exactly one changed field: root digest. Algorithm, release string, rollback
fields, flags, descriptor order, chain keys, salts, image sizes, tree/FEC
geometry, and signing public-key identity are unchanged.

## Debug system preservation

The unchanged debug system image remains:

`68b4639959dd189fcc6e6603742a4b4ef57f6106d444da48ef884031a69d1a99`

The unchanged matching `vbmeta_system_b` image remains:

`9adb5fb2d3b2375d08884bdb1721097fa26b96f6cbb708408cec47b7862ddfc9`

Its `system` root digest remains:

`aa57361b018f99c0985c15b2e29934192849adeb`

The root-vbmeta chain key for `vbmeta_system` is unchanged, so the vanilla
product pair does not regress the current authorized-ADB system chain.

## Evidence

- [`VBMETA-B-BEFORE.txt`](VBMETA-B-BEFORE.txt)
- [`VBMETA-B-AFTER.txt`](VBMETA-B-AFTER.txt)
- [`VBMETA-B-DESCRIPTOR-AUDIT.txt`](VBMETA-B-DESCRIPTOR-AUDIT.txt)
- [`PRODUCT-B-AVB-INFO.txt`](PRODUCT-B-AVB-INFO.txt)
- [`PRODUCT-B-AVB-VERIFY.txt`](PRODUCT-B-AVB-VERIFY.txt)

No vbmeta image was written to the phone.
