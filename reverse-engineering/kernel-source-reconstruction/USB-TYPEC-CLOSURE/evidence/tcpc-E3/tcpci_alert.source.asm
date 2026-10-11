source tcpci_alert section=.text address=0xba78 size=1936
    ba78:      	paciasp
    ba7c:      	sub	sp, sp, #0x70
    ba80:      	stp	x29, x30, [sp, #0x20]
    ba84:      	stp	x26, x25, [sp, #0x30]
    ba88:      	stp	x24, x23, [sp, #0x40]
    ba8c:      	stp	x22, x21, [sp, #0x50]
    ba90:      	stp	x20, x19, [sp, #0x60]
    ba94:      	add	x29, sp, #0x20
    ba98:      	mrs	x8, SP_EL0
    ba9c:      	mov	w9, #0x2c71
    baa0:      	ldr	x8, [x8, #0x638]
    baa4:      	add	x25, x0, x9
    baa8:      	mov	x19, x0
    baac:      	mov	w22, w1
    bab0:      	stur	x8, [x29, #-0x8]
    bab4:      	mov	w8, #0x2248
    bab8:      	add	x21, x0, x8
    babc:      	ldrb	w23, [x25]
    bac0:      	mov	x0, x21
    bac4:      	ldrb	w26, [x25, #0x8cf]
    bac8:      	str	xzr, [sp]
    bacc:      	bl	0xbacc <tcpci_alert+0x54>
		000000000000bacc:  R_AARCH64_CALL26	mutex_lock
    bad0:      	bl	0xbad0 <tcpci_alert+0x58>
		000000000000bad0:  R_AARCH64_CALL26	sched_clock
    bad4:      	str	x0, [x19, #0x2c90]
    bad8:      	mov	x0, x21
    badc:      	bl	0xbadc <tcpci_alert+0x64>
		000000000000badc:  R_AARCH64_CALL26	mutex_unlock
    bae0:      	add	x1, sp, #0x4
    bae4:      	mov	x2, sp
    bae8:      	mov	x0, x19
    baec:      	bl	0xbaec <tcpci_alert+0x74>
		000000000000baec:  R_AARCH64_CALL26	tcpci_get_alert_status_and_mask
    baf0:      	mov	w20, w0
    baf4:      	tbnz	w0, #0x1f, 0xbb8c <tcpci_alert+0x114>
    baf8:      	mov	w8, #0x3578
    bafc:      	adrp	x1, 0xb000 <tcpci_enter_mode+0x78>
		000000000000bafc:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x1caf
    bb00:      	add	x1, x1, #0x0
		000000000000bb00:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x1caf
    bb04:      	add	x0, x19, x8
    bb08:      	bl	0xbb08 <tcpci_alert+0x90>
		000000000000bb08:  R_AARCH64_CALL26	___ratelimit
    bb0c:      	cbz	w0, 0xbb58 <tcpci_alert+0xe0>
    bb10:      	mov	x0, x19
    bb14:      	mov	w1, wzr
    bb18:      	bl	0xbb18 <tcpci_alert+0xa0>
		000000000000bb18:  R_AARCH64_CALL26	tcpci_notify_alert_ratelimited
    bb1c:      	ldp	w2, w1, [sp]
    bb20:      	adrp	x0, 0xb000 <tcpci_enter_mode+0x78>
		000000000000bb20:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x2ef4
    bb24:      	add	x0, x0, #0x0
		000000000000bb24:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x2ef4
    bb28:      	bl	0xbb28 <tcpci_alert+0xb0>
		000000000000bb28:  R_AARCH64_CALL26	pd_dbg_info
    bb2c:      	ldp	w8, w9, [sp]
    bb30:      	and	w1, w9, w8
    bb34:      	sub	w8, w23, #0x6
    bb38:      	cmn	w8, #0x6
    bb3c:      	str	w1, [sp, #0x4]
    bb40:      	b.hi	0xbbc4 <tcpci_alert+0x14c>
    bb44:      	adrp	x0, 0xb000 <tcpci_enter_mode+0x78>
		000000000000bb44:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x3240
    bb48:      	add	x0, x0, #0x0
		000000000000bb48:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x3240
    bb4c:      	mov	w1, w23
    bb50:      	bl	0xbb50 <tcpci_alert+0xd8>
		000000000000bb50:  R_AARCH64_CALL26	pd_dbg_info
    bb54:      	b	0xbb7c <tcpci_alert+0x104>
    bb58:      	mov	x0, x19
    bb5c:      	mov	w1, #0x1
    bb60:      	bl	0xbb60 <tcpci_alert+0xe8>
		000000000000bb60:  R_AARCH64_CALL26	tcpci_notify_alert_ratelimited
    bb64:      	ldp	w8, w9, [sp]
    bb68:      	and	w1, w9, w8
    bb6c:      	str	w1, [sp, #0x4]
    bb70:      	tbz	w1, #0xf, 0xbb80 <tcpci_alert+0x108>
    bb74:      	mov	x0, x19
    bb78:      	bl	0xbb78 <tcpci_alert+0x100>
		000000000000bb78:  R_AARCH64_CALL26	tcpci_alert_vendor_defined_handler
    bb7c:      	ldr	w1, [sp, #0x4]
    bb80:      	mov	x0, x19
    bb84:      	bl	0xbb84 <tcpci_alert+0x10c>
		000000000000bb84:  R_AARCH64_CALL26	tcpci_alert_status_clear
    bb88:      	mov	w20, w0
    bb8c:      	mrs	x8, SP_EL0
    bb90:      	ldr	x8, [x8, #0x638]
    bb94:      	ldur	x9, [x29, #-0x8]
    bb98:      	cmp	x8, x9
    bb9c:      	b.ne	0xc204 <tcpci_alert+0x78c>
    bba0:      	mov	w0, w20
    bba4:      	ldp	x20, x19, [sp, #0x60]
    bba8:      	ldp	x22, x21, [sp, #0x50]
    bbac:      	ldp	x24, x23, [sp, #0x40]
    bbb0:      	ldp	x26, x25, [sp, #0x30]
    bbb4:      	ldp	x29, x30, [sp, #0x20]
    bbb8:      	add	sp, sp, #0x70
    bbbc:      	autiasp
    bbc0:      	ret
    bbc4:      	tbz	w22, #0x0, 0xbbe0 <tcpci_alert+0x168>
    bbc8:      	mov	x0, x19
    bbcc:      	mov	w1, wzr
    bbd0:      	bl	0xbbd0 <tcpci_alert+0x158>
		000000000000bbd0:  R_AARCH64_CALL26	tcpci_set_alert_mask
    bbd4:      	ldr	w1, [sp, #0x4]
    bbd8:      	tbnz	w0, #0x1f, 0xbb80 <tcpci_alert+0x108>
    bbdc:      	mov	w20, w0
    bbe0:      	tbz	w1, #0x2, 0xbc50 <tcpci_alert+0x1d8>
    bbe4:      	mov	w8, #0x3510
    bbe8:      	add	x0, x19, x8
    bbec:      	bl	0xbbec <tcpci_alert+0x174>
		000000000000bbec:  R_AARCH64_CALL26	mutex_lock
    bbf0:      	ldrb	w8, [sp, #0x4]
    bbf4:      	tbnz	w8, #0x3, 0xbc50 <tcpci_alert+0x1d8>
    bbf8:      	mov	x0, x19
    bbfc:      	bl	0xbbfc <tcpci_alert+0x184>
		000000000000bbfc:  R_AARCH64_CALL26	pd_alloc_msg
    bc00:      	cbz	x0, 0xbc50 <tcpci_alert+0x1d8>
    bc04:      	mov	x23, x0
    bc08:      	add	x24, x0, #0x4
    bc0c:      	add	x1, x0, #0x8
    bc10:      	mov	x0, x19
    bc14:      	mov	x2, x24
    bc18:      	mov	x3, x23
    bc1c:      	bl	0xbc1c <tcpci_alert+0x1a4>
		000000000000bc1c:  R_AARCH64_CALL26	tcpci_get_message
    bc20:      	mov	w1, w0
    bc24:      	tbnz	w0, #0x1f, 0xbc38 <tcpci_alert+0x1c0>
    bc28:      	ldrh	w8, [x24]
    bc2c:      	cbz	w8, 0xbc38 <tcpci_alert+0x1c0>
    bc30:      	str	x23, [x19, #0x2f00]
    bc34:      	b	0xbc50 <tcpci_alert+0x1d8>
    bc38:      	adrp	x0, 0xb000 <tcpci_enter_mode+0x78>
		000000000000bc38:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x1cbb
    bc3c:      	add	x0, x0, #0x0
		000000000000bc3c:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x1cbb
    bc40:      	bl	0xbc40 <tcpci_alert+0x1c8>
		000000000000bc40:  R_AARCH64_CALL26	pd_dbg_info
    bc44:      	mov	x0, x19
    bc48:      	mov	x1, x23
    bc4c:      	bl	0xbc4c <tcpci_alert+0x1d4>
		000000000000bc4c:  R_AARCH64_CALL26	pd_free_msg
    bc50:      	ldr	w1, [sp, #0x4]
    bc54:      	mov	x0, x19
    bc58:      	bl	0xbc58 <tcpci_alert+0x1e0>
		000000000000bc58:  R_AARCH64_CALL26	tcpci_alert_status_clear
    bc5c:      	ldrb	w8, [x25, #0x385]
    bc60:      	cmp	w8, #0x7
    bc64:      	b.ne	0xbc94 <tcpci_alert+0x21c>
    bc68:      	ldr	w8, [sp, #0x4]
    bc6c:      	mov	w9, #0x50
    bc70:      	bics	wzr, w9, w8
    bc74:      	b.ne	0xbc90 <tcpci_alert+0x218>
    bc78:      	mov	w9, #-0x51
    bc7c:      	mov	x0, x19
    bc80:      	and	w8, w8, w9
    bc84:      	str	w8, [sp, #0x4]
    bc88:      	bl	0xbc88 <tcpci_alert+0x210>
		000000000000bc88:  R_AARCH64_CALL26	pd_put_sent_hard_reset_event
    bc8c:      	b	0xc12c <tcpci_alert+0x6b4>
    bc90:      	tbnz	w8, #0x5, 0xc0e8 <tcpci_alert+0x670>
    bc94:      	ldr	w8, [sp, #0x4]
    bc98:      	ands	w8, w8, #0x70
    bc9c:      	b.eq	0xbdf0 <tcpci_alert+0x378>
    bca0:      	lsr	w9, w8, #1
    bca4:      	mov	w10, #0x3470
    bca8:      	and	w9, w9, #0x55555555
    bcac:      	sub	w8, w8, w9
    bcb0:      	lsr	w9, w8, #2
    bcb4:      	and	w8, w8, #0x33333333
    bcb8:      	and	w9, w9, #0x33333333
    bcbc:      	add	w8, w8, w9
    bcc0:      	mov	w9, #0x1010101
    bcc4:      	add	w8, w8, w8, lsr #4
    bcc8:      	and	w8, w8, #0xf0f0f0f
    bccc:      	mul	w8, w8, w9
    bcd0:      	lsr	w9, w8, #24
    bcd4:      	add	x8, x19, x10
    bcd8:      	ldr	w10, [x19, #0x3470]
    bcdc:      	subs	w2, w10, #0x1
    bce0:      	b.mi	0xbd30 <tcpci_alert+0x2b8>
    bce4:      	b	0xbd0c <tcpci_alert+0x294>
    bce8:      	mov	x0, x8
    bcec:      	mov	w1, w10
    bcf0:      	mov	w11, w1
    bcf4:      	casal	w11, w2, [x8]
    bcf8:      	mov	w0, w11
    bcfc:      	cmp	w10, w0
    bd00:      	mov	w10, w0
    bd04:      	b.eq	0xbd30 <tcpci_alert+0x2b8>
    bd08:      	b	0xbcdc <tcpci_alert+0x264>
    bd0c:      	mov	w11, w10
    bd10:      	prfm	pstl1strm, [x8]
    bd14:      	ldxr	w0, [x8]
    bd18:      	eor	w12, w0, w11
    bd1c:      	cbnz	w12, 0xbd2c <tcpci_alert+0x2b4>
    bd20:      	stlxr	w12, w2, [x8]
    bd24:      	cbnz	w12, 0xbd14 <tcpci_alert+0x29c>
    bd28:      	dmb	ish
    bd2c:      	b	0xbcfc <tcpci_alert+0x284>
    bd30:      	cmp	w9, #0x2
    bd34:      	b.lo	0xbdf0 <tcpci_alert+0x378>
    bd38:      	ldr	w10, [x8]
    bd3c:      	subs	w2, w10, #0x1
    bd40:      	b.mi	0xbd90 <tcpci_alert+0x318>
    bd44:      	b	0xbd6c <tcpci_alert+0x2f4>
    bd48:      	mov	x0, x8
    bd4c:      	mov	w1, w10
    bd50:      	mov	w11, w1
    bd54:      	casal	w11, w2, [x8]
    bd58:      	mov	w0, w11
    bd5c:      	cmp	w10, w0
    bd60:      	mov	w10, w0
    bd64:      	b.eq	0xbd90 <tcpci_alert+0x318>
    bd68:      	b	0xbd3c <tcpci_alert+0x2c4>
    bd6c:      	mov	w11, w10
    bd70:      	prfm	pstl1strm, [x8]
    bd74:      	ldxr	w0, [x8]
    bd78:      	eor	w12, w0, w11
    bd7c:      	cbnz	w12, 0xbd8c <tcpci_alert+0x314>
    bd80:      	stlxr	w12, w2, [x8]
    bd84:      	cbnz	w12, 0xbd74 <tcpci_alert+0x2fc>
    bd88:      	dmb	ish
    bd8c:      	b	0xbd5c <tcpci_alert+0x2e4>
    bd90:      	cmp	w9, #0x3
    bd94:      	b.ne	0xbdf0 <tcpci_alert+0x378>
    bd98:      	ldr	w9, [x8]
    bd9c:      	subs	w2, w9, #0x1
    bda0:      	b.mi	0xbdf0 <tcpci_alert+0x378>
    bda4:      	b	0xbdcc <tcpci_alert+0x354>
    bda8:      	mov	x0, x8
    bdac:      	mov	w1, w9
    bdb0:      	mov	w10, w1
    bdb4:      	casal	w10, w2, [x8]
    bdb8:      	mov	w0, w10
    bdbc:      	cmp	w9, w0
    bdc0:      	mov	w9, w0
    bdc4:      	b.eq	0xbdf0 <tcpci_alert+0x378>
    bdc8:      	b	0xbd9c <tcpci_alert+0x324>
    bdcc:      	mov	w10, w9
    bdd0:      	prfm	pstl1strm, [x8]
    bdd4:      	ldxr	w0, [x8]
    bdd8:      	eor	w11, w0, w10
    bddc:      	cbnz	w11, 0xbdec <tcpci_alert+0x374>
    bde0:      	stlxr	w11, w2, [x8]
    bde4:      	cbnz	w11, 0xbdd4 <tcpci_alert+0x35c>
    bde8:      	dmb	ish
    bdec:      	b	0xbdbc <tcpci_alert+0x344>
    bdf0:      	ldr	w8, [x19, #0x3470]
    bdf4:      	cbnz	w8, 0xbe10 <tcpci_alert+0x398>
    bdf8:      	mov	w8, #0x3458
    bdfc:      	mov	w1, #0x3
    be00:      	add	x0, x19, x8
    be04:      	mov	w2, #0x1
    be08:      	mov	x3, xzr
    be0c:      	bl	0xbe0c <tcpci_alert+0x394>
		000000000000be0c:  R_AARCH64_CALL26	__wake_up
    be10:      	mov	w8, #0x2c8c
    be14:      	ldrb	w9, [x19, x8]
    be18:      	ldr	w8, [sp, #0x4]
    be1c:      	tbz	w9, #0x7, 0xbe2c <tcpci_alert+0x3b4>
    be20:      	tbz	w8, #0x11, 0xbe2c <tcpci_alert+0x3b4>
    be24:      	orr	w8, w8, #0x2
    be28:      	str	w8, [sp, #0x4]
    be2c:      	tbnz	w8, #0xf, 0xbe44 <tcpci_alert+0x3cc>
    be30:      	tbnz	w8, #0x4, 0xbe54 <tcpci_alert+0x3dc>
    be34:      	tbnz	w8, #0x5, 0xbeb4 <tcpci_alert+0x43c>
    be38:      	tbnz	w8, #0x6, 0xbec4 <tcpci_alert+0x44c>
    be3c:      	tbnz	w8, #0x2, 0xbf44 <tcpci_alert+0x4cc>
    be40:      	b	0xbf5c <tcpci_alert+0x4e4>
    be44:      	mov	x0, x19
    be48:      	bl	0xbe48 <tcpci_alert+0x3d0>
		000000000000be48:  R_AARCH64_CALL26	tcpci_alert_vendor_defined_handler
    be4c:      	ldr	w8, [sp, #0x4]
    be50:      	tbz	w8, #0x4, 0xbe34 <tcpci_alert+0x3bc>
    be54:      	mov	x0, x21
    be58:      	bl	0xbe58 <tcpci_alert+0x3e0>
		000000000000be58:  R_AARCH64_CALL26	mutex_lock
    be5c:      	mov	w8, #0x1
    be60:      	mov	x0, x21
    be64:      	ldrb	w23, [x25, #0x385]
    be68:      	str	xzr, [x19, #0x2c98]
    be6c:      	strb	w8, [x25, #0x385]
    be70:      	bl	0xbe70 <tcpci_alert+0x3f8>
		000000000000be70:  R_AARCH64_CALL26	mutex_unlock
    be74:      	mov	w8, #0x705
    be78:      	cmp	w23, #0x5
    be7c:      	b.ne	0xbe98 <tcpci_alert+0x420>
    be80:      	add	x1, sp, #0x8
    be84:      	mov	x0, x19
    be88:      	mov	w2, wzr
    be8c:      	stp	x8, xzr, [sp, #0x8]
    be90:      	bl	0xbe90 <tcpci_alert+0x418>
		000000000000be90:  R_AARCH64_CALL26	pd_put_vdm_event
    be94:      	b	0xbeac <tcpci_alert+0x434>
    be98:      	add	x1, sp, #0x8
    be9c:      	mov	x0, x19
    bea0:      	mov	w2, wzr
    bea4:      	stp	x8, xzr, [sp, #0x8]
    bea8:      	bl	0xbea8 <tcpci_alert+0x430>
		000000000000bea8:  R_AARCH64_CALL26	pd_put_event
    beac:      	ldr	w8, [sp, #0x4]
    beb0:      	tbz	w8, #0x5, 0xbe38 <tcpci_alert+0x3c0>
    beb4:      	mov	x0, x19
    beb8:      	bl	0xc400 <tcpci_alert_tx_discard>
    bebc:      	ldr	w8, [sp, #0x4]
    bec0:      	tbz	w8, #0x6, 0xbe3c <tcpci_alert+0x3c4>
    bec4:      	adrp	x8, 0xb000 <tcpci_enter_mode+0x78>
		000000000000bec4:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.cst16+0x40
    bec8:      	add	x8, x8, #0x0
		000000000000bec8:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.cst16+0x40
    becc:      	mov	x0, x21
    bed0:      	ldp	x9, x8, [x8]
    bed4:      	stp	x9, x8, [sp, #0x8]
    bed8:      	bl	0xbed8 <tcpci_alert+0x460>
		000000000000bed8:  R_AARCH64_CALL26	mutex_lock
    bedc:      	bl	0xbedc <tcpci_alert+0x464>
		000000000000bedc:  R_AARCH64_CALL26	sched_clock
    bee0:      	ldr	x8, [x19, #0x2c90]
    bee4:      	mov	x9, #0xf7cf
    bee8:      	movk	x9, #0xe353, lsl #16
    beec:      	ldrb	w23, [x25, #0x385]
    bef0:      	movk	x9, #0x9ba5, lsl #32
    bef4:      	strb	wzr, [x25, #0x385]
    bef8:      	sub	x8, x0, x8
    befc:      	movk	x9, #0x20c4, lsl #48
    bf00:      	lsr	x8, x8, #3
    bf04:      	mov	x0, x21
    bf08:      	umulh	x8, x8, x9
    bf0c:      	lsr	x8, x8, #4
    bf10:      	str	x8, [x19, #0x2c98]
    bf14:      	bl	0xbf14 <tcpci_alert+0x49c>
		000000000000bf14:  R_AARCH64_CALL26	mutex_unlock
    bf18:      	add	x1, sp, #0x8
    bf1c:      	mov	x0, x19
    bf20:      	cmp	w23, #0x5
    bf24:      	b.ne	0xbf34 <tcpci_alert+0x4bc>
    bf28:      	mov	w2, wzr
    bf2c:      	bl	0xbf2c <tcpci_alert+0x4b4>
		000000000000bf2c:  R_AARCH64_CALL26	pd_put_vdm_event
    bf30:      	b	0xbf3c <tcpci_alert+0x4c4>
    bf34:      	mov	w2, wzr
    bf38:      	bl	0xbf38 <tcpci_alert+0x4c0>
		000000000000bf38:  R_AARCH64_CALL26	pd_put_event
    bf3c:      	ldr	w8, [sp, #0x4]
    bf40:      	tbz	w8, #0x2, 0xbf5c <tcpci_alert+0x4e4>
    bf44:      	ldr	x1, [x19, #0x2f00]
    bf48:      	cbz	x1, 0xbf5c <tcpci_alert+0x4e4>
    bf4c:      	mov	x0, x19
    bf50:      	bl	0xbf50 <tcpci_alert+0x4d8>
		000000000000bf50:  R_AARCH64_CALL26	pd_put_pd_msg_event
    bf54:      	ldr	w8, [sp, #0x4]
    bf58:      	str	xzr, [x19, #0x2f00]
    bf5c:      	tbnz	w8, #0x3, 0xbf74 <tcpci_alert+0x4fc>
    bf60:      	tbnz	w8, #0x9, 0xbfc0 <tcpci_alert+0x548>
    bf64:      	tbnz	w8, #0x0, 0xbff4 <tcpci_alert+0x57c>
    bf68:      	tbnz	w8, #0x1, 0xc004 <tcpci_alert+0x58c>
    bf6c:      	tbnz	w8, #0x10, 0xc014 <tcpci_alert+0x59c>
    bf70:      	b	0xc060 <tcpci_alert+0x5e8>
    bf74:      	mov	w8, #0x3488
    bf78:      	add	x0, x19, x8
    bf7c:      	bl	0xbf7c <tcpci_alert+0x504>
		000000000000bf7c:  R_AARCH64_CALL26	cancel_delayed_work_sync
    bf80:      	mov	w8, #0x3458
    bf84:      	mov	w1, #0x3
    bf88:      	add	x0, x19, x8
    bf8c:      	mov	w2, #0x1
    bf90:      	mov	x3, xzr
    bf94:      	str	wzr, [x19, #0x3470]
    bf98:      	bl	0xbf98 <tcpci_alert+0x520>
		000000000000bf98:  R_AARCH64_CALL26	__wake_up
    bf9c:      	adrp	x0, 0xb000 <tcpci_enter_mode+0x78>
		000000000000bf9c:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x18d0
    bfa0:      	add	x0, x0, #0x0
		000000000000bfa0:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x18d0
    bfa4:      	bl	0xbfa4 <tcpci_alert+0x52c>
		000000000000bfa4:  R_AARCH64_CALL26	pd_dbg_info
    bfa8:      	mov	x0, x19
    bfac:      	bl	0xbfac <tcpci_alert+0x534>
		000000000000bfac:  R_AARCH64_CALL26	pd_put_recv_hard_reset_event
    bfb0:      	mov	x0, x19
    bfb4:      	bl	0xbfb4 <tcpci_alert+0x53c>
		000000000000bfb4:  R_AARCH64_CALL26	tcpci_init_alert_mask
    bfb8:      	ldr	w8, [sp, #0x4]
    bfbc:      	tbz	w8, #0x9, 0xbf64 <tcpci_alert+0x4ec>
    bfc0:      	add	x1, sp, #0x8
    bfc4:      	mov	x0, x19
    bfc8:      	strb	wzr, [sp, #0x8]
    bfcc:      	bl	0xbfcc <tcpci_alert+0x554>
		000000000000bfcc:  R_AARCH64_CALL26	tcpci_get_fault_status
    bfd0:      	ldrb	w1, [sp, #0x8]
    bfd4:      	adrp	x0, 0xb000 <tcpci_enter_mode+0x78>
		000000000000bfd4:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x29fd
    bfd8:      	add	x0, x0, #0x0
		000000000000bfd8:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x29fd
    bfdc:      	bl	0xbfdc <tcpci_alert+0x564>
		000000000000bfdc:  R_AARCH64_CALL26	pd_dbg_info
    bfe0:      	ldrb	w1, [sp, #0x8]
    bfe4:      	mov	x0, x19
    bfe8:      	bl	0xbfe8 <tcpci_alert+0x570>
		000000000000bfe8:  R_AARCH64_CALL26	tcpci_fault_status_clear
    bfec:      	ldr	w8, [sp, #0x4]
    bff0:      	tbz	w8, #0x0, 0xbf68 <tcpci_alert+0x4f0>
    bff4:      	mov	x0, x19
    bff8:      	bl	0xbff8 <tcpci_alert+0x580>
		000000000000bff8:  R_AARCH64_CALL26	tcpc_typec_handle_cc_change
    bffc:      	ldr	w8, [sp, #0x4]
    c000:      	tbz	w8, #0x1, 0xbf6c <tcpci_alert+0x4f4>
    c004:      	mov	x0, x19
    c008:      	bl	0xc504 <tcpci_alert_power_status_changed>
    c00c:      	ldr	w8, [sp, #0x4]
    c010:      	tbz	w8, #0x10, 0xc060 <tcpci_alert+0x5e8>
    c014:      	ldrb	w9, [x25, #0xc]
    c018:      	cbz	w9, 0xc060 <tcpci_alert+0x5e8>
    c01c:      	ldr	x8, [x19]
    c020:      	ldr	x8, [x8, #0xa8]
    c024:      	cbz	x8, 0xc050 <tcpci_alert+0x5d8>
    c028:      	mov	x0, x19
    c02c:      	mov	w1, wzr
    c030:      	mov	w2, #0x3
    c034:      	ldur	w16, [x8, #-0x4]
    c038:      	movk	w17, #0xb3e5
    c03c:      	movk	w17, #0x1fef, lsl #16
    c040:      	cmp	w16, w17
    c044:      	b.eq	0xc04c <tcpci_alert+0x5d4>
    c048:      	brk	#0x8228
    c04c:      	blr	x8
    c050:      	mov	x0, x19
    c054:      	mov	w1, #0x1
    c058:      	bl	0xc058 <tcpci_alert+0x5e0>
		000000000000c058:  R_AARCH64_CALL26	tcpc_enable_lpm_timer
    c05c:      	ldr	w8, [sp, #0x4]
    c060:      	tbz	w8, #0x2, 0xc078 <tcpci_alert+0x600>
    c064:      	mov	w8, #0x3510
    c068:      	add	x0, x19, x8
    c06c:      	bl	0xc06c <tcpci_alert+0x5f4>
		000000000000c06c:  R_AARCH64_CALL26	mutex_unlock
    c070:      	mov	x0, x19
    c074:      	bl	0xc074 <tcpci_alert+0x5fc>
		000000000000c074:  R_AARCH64_CALL26	tcpc_event_thread_wake_up
    c078:      	tbz	w22, #0x0, 0xc094 <tcpci_alert+0x61c>
    c07c:      	ldrb	w8, [sp, #0x4]
    c080:      	tbnz	w8, #0x3, 0xc094 <tcpci_alert+0x61c>
    c084:      	ldr	w1, [sp]
    c088:      	mov	x0, x19
    c08c:      	bl	0xc08c <tcpci_alert+0x614>
		000000000000c08c:  R_AARCH64_CALL26	tcpci_set_alert_mask
    c090:      	mov	w20, w0
    c094:      	mov	w8, #0x2c8c
    c098:      	ldrb	w8, [x19, x8]
    c09c:      	tbnz	w8, #0x7, 0xbb8c <tcpci_alert+0x114>
    c0a0:      	mov	x0, x21
    c0a4:      	bl	0xc0a4 <tcpci_alert+0x62c>
		000000000000c0a4:  R_AARCH64_CALL26	mutex_lock
    c0a8:      	ldrb	w8, [x25, #0x8d1]
    c0ac:      	mov	w10, #0x1
    c0b0:      	ldrb	w9, [x25, #0x8cf]
    c0b4:      	ldrb	w12, [x25, #0x8d0]
    c0b8:      	cmp	w8, #0x0
    c0bc:      	cinc	w10, w10, ne
    c0c0:      	and	w9, w9, #0xfffffffc
    c0c4:      	orr	w11, w9, w10
    c0c8:      	strb	w11, [x25, #0x8cf]
    c0cc:      	cbz	w12, 0xc190 <tcpci_alert+0x718>
    c0d0:      	cbz	w8, 0xc18c <tcpci_alert+0x714>
    c0d4:      	and	w1, w10, #0xff
    c0d8:      	adrp	x0, 0xc000 <tcpci_alert+0x588>
		000000000000c0d8:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x37a0
    c0dc:      	add	x0, x0, #0x0
		000000000000c0dc:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x37a0
    c0e0:      	bl	0xc0e0 <tcpci_alert+0x668>
		000000000000c0e0:  R_AARCH64_CALL26	pd_dbg_info
    c0e4:      	b	0xc190 <tcpci_alert+0x718>
    c0e8:      	and	w8, w8, #0xffffffdf
    c0ec:      	adrp	x0, 0xc000 <tcpci_alert+0x588>
		000000000000c0ec:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0xd07
    c0f0:      	add	x0, x0, #0x0
		000000000000c0f0:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0xd07
    c0f4:      	str	w8, [sp, #0x4]
    c0f8:      	bl	0xc0f8 <tcpci_alert+0x680>
		000000000000c0f8:  R_AARCH64_CALL26	pd_dbg_info
    c0fc:      	mov	x0, x21
    c100:      	bl	0xc100 <tcpci_alert+0x688>
		000000000000c100:  R_AARCH64_CALL26	mutex_lock
    c104:      	mov	w8, #0x2
    c108:      	mov	x0, x21
    c10c:      	strb	w8, [x25, #0x385]
    c110:      	bl	0xc110 <tcpci_alert+0x698>
		000000000000c110:  R_AARCH64_CALL26	mutex_unlock
    c114:      	mov	w8, #0x705
    c118:      	add	x1, sp, #0x8
    c11c:      	mov	x0, x19
    c120:      	mov	w2, wzr
    c124:      	stp	x8, xzr, [sp, #0x8]
    c128:      	bl	0xc128 <tcpci_alert+0x6b0>
		000000000000c128:  R_AARCH64_CALL26	pd_put_event
    c12c:      	mov	w8, #0x3470
    c130:      	ldr	w9, [x19, #0x3470]
    c134:      	add	x8, x19, x8
    c138:      	subs	w2, w9, #0x1
    c13c:      	b.mi	0xbc94 <tcpci_alert+0x21c>
    c140:      	b	0xc168 <tcpci_alert+0x6f0>
    c144:      	mov	x0, x8
    c148:      	mov	w1, w9
    c14c:      	mov	w10, w1
    c150:      	casal	w10, w2, [x8]
    c154:      	mov	w0, w10
    c158:      	cmp	w9, w0
    c15c:      	mov	w9, w0
    c160:      	b.eq	0xbc94 <tcpci_alert+0x21c>
    c164:      	b	0xc138 <tcpci_alert+0x6c0>
    c168:      	mov	w10, w9
    c16c:      	prfm	pstl1strm, [x8]
    c170:      	ldxr	w0, [x8]
    c174:      	eor	w11, w0, w10
    c178:      	cbnz	w11, 0xc188 <tcpci_alert+0x710>
    c17c:      	stlxr	w11, w2, [x8]
    c180:      	cbnz	w11, 0xc170 <tcpci_alert+0x6f8>
    c184:      	dmb	ish
    c188:      	b	0xc158 <tcpci_alert+0x6e0>
    c18c:      	strb	w9, [x25, #0x8cf]
    c190:      	mov	x0, x21
    c194:      	bl	0xc194 <tcpci_alert+0x71c>
		000000000000c194:  R_AARCH64_CALL26	mutex_unlock
    c198:      	ldrb	w8, [x25, #0x8cf]
    c19c:      	eor	w9, w8, w26
    c1a0:      	tst	w9, #0x3
    c1a4:      	b.eq	0xbb8c <tcpci_alert+0x114>
    c1a8:      	and	w1, w8, #0x3
    c1ac:      	adrp	x0, 0xc000 <tcpci_alert+0x588>
		000000000000c1ac:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x32a0
    c1b0:      	add	x0, x0, #0x0
		000000000000c1b0:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x32a0
    c1b4:      	bl	0xc1b4 <tcpci_alert+0x73c>
		000000000000c1b4:  R_AARCH64_CALL26	pd_dbg_info
    c1b8:      	ldrb	w8, [x25, #0x8cf]
    c1bc:      	mov	x0, x19
    c1c0:      	and	w1, w8, #0x3
    c1c4:      	bl	0xc1c4 <tcpci_alert+0x74c>
		000000000000c1c4:  R_AARCH64_CALL26	tcpc_typec_handle_ps_change
    c1c8:      	mov	w20, w0
    c1cc:      	tbnz	w0, #0x1f, 0xbb8c <tcpci_alert+0x114>
    c1d0:      	mov	x0, x19
    c1d4:      	mov	w1, #0x1a
    c1d8:      	bl	0xc1d8 <tcpci_alert+0x760>
		000000000000c1d8:  R_AARCH64_CALL26	tcpc_enable_timer
    c1dc:      	ldrb	w8, [x25, #0x8cf]
    c1e0:      	tst	w8, #0x3
    c1e4:      	b.ne	0xbb8c <tcpci_alert+0x114>
    c1e8:      	mov	x0, x19
    c1ec:      	bl	0xc1ec <tcpci_alert+0x774>
		000000000000c1ec:  R_AARCH64_CALL26	tcpc_typec_handle_vsafe0v
    c1f0:      	mov	x0, x19
    c1f4:      	mov	w1, #0x18
    c1f8:      	bl	0xc1f8 <tcpci_alert+0x780>
		000000000000c1f8:  R_AARCH64_CALL26	tcpc_enable_timer
    c1fc:      	mov	w20, wzr
    c200:      	b	0xbb8c <tcpci_alert+0x114>
    c204:      	bl	0xc204 <tcpci_alert+0x78c>
		000000000000c204:  R_AARCH64_CALL26	__stack_chk_fail
