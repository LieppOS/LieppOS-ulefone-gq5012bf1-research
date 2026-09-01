.section .text
.global _start
.type _start, %function

/*
 * Diagnostic init wrapper.
 *
 * Parent:
 *   clone watchdog child
 *   exec exact original Android init as /init.stock
 *
 * Child:
 *   wait at least 90 seconds
 *   sync filesystems
 *   reboot with RESTART2("recovery")
 *
 * No libc.
 * No dynamic linker.
 * No filesystem writes of our own.
 */

_start:
    mov     x19, sp

    /* clone(SIGCHLD, NULL, NULL, NULL, NULL) */
    mov     x0, #17
    mov     x1, xzr
    mov     x2, xzr
    mov     x3, xzr
    mov     x4, xzr
    mov     x8, #220
    svc     #0

    cbz     x0, watchdog_child

    /*
     * Preserve original argv/envp.
     *
     * stack:
     * argc
     * argv[]
     * NULL
     * envp[]
     * NULL
     */
    ldr     x20, [x19]
    add     x1, x19, #8

    add     x2, x1, x20, lsl #3
    add     x2, x2, #8

    adr     x0, init_stock

    /* execve("/init.stock", argv, envp) */
    mov     x8, #221
    svc     #0

    /*
     * execve failure is fatal to normal boot.
     * Recover rather than letting PID 1 exit.
     */
    b       reboot_recovery


watchdog_child:

sleep_again:
    /*
     * Recreate a full 90-second timespec each attempt.
     * Therefore a signal can only LENGTHEN the timer,
     * never make it reboot early.
     */
    sub     sp, sp, #16

    mov     x0, #90
    str     x0, [sp]
    str     xzr, [sp, #8]

    mov     x0, sp
    mov     x1, xzr

    /* nanosleep */
    mov     x8, #101
    svc     #0

    add     sp, sp, #16

    /*
     * syscall result:
     *   0       success
     *   negative errno on failure/interruption
     */
    cbnz    x0, sleep_again


reboot_recovery:
    /*
     * sync()
     * AArch64 __NR_sync = 81
     */
    mov     x8, #81
    svc     #0

    /*
     * reboot(
     *   0xfee1dead,
     *   0x28121969,
     *   0xa1b2c3d4,   // LINUX_REBOOT_CMD_RESTART2
     *   "recovery"
     * )
     *
     * AArch64 __NR_reboot = 142
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
     * If reboot unexpectedly fails, do NOT kill
     * the watchdog or PID 1.
     */
1:
    wfe
    b       1b


.section .rodata

init_stock:
    .asciz "/init.stock"

recovery_string:
    .asciz "recovery"
