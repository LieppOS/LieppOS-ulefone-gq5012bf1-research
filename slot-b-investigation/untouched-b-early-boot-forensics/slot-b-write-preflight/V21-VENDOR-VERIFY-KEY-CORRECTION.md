# V21 vendor verification correction

The first V21 packaging run incorrectly supplied vendor.pem to
`avbtool verify_image` for the resized vendor image.

The proven V20 procedure verifies vendor.img using its embedded AVB key.
vendor.pem is used to sign and verify the generated vbmeta_vendor image.

The earlier key-mismatch was therefore a host verification error, not
evidence that the V21 vendor image was invalid.

PHONE_MODIFIED=0
