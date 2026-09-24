# V17 regeneration OUT-variable correction

The V17 regeneration build completed successfully with BUILD_RC=0.

The initial artifact-copy step failed because Android envsetup/lunch overwrote the
shell variable named OUT, changing it from vendor/etc/selinux to PRODUCT_OUT.

The build itself was not affected.

V21 source was restored after the build and before any subsequent rebuild.

PHONE_MODIFIED=0
