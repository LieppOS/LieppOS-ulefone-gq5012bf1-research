.section .text
.global _start
.type _start, %function

/*
 * Android init_boot diagnostic wrapper.
 *
 * PID 1:
 *   clone() watchdog child
 *   execve("/init.stock", original argv, original envp)
 *
 * Child:
 *   nanosleep(90 seconds)
 *   reboot(RESTART2, "recovery")
 *
 * No libc.
 * No filesystem writes.
 * No /data or /metadata access.
 */

_start:
    /* Preserve original process stack. */
    mov     x19, sp

    /*
     * clone(SIGCHLD, NULL, NULL, NULL, NULL)
     *
     * AArch64 __NR_clone = 220
     * SIGCHLD = 17
     */
    mov     x0, #17
    mov     x1, xzr
    mov     x2, xzr
    mov     x3, xzr
    mov     x4, xzr
    mov     x8, #220
    svc     #0

    /* x0 == 0 only in watchdog child. */
    cbz     x0, watchdog_child

    /*
     * Parent remains PID 1.
     *
     * Original initial stack:
     *   [argc]
     *   [argv...]
     *   [NULL]
     *   [envp...]
     *   [NULL]
     */

    ldr     x20, [x19]          /* argc */
    add     x1, x19, #8         /* argv */

    /* envp = argv + (argc + 1) pointers */
    add     x2, x1, x20, lsl #3
    add     x2, x2, #8

    adr     x0, init_stock

    /*
     * execve("/init.stock", argv, envp)
     *
     * AArch64 __NR_execve = 221
     */
    mov     x8, #221
    svc     #0

    /*
     * execve must never return.
     * If it does, reboot directly to recovery instead of
     * leaving PID 1 dead.
     */
    b       reboot_recovery


watchdog_child:
    /*
     * struct timespec {
     *     long tv_sec  = 90;
     *     long tv_nsec = 0;
     * };
     */
    sub     sp, sp, #16
    mov     x0, #90
    str     x0, [sp]
    str     xzr, [sp, #8]

    /*
     * nanosleep(&ts, NULL)
     *
     * AArch64 __NR_nanosleep = 101
     */
    mov     x0, sp
    mov     x1, xzr
    mov     x8, #101
    svc     #0

reboot_recovery:
    /*
     * reboot(
     *   LINUX_REBOOT_MAGIC1,
     *   LINUX_REBOOT_MAGIC2,
     *   LINUX_REBOOT_CMD_RESTART2,
     *   "recovery"
     * )
     *
     * AArch64 __NR_reboot = 142
     *
     * MAGIC1   = 0xfee1dead
     * MAGIC2   = 0x28121969
     * RESTART2 = 0xa1b2c3d4
     */

    movz    w0, #0xdead
    movk    w0, #0xfee1, lsl #16

    movz    w1, #0x1969
    movk    w1, #0x2812, lsl #16

    movz    w2, #0xc3d4
    movk    w2, #0xa1b2, lsl #16

    adr     x3, recovery_string

    mov     x8, #142
    svc     #0

    /*
     * reboot() should never return.
     * If denied/fails, remain alive rather than exiting.
     */
1:
    wfe
    b       1b


.section .rodata

init_stock:
    .asciz "/init.stock"

recovery_string:
    .asciz "recovery"

