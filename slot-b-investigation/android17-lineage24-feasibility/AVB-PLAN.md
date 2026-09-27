# Android 17 AVB plan

No AVB image was built or written in this task.

## Proven current descriptor ownership

| Changed partition | Descriptor owner to regenerate |
|---|---|
| `system_b` | `vbmeta_system_b` |
| `system_ext_b` | root `vbmeta_b` |
| `product_b` | root `vbmeta_b` |
| `vendor_b` | `vbmeta_vendor_b` |
| `vendor_dlkm_b` | root `vbmeta_b` |
| `system_dlkm_b` | root `vbmeta_b` |
| `odm_dlkm_b` | root `vbmeta_b` |

Root `vbmeta_b` carries chain descriptors for `boot` (rollback location 3),
`vbmeta_system` (2) and `vbmeta_vendor` (4). A changed child image signed with
the already-chained key does not require changing that chain descriptor; a
changed key does.

## Required future construction

1. Give every logical image an AVB hashtree/footer inside its exact existing
   extent; account for tree, FEC and footer before declaring fit.
2. Build `vbmeta_system_b` from the Android17 `system` descriptor with the same
   accepted system key identity, `SHA256_RSA2048` and rollback metadata.
3. Rebuild root `vbmeta_b` whenever product/system_ext/root-owned DLKM or any
   root hash descriptor changes. Preserve descriptor order, chain keys, rollback
   locations and 8192-byte root size where the existing chain requires them.
4. Leave `vbmeta_vendor_b` unchanged while vendor is unchanged. Rebuild it with
   the existing vendor key if vendor changes.
5. Verify individual footers, each child vbmeta and the complete followed chain
   against exact candidate images before any write.

## No disabled verification

The proven diagnostic root currently has flags `3`; that historical state is
not a production template. The Android17 chain must be generated with AVB flags
`0` and must not use `--disable-verity` or `--disable-verification`.

**KNOWN BLOCKER:** current verification evidence reaches a pre-existing
`init_boot` hash-descriptor mismatch. Flags 0 cannot be proposed until every
root-owned/boot-chain descriptor is reconciled with the exact intended B image.
The first AVB milestone is therefore a fully coherent host-verified flags-0 B
chain, not reuse of the diagnostic flags-3 root.

## Rollback and identity

- keep current rollback index/location values unless bootloader evidence requires
  a monotonic value;
- do not burn or raise hardware rollback indices during first bring-up;
- keep private keys outside Git and record only public-key hashes;
- update Android17 OS/security-patch properties truthfully;
- never mix A images/keys or write A vbmeta.

## DSU note

A DSU first proof uses Android's DSU verification path and does not require
rewriting the current B AVB chain. That is another reason to validate userspace
through DSU before constructing the final split B chain.

**TEST TO CONFIRM:** exact full-chain `avbtool verify_image --follow_chain_partitions`
with all Android17 candidate and unchanged B images, then a separately authorized
flags-0 acceptance test. None was executed here.
