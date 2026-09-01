.section .text
.global _start
.type _start, %function

.extern capture_main

/*
 * V3 diagnostic init wrapper.
 *
 * Parent:
 *   clone watchdog child
 *   exec exact original Android init as /init.stock
 *
 * Child:
 *   wait at least 80 seconds
 *   capture diagnostic state into reserved pstore partition tail
 *   sync
 *   reboot with RESTART2("recovery")
 *
 * Parent boot behavior intentionally follows proven V2 structure.
 */

_start:
    mov     x19, sp

   /*
    * V9: obtain AID_READPROC before SELinux starts.
    * Child inherits this supplementary group.
    */
   sub     sp, sp, #16

   mov     w9, #3009
   str     w9, [sp]

   mov     x0, #1
   mov     x1, sp
   mov     x8, #159
   svc     #0

   adrp    x9, early_setgroups_rc
   add     x9, x9, :lo12:early_setgroups_rc
   str     x0, [x9]

   add     sp, sp, #16


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
    * Parent only: remove diagnostic supplementary group
    * before execve("/init.stock").
    */
   mov     x0, xzr
   mov     x1, xzr
   mov     x8, #159
   svc     #0


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

    /* V10: parent exec failure -> bootloader */
    b       reboot_bootloader


watchdog_child:

sleep_again:
    /*
     * Full 80-second timespec each attempt.
     * Interruption can only lengthen the delay.
     */
    sub     sp, sp, #16

    mov     x0, #80
    str     x0, [sp]
    str     xzr, [sp, #8]

    mov     x0, sp
    mov     x1, xzr

    /* nanosleep */
    mov     x8, #101
    svc     #0

    add     sp, sp, #16

    cbnz    x0, sleep_again

    /*
     * Capture routine is freestanding/static and returns even
     * when any individual diagnostic source is unavailable.
     */
    bl      capture_main


reboot_bootloader:
    /* sync() */
    mov     x8, #81
    svc     #0

    movz    w0, #0xdead
    movk    w0, #0xfee1, lsl #16

    movz    w1, #0x1969
    movk    w1, #0x2812, lsl #16

    movz    w2, #0xc3d4
    movk    w2, #0xa1b2, lsl #16

    adr     x3, bootloader_string

    mov     x8, #142
    svc     #0

2:
    wfe
    b       2b


reboot_recovery:
    /* sync() */
    mov     x8, #81
    svc     #0

    /*
     * reboot(
     *   0xfee1dead,
     *   0x28121969,
     *   0xa1b2c3d4,
     *   "recovery"
     * )
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

1:
    wfe
    b       1b


.section .rodata

init_stock:
    .asciz "/init.stock"

recovery_string:
    .asciz "recovery"

bootloader_string:
    .asciz "bootloader"

.section .bss
.align 3

.global early_setgroups_rc
.type early_setgroups_rc, %object
.size early_setgroups_rc, 8

early_setgroups_rc:
   .skip 8

