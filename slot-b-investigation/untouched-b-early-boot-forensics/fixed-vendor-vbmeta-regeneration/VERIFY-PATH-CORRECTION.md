# AVB pair verification path-guard correction

The previous complete-pair verification attempt stopped before invoking
`avbtool verify_image`.

The temporary verification directory successfully created:

`vendor.img -> fixed built vendor.img`

but the script then compared:

`readlink -f verification/vendor.img`

against the literal source pathname.

That is an invalid identity check when any pathname component is a symlink,
canonicalized mount path, or otherwise has multiple equivalent names.

`readlink -f` canonicalizes the path, while the source variable retains its
literal pathname.

Therefore a textual inequality does not prove that the symlink references a
different file.

Correct identity validation uses:

1. shell `-ef` to prove both names resolve to the same filesystem object;
2. SHA-256 to prove image-byte identity.

This stop occurred before complete AVB pair verification and does not indicate
an AVB, image, descriptor, or signature failure.

No phone operation occurred.
