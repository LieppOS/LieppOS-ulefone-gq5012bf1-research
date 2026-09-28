# AVB structure

## Generated host chain

All image footers and vbmeta headers have flags 0. Verity/FEC remain enabled.

| Artifact | Algorithm | Descriptors |
|---|---|---|
| `system.img` footer | NONE wrapper | SHA-256 hashtree + two-root FEC for system, 625823744 bytes (tree 4935680 + FEC 4988928) |
| `system_ext.img` footer | NONE wrapper | SHA-256 hashtree + two-root FEC for system_ext, 235327488 bytes (tree 1859584 + FEC 1875968) |
| `product.img` footer | NONE wrapper | SHA-256 hashtree + two-root FEC for product, 291459072 bytes (tree 2301952 + FEC 2326528) |
| `vbmeta_system.img` | SHA256_RSA2048 | system descriptor |
| `vbmeta.img` | SHA256_RSA4096 | chain descriptor for vbmeta_system plus product and system_ext descriptors |

The root-to-child test chain and all three data hashtrees pass:

```text
avbtool extract_public_key --key external/avb/test/data/testkey_rsa2048.pem \
  --output vbmeta_system_pubkey.der

avbtool verify_image --image vbmeta.img --follow_chain_partitions \
  --expected_chain_partition vbmeta_system:1:vbmeta_system_pubkey.der
```

Two invocation details matter and were both measured here:

- `--expected_chain_partition` is compared against the raw DER public-key blob
  stored in the chain descriptor, so the extracted `.der` must be passed; the
  PEM file is rejected with `Expected public key blob does not match public key
  blob in descriptor`;
- `--key` must be omitted together with `--follow_chain_partitions`, because the
  recursion re-uses `--key` for the chained image and then reports a spurious
  `Embedded public key does not match given key` for the RSA-2048 child. The
  parent key is checked separately without `--follow_chain_partitions`.

The full output is preserved under
`/mnt/WDBlue/TIER3-phase5-android17/split-iterations/i3-generated-properties/`
(`verify.log`, plus the iteration-2 directory for comparison).

## Descriptor ownership versus current B

The ownership is correct:

- `system_b` → `vbmeta_system_b`;
- `product_b`, `system_ext_b` → root `vbmeta_b`;
- unchanged `vendor_b` remains owned by `vbmeta_vendor_b`;
- unchanged vendor/system/odm DLKM descriptors remain root-owned.

## Host-only limitations

The generated root and child use AOSP test keys. They do not match the accepted
current B key identities and must not be flashed. The host chain uses rollback
location 1 for `vbmeta_system`; current B's root chain uses location 2. A real
B-chain build must preserve location 2 and current boot/vendor chain locations
3 and 4.

The previously observed `init_boot` descriptor mismatch is also unresolved.
Consequently these vbmeta files prove coherent build output only; they are not a
phone-flash package. Verification and verity were never disabled.
