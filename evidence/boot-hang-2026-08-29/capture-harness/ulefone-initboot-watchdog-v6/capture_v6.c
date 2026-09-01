/*
 * Ulefone Armor 29 Pro Thermal diagnostic capture helper.
 *
 * Freestanding AArch64 Linux code:
 *   - no libc
 *   - no dynamic linker
 *   - no malloc
 *
 * Writes ONLY inside:
 *
 *   physical partition: /dev/block/by-name/pstore
 *   offset:             0x08100000
 *   maximum length:     0x00400000 (4 MiB)
 *
 * Partition total size previously verified:
 *   0x08500000 (133 MiB)
 */

typedef unsigned long      ulong;
typedef unsigned long long u64;
typedef long               slong;

#define AT_FDCWD       (-100L)

#define O_RDONLY       0
#define O_WRONLY       1
#define O_NONBLOCK     0x800
#define O_DIRECTORY    0x10000

#define SEEK_SET       0

#define NR_openat      56
#define NR_close       57
#define NR_getdents64  61
#define NR_lseek       62
#define NR_read        63
#define NR_write       64
#define NR_fsync       82

/*
 * asm-generic / AArch64 syscall numbers.
 * Host header gate verifies these before compilation.
 */
#define NR_getxattr    8
#define NR_syslog      116

#define SYSLOG_ACTION_READ_ALL    3
#define SYSLOG_ACTION_SIZE_BUFFER 10

#define SCRATCH_OFFSET 0x08100000ULL
#define SCRATCH_SIZE   0x00400000UL

struct writer {
    slong fd;
    ulong remaining;
};

struct linux_dirent64 {
    u64 d_ino;
    slong d_off;
    unsigned short d_reclen;
    unsigned char d_type;
    char d_name[];
};

static inline slong sc1(slong nr, slong a0)
{
    register slong x0 __asm__("x0") = a0;
    register slong x8 __asm__("x8") = nr;

    __asm__ volatile(
        "svc #0"
        : "+r"(x0)
        : "r"(x8)
        : "memory"
    );

    return x0;
}

static inline slong sc2(
    slong nr,
    slong a0,
    slong a1
)
{
    register slong x0 __asm__("x0") = a0;
    register slong x1 __asm__("x1") = a1;
    register slong x8 __asm__("x8") = nr;

    __asm__ volatile(
        "svc #0"
        : "+r"(x0)
        : "r"(x1), "r"(x8)
        : "memory"
    );

    return x0;
}

static inline slong sc3(
    slong nr,
    slong a0,
    slong a1,
    slong a2
)
{
    register slong x0 __asm__("x0") = a0;
    register slong x1 __asm__("x1") = a1;
    register slong x2 __asm__("x2") = a2;
    register slong x8 __asm__("x8") = nr;

    __asm__ volatile(
        "svc #0"
        : "+r"(x0)
        : "r"(x1), "r"(x2), "r"(x8)
        : "memory"
    );

    return x0;
}

static inline slong sc4(
    slong nr,
    slong a0,
    slong a1,
    slong a2,
    slong a3
)
{
    register slong x0 __asm__("x0") = a0;
    register slong x1 __asm__("x1") = a1;
    register slong x2 __asm__("x2") = a2;
    register slong x3 __asm__("x3") = a3;
    register slong x8 __asm__("x8") = nr;

    __asm__ volatile(
        "svc #0"
        : "+r"(x0)
        : "r"(x1), "r"(x2), "r"(x3), "r"(x8)
        : "memory"
    );

    return x0;
}

static slong xopen(
    const char *path,
    slong flags
)
{
    return sc4(
        NR_openat,
        AT_FDCWD,
        (slong)path,
        flags,
        0
    );
}

static slong xclose(slong fd)
{
    return sc1(
        NR_close,
        fd
    );
}

static slong xread(
    slong fd,
    void *buf,
    ulong len
)
{
    return sc3(
        NR_read,
        fd,
        (slong)buf,
        (slong)len
    );
}

static slong xwrite(
    slong fd,
    const void *buf,
    ulong len
)
{
    return sc3(
        NR_write,
        fd,
        (slong)buf,
        (slong)len
    );
}

static slong xlseek(
    slong fd,
    u64 off,
    slong whence
)
{
    return sc3(
        NR_lseek,
        fd,
        (slong)off,
        whence
    );
}

static slong xfsync(slong fd)
{
    return sc1(
        NR_fsync,
        fd
    );
}

static slong xgetdents64(
    slong fd,
    void *buf,
    ulong len
)
{
    return sc3(
        NR_getdents64,
        fd,
        (slong)buf,
        (slong)len
    );
}


static slong xgetxattr(
    const char *path,
    const char *name,
    void *value,
    ulong size
)
{
    return sc4(
        NR_getxattr,
        (slong)path,
        (slong)name,
        (slong)value,
        (slong)size
    );
}

static slong xsyslog(
    slong type,
    void *buf,
    ulong len
)
{
    return sc3(
        NR_syslog,
        type,
        (slong)buf,
        (slong)len
    );
}

/*
 * Global BSS so we do not place a 2 MiB buffer on the
 * tiny watchdog stack. BSS does not materially enlarge
 * the ELF file on disk.
 */
static char syslog_capture_buffer[
    2UL * 1024UL * 1024UL
];

static ulong slen(const char *s)
{
    ulong n = 0;

    while (s[n])
        n++;

    return n;
}

static int is_digit_string(const char *s)
{
    ulong i = 0;

    if (!s[0])
        return 0;

    while (s[i]) {
        if (s[i] < '0' || s[i] > '9')
            return 0;

        i++;
    }

    return 1;
}

static void writer_bytes(
    struct writer *w,
    const void *data,
    ulong len
)
{
    const char *p = (const char *)data;

    while (len && w->remaining) {
        ulong amount = len;

        if (amount > w->remaining)
            amount = w->remaining;

        slong rc = xwrite(
            w->fd,
            p,
            amount
        );

        if (rc <= 0)
            return;

        p += (ulong)rc;
        len -= (ulong)rc;
        w->remaining -= (ulong)rc;
    }
}

static void writer_str(
    struct writer *w,
    const char *s
)
{
    writer_bytes(
        w,
        s,
        slen(s)
    );
}

static void writer_decimal(
    struct writer *w,
    slong value
)
{
    char buf[32];
    ulong n = 0;
    ulong i;
    unsigned long v;

    if (value < 0) {
        writer_str(w, "-");
        v = (unsigned long)(-value);
    } else {
        v = (unsigned long)value;
    }

    if (v == 0) {
        writer_str(w, "0");
        return;
    }

    while (v && n < sizeof(buf)) {
        buf[n++] = (char)(
            '0' + (v % 10)
        );

        v /= 10;
    }

    for (i = 0; i < n / 2; i++) {
        char t = buf[i];

        buf[i] = buf[n - 1 - i];
        buf[n - 1 - i] = t;
    }

    writer_bytes(
        w,
        buf,
        n
    );
}

static slong read_small(
    const char *path,
    char *buf,
    ulong cap
)
{
    slong fd;
    slong rc;

    if (!cap)
        return -1;

    fd = xopen(
        path,
        O_RDONLY
    );

    if (fd < 0)
        return fd;

    rc = xread(
        fd,
        buf,
        cap
    );

    xclose(fd);

    return rc;
}

static void copy_file_limited(
    struct writer *w,
    const char *label,
    const char *path,
    ulong max_bytes
)
{
    char buf[4096];
    slong fd;
    ulong total = 0;

    writer_str(w, "\n=== ");
    writer_str(w, label);
    writer_str(w, " ===\n");

    fd = xopen(
        path,
        O_RDONLY
    );

    if (fd < 0) {
        writer_str(w, "[OPEN_FAILED rc=");
        writer_decimal(w, fd);
        writer_str(w, "]\n");
        return;
    }

    while (
        total < max_bytes &&
        w->remaining
    ) {
        ulong want = sizeof(buf);

        if (
            want >
            max_bytes - total
        )
            want = max_bytes - total;

        if (
            want >
            w->remaining
        )
            want = w->remaining;

        if (!want)
            break;

        slong rc = xread(
            fd,
            buf,
            want
        );

        if (rc <= 0)
            break;

        writer_bytes(
            w,
            buf,
            (ulong)rc
        );

        total += (ulong)rc;
    }

    xclose(fd);

    writer_str(w, "\n");
}


static void capture_selinux_xattr(
    struct writer *w,
    const char *path
)
{
    char buf[512];
    slong rc;
    ulong n;

    writer_str(w, "\n=== SELINUX_XATTR ");
    writer_str(w, path);
    writer_str(w, " ===\n");

    rc = xgetxattr(
        path,
        "security.selinux",
        buf,
        sizeof(buf)
    );

    writer_str(w, "GETXATTR_RC=");
    writer_decimal(w, rc);
    writer_str(w, "\n");

    if (rc <= 0)
        return;

    n = (ulong)rc;

    /*
     * security.selinux is textual and normally has
     * a trailing NUL. Do not put that NUL into our
     * otherwise textual diagnostic stream.
     */
    if (n && buf[n - 1] == 0)
        n--;

    writer_str(w, "VALUE=");
    writer_bytes(w, buf, n);
    writer_str(w, "\n");
}

static void capture_syslog_direct(
    struct writer *w
)
{
    slong size_rc;
    slong read_rc;

    writer_str(
        w,
        "\n=== DIRECT_SYSLOG ===\n"
    );

    /*
     * Action 10 asks only for kernel log ring capacity.
     * It requires no output buffer.
     */
    size_rc = xsyslog(
        SYSLOG_ACTION_SIZE_BUFFER,
        (void *)0,
        0
    );

    writer_str(
        w,
        "SIZE_BUFFER_RC="
    );
    writer_decimal(
        w,
        size_rc
    );
    writer_str(
        w,
        "\n"
    );

    /*
     * Action 3 is READ_ALL: non-destructive snapshot of
     * the kernel printk ring. It does NOT clear the log.
     */
    read_rc = xsyslog(
        SYSLOG_ACTION_READ_ALL,
        syslog_capture_buffer,
        sizeof(syslog_capture_buffer)
    );

    writer_str(
        w,
        "READ_ALL_RC="
    );
    writer_decimal(
        w,
        read_rc
    );
    writer_str(
        w,
        "\n"
    );

    if (read_rc > 0) {
        writer_str(
            w,
            "--- SYSLOG_DATA_BEGIN ---\n"
        );

        writer_bytes(
            w,
            syslog_capture_buffer,
            (ulong)read_rc
        );

        writer_str(
            w,
            "\n--- SYSLOG_DATA_END ---\n"
        );
    }
}

static void copy_kmsg(
    struct writer *w
)
{
    char buf[4096];
    slong fd;
    ulong total = 0;

    const ulong limit =
        2UL * 1024UL * 1024UL;

    writer_str(
        w,
        "\n=== /dev/kmsg ===\n"
    );

    fd = xopen(
        "/dev/kmsg",
        O_RDONLY | O_NONBLOCK
    );

    if (fd < 0) {
        writer_str(w, "[OPEN_FAILED rc=");
        writer_decimal(w, fd);
        writer_str(w, "]\n");
        return;
    }

    while (
        total < limit &&
        w->remaining
    ) {
        ulong want = sizeof(buf);

        if (want > limit - total)
            want = limit - total;

        slong rc = xread(
            fd,
            buf,
            want
        );

        if (rc <= 0)
            break;

        writer_bytes(
            w,
            buf,
            (ulong)rc
        );

        total += (ulong)rc;
    }

    xclose(fd);

    writer_str(w, "\n");
}

static int append_str(
    char *dst,
    ulong cap,
    ulong *pos,
    const char *src
)
{
    ulong i = 0;

    while (src[i]) {
        if (*pos + 1 >= cap)
            return 0;

        dst[*pos] = src[i];
        (*pos)++;
        i++;
    }

    dst[*pos] = 0;

    return 1;
}

static int build_proc_path(
    char *dst,
    ulong cap,
    const char *pid,
    const char *suffix
)
{
    ulong pos = 0;

    if (!append_str(
        dst,
        cap,
        &pos,
        "/proc/"
    ))
        return 0;

    if (!append_str(
        dst,
        cap,
        &pos,
        pid
    ))
        return 0;

    if (!append_str(
        dst,
        cap,
        &pos,
        suffix
    ))
        return 0;

    return 1;
}

static int contains_n(
    const char *buf,
    ulong len,
    const char *needle
)
{
    ulong nl = slen(needle);
    ulong i;
    ulong j;

    if (!nl || nl > len)
        return 0;

    for (i = 0; i + nl <= len; i++) {
        for (j = 0; j < nl; j++) {
            if (buf[i + j] != needle[j])
                break;
        }

        if (j == nl)
            return 1;
    }

    return 0;
}

static int interesting_process(
    const char *comm,
    ulong comm_len,
    const char *cmd,
    ulong cmd_len
)
{
    static const char *keys[] = {
        "vold",
        "keystore",
        "keymint",
        "keymaster",
        "gatekeeper",
        "servicemanager",
        "hwservicemanager",
        "tee",
        "trusty",
    };

    ulong i;

    for (
        i = 0;
        i < sizeof(keys) / sizeof(keys[0]);
        i++
    ) {
        if (
            contains_n(
                comm,
                comm_len,
                keys[i]
            )
        )
            return 1;

        if (
            contains_n(
                cmd,
                cmd_len,
                keys[i]
            )
        )
            return 1;
    }

    return 0;
}

static void capture_processes(
    struct writer *w
)
{
    char dent_buf[4096];
    char path[128];

    char comm[256];
    char cmd[512];
    char wchan[256];

    slong proc_fd;

    writer_str(
        w,
        "\n=== PROCESS INVENTORY ===\n"
    );

    proc_fd = xopen(
        "/proc",
        O_RDONLY | O_DIRECTORY
    );

    if (proc_fd < 0) {
        writer_str(
            w,
            "[OPEN /proc FAILED]\n"
        );

        return;
    }

    while (w->remaining > 65536) {
        slong nr = xgetdents64(
            proc_fd,
            dent_buf,
            sizeof(dent_buf)
        );

        if (nr <= 0)
            break;

        ulong pos = 0;

        while (
            pos < (ulong)nr &&
            w->remaining > 65536
        ) {
            struct linux_dirent64 *d =
                (struct linux_dirent64 *)
                (dent_buf + pos);

            if (
                d->d_reclen < 20 ||
                pos + d->d_reclen >
                    (ulong)nr
            )
                break;

            const char *pid =
                d->d_name;

            if (is_digit_string(pid)) {
                slong comm_n = -1;
                slong cmd_n = -1;
                slong wchan_n = -1;

                if (
                    build_proc_path(
                        path,
                        sizeof(path),
                        pid,
                        "/comm"
                    )
                ) {
                    comm_n = read_small(
                        path,
                        comm,
                        sizeof(comm)
                    );
                }

                if (
                    build_proc_path(
                        path,
                        sizeof(path),
                        pid,
                        "/cmdline"
                    )
                ) {
                    cmd_n = read_small(
                        path,
                        cmd,
                        sizeof(cmd)
                    );
                }

                if (
                    build_proc_path(
                        path,
                        sizeof(path),
                        pid,
                        "/wchan"
                    )
                ) {
                    wchan_n = read_small(
                        path,
                        wchan,
                        sizeof(wchan)
                    );
                }

                writer_str(w, "PID=");
                writer_str(w, pid);

                writer_str(w, " COMM=");

                if (comm_n > 0)
                    writer_bytes(
                        w,
                        comm,
                        (ulong)comm_n
                    );

                writer_str(w, " CMD=");

                if (cmd_n > 0) {
                    slong i;

                    for (
                        i = 0;
                        i < cmd_n;
                        i++
                    ) {
                        if (!cmd[i])
                            cmd[i] = ' ';
                    }

                    writer_bytes(
                        w,
                        cmd,
                        (ulong)cmd_n
                    );
                }

                writer_str(w, " WCHAN=");

                if (wchan_n > 0)
                    writer_bytes(
                        w,
                        wchan,
                        (ulong)wchan_n
                    );

                writer_str(w, "\n");

                if (
                    interesting_process(
                        comm,
                        comm_n > 0 ?
                            (ulong)comm_n : 0,
                        cmd,
                        cmd_n > 0 ?
                            (ulong)cmd_n : 0
                    )
                ) {
                    writer_str(
                        w,
                        "--- INTERESTING PID "
                    );

                    writer_str(w, pid);
                    writer_str(w, " ---\n");

                    if (
                        build_proc_path(
                            path,
                            sizeof(path),
                            pid,
                            "/status"
                        )
                    ) {
                        copy_file_limited(
                            w,
                            path,
                            path,
                            32768
                        );
                    }

                    if (
                        build_proc_path(
                            path,
                            sizeof(path),
                            pid,
                            "/stack"
                        )
                    ) {
                        copy_file_limited(
                            w,
                            path,
                            path,
                            16384
                        );
                    }
                }
            }

            pos += d->d_reclen;
        }
    }

    xclose(proc_fd);
}

__attribute__((visibility("default")))
void capture_main(void)
{
    slong fd;
    slong seek_rc;

    struct writer w;

    /*
     * Do not fall back to an ambiguous block device path.
     * Either exact by-name pstore exists or capture is skipped.
     */
    fd = xopen(
        "/dev/block/by-name/pstore",
        O_WRONLY
    );

    if (fd < 0)
        return;

    seek_rc = xlseek(
        fd,
        SCRATCH_OFFSET,
        SEEK_SET
    );

    if (
        seek_rc < 0 ||
        (u64)seek_rc != SCRATCH_OFFSET
    ) {
        xclose(fd);
        return;
    }

    w.fd = fd;
    w.remaining = SCRATCH_SIZE;

    writer_str(
        &w,
        "ULEFONE_DIAG_V6\n"
        "DEVICE=Armor_29_Pro_Thermal\n"
        "SCRATCH_OFFSET=0x08100000\n"
        "SCRATCH_LIMIT=0x00400000\n"
        "CAPTURE_DELAY_SECONDS=80\n"
        "PURPOSE=kmsg-label+direct-syslog-policy-test\n"
    );

    /*
     * Determine the watchdog's ACTUAL security identity
     * after Android has loaded SELinux and reached the hang.
     */
    copy_file_limited(
        &w,
        "/proc/self/attr/current",
        "/proc/self/attr/current",
        4096
    );

    copy_file_limited(
        &w,
        "/proc/self/status",
        "/proc/self/status",
        32768
    );

    copy_file_limited(
        &w,
        "/proc/self/mountinfo",
        "/proc/self/mountinfo",
        262144
    );

    copy_file_limited(
        &w,
        "/proc/self/cgroup",
        "/proc/self/cgroup",
        32768
    );

    copy_file_limited(
        &w,
        "/sys/fs/selinux/enforce",
        "/sys/fs/selinux/enforce",
        4096
    );

    copy_file_limited(
        &w,
        "/proc/sys/kernel/dmesg_restrict",
        "/proc/sys/kernel/dmesg_restrict",
        4096
    );

    copy_file_limited(
        &w,
        "/proc/sys/kernel/kptr_restrict",
        "/proc/sys/kernel/kptr_restrict",
        4096
    );

    capture_selinux_xattr(
        &w,
        "/dev/kmsg"
    );

    capture_selinux_xattr(
        &w,
        "/sys/fs/selinux/policy"
    );

    capture_selinux_xattr(
        &w,
        "/dev/block/sdc21"
    );

    capture_selinux_xattr(
        &w,
        "/dev/block/by-name/pstore"
    );

    /*
     * This bypasses /dev/kmsg completely and therefore
     * tests kernel:system syslog_read independently of
     * the /dev/kmsg inode label.
     */
    capture_syslog_direct(
        &w
    );

    /*
     * Capture the actually loaded SELinux policy.
     * Expected stock size is ~1.22 MiB; hard cap is 2 MiB.
     *
     * This is binary data and can contain NUL bytes.
     * During extraction we locate it between this section
     * marker and the following /dev/kmsg marker.
     */
    copy_file_limited(
        &w,
        "/sys/fs/selinux/policy",
        "/sys/fs/selinux/policy",
        2UL * 1024UL * 1024UL
    );

    copy_kmsg(&w);

    copy_file_limited(
        &w,
        "/proc/cmdline",
        "/proc/cmdline",
        16384
    );

    copy_file_limited(
        &w,
        "/proc/mounts",
        "/proc/mounts",
        131072
    );

    copy_file_limited(
        &w,
        "/proc/1/mountinfo",
        "/proc/1/mountinfo",
        262144
    );

    copy_file_limited(
        &w,
        "/proc/1/status",
        "/proc/1/status",
        65536
    );

    copy_file_limited(
        &w,
        "/proc/1/wchan",
        "/proc/1/wchan",
        4096
    );

    copy_file_limited(
        &w,
        "/proc/1/stack",
        "/proc/1/stack",
        16384
    );

    copy_file_limited(
        &w,
        "/proc/filesystems",
        "/proc/filesystems",
        32768
    );

    copy_file_limited(
        &w,
        "/sys/fs/selinux/enforce",
        "/sys/fs/selinux/enforce",
        4096
    );

    capture_processes(&w);

    writer_str(
        &w,
        "\n=== END ULEFONE_DIAG_V6 ===\n"
    );

    xfsync(fd);
    xclose(fd);
}
