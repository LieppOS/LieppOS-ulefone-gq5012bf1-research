source tcpci_alert section=.text address=0xbaac size=1948
    baac:      	paciasp
    bab0:      	sub	sp, sp, #0x70
    bab4:      	stp	x29, x30, [sp, #0x20]
    bab8:      	stp	x26, x25, [sp, #0x30]
    babc:      	stp	x24, x23, [sp, #0x40]
    bac0:      	stp	x22, x21, [sp, #0x50]
    bac4:      	stp	x20, x19, [sp, #0x60]
    bac8:      	add	x29, sp, #0x20
    bacc:      	mrs	x8, SP_EL0
    bad0:      	mov	w9, #0x2c71
    bad4:      	ldr	x8, [x8, #0x638]
    bad8:      	add	x25, x0, x9
    badc:      	mov	x19, x0
    bae0:      	mov	w22, w1
    bae4:      	stur	x8, [x29, #-0x8]
    bae8:      	mov	w8, #0x2248
    baec:      	add	x21, x0, x8
    baf0:      	ldrb	w23, [x25]
    baf4:      	mov	x0, x21
    baf8:      	ldrb	w26, [x25, #0x8cf]
    bafc:      	str	xzr, [sp]
    bb00:      	bl	0xbb00 <tcpci_alert+0x54>
		000000000000bb00:  R_AARCH64_CALL26	mutex_lock
    bb04:      	ldrb	w24, [x25, #0x384]
    bb08:      	bl	0xbb08 <tcpci_alert+0x5c>
		000000000000bb08:  R_AARCH64_CALL26	sched_clock
    bb0c:      	str	x0, [x19, #0x2c90]
    bb10:      	mov	x0, x21
    bb14:      	bl	0xbb14 <tcpci_alert+0x68>
		000000000000bb14:  R_AARCH64_CALL26	mutex_unlock
    bb18:      	add	x1, sp, #0x4
    bb1c:      	mov	x2, sp
    bb20:      	mov	x0, x19
    bb24:      	bl	0xbb24 <tcpci_alert+0x78>
		000000000000bb24:  R_AARCH64_CALL26	tcpci_get_alert_status_and_mask
    bb28:      	mov	w20, w0
    bb2c:      	tbnz	w0, #0x1f, 0xbbc4 <tcpci_alert+0x118>
    bb30:      	mov	w8, #0x3578
    bb34:      	adrp	x1, 0xb000 <tcpci_enter_mode+0x44>
		000000000000bb34:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x1cca
    bb38:      	add	x1, x1, #0x0
		000000000000bb38:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x1cca
    bb3c:      	add	x0, x19, x8
    bb40:      	bl	0xbb40 <tcpci_alert+0x94>
		000000000000bb40:  R_AARCH64_CALL26	___ratelimit
    bb44:      	cbz	w0, 0xbb90 <tcpci_alert+0xe4>
    bb48:      	mov	x0, x19
    bb4c:      	mov	w1, wzr
    bb50:      	bl	0xbb50 <tcpci_alert+0xa4>
		000000000000bb50:  R_AARCH64_CALL26	tcpci_notify_alert_ratelimited
    bb54:      	ldp	w2, w1, [sp]
    bb58:      	adrp	x0, 0xb000 <tcpci_enter_mode+0x44>
		000000000000bb58:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x2f2e
    bb5c:      	add	x0, x0, #0x0
		000000000000bb5c:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x2f2e
    bb60:      	bl	0xbb60 <tcpci_alert+0xb4>
		000000000000bb60:  R_AARCH64_CALL26	pd_dbg_info
    bb64:      	ldp	w8, w9, [sp]
    bb68:      	and	w1, w9, w8
    bb6c:      	sub	w8, w23, #0x6
    bb70:      	cmn	w8, #0x6
    bb74:      	str	w1, [sp, #0x4]
    bb78:      	b.hi	0xbbfc <tcpci_alert+0x150>
    bb7c:      	adrp	x0, 0xb000 <tcpci_enter_mode+0x44>
		000000000000bb7c:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x32e9
    bb80:      	add	x0, x0, #0x0
		000000000000bb80:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x32e9
    bb84:      	mov	w1, w23
    bb88:      	bl	0xbb88 <tcpci_alert+0xdc>
		000000000000bb88:  R_AARCH64_CALL26	pd_dbg_info
    bb8c:      	b	0xbbb4 <tcpci_alert+0x108>
    bb90:      	mov	x0, x19
    bb94:      	mov	w1, #0x1
    bb98:      	bl	0xbb98 <tcpci_alert+0xec>
		000000000000bb98:  R_AARCH64_CALL26	tcpci_notify_alert_ratelimited
    bb9c:      	ldp	w8, w9, [sp]
    bba0:      	and	w1, w9, w8
    bba4:      	str	w1, [sp, #0x4]
    bba8:      	tbz	w1, #0xf, 0xbbb8 <tcpci_alert+0x10c>
    bbac:      	mov	x0, x19
    bbb0:      	bl	0xbbb0 <tcpci_alert+0x104>
		000000000000bbb0:  R_AARCH64_CALL26	tcpci_alert_vendor_defined_handler
    bbb4:      	ldr	w1, [sp, #0x4]
    bbb8:      	mov	x0, x19
    bbbc:      	bl	0xbbbc <tcpci_alert+0x110>
		000000000000bbbc:  R_AARCH64_CALL26	tcpci_alert_status_clear
    bbc0:      	mov	w20, w0
    bbc4:      	mrs	x8, SP_EL0
    bbc8:      	ldr	x8, [x8, #0x638]
    bbcc:      	ldur	x9, [x29, #-0x8]
    bbd0:      	cmp	x8, x9
    bbd4:      	b.ne	0xc244 <tcpci_alert+0x798>
    bbd8:      	mov	w0, w20
    bbdc:      	ldp	x20, x19, [sp, #0x60]
    bbe0:      	ldp	x22, x21, [sp, #0x50]
    bbe4:      	ldp	x24, x23, [sp, #0x40]
    bbe8:      	ldp	x26, x25, [sp, #0x30]
    bbec:      	ldp	x29, x30, [sp, #0x20]
    bbf0:      	add	sp, sp, #0x70
    bbf4:      	autiasp
    bbf8:      	ret
    bbfc:      	tbz	w22, #0x0, 0xbc18 <tcpci_alert+0x16c>
    bc00:      	mov	x0, x19
    bc04:      	mov	w1, wzr
    bc08:      	bl	0xbc08 <tcpci_alert+0x15c>
		000000000000bc08:  R_AARCH64_CALL26	tcpci_set_alert_mask
    bc0c:      	ldr	w1, [sp, #0x4]
    bc10:      	tbnz	w0, #0x1f, 0xbbb8 <tcpci_alert+0x10c>
    bc14:      	mov	w20, w0
    bc18:      	tbnz	w1, #0x2, 0xbc5c <tcpci_alert+0x1b0>
    bc1c:      	ldr	w1, [sp, #0x4]
    bc20:      	mov	x0, x19
    bc24:      	bl	0xbc24 <tcpci_alert+0x178>
		000000000000bc24:  R_AARCH64_CALL26	tcpci_alert_status_clear
    bc28:      	ldrb	w8, [x25, #0x385]
    bc2c:      	cmp	w8, #0x7
    bc30:      	b.ne	0xbcb8 <tcpci_alert+0x20c>
    bc34:      	ldr	w8, [sp, #0x4]
    bc38:      	mov	w9, #0x50
    bc3c:      	bics	wzr, w9, w8
    bc40:      	b.ne	0xbcb4 <tcpci_alert+0x208>
    bc44:      	mov	w9, #-0x51
    bc48:      	mov	x0, x19
    bc4c:      	and	w8, w8, w9
    bc50:      	str	w8, [sp, #0x4]
    bc54:      	bl	0xbc54 <tcpci_alert+0x1a8>
		000000000000bc54:  R_AARCH64_CALL26	pd_put_sent_hard_reset_event
    bc58:      	b	0xc150 <tcpci_alert+0x6a4>
    bc5c:      	mov	w8, #0x3510
    bc60:      	add	x0, x19, x8
    bc64:      	bl	0xbc64 <tcpci_alert+0x1b8>
		000000000000bc64:  R_AARCH64_CALL26	mutex_lock
    bc68:      	ldrb	w8, [sp, #0x4]
    bc6c:      	tbnz	w8, #0x3, 0xbc1c <tcpci_alert+0x170>
    bc70:      	cbnz	w24, 0xbc1c <tcpci_alert+0x170>
    bc74:      	mov	x0, x19
    bc78:      	bl	0xbc78 <tcpci_alert+0x1cc>
		000000000000bc78:  R_AARCH64_CALL26	pd_alloc_msg
    bc7c:      	cbz	x0, 0xbc1c <tcpci_alert+0x170>
    bc80:      	mov	x23, x0
    bc84:      	add	x24, x0, #0x4
    bc88:      	add	x1, x0, #0x8
    bc8c:      	mov	x0, x19
    bc90:      	mov	x2, x24
    bc94:      	mov	x3, x23
    bc98:      	bl	0xbc98 <tcpci_alert+0x1ec>
		000000000000bc98:  R_AARCH64_CALL26	tcpci_get_message
    bc9c:      	mov	w1, w0
    bca0:      	tbnz	w0, #0x1f, 0xc228 <tcpci_alert+0x77c>
    bca4:      	ldrh	w8, [x24]
    bca8:      	cbz	w8, 0xc228 <tcpci_alert+0x77c>
    bcac:      	str	x23, [x19, #0x2f00]
    bcb0:      	b	0xbc1c <tcpci_alert+0x170>
    bcb4:      	tbnz	w8, #0x5, 0xc10c <tcpci_alert+0x660>
    bcb8:      	ldr	w8, [sp, #0x4]
    bcbc:      	ands	w8, w8, #0x70
    bcc0:      	b.eq	0xbe14 <tcpci_alert+0x368>
    bcc4:      	lsr	w9, w8, #1
    bcc8:      	mov	w10, #0x3470
    bccc:      	and	w9, w9, #0x55555555
    bcd0:      	sub	w8, w8, w9
    bcd4:      	lsr	w9, w8, #2
    bcd8:      	and	w8, w8, #0x33333333
    bcdc:      	and	w9, w9, #0x33333333
    bce0:      	add	w8, w8, w9
    bce4:      	mov	w9, #0x1010101
    bce8:      	add	w8, w8, w8, lsr #4
    bcec:      	and	w8, w8, #0xf0f0f0f
    bcf0:      	mul	w8, w8, w9
    bcf4:      	lsr	w9, w8, #24
    bcf8:      	add	x8, x19, x10
    bcfc:      	ldr	w10, [x19, #0x3470]
    bd00:      	subs	w2, w10, #0x1
    bd04:      	b.mi	0xbd54 <tcpci_alert+0x2a8>
    bd08:      	b	0xbd30 <tcpci_alert+0x284>
    bd0c:      	mov	x0, x8
    bd10:      	mov	w1, w10
    bd14:      	mov	w11, w1
    bd18:      	casal	w11, w2, [x8]
    bd1c:      	mov	w0, w11
    bd20:      	cmp	w10, w0
    bd24:      	mov	w10, w0
    bd28:      	b.eq	0xbd54 <tcpci_alert+0x2a8>
    bd2c:      	b	0xbd00 <tcpci_alert+0x254>
    bd30:      	mov	w11, w10
    bd34:      	prfm	pstl1strm, [x8]
    bd38:      	ldxr	w0, [x8]
    bd3c:      	eor	w12, w0, w11
    bd40:      	cbnz	w12, 0xbd50 <tcpci_alert+0x2a4>
    bd44:      	stlxr	w12, w2, [x8]
    bd48:      	cbnz	w12, 0xbd38 <tcpci_alert+0x28c>
    bd4c:      	dmb	ish
    bd50:      	b	0xbd20 <tcpci_alert+0x274>
    bd54:      	cmp	w9, #0x2
    bd58:      	b.lo	0xbe14 <tcpci_alert+0x368>
    bd5c:      	ldr	w10, [x8]
    bd60:      	subs	w2, w10, #0x1
    bd64:      	b.mi	0xbdb4 <tcpci_alert+0x308>
    bd68:      	b	0xbd90 <tcpci_alert+0x2e4>
    bd6c:      	mov	x0, x8
    bd70:      	mov	w1, w10
    bd74:      	mov	w11, w1
    bd78:      	casal	w11, w2, [x8]
    bd7c:      	mov	w0, w11
    bd80:      	cmp	w10, w0
    bd84:      	mov	w10, w0
    bd88:      	b.eq	0xbdb4 <tcpci_alert+0x308>
    bd8c:      	b	0xbd60 <tcpci_alert+0x2b4>
    bd90:      	mov	w11, w10
    bd94:      	prfm	pstl1strm, [x8]
    bd98:      	ldxr	w0, [x8]
    bd9c:      	eor	w12, w0, w11
    bda0:      	cbnz	w12, 0xbdb0 <tcpci_alert+0x304>
    bda4:      	stlxr	w12, w2, [x8]
    bda8:      	cbnz	w12, 0xbd98 <tcpci_alert+0x2ec>
    bdac:      	dmb	ish
    bdb0:      	b	0xbd80 <tcpci_alert+0x2d4>
    bdb4:      	cmp	w9, #0x3
    bdb8:      	b.ne	0xbe14 <tcpci_alert+0x368>
    bdbc:      	ldr	w9, [x8]
    bdc0:      	subs	w2, w9, #0x1
    bdc4:      	b.mi	0xbe14 <tcpci_alert+0x368>
    bdc8:      	b	0xbdf0 <tcpci_alert+0x344>
    bdcc:      	mov	x0, x8
    bdd0:      	mov	w1, w9
    bdd4:      	mov	w10, w1
    bdd8:      	casal	w10, w2, [x8]
    bddc:      	mov	w0, w10
    bde0:      	cmp	w9, w0
    bde4:      	mov	w9, w0
    bde8:      	b.eq	0xbe14 <tcpci_alert+0x368>
    bdec:      	b	0xbdc0 <tcpci_alert+0x314>
    bdf0:      	mov	w10, w9
    bdf4:      	prfm	pstl1strm, [x8]
    bdf8:      	ldxr	w0, [x8]
    bdfc:      	eor	w11, w0, w10
    be00:      	cbnz	w11, 0xbe10 <tcpci_alert+0x364>
    be04:      	stlxr	w11, w2, [x8]
    be08:      	cbnz	w11, 0xbdf8 <tcpci_alert+0x34c>
    be0c:      	dmb	ish
    be10:      	b	0xbde0 <tcpci_alert+0x334>
    be14:      	ldr	w8, [x19, #0x3470]
    be18:      	cbnz	w8, 0xbe34 <tcpci_alert+0x388>
    be1c:      	mov	w8, #0x3458
    be20:      	mov	w1, #0x3
    be24:      	add	x0, x19, x8
    be28:      	mov	w2, #0x1
    be2c:      	mov	x3, xzr
    be30:      	bl	0xbe30 <tcpci_alert+0x384>
		000000000000be30:  R_AARCH64_CALL26	__wake_up
    be34:      	mov	w8, #0x2c8c
    be38:      	ldrb	w9, [x19, x8]
    be3c:      	ldr	w8, [sp, #0x4]
    be40:      	tbz	w9, #0x7, 0xbe50 <tcpci_alert+0x3a4>
    be44:      	tbz	w8, #0x11, 0xbe50 <tcpci_alert+0x3a4>
    be48:      	orr	w8, w8, #0x2
    be4c:      	str	w8, [sp, #0x4]
    be50:      	tbnz	w8, #0xf, 0xbe68 <tcpci_alert+0x3bc>
    be54:      	tbnz	w8, #0x4, 0xbe78 <tcpci_alert+0x3cc>
    be58:      	tbnz	w8, #0x5, 0xbed8 <tcpci_alert+0x42c>
    be5c:      	tbnz	w8, #0x6, 0xbee8 <tcpci_alert+0x43c>
    be60:      	tbnz	w8, #0x2, 0xbf68 <tcpci_alert+0x4bc>
    be64:      	b	0xbf80 <tcpci_alert+0x4d4>
    be68:      	mov	x0, x19
    be6c:      	bl	0xbe6c <tcpci_alert+0x3c0>
		000000000000be6c:  R_AARCH64_CALL26	tcpci_alert_vendor_defined_handler
    be70:      	ldr	w8, [sp, #0x4]
    be74:      	tbz	w8, #0x4, 0xbe58 <tcpci_alert+0x3ac>
    be78:      	mov	x0, x21
    be7c:      	bl	0xbe7c <tcpci_alert+0x3d0>
		000000000000be7c:  R_AARCH64_CALL26	mutex_lock
    be80:      	mov	w8, #0x1
    be84:      	mov	x0, x21
    be88:      	ldrb	w23, [x25, #0x385]
    be8c:      	str	xzr, [x19, #0x2c98]
    be90:      	strb	w8, [x25, #0x385]
    be94:      	bl	0xbe94 <tcpci_alert+0x3e8>
		000000000000be94:  R_AARCH64_CALL26	mutex_unlock
    be98:      	mov	w8, #0x705
    be9c:      	cmp	w23, #0x5
    bea0:      	b.ne	0xbebc <tcpci_alert+0x410>
    bea4:      	add	x1, sp, #0x8
    bea8:      	mov	x0, x19
    beac:      	mov	w2, wzr
    beb0:      	stp	x8, xzr, [sp, #0x8]
    beb4:      	bl	0xbeb4 <tcpci_alert+0x408>
		000000000000beb4:  R_AARCH64_CALL26	pd_put_vdm_event
    beb8:      	b	0xbed0 <tcpci_alert+0x424>
    bebc:      	add	x1, sp, #0x8
    bec0:      	mov	x0, x19
    bec4:      	mov	w2, wzr
    bec8:      	stp	x8, xzr, [sp, #0x8]
    becc:      	bl	0xbecc <tcpci_alert+0x420>
		000000000000becc:  R_AARCH64_CALL26	pd_put_event
    bed0:      	ldr	w8, [sp, #0x4]
    bed4:      	tbz	w8, #0x5, 0xbe5c <tcpci_alert+0x3b0>
    bed8:      	mov	x0, x19
    bedc:      	bl	0xc440 <tcpci_alert_tx_discard>
    bee0:      	ldr	w8, [sp, #0x4]
    bee4:      	tbz	w8, #0x6, 0xbe60 <tcpci_alert+0x3b4>
    bee8:      	adrp	x8, 0xb000 <tcpci_enter_mode+0x44>
		000000000000bee8:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.cst16+0x40
    beec:      	add	x8, x8, #0x0
		000000000000beec:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.cst16+0x40
    bef0:      	mov	x0, x21
    bef4:      	ldp	x9, x8, [x8]
    bef8:      	stp	x9, x8, [sp, #0x8]
    befc:      	bl	0xbefc <tcpci_alert+0x450>
		000000000000befc:  R_AARCH64_CALL26	mutex_lock
    bf00:      	bl	0xbf00 <tcpci_alert+0x454>
		000000000000bf00:  R_AARCH64_CALL26	sched_clock
    bf04:      	ldr	x8, [x19, #0x2c90]
    bf08:      	mov	x9, #0xf7cf
    bf0c:      	movk	x9, #0xe353, lsl #16
    bf10:      	ldrb	w23, [x25, #0x385]
    bf14:      	movk	x9, #0x9ba5, lsl #32
    bf18:      	strb	wzr, [x25, #0x385]
    bf1c:      	sub	x8, x0, x8
    bf20:      	movk	x9, #0x20c4, lsl #48
    bf24:      	lsr	x8, x8, #3
    bf28:      	mov	x0, x21
    bf2c:      	umulh	x8, x8, x9
    bf30:      	lsr	x8, x8, #4
    bf34:      	str	x8, [x19, #0x2c98]
    bf38:      	bl	0xbf38 <tcpci_alert+0x48c>
		000000000000bf38:  R_AARCH64_CALL26	mutex_unlock
    bf3c:      	add	x1, sp, #0x8
    bf40:      	mov	x0, x19
    bf44:      	cmp	w23, #0x5
    bf48:      	b.ne	0xbf58 <tcpci_alert+0x4ac>
    bf4c:      	mov	w2, wzr
    bf50:      	bl	0xbf50 <tcpci_alert+0x4a4>
		000000000000bf50:  R_AARCH64_CALL26	pd_put_vdm_event
    bf54:      	b	0xbf60 <tcpci_alert+0x4b4>
    bf58:      	mov	w2, wzr
    bf5c:      	bl	0xbf5c <tcpci_alert+0x4b0>
		000000000000bf5c:  R_AARCH64_CALL26	pd_put_event
    bf60:      	ldr	w8, [sp, #0x4]
    bf64:      	tbz	w8, #0x2, 0xbf80 <tcpci_alert+0x4d4>
    bf68:      	ldr	x1, [x19, #0x2f00]
    bf6c:      	cbz	x1, 0xbf80 <tcpci_alert+0x4d4>
    bf70:      	mov	x0, x19
    bf74:      	bl	0xbf74 <tcpci_alert+0x4c8>
		000000000000bf74:  R_AARCH64_CALL26	pd_put_pd_msg_event
    bf78:      	ldr	w8, [sp, #0x4]
    bf7c:      	str	xzr, [x19, #0x2f00]
    bf80:      	tbnz	w8, #0x3, 0xbf98 <tcpci_alert+0x4ec>
    bf84:      	tbnz	w8, #0x9, 0xbfe4 <tcpci_alert+0x538>
    bf88:      	tbnz	w8, #0x0, 0xc018 <tcpci_alert+0x56c>
    bf8c:      	tbnz	w8, #0x1, 0xc028 <tcpci_alert+0x57c>
    bf90:      	tbnz	w8, #0x10, 0xc038 <tcpci_alert+0x58c>
    bf94:      	b	0xc084 <tcpci_alert+0x5d8>
    bf98:      	mov	w8, #0x3488
    bf9c:      	add	x0, x19, x8
    bfa0:      	bl	0xbfa0 <tcpci_alert+0x4f4>
		000000000000bfa0:  R_AARCH64_CALL26	cancel_delayed_work_sync
    bfa4:      	mov	w8, #0x3458
    bfa8:      	mov	w1, #0x3
    bfac:      	add	x0, x19, x8
    bfb0:      	mov	w2, #0x1
    bfb4:      	mov	x3, xzr
    bfb8:      	str	wzr, [x19, #0x3470]
    bfbc:      	bl	0xbfbc <tcpci_alert+0x510>
		000000000000bfbc:  R_AARCH64_CALL26	__wake_up
    bfc0:      	adrp	x0, 0xb000 <tcpci_enter_mode+0x44>
		000000000000bfc0:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x18eb
    bfc4:      	add	x0, x0, #0x0
		000000000000bfc4:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x18eb
    bfc8:      	bl	0xbfc8 <tcpci_alert+0x51c>
		000000000000bfc8:  R_AARCH64_CALL26	pd_dbg_info
    bfcc:      	mov	x0, x19
    bfd0:      	bl	0xbfd0 <tcpci_alert+0x524>
		000000000000bfd0:  R_AARCH64_CALL26	pd_put_recv_hard_reset_event
    bfd4:      	mov	x0, x19
    bfd8:      	bl	0xbfd8 <tcpci_alert+0x52c>
		000000000000bfd8:  R_AARCH64_CALL26	tcpci_init_alert_mask
    bfdc:      	ldr	w8, [sp, #0x4]
    bfe0:      	tbz	w8, #0x9, 0xbf88 <tcpci_alert+0x4dc>
    bfe4:      	add	x1, sp, #0x8
    bfe8:      	mov	x0, x19
    bfec:      	strb	wzr, [sp, #0x8]
    bff0:      	bl	0xbff0 <tcpci_alert+0x544>
		000000000000bff0:  R_AARCH64_CALL26	tcpci_get_fault_status
    bff4:      	ldrb	w1, [sp, #0x8]
    bff8:      	adrp	x0, 0xb000 <tcpci_enter_mode+0x44>
		000000000000bff8:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x2a22
    bffc:      	add	x0, x0, #0x0
		000000000000bffc:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x2a22
    c000:      	bl	0xc000 <tcpci_alert+0x554>
		000000000000c000:  R_AARCH64_CALL26	pd_dbg_info
    c004:      	ldrb	w1, [sp, #0x8]
    c008:      	mov	x0, x19
    c00c:      	bl	0xc00c <tcpci_alert+0x560>
		000000000000c00c:  R_AARCH64_CALL26	tcpci_fault_status_clear
    c010:      	ldr	w8, [sp, #0x4]
    c014:      	tbz	w8, #0x0, 0xbf8c <tcpci_alert+0x4e0>
    c018:      	mov	x0, x19
    c01c:      	bl	0xc01c <tcpci_alert+0x570>
		000000000000c01c:  R_AARCH64_CALL26	tcpc_typec_handle_cc_change
    c020:      	ldr	w8, [sp, #0x4]
    c024:      	tbz	w8, #0x1, 0xbf90 <tcpci_alert+0x4e4>
    c028:      	mov	x0, x19
    c02c:      	bl	0xc544 <tcpci_alert_power_status_changed>
    c030:      	ldr	w8, [sp, #0x4]
    c034:      	tbz	w8, #0x10, 0xc084 <tcpci_alert+0x5d8>
    c038:      	ldrb	w9, [x25, #0xc]
    c03c:      	cbz	w9, 0xc084 <tcpci_alert+0x5d8>
    c040:      	ldr	x8, [x19]
    c044:      	ldr	x8, [x8, #0xa8]
    c048:      	cbz	x8, 0xc074 <tcpci_alert+0x5c8>
    c04c:      	mov	x0, x19
    c050:      	mov	w1, wzr
    c054:      	mov	w2, #0x3
    c058:      	ldur	w16, [x8, #-0x4]
    c05c:      	movk	w17, #0xb3e5
    c060:      	movk	w17, #0x1fef, lsl #16
    c064:      	cmp	w16, w17
    c068:      	b.eq	0xc070 <tcpci_alert+0x5c4>
    c06c:      	brk	#0x8228
    c070:      	blr	x8
    c074:      	mov	x0, x19
    c078:      	mov	w1, #0x1
    c07c:      	bl	0xc07c <tcpci_alert+0x5d0>
		000000000000c07c:  R_AARCH64_CALL26	tcpc_enable_lpm_timer
    c080:      	ldr	w8, [sp, #0x4]
    c084:      	tbz	w8, #0x2, 0xc09c <tcpci_alert+0x5f0>
    c088:      	mov	w8, #0x3510
    c08c:      	add	x0, x19, x8
    c090:      	bl	0xc090 <tcpci_alert+0x5e4>
		000000000000c090:  R_AARCH64_CALL26	mutex_unlock
    c094:      	mov	x0, x19
    c098:      	bl	0xc098 <tcpci_alert+0x5ec>
		000000000000c098:  R_AARCH64_CALL26	tcpc_event_thread_wake_up
    c09c:      	tbz	w22, #0x0, 0xc0b8 <tcpci_alert+0x60c>
    c0a0:      	ldrb	w8, [sp, #0x4]
    c0a4:      	tbnz	w8, #0x3, 0xc0b8 <tcpci_alert+0x60c>
    c0a8:      	ldr	w1, [sp]
    c0ac:      	mov	x0, x19
    c0b0:      	bl	0xc0b0 <tcpci_alert+0x604>
		000000000000c0b0:  R_AARCH64_CALL26	tcpci_set_alert_mask
    c0b4:      	mov	w20, w0
    c0b8:      	mov	w8, #0x2c8c
    c0bc:      	ldrb	w8, [x19, x8]
    c0c0:      	tbnz	w8, #0x7, 0xbbc4 <tcpci_alert+0x118>
    c0c4:      	mov	x0, x21
    c0c8:      	bl	0xc0c8 <tcpci_alert+0x61c>
		000000000000c0c8:  R_AARCH64_CALL26	mutex_lock
    c0cc:      	ldrb	w8, [x25, #0x8d1]
    c0d0:      	mov	w10, #0x1
    c0d4:      	ldrb	w9, [x25, #0x8cf]
    c0d8:      	ldrb	w12, [x25, #0x8d0]
    c0dc:      	cmp	w8, #0x0
    c0e0:      	cinc	w10, w10, ne
    c0e4:      	and	w9, w9, #0xfffffffc
    c0e8:      	orr	w11, w9, w10
    c0ec:      	strb	w11, [x25, #0x8cf]
    c0f0:      	cbz	w12, 0xc1b4 <tcpci_alert+0x708>
    c0f4:      	cbz	w8, 0xc1b0 <tcpci_alert+0x704>
    c0f8:      	and	w1, w10, #0xff
    c0fc:      	adrp	x0, 0xc000 <tcpci_alert+0x554>
		000000000000c0fc:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x3849
    c100:      	add	x0, x0, #0x0
		000000000000c100:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x3849
    c104:      	bl	0xc104 <tcpci_alert+0x658>
		000000000000c104:  R_AARCH64_CALL26	pd_dbg_info
    c108:      	b	0xc1b4 <tcpci_alert+0x708>
    c10c:      	and	w8, w8, #0xffffffdf
    c110:      	adrp	x0, 0xc000 <tcpci_alert+0x554>
		000000000000c110:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0xc41
    c114:      	add	x0, x0, #0x0
		000000000000c114:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0xc41
    c118:      	str	w8, [sp, #0x4]
    c11c:      	bl	0xc11c <tcpci_alert+0x670>
		000000000000c11c:  R_AARCH64_CALL26	pd_dbg_info
    c120:      	mov	x0, x21
    c124:      	bl	0xc124 <tcpci_alert+0x678>
		000000000000c124:  R_AARCH64_CALL26	mutex_lock
    c128:      	mov	w8, #0x2
    c12c:      	mov	x0, x21
    c130:      	strb	w8, [x25, #0x385]
    c134:      	bl	0xc134 <tcpci_alert+0x688>
		000000000000c134:  R_AARCH64_CALL26	mutex_unlock
    c138:      	mov	w8, #0x705
    c13c:      	add	x1, sp, #0x8
    c140:      	mov	x0, x19
    c144:      	mov	w2, wzr
    c148:      	stp	x8, xzr, [sp, #0x8]
    c14c:      	bl	0xc14c <tcpci_alert+0x6a0>
		000000000000c14c:  R_AARCH64_CALL26	pd_put_event
    c150:      	mov	w8, #0x3470
    c154:      	ldr	w9, [x19, #0x3470]
    c158:      	add	x8, x19, x8
    c15c:      	subs	w2, w9, #0x1
    c160:      	b.mi	0xbcb8 <tcpci_alert+0x20c>
    c164:      	b	0xc18c <tcpci_alert+0x6e0>
    c168:      	mov	x0, x8
    c16c:      	mov	w1, w9
    c170:      	mov	w10, w1
    c174:      	casal	w10, w2, [x8]
    c178:      	mov	w0, w10
    c17c:      	cmp	w9, w0
    c180:      	mov	w9, w0
    c184:      	b.eq	0xbcb8 <tcpci_alert+0x20c>
    c188:      	b	0xc15c <tcpci_alert+0x6b0>
    c18c:      	mov	w10, w9
    c190:      	prfm	pstl1strm, [x8]
    c194:      	ldxr	w0, [x8]
    c198:      	eor	w11, w0, w10
    c19c:      	cbnz	w11, 0xc1ac <tcpci_alert+0x700>
    c1a0:      	stlxr	w11, w2, [x8]
    c1a4:      	cbnz	w11, 0xc194 <tcpci_alert+0x6e8>
    c1a8:      	dmb	ish
    c1ac:      	b	0xc17c <tcpci_alert+0x6d0>
    c1b0:      	strb	w9, [x25, #0x8cf]
    c1b4:      	mov	x0, x21
    c1b8:      	bl	0xc1b8 <tcpci_alert+0x70c>
		000000000000c1b8:  R_AARCH64_CALL26	mutex_unlock
    c1bc:      	ldrb	w8, [x25, #0x8cf]
    c1c0:      	eor	w9, w8, w26
    c1c4:      	tst	w9, #0x3
    c1c8:      	b.eq	0xbbc4 <tcpci_alert+0x118>
    c1cc:      	and	w1, w8, #0x3
    c1d0:      	adrp	x0, 0xc000 <tcpci_alert+0x554>
		000000000000c1d0:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x3349
    c1d4:      	add	x0, x0, #0x0
		000000000000c1d4:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x3349
    c1d8:      	bl	0xc1d8 <tcpci_alert+0x72c>
		000000000000c1d8:  R_AARCH64_CALL26	pd_dbg_info
    c1dc:      	ldrb	w8, [x25, #0x8cf]
    c1e0:      	mov	x0, x19
    c1e4:      	and	w1, w8, #0x3
    c1e8:      	bl	0xc1e8 <tcpci_alert+0x73c>
		000000000000c1e8:  R_AARCH64_CALL26	tcpc_typec_handle_ps_change
    c1ec:      	mov	w20, w0
    c1f0:      	tbnz	w0, #0x1f, 0xbbc4 <tcpci_alert+0x118>
    c1f4:      	mov	x0, x19
    c1f8:      	mov	w1, #0x1a
    c1fc:      	bl	0xc1fc <tcpci_alert+0x750>
		000000000000c1fc:  R_AARCH64_CALL26	tcpc_enable_timer
    c200:      	ldrb	w8, [x25, #0x8cf]
    c204:      	tst	w8, #0x3
    c208:      	b.ne	0xbbc4 <tcpci_alert+0x118>
    c20c:      	mov	x0, x19
    c210:      	bl	0xc210 <tcpci_alert+0x764>
		000000000000c210:  R_AARCH64_CALL26	tcpc_typec_handle_vsafe0v
    c214:      	mov	x0, x19
    c218:      	mov	w1, #0x18
    c21c:      	bl	0xc21c <tcpci_alert+0x770>
		000000000000c21c:  R_AARCH64_CALL26	tcpc_enable_timer
    c220:      	mov	w20, wzr
    c224:      	b	0xbbc4 <tcpci_alert+0x118>
    c228:      	adrp	x0, 0xc000 <tcpci_alert+0x554>
		000000000000c228:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x1cd6
    c22c:      	add	x0, x0, #0x0
		000000000000c22c:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x1cd6
    c230:      	bl	0xc230 <tcpci_alert+0x784>
		000000000000c230:  R_AARCH64_CALL26	pd_dbg_info
    c234:      	mov	x0, x19
    c238:      	mov	x1, x23
    c23c:      	bl	0xc23c <tcpci_alert+0x790>
		000000000000c23c:  R_AARCH64_CALL26	pd_free_msg
    c240:      	b	0xbc1c <tcpci_alert+0x170>
    c244:      	bl	0xc244 <tcpci_alert+0x798>
		000000000000c244:  R_AARCH64_CALL26	__stack_chk_fail
