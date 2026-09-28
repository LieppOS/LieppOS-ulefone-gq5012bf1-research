# Build log summary

Full logs remain outside Git under:

`/mnt/SamsungSSD/TIER3/phase5/android17/logs/`

## Attempts

1. A preliminary harness invocation failed before compilation because the host
   lacks `/usr/bin/time`. The script was corrected to use shell timestamps.
2. An agent-launched compile was canceled cleanly at the user's request so the
   user could run the NUMA-bound command. This was not a source/build failure.
3. The NUMA-bound build ran from `2026-09-28T00:44:41+03:00` to
   `14:04:08+03:00`, reached 92%, then failed at exactly one source input:

   ```text
   external/chromium-webview/prebuilt/arm64/webview.apk: failed opening zip
   ```

   The file was a 134-byte Git LFS pointer for object
   `3b98460ccd41b2a1851c5a46e6dec6f86f1d14302ff2fa4deeb1d781e32f89a4`,
   expected size 267260603. This was a legitimate checkout/environment problem,
   not a framework problem.
4. `git lfs install --local` and `git lfs pull github` were run only in
   `external/chromium-webview/prebuilt/arm64`. The resulting APK was exactly
   267260603 bytes, its SHA-256 matched the pointer, ZIP validation passed and
   Git status stayed clean.
5. Incremental resume started `14:07:27` and completed `14:24:46`:

   ```text
   ninja: 13m14.58s Build Succeeded: 13955 steps - 17.56/s
   #### build completed successfully (17:12) ####
   BUILD_EXIT=0
   ```

No source patch, framework hack, random package deletion or branch resync was
used.

## Principal logs

| Log | Purpose |
|---|---|
| `build-lineage_gsi_arm64-cp2a-userdebug-erofs.log` | successful incremental run |
| `build-lineage_gsi_arm64-cp2a-userdebug-erofs-attempt3-lfs-pointer.log` | first complete compile and LFS failure |
| `git-lfs-install-pull-chromium-webview-arm64.log` | exact checkout repair |
| `configure-lineage_gsi_arm64-erofs.log` | lunch/configuration capture |
| `fsck-erofs-extract-system.log` | read-only image integrity/extraction |
| `mkfs-split-measurements.log` | split EROFS measurement repack |
| `repo-status-before-build.txt` / `repo-status-after-build.txt` | clean-tree evidence |

The successful build emitted API documentation warnings and the expected GSI
debug-policy warning, but no failed steps.
