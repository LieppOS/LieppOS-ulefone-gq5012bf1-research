# V21 attempt 1: Android envsetup failure

The first V21 construction attempt successfully reached the intended
experimental source layout:

- V20 dummy declaration disabled;
- V21 dummy inserted after the final V17 source declaration mechanism;
- phone untouched.

The build did not actually start.

The shell running the experiment had `set -u` / `nounset` enabled.
Android's `build/envsetup.sh` referenced `TOP` before it had been initialized,
causing:

    build/envsetup.sh: line 21: TOP: unbound variable
    Couldn't locate the top of the tree.

This is a host-shell/script error, not evidence about V21 SELinux policy.

The experiment automatically restored both modified source files afterward.

The retry therefore runs the Android build environment without shell
`nounset`.

PHONE_MODIFIED=0
