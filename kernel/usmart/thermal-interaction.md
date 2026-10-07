# Interaction with the internal Tiny2-C thermal camera

Authoritative thermal details: `reverse-engineering/thermal-camera/internal-usb/`.
The devices are physically and logically distinct.

## uSmart insertion while thermal is active

1. GPIO28 LOW work still sets GPIO152=1, GPIO55=1 and status=1.
2. Only then it sees `yft_usb_flag=1` and skips the uSmart HOST request.
3. Thermal already holds HOST, so role remains HOST.
4. GPIO55 nevertheless selects uSmart; the thermal USB connection can be displaced while
   both accessories remain powered. The uSmart device may enumerate on the existing host.

## Thermal start while uSmart is attached

1. uSmart already has GPIO152=1, GPIO55=1, status=1 and HOST.
2. Thermal app powers GPIO149/191/192 and sets `yft_usb_flag=1`.
3. Its `tiny2c_mode=1` HOST request is a role no-op.
4. Nothing clears GPIO55 or uSmart power, so the route remains uSmart and Tiny2-C may fail
   to enumerate until uSmart is removed.

## uSmart removal during thermal

Removal clears GPIO152, GPIO55 and status, then the thermal flag suppresses the NONE
request. This is accidentally favorable: route returns from uSmart while HOST remains for
the thermal module.

There is no static arbitration, mutual exclusion or electrical conflict prevention beyond
skipping the ID worker's final role request. The thermal flag does **not** protect route or
power. A safe replacement must serialize the two clients.
