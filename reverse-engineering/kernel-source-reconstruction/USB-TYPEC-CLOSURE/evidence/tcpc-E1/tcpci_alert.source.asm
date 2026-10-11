source tcpci_alert section=.text address=0xba8c size=1948
    ba8c:      	paciasp
    ba90:      	sub	sp, sp, #0x70
    ba94:      	stp	x29, x30, [sp, #0x20]
    ba98:      	stp	x26, x25, [sp, #0x30]
    ba9c:      	stp	x24, x23, [sp, #0x40]
    baa0:      	stp	x22, x21, [sp, #0x50]
    baa4:      	stp	x20, x19, [sp, #0x60]
    baa8:      	add	x29, sp, #0x20
    baac:      	mrs	x8, SP_EL0
    bab0:      	mov	w9, #0x2c71
    bab4:      	ldr	x8, [x8, #0x638]
    bab8:      	add	x25, x0, x9
    babc:      	mov	x19, x0
    bac0:      	mov	w22, w1
    bac4:      	stur	x8, [x29, #-0x8]
    bac8:      	mov	w8, #0x2248
    bacc:      	add	x21, x0, x8
    bad0:      	ldrb	w23, [x25]
    bad4:      	mov	x0, x21
    bad8:      	ldrb	w26, [x25, #0x8cf]
    badc:      	str	xzr, [sp]
    bae0:      	bl	0xbae0 <tcpci_alert+0x54>
		000000000000bae0:  R_AARCH64_CALL26	mutex_lock
    bae4:      	ldrb	w24, [x25, #0x384]
    bae8:      	bl	0xbae8 <tcpci_alert+0x5c>
		000000000000bae8:  R_AARCH64_CALL26	sched_clock
    baec:      	str	x0, [x19, #0x2c90]
    baf0:      	mov	x0, x21
    baf4:      	bl	0xbaf4 <tcpci_alert+0x68>
		000000000000baf4:  R_AARCH64_CALL26	mutex_unlock
    baf8:      	add	x1, sp, #0x4
    bafc:      	mov	x2, sp
    bb00:      	mov	x0, x19
    bb04:      	bl	0xbb04 <tcpci_alert+0x78>
		000000000000bb04:  R_AARCH64_CALL26	tcpci_get_alert_status_and_mask
    bb08:      	mov	w20, w0
    bb0c:      	tbnz	w0, #0x1f, 0xbba4 <tcpci_alert+0x118>
    bb10:      	mov	w8, #0x3578
    bb14:      	adrp	x1, 0xb000 <tcpci_enter_mode+0x64>
		000000000000bb14:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x1cb2
    bb18:      	add	x1, x1, #0x0
		000000000000bb18:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x1cb2
    bb1c:      	add	x0, x19, x8
    bb20:      	bl	0xbb20 <tcpci_alert+0x94>
		000000000000bb20:  R_AARCH64_CALL26	___ratelimit
    bb24:      	cbz	w0, 0xbb70 <tcpci_alert+0xe4>
    bb28:      	mov	x0, x19
    bb2c:      	mov	w1, wzr
    bb30:      	bl	0xbb30 <tcpci_alert+0xa4>
		000000000000bb30:  R_AARCH64_CALL26	tcpci_notify_alert_ratelimited
    bb34:      	ldp	w2, w1, [sp]
    bb38:      	adrp	x0, 0xb000 <tcpci_enter_mode+0x64>
		000000000000bb38:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x2f01
    bb3c:      	add	x0, x0, #0x0
		000000000000bb3c:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x2f01
    bb40:      	bl	0xbb40 <tcpci_alert+0xb4>
		000000000000bb40:  R_AARCH64_CALL26	pd_dbg_info
    bb44:      	ldp	w8, w9, [sp]
    bb48:      	and	w1, w9, w8
    bb4c:      	sub	w8, w23, #0x6
    bb50:      	cmn	w8, #0x6
    bb54:      	str	w1, [sp, #0x4]
    bb58:      	b.hi	0xbbdc <tcpci_alert+0x150>
    bb5c:      	adrp	x0, 0xb000 <tcpci_enter_mode+0x64>
		000000000000bb5c:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x32bc
    bb60:      	add	x0, x0, #0x0
		000000000000bb60:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x32bc
    bb64:      	mov	w1, w23
    bb68:      	bl	0xbb68 <tcpci_alert+0xdc>
		000000000000bb68:  R_AARCH64_CALL26	pd_dbg_info
    bb6c:      	b	0xbb94 <tcpci_alert+0x108>
    bb70:      	mov	x0, x19
    bb74:      	mov	w1, #0x1
    bb78:      	bl	0xbb78 <tcpci_alert+0xec>
		000000000000bb78:  R_AARCH64_CALL26	tcpci_notify_alert_ratelimited
    bb7c:      	ldp	w8, w9, [sp]
    bb80:      	and	w1, w9, w8
    bb84:      	str	w1, [sp, #0x4]
    bb88:      	tbz	w1, #0xf, 0xbb98 <tcpci_alert+0x10c>
    bb8c:      	mov	x0, x19
    bb90:      	bl	0xbb90 <tcpci_alert+0x104>
		000000000000bb90:  R_AARCH64_CALL26	tcpci_alert_vendor_defined_handler
    bb94:      	ldr	w1, [sp, #0x4]
    bb98:      	mov	x0, x19
    bb9c:      	bl	0xbb9c <tcpci_alert+0x110>
		000000000000bb9c:  R_AARCH64_CALL26	tcpci_alert_status_clear
    bba0:      	mov	w20, w0
    bba4:      	mrs	x8, SP_EL0
    bba8:      	ldr	x8, [x8, #0x638]
    bbac:      	ldur	x9, [x29, #-0x8]
    bbb0:      	cmp	x8, x9
    bbb4:      	b.ne	0xc224 <tcpci_alert+0x798>
    bbb8:      	mov	w0, w20
    bbbc:      	ldp	x20, x19, [sp, #0x60]
    bbc0:      	ldp	x22, x21, [sp, #0x50]
    bbc4:      	ldp	x24, x23, [sp, #0x40]
    bbc8:      	ldp	x26, x25, [sp, #0x30]
    bbcc:      	ldp	x29, x30, [sp, #0x20]
    bbd0:      	add	sp, sp, #0x70
    bbd4:      	autiasp
    bbd8:      	ret
    bbdc:      	tbz	w22, #0x0, 0xbbf8 <tcpci_alert+0x16c>
    bbe0:      	mov	x0, x19
    bbe4:      	mov	w1, wzr
    bbe8:      	bl	0xbbe8 <tcpci_alert+0x15c>
		000000000000bbe8:  R_AARCH64_CALL26	tcpci_set_alert_mask
    bbec:      	ldr	w1, [sp, #0x4]
    bbf0:      	tbnz	w0, #0x1f, 0xbb98 <tcpci_alert+0x10c>
    bbf4:      	mov	w20, w0
    bbf8:      	tbnz	w1, #0x2, 0xbc3c <tcpci_alert+0x1b0>
    bbfc:      	ldr	w1, [sp, #0x4]
    bc00:      	mov	x0, x19
    bc04:      	bl	0xbc04 <tcpci_alert+0x178>
		000000000000bc04:  R_AARCH64_CALL26	tcpci_alert_status_clear
    bc08:      	ldrb	w8, [x25, #0x385]
    bc0c:      	cmp	w8, #0x7
    bc10:      	b.ne	0xbc98 <tcpci_alert+0x20c>
    bc14:      	ldr	w8, [sp, #0x4]
    bc18:      	mov	w9, #0x50
    bc1c:      	bics	wzr, w9, w8
    bc20:      	b.ne	0xbc94 <tcpci_alert+0x208>
    bc24:      	mov	w9, #-0x51
    bc28:      	mov	x0, x19
    bc2c:      	and	w8, w8, w9
    bc30:      	str	w8, [sp, #0x4]
    bc34:      	bl	0xbc34 <tcpci_alert+0x1a8>
		000000000000bc34:  R_AARCH64_CALL26	pd_put_sent_hard_reset_event
    bc38:      	b	0xc130 <tcpci_alert+0x6a4>
    bc3c:      	mov	w8, #0x3510
    bc40:      	add	x0, x19, x8
    bc44:      	bl	0xbc44 <tcpci_alert+0x1b8>
		000000000000bc44:  R_AARCH64_CALL26	mutex_lock
    bc48:      	ldrb	w8, [sp, #0x4]
    bc4c:      	tbnz	w8, #0x3, 0xbbfc <tcpci_alert+0x170>
    bc50:      	cbnz	w24, 0xbbfc <tcpci_alert+0x170>
    bc54:      	mov	x0, x19
    bc58:      	bl	0xbc58 <tcpci_alert+0x1cc>
		000000000000bc58:  R_AARCH64_CALL26	pd_alloc_msg
    bc5c:      	cbz	x0, 0xbbfc <tcpci_alert+0x170>
    bc60:      	mov	x23, x0
    bc64:      	add	x24, x0, #0x4
    bc68:      	add	x1, x0, #0x8
    bc6c:      	mov	x0, x19
    bc70:      	mov	x2, x24
    bc74:      	mov	x3, x23
    bc78:      	bl	0xbc78 <tcpci_alert+0x1ec>
		000000000000bc78:  R_AARCH64_CALL26	tcpci_get_message
    bc7c:      	mov	w1, w0
    bc80:      	tbnz	w0, #0x1f, 0xc208 <tcpci_alert+0x77c>
    bc84:      	ldrh	w8, [x24]
    bc88:      	cbz	w8, 0xc208 <tcpci_alert+0x77c>
    bc8c:      	str	x23, [x19, #0x2f00]
    bc90:      	b	0xbbfc <tcpci_alert+0x170>
    bc94:      	tbnz	w8, #0x5, 0xc0ec <tcpci_alert+0x660>
    bc98:      	ldr	w8, [sp, #0x4]
    bc9c:      	ands	w8, w8, #0x70
    bca0:      	b.eq	0xbdf4 <tcpci_alert+0x368>
    bca4:      	lsr	w9, w8, #1
    bca8:      	mov	w10, #0x3470
    bcac:      	and	w9, w9, #0x55555555
    bcb0:      	sub	w8, w8, w9
    bcb4:      	lsr	w9, w8, #2
    bcb8:      	and	w8, w8, #0x33333333
    bcbc:      	and	w9, w9, #0x33333333
    bcc0:      	add	w8, w8, w9
    bcc4:      	mov	w9, #0x1010101
    bcc8:      	add	w8, w8, w8, lsr #4
    bccc:      	and	w8, w8, #0xf0f0f0f
    bcd0:      	mul	w8, w8, w9
    bcd4:      	lsr	w9, w8, #24
    bcd8:      	add	x8, x19, x10
    bcdc:      	ldr	w10, [x19, #0x3470]
    bce0:      	subs	w2, w10, #0x1
    bce4:      	b.mi	0xbd34 <tcpci_alert+0x2a8>
    bce8:      	b	0xbd10 <tcpci_alert+0x284>
    bcec:      	mov	x0, x8
    bcf0:      	mov	w1, w10
    bcf4:      	mov	w11, w1
    bcf8:      	casal	w11, w2, [x8]
    bcfc:      	mov	w0, w11
    bd00:      	cmp	w10, w0
    bd04:      	mov	w10, w0
    bd08:      	b.eq	0xbd34 <tcpci_alert+0x2a8>
    bd0c:      	b	0xbce0 <tcpci_alert+0x254>
    bd10:      	mov	w11, w10
    bd14:      	prfm	pstl1strm, [x8]
    bd18:      	ldxr	w0, [x8]
    bd1c:      	eor	w12, w0, w11
    bd20:      	cbnz	w12, 0xbd30 <tcpci_alert+0x2a4>
    bd24:      	stlxr	w12, w2, [x8]
    bd28:      	cbnz	w12, 0xbd18 <tcpci_alert+0x28c>
    bd2c:      	dmb	ish
    bd30:      	b	0xbd00 <tcpci_alert+0x274>
    bd34:      	cmp	w9, #0x2
    bd38:      	b.lo	0xbdf4 <tcpci_alert+0x368>
    bd3c:      	ldr	w10, [x8]
    bd40:      	subs	w2, w10, #0x1
    bd44:      	b.mi	0xbd94 <tcpci_alert+0x308>
    bd48:      	b	0xbd70 <tcpci_alert+0x2e4>
    bd4c:      	mov	x0, x8
    bd50:      	mov	w1, w10
    bd54:      	mov	w11, w1
    bd58:      	casal	w11, w2, [x8]
    bd5c:      	mov	w0, w11
    bd60:      	cmp	w10, w0
    bd64:      	mov	w10, w0
    bd68:      	b.eq	0xbd94 <tcpci_alert+0x308>
    bd6c:      	b	0xbd40 <tcpci_alert+0x2b4>
    bd70:      	mov	w11, w10
    bd74:      	prfm	pstl1strm, [x8]
    bd78:      	ldxr	w0, [x8]
    bd7c:      	eor	w12, w0, w11
    bd80:      	cbnz	w12, 0xbd90 <tcpci_alert+0x304>
    bd84:      	stlxr	w12, w2, [x8]
    bd88:      	cbnz	w12, 0xbd78 <tcpci_alert+0x2ec>
    bd8c:      	dmb	ish
    bd90:      	b	0xbd60 <tcpci_alert+0x2d4>
    bd94:      	cmp	w9, #0x3
    bd98:      	b.ne	0xbdf4 <tcpci_alert+0x368>
    bd9c:      	ldr	w9, [x8]
    bda0:      	subs	w2, w9, #0x1
    bda4:      	b.mi	0xbdf4 <tcpci_alert+0x368>
    bda8:      	b	0xbdd0 <tcpci_alert+0x344>
    bdac:      	mov	x0, x8
    bdb0:      	mov	w1, w9
    bdb4:      	mov	w10, w1
    bdb8:      	casal	w10, w2, [x8]
    bdbc:      	mov	w0, w10
    bdc0:      	cmp	w9, w0
    bdc4:      	mov	w9, w0
    bdc8:      	b.eq	0xbdf4 <tcpci_alert+0x368>
    bdcc:      	b	0xbda0 <tcpci_alert+0x314>
    bdd0:      	mov	w10, w9
    bdd4:      	prfm	pstl1strm, [x8]
    bdd8:      	ldxr	w0, [x8]
    bddc:      	eor	w11, w0, w10
    bde0:      	cbnz	w11, 0xbdf0 <tcpci_alert+0x364>
    bde4:      	stlxr	w11, w2, [x8]
    bde8:      	cbnz	w11, 0xbdd8 <tcpci_alert+0x34c>
    bdec:      	dmb	ish
    bdf0:      	b	0xbdc0 <tcpci_alert+0x334>
    bdf4:      	ldr	w8, [x19, #0x3470]
    bdf8:      	cbnz	w8, 0xbe14 <tcpci_alert+0x388>
    bdfc:      	mov	w8, #0x3458
    be00:      	mov	w1, #0x3
    be04:      	add	x0, x19, x8
    be08:      	mov	w2, #0x1
    be0c:      	mov	x3, xzr
    be10:      	bl	0xbe10 <tcpci_alert+0x384>
		000000000000be10:  R_AARCH64_CALL26	__wake_up
    be14:      	mov	w8, #0x2c8c
    be18:      	ldrb	w9, [x19, x8]
    be1c:      	ldr	w8, [sp, #0x4]
    be20:      	tbz	w9, #0x7, 0xbe30 <tcpci_alert+0x3a4>
    be24:      	tbz	w8, #0x11, 0xbe30 <tcpci_alert+0x3a4>
    be28:      	orr	w8, w8, #0x2
    be2c:      	str	w8, [sp, #0x4]
    be30:      	tbnz	w8, #0xf, 0xbe48 <tcpci_alert+0x3bc>
    be34:      	tbnz	w8, #0x4, 0xbe58 <tcpci_alert+0x3cc>
    be38:      	tbnz	w8, #0x5, 0xbeb8 <tcpci_alert+0x42c>
    be3c:      	tbnz	w8, #0x6, 0xbec8 <tcpci_alert+0x43c>
    be40:      	tbnz	w8, #0x2, 0xbf48 <tcpci_alert+0x4bc>
    be44:      	b	0xbf60 <tcpci_alert+0x4d4>
    be48:      	mov	x0, x19
    be4c:      	bl	0xbe4c <tcpci_alert+0x3c0>
		000000000000be4c:  R_AARCH64_CALL26	tcpci_alert_vendor_defined_handler
    be50:      	ldr	w8, [sp, #0x4]
    be54:      	tbz	w8, #0x4, 0xbe38 <tcpci_alert+0x3ac>
    be58:      	mov	x0, x21
    be5c:      	bl	0xbe5c <tcpci_alert+0x3d0>
		000000000000be5c:  R_AARCH64_CALL26	mutex_lock
    be60:      	mov	w8, #0x1
    be64:      	mov	x0, x21
    be68:      	ldrb	w23, [x25, #0x385]
    be6c:      	str	xzr, [x19, #0x2c98]
    be70:      	strb	w8, [x25, #0x385]
    be74:      	bl	0xbe74 <tcpci_alert+0x3e8>
		000000000000be74:  R_AARCH64_CALL26	mutex_unlock
    be78:      	mov	w8, #0x705
    be7c:      	cmp	w23, #0x5
    be80:      	b.ne	0xbe9c <tcpci_alert+0x410>
    be84:      	add	x1, sp, #0x8
    be88:      	mov	x0, x19
    be8c:      	mov	w2, wzr
    be90:      	stp	x8, xzr, [sp, #0x8]
    be94:      	bl	0xbe94 <tcpci_alert+0x408>
		000000000000be94:  R_AARCH64_CALL26	pd_put_vdm_event
    be98:      	b	0xbeb0 <tcpci_alert+0x424>
    be9c:      	add	x1, sp, #0x8
    bea0:      	mov	x0, x19
    bea4:      	mov	w2, wzr
    bea8:      	stp	x8, xzr, [sp, #0x8]
    beac:      	bl	0xbeac <tcpci_alert+0x420>
		000000000000beac:  R_AARCH64_CALL26	pd_put_event
    beb0:      	ldr	w8, [sp, #0x4]
    beb4:      	tbz	w8, #0x5, 0xbe3c <tcpci_alert+0x3b0>
    beb8:      	mov	x0, x19
    bebc:      	bl	0xc420 <tcpci_alert_tx_discard>
    bec0:      	ldr	w8, [sp, #0x4]
    bec4:      	tbz	w8, #0x6, 0xbe40 <tcpci_alert+0x3b4>
    bec8:      	adrp	x8, 0xb000 <tcpci_enter_mode+0x64>
		000000000000bec8:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.cst16+0x40
    becc:      	add	x8, x8, #0x0
		000000000000becc:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.cst16+0x40
    bed0:      	mov	x0, x21
    bed4:      	ldp	x9, x8, [x8]
    bed8:      	stp	x9, x8, [sp, #0x8]
    bedc:      	bl	0xbedc <tcpci_alert+0x450>
		000000000000bedc:  R_AARCH64_CALL26	mutex_lock
    bee0:      	bl	0xbee0 <tcpci_alert+0x454>
		000000000000bee0:  R_AARCH64_CALL26	sched_clock
    bee4:      	ldr	x8, [x19, #0x2c90]
    bee8:      	mov	x9, #0xf7cf
    beec:      	movk	x9, #0xe353, lsl #16
    bef0:      	ldrb	w23, [x25, #0x385]
    bef4:      	movk	x9, #0x9ba5, lsl #32
    bef8:      	strb	wzr, [x25, #0x385]
    befc:      	sub	x8, x0, x8
    bf00:      	movk	x9, #0x20c4, lsl #48
    bf04:      	lsr	x8, x8, #3
    bf08:      	mov	x0, x21
    bf0c:      	umulh	x8, x8, x9
    bf10:      	lsr	x8, x8, #4
    bf14:      	str	x8, [x19, #0x2c98]
    bf18:      	bl	0xbf18 <tcpci_alert+0x48c>
		000000000000bf18:  R_AARCH64_CALL26	mutex_unlock
    bf1c:      	add	x1, sp, #0x8
    bf20:      	mov	x0, x19
    bf24:      	cmp	w23, #0x5
    bf28:      	b.ne	0xbf38 <tcpci_alert+0x4ac>
    bf2c:      	mov	w2, wzr
    bf30:      	bl	0xbf30 <tcpci_alert+0x4a4>
		000000000000bf30:  R_AARCH64_CALL26	pd_put_vdm_event
    bf34:      	b	0xbf40 <tcpci_alert+0x4b4>
    bf38:      	mov	w2, wzr
    bf3c:      	bl	0xbf3c <tcpci_alert+0x4b0>
		000000000000bf3c:  R_AARCH64_CALL26	pd_put_event
    bf40:      	ldr	w8, [sp, #0x4]
    bf44:      	tbz	w8, #0x2, 0xbf60 <tcpci_alert+0x4d4>
    bf48:      	ldr	x1, [x19, #0x2f00]
    bf4c:      	cbz	x1, 0xbf60 <tcpci_alert+0x4d4>
    bf50:      	mov	x0, x19
    bf54:      	bl	0xbf54 <tcpci_alert+0x4c8>
		000000000000bf54:  R_AARCH64_CALL26	pd_put_pd_msg_event
    bf58:      	ldr	w8, [sp, #0x4]
    bf5c:      	str	xzr, [x19, #0x2f00]
    bf60:      	tbnz	w8, #0x3, 0xbf78 <tcpci_alert+0x4ec>
    bf64:      	tbnz	w8, #0x9, 0xbfc4 <tcpci_alert+0x538>
    bf68:      	tbnz	w8, #0x0, 0xbff8 <tcpci_alert+0x56c>
    bf6c:      	tbnz	w8, #0x1, 0xc008 <tcpci_alert+0x57c>
    bf70:      	tbnz	w8, #0x10, 0xc018 <tcpci_alert+0x58c>
    bf74:      	b	0xc064 <tcpci_alert+0x5d8>
    bf78:      	mov	w8, #0x3488
    bf7c:      	add	x0, x19, x8
    bf80:      	bl	0xbf80 <tcpci_alert+0x4f4>
		000000000000bf80:  R_AARCH64_CALL26	cancel_delayed_work_sync
    bf84:      	mov	w8, #0x3458
    bf88:      	mov	w1, #0x3
    bf8c:      	add	x0, x19, x8
    bf90:      	mov	w2, #0x1
    bf94:      	mov	x3, xzr
    bf98:      	str	wzr, [x19, #0x3470]
    bf9c:      	bl	0xbf9c <tcpci_alert+0x510>
		000000000000bf9c:  R_AARCH64_CALL26	__wake_up
    bfa0:      	adrp	x0, 0xb000 <tcpci_enter_mode+0x64>
		000000000000bfa0:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x18d3
    bfa4:      	add	x0, x0, #0x0
		000000000000bfa4:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x18d3
    bfa8:      	bl	0xbfa8 <tcpci_alert+0x51c>
		000000000000bfa8:  R_AARCH64_CALL26	pd_dbg_info
    bfac:      	mov	x0, x19
    bfb0:      	bl	0xbfb0 <tcpci_alert+0x524>
		000000000000bfb0:  R_AARCH64_CALL26	pd_put_recv_hard_reset_event
    bfb4:      	mov	x0, x19
    bfb8:      	bl	0xbfb8 <tcpci_alert+0x52c>
		000000000000bfb8:  R_AARCH64_CALL26	tcpci_init_alert_mask
    bfbc:      	ldr	w8, [sp, #0x4]
    bfc0:      	tbz	w8, #0x9, 0xbf68 <tcpci_alert+0x4dc>
    bfc4:      	add	x1, sp, #0x8
    bfc8:      	mov	x0, x19
    bfcc:      	strb	wzr, [sp, #0x8]
    bfd0:      	bl	0xbfd0 <tcpci_alert+0x544>
		000000000000bfd0:  R_AARCH64_CALL26	tcpci_get_fault_status
    bfd4:      	ldrb	w1, [sp, #0x8]
    bfd8:      	adrp	x0, 0xb000 <tcpci_enter_mode+0x64>
		000000000000bfd8:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x2a0a
    bfdc:      	add	x0, x0, #0x0
		000000000000bfdc:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x2a0a
    bfe0:      	bl	0xbfe0 <tcpci_alert+0x554>
		000000000000bfe0:  R_AARCH64_CALL26	pd_dbg_info
    bfe4:      	ldrb	w1, [sp, #0x8]
    bfe8:      	mov	x0, x19
    bfec:      	bl	0xbfec <tcpci_alert+0x560>
		000000000000bfec:  R_AARCH64_CALL26	tcpci_fault_status_clear
    bff0:      	ldr	w8, [sp, #0x4]
    bff4:      	tbz	w8, #0x0, 0xbf6c <tcpci_alert+0x4e0>
    bff8:      	mov	x0, x19
    bffc:      	bl	0xbffc <tcpci_alert+0x570>
		000000000000bffc:  R_AARCH64_CALL26	tcpc_typec_handle_cc_change
    c000:      	ldr	w8, [sp, #0x4]
    c004:      	tbz	w8, #0x1, 0xbf70 <tcpci_alert+0x4e4>
    c008:      	mov	x0, x19
    c00c:      	bl	0xc524 <tcpci_alert_power_status_changed>
    c010:      	ldr	w8, [sp, #0x4]
    c014:      	tbz	w8, #0x10, 0xc064 <tcpci_alert+0x5d8>
    c018:      	ldrb	w9, [x25, #0xc]
    c01c:      	cbz	w9, 0xc064 <tcpci_alert+0x5d8>
    c020:      	ldr	x8, [x19]
    c024:      	ldr	x8, [x8, #0xa8]
    c028:      	cbz	x8, 0xc054 <tcpci_alert+0x5c8>
    c02c:      	mov	x0, x19
    c030:      	mov	w1, wzr
    c034:      	mov	w2, #0x3
    c038:      	ldur	w16, [x8, #-0x4]
    c03c:      	movk	w17, #0xb3e5
    c040:      	movk	w17, #0x1fef, lsl #16
    c044:      	cmp	w16, w17
    c048:      	b.eq	0xc050 <tcpci_alert+0x5c4>
    c04c:      	brk	#0x8228
    c050:      	blr	x8
    c054:      	mov	x0, x19
    c058:      	mov	w1, #0x1
    c05c:      	bl	0xc05c <tcpci_alert+0x5d0>
		000000000000c05c:  R_AARCH64_CALL26	tcpc_enable_lpm_timer
    c060:      	ldr	w8, [sp, #0x4]
    c064:      	tbz	w8, #0x2, 0xc07c <tcpci_alert+0x5f0>
    c068:      	mov	w8, #0x3510
    c06c:      	add	x0, x19, x8
    c070:      	bl	0xc070 <tcpci_alert+0x5e4>
		000000000000c070:  R_AARCH64_CALL26	mutex_unlock
    c074:      	mov	x0, x19
    c078:      	bl	0xc078 <tcpci_alert+0x5ec>
		000000000000c078:  R_AARCH64_CALL26	tcpc_event_thread_wake_up
    c07c:      	tbz	w22, #0x0, 0xc098 <tcpci_alert+0x60c>
    c080:      	ldrb	w8, [sp, #0x4]
    c084:      	tbnz	w8, #0x3, 0xc098 <tcpci_alert+0x60c>
    c088:      	ldr	w1, [sp]
    c08c:      	mov	x0, x19
    c090:      	bl	0xc090 <tcpci_alert+0x604>
		000000000000c090:  R_AARCH64_CALL26	tcpci_set_alert_mask
    c094:      	mov	w20, w0
    c098:      	mov	w8, #0x2c8c
    c09c:      	ldrb	w8, [x19, x8]
    c0a0:      	tbnz	w8, #0x7, 0xbba4 <tcpci_alert+0x118>
    c0a4:      	mov	x0, x21
    c0a8:      	bl	0xc0a8 <tcpci_alert+0x61c>
		000000000000c0a8:  R_AARCH64_CALL26	mutex_lock
    c0ac:      	ldrb	w8, [x25, #0x8d1]
    c0b0:      	mov	w10, #0x1
    c0b4:      	ldrb	w9, [x25, #0x8cf]
    c0b8:      	ldrb	w12, [x25, #0x8d0]
    c0bc:      	cmp	w8, #0x0
    c0c0:      	cinc	w10, w10, ne
    c0c4:      	and	w9, w9, #0xfffffffc
    c0c8:      	orr	w11, w9, w10
    c0cc:      	strb	w11, [x25, #0x8cf]
    c0d0:      	cbz	w12, 0xc194 <tcpci_alert+0x708>
    c0d4:      	cbz	w8, 0xc190 <tcpci_alert+0x704>
    c0d8:      	and	w1, w10, #0xff
    c0dc:      	adrp	x0, 0xc000 <tcpci_alert+0x574>
		000000000000c0dc:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x381c
    c0e0:      	add	x0, x0, #0x0
		000000000000c0e0:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x381c
    c0e4:      	bl	0xc0e4 <tcpci_alert+0x658>
		000000000000c0e4:  R_AARCH64_CALL26	pd_dbg_info
    c0e8:      	b	0xc194 <tcpci_alert+0x708>
    c0ec:      	and	w8, w8, #0xffffffdf
    c0f0:      	adrp	x0, 0xc000 <tcpci_alert+0x574>
		000000000000c0f0:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0xc29
    c0f4:      	add	x0, x0, #0x0
		000000000000c0f4:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0xc29
    c0f8:      	str	w8, [sp, #0x4]
    c0fc:      	bl	0xc0fc <tcpci_alert+0x670>
		000000000000c0fc:  R_AARCH64_CALL26	pd_dbg_info
    c100:      	mov	x0, x21
    c104:      	bl	0xc104 <tcpci_alert+0x678>
		000000000000c104:  R_AARCH64_CALL26	mutex_lock
    c108:      	mov	w8, #0x2
    c10c:      	mov	x0, x21
    c110:      	strb	w8, [x25, #0x385]
    c114:      	bl	0xc114 <tcpci_alert+0x688>
		000000000000c114:  R_AARCH64_CALL26	mutex_unlock
    c118:      	mov	w8, #0x705
    c11c:      	add	x1, sp, #0x8
    c120:      	mov	x0, x19
    c124:      	mov	w2, wzr
    c128:      	stp	x8, xzr, [sp, #0x8]
    c12c:      	bl	0xc12c <tcpci_alert+0x6a0>
		000000000000c12c:  R_AARCH64_CALL26	pd_put_event
    c130:      	mov	w8, #0x3470
    c134:      	ldr	w9, [x19, #0x3470]
    c138:      	add	x8, x19, x8
    c13c:      	subs	w2, w9, #0x1
    c140:      	b.mi	0xbc98 <tcpci_alert+0x20c>
    c144:      	b	0xc16c <tcpci_alert+0x6e0>
    c148:      	mov	x0, x8
    c14c:      	mov	w1, w9
    c150:      	mov	w10, w1
    c154:      	casal	w10, w2, [x8]
    c158:      	mov	w0, w10
    c15c:      	cmp	w9, w0
    c160:      	mov	w9, w0
    c164:      	b.eq	0xbc98 <tcpci_alert+0x20c>
    c168:      	b	0xc13c <tcpci_alert+0x6b0>
    c16c:      	mov	w10, w9
    c170:      	prfm	pstl1strm, [x8]
    c174:      	ldxr	w0, [x8]
    c178:      	eor	w11, w0, w10
    c17c:      	cbnz	w11, 0xc18c <tcpci_alert+0x700>
    c180:      	stlxr	w11, w2, [x8]
    c184:      	cbnz	w11, 0xc174 <tcpci_alert+0x6e8>
    c188:      	dmb	ish
    c18c:      	b	0xc15c <tcpci_alert+0x6d0>
    c190:      	strb	w9, [x25, #0x8cf]
    c194:      	mov	x0, x21
    c198:      	bl	0xc198 <tcpci_alert+0x70c>
		000000000000c198:  R_AARCH64_CALL26	mutex_unlock
    c19c:      	ldrb	w8, [x25, #0x8cf]
    c1a0:      	eor	w9, w8, w26
    c1a4:      	tst	w9, #0x3
    c1a8:      	b.eq	0xbba4 <tcpci_alert+0x118>
    c1ac:      	and	w1, w8, #0x3
    c1b0:      	adrp	x0, 0xc000 <tcpci_alert+0x574>
		000000000000c1b0:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x331c
    c1b4:      	add	x0, x0, #0x0
		000000000000c1b4:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x331c
    c1b8:      	bl	0xc1b8 <tcpci_alert+0x72c>
		000000000000c1b8:  R_AARCH64_CALL26	pd_dbg_info
    c1bc:      	ldrb	w8, [x25, #0x8cf]
    c1c0:      	mov	x0, x19
    c1c4:      	and	w1, w8, #0x3
    c1c8:      	bl	0xc1c8 <tcpci_alert+0x73c>
		000000000000c1c8:  R_AARCH64_CALL26	tcpc_typec_handle_ps_change
    c1cc:      	mov	w20, w0
    c1d0:      	tbnz	w0, #0x1f, 0xbba4 <tcpci_alert+0x118>
    c1d4:      	mov	x0, x19
    c1d8:      	mov	w1, #0x1a
    c1dc:      	bl	0xc1dc <tcpci_alert+0x750>
		000000000000c1dc:  R_AARCH64_CALL26	tcpc_enable_timer
    c1e0:      	ldrb	w8, [x25, #0x8cf]
    c1e4:      	tst	w8, #0x3
    c1e8:      	b.ne	0xbba4 <tcpci_alert+0x118>
    c1ec:      	mov	x0, x19
    c1f0:      	bl	0xc1f0 <tcpci_alert+0x764>
		000000000000c1f0:  R_AARCH64_CALL26	tcpc_typec_handle_vsafe0v
    c1f4:      	mov	x0, x19
    c1f8:      	mov	w1, #0x18
    c1fc:      	bl	0xc1fc <tcpci_alert+0x770>
		000000000000c1fc:  R_AARCH64_CALL26	tcpc_enable_timer
    c200:      	mov	w20, wzr
    c204:      	b	0xbba4 <tcpci_alert+0x118>
    c208:      	adrp	x0, 0xc000 <tcpci_alert+0x574>
		000000000000c208:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x1cbe
    c20c:      	add	x0, x0, #0x0
		000000000000c20c:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x1cbe
    c210:      	bl	0xc210 <tcpci_alert+0x784>
		000000000000c210:  R_AARCH64_CALL26	pd_dbg_info
    c214:      	mov	x0, x19
    c218:      	mov	x1, x23
    c21c:      	bl	0xc21c <tcpci_alert+0x790>
		000000000000c21c:  R_AARCH64_CALL26	pd_free_msg
    c220:      	b	0xbbfc <tcpci_alert+0x170>
    c224:      	bl	0xc224 <tcpci_alert+0x798>
		000000000000c224:  R_AARCH64_CALL26	__stack_chk_fail
