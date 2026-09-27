# Host environment

Captured before sync unless marked current.

| Item | Value |
|---|---|
| distro | Gentoo Linux |
| host kernel | Linux `7.2.3-cachyos-dist` x86_64 |
| CPU | AMD Ryzen Threadripper 2990WX, 32 cores / 64 threads, 1 socket |
| RAM | 236488421376 bytes total; 220273700864 bytes available at final capture |
| source filesystem | `/dev/sda1`, ext4, 1967864131584 bytes |
| free before sync | 278883577856 bytes (about 260 GiB) |
| free after sync + `m nothing` | 57484181504 bytes (about 53.5 GiB) |
| Git | 2.55.0 |
| repo launcher | 2.54; checkout downloaded repo 2.65 |
| Java | Temurin OpenJDK 21.0.12.1 LTS |
| Python | 3.14.7 |
| Git LFS | 3.8.0, locally staged under phase5 tools |

Git LFS was absent initially. Official `git-lfs` 3.8.0 was downloaded to the
phase5 workspace; tarball SHA-256:
`e455e00f15d9b95661b8d53498ffb0c3367962cf1ec73c31ab7369516cd6ab8d`.
No system package or existing Android tree was replaced.

## Storage gate

The checkout occupies `203965796352` bytes (190 GiB). Successful graph
generation added `17296154624` bytes. Only `57484259328` bytes remained.
Using a 150,000,000,000-byte Android build-output planning allowance, the
minimum immediate shortfall is:

```text
150000000000 - 57484259328 = 92515740672 bytes
```

For a 150 GiB allowance the shortfall is `103577014272` bytes. A practical
next run should provide at least 110 GB additional free space, preferably
150 GB for margin. **BLOCKER:** do not start a full build on the current 97%-full
filesystem. Nothing was deleted to make room.
