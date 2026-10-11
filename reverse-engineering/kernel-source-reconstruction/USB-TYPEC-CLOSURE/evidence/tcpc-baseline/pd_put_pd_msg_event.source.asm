source pd_put_pd_msg_event section=.text address=0x11d30 size=808
   11d30:      	paciasp
   11d34:      	sub	sp, sp, #0x70
   11d38:      	stp	x29, x30, [sp, #0x20]
   11d3c:      	stp	x26, x25, [sp, #0x30]
   11d40:      	stp	x24, x23, [sp, #0x40]
   11d44:      	stp	x22, x21, [sp, #0x50]
   11d48:      	stp	x20, x19, [sp, #0x60]
   11d4c:      	add	x29, sp, #0x20
   11d50:      	mrs	x8, SP_EL0
   11d54:      	mov	w9, #0x2248
   11d58:      	ldr	x8, [x8, #0x638]
   11d5c:      	add	x19, x0, x9
   11d60:      	mov	x20, x0
   11d64:      	mov	x21, x1
   11d68:      	stur	x8, [x29, #-0x8]
   11d6c:      	mov	w8, #0x22dc
   11d70:      	ldrh	w25, [x1, #0x4]
   11d74:      	add	x24, x0, x8
   11d78:      	mov	x0, x19
   11d7c:      	stp	xzr, x1, [sp, #0x8]
   11d80:      	ubfx	w23, w25, #12, #3
   11d84:      	and	w22, w25, #0x1f
   11d88:      	bl	0x11d88 <pd_put_pd_msg_event+0x58>
		0000000000011d88:  R_AARCH64_CALL26	mutex_lock
   11d8c:      	ldrb	w26, [x24, #0xd1e]
   11d90:      	cbz	w26, 0x11e6c <pd_put_pd_msg_event+0x13c>
   11d94:      	strb	wzr, [x24, #0xd1e]
   11d98:      	cbnz	w23, 0x11e6c <pd_put_pd_msg_event+0x13c>
   11d9c:      	cmp	w22, #0x1
   11da0:      	b.ne	0x11e6c <pd_put_pd_msg_event+0x13c>
   11da4:      	adrp	x0, 0x11000 <pd_get_deferred_tcp_event+0x64>
		0000000000011da4:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x1eb8
   11da8:      	add	x0, x0, #0x0
		0000000000011da8:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x1eb8
   11dac:      	bl	0x11dac <pd_put_pd_msg_event+0x7c>
		0000000000011dac:  R_AARCH64_CALL26	pd_dbg_info
   11db0:      	cbz	x21, 0x11dec <pd_put_pd_msg_event+0xbc>
   11db4:      	sub	x8, x21, x20
   11db8:      	mov	x9, #-0x2ce0
   11dbc:      	add	x8, x8, x9
   11dc0:      	mov	w9, #0x8e39
   11dc4:      	lsr	x8, x8, #2
   11dc8:      	movk	w9, #0x38e3, lsl #16
   11dcc:      	mov	w10, #0x1
   11dd0:      	mul	w8, w8, w9
   11dd4:      	ldrb	w9, [x24, #0x9c6]
   11dd8:      	lsl	w8, w10, w8
   11ddc:      	tst	w8, w9
   11de0:      	b.eq	0x1200c <pd_put_pd_msg_event+0x2dc>
   11de4:      	bic	w8, w9, w8
   11de8:      	strb	w8, [x24, #0x9c6]
   11dec:      	mov	x0, x19
   11df0:      	bl	0x11df0 <pd_put_pd_msg_event+0xc0>
		0000000000011df0:  R_AARCH64_CALL26	mutex_unlock
   11df4:      	mov	x0, x20
   11df8:      	mov	w1, #0x1b
   11dfc:      	bl	0x11dfc <pd_put_pd_msg_event+0xcc>
		0000000000011dfc:  R_AARCH64_CALL26	tcpc_disable_timer
   11e00:      	mov	x0, x19
   11e04:      	bl	0x11e04 <pd_put_pd_msg_event+0xd4>
		0000000000011e04:  R_AARCH64_CALL26	mutex_lock
   11e08:      	ldrb	w8, [x24, #0x9c4]
   11e0c:      	cmp	w8, #0x10
   11e10:      	b.hs	0x11fbc <pd_put_pd_msg_event+0x28c>
   11e14:      	ldrb	w9, [x24, #0x9c5]
   11e18:      	mov	w10, #0x2e00
   11e1c:      	mov	w11, #0xa05
   11e20:      	add	w9, w9, w8
   11e24:      	add	w8, w8, #0x1
   11e28:      	and	x9, x9, #0xf
   11e2c:      	add	x9, x20, x9, lsl #4
   11e30:      	strb	w8, [x24, #0x9c4]
   11e34:      	add	x10, x9, x10
   11e38:      	str	xzr, [x9, #0x2e08]
   11e3c:      	strh	w11, [x10]
   11e40:      	stur	xzr, [x10, #0x2]
   11e44:      	b	0x12040 <pd_put_pd_msg_event+0x310>
   11e48:      	mov	w8, #0x1
   11e4c:      	stadd	w8, [x24]
   11e50:      	mov	w8, #0x22f0
   11e54:      	mov	w1, #0x3
   11e58:      	add	x0, x20, x8
   11e5c:      	mov	w2, #0x1
   11e60:      	mov	x3, xzr
   11e64:      	bl	0x11e64 <pd_put_pd_msg_event+0x134>
		0000000000011e64:  R_AARCH64_CALL26	__wake_up
   11e68:      	b	0x11fc8 <pd_put_pd_msg_event+0x298>
   11e6c:      	sxth	w25, w25
   11e70:      	cbz	w23, 0x11e88 <pd_put_pd_msg_event+0x158>
   11e74:      	cmp	w22, #0x3
   11e78:      	b.ne	0x11e88 <pd_put_pd_msg_event+0x158>
   11e7c:      	tbnz	w25, #0x1f, 0x11e88 <pd_put_pd_msg_event+0x158>
   11e80:      	mov	w8, #0x1
   11e84:      	strb	w8, [x24, #0xd19]
   11e88:      	mov	x0, x19
   11e8c:      	bl	0x11e8c <pd_put_pd_msg_event+0x15c>
		0000000000011e8c:  R_AARCH64_CALL26	mutex_unlock
   11e90:      	cbz	w26, 0x11f20 <pd_put_pd_msg_event+0x1f0>
   11e94:      	mov	x0, x20
   11e98:      	mov	w1, #0x1b
   11e9c:      	bl	0x11e9c <pd_put_pd_msg_event+0x16c>
		0000000000011e9c:  R_AARCH64_CALL26	tcpc_disable_timer
   11ea0:      	mov	x0, x19
   11ea4:      	bl	0x11ea4 <pd_put_pd_msg_event+0x174>
		0000000000011ea4:  R_AARCH64_CALL26	mutex_lock
   11ea8:      	ldrb	w8, [x24, #0x9c4]
   11eac:      	cmp	w8, #0x10
   11eb0:      	b.hs	0x11f0c <pd_put_pd_msg_event+0x1dc>
   11eb4:      	ldrb	w9, [x24, #0x9c5]
   11eb8:      	mov	w10, #0x2e00
   11ebc:      	mov	w11, #0x805
   11ec0:      	add	w9, w9, w8
   11ec4:      	add	w8, w8, #0x1
   11ec8:      	and	x9, x9, #0xf
   11ecc:      	add	x9, x20, x9, lsl #4
   11ed0:      	strb	w8, [x24, #0x9c4]
   11ed4:      	add	x10, x9, x10
   11ed8:      	str	xzr, [x9, #0x2e08]
   11edc:      	strh	w11, [x10]
   11ee0:      	stur	xzr, [x10, #0x2]
   11ee4:      	b	0x12028 <pd_put_pd_msg_event+0x2f8>
   11ee8:      	mov	w8, #0x1
   11eec:      	stadd	w8, [x24]
   11ef0:      	mov	w8, #0x22f0
   11ef4:      	mov	w1, #0x3
   11ef8:      	add	x0, x20, x8
   11efc:      	mov	w2, #0x1
   11f00:      	mov	x3, xzr
   11f04:      	bl	0x11f04 <pd_put_pd_msg_event+0x1d4>
		0000000000011f04:  R_AARCH64_CALL26	__wake_up
   11f08:      	b	0x11f18 <pd_put_pd_msg_event+0x1e8>
   11f0c:      	adrp	x0, 0x11000 <pd_get_deferred_tcp_event+0x64>
		0000000000011f0c:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x3503
   11f10:      	add	x0, x0, #0x0
		0000000000011f10:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x3503
   11f14:      	bl	0x11f14 <pd_put_pd_msg_event+0x1e4>
		0000000000011f14:  R_AARCH64_CALL26	pd_dbg_info
   11f18:      	mov	x0, x19
   11f1c:      	bl	0x11f1c <pd_put_pd_msg_event+0x1ec>
		0000000000011f1c:  R_AARCH64_CALL26	mutex_unlock
   11f20:      	cbz	w23, 0x11f48 <pd_put_pd_msg_event+0x218>
   11f24:      	cmp	w22, #0xf
   11f28:      	b.ne	0x11f48 <pd_put_pd_msg_event+0x218>
   11f2c:      	tbnz	w25, #0x1f, 0x11f48 <pd_put_pd_msg_event+0x218>
   11f30:      	add	x1, sp, #0x8
   11f34:      	mov	x0, x20
   11f38:      	mov	w2, #0x1
   11f3c:      	bl	0x11f3c <pd_put_pd_msg_event+0x20c>
		0000000000011f3c:  R_AARCH64_CALL26	pd_put_vdm_event
   11f40:      	mov	w22, w0
   11f44:      	b	0x11fd4 <pd_put_pd_msg_event+0x2a4>
   11f48:      	mov	x0, x19
   11f4c:      	bl	0x11f4c <pd_put_pd_msg_event+0x21c>
		0000000000011f4c:  R_AARCH64_CALL26	mutex_lock
   11f50:      	add	x1, sp, #0x8
   11f54:      	mov	x0, x20
   11f58:      	mov	w2, #0x1
   11f5c:      	mov	w22, #0x1
   11f60:      	bl	0x109c4 <__pd_put_event>
   11f64:      	mov	w23, w0
   11f68:      	mov	x0, x19
   11f6c:      	bl	0x11f6c <pd_put_pd_msg_event+0x23c>
		0000000000011f6c:  R_AARCH64_CALL26	mutex_unlock
   11f70:      	tbnz	w23, #0x0, 0x11fd4 <pd_put_pd_msg_event+0x2a4>
   11f74:      	mov	x0, x19
   11f78:      	bl	0x11f78 <pd_put_pd_msg_event+0x248>
		0000000000011f78:  R_AARCH64_CALL26	mutex_lock
   11f7c:      	cbz	x21, 0x11fc8 <pd_put_pd_msg_event+0x298>
   11f80:      	sub	x8, x21, x20
   11f84:      	mov	x9, #-0x2ce0
   11f88:      	add	x8, x8, x9
   11f8c:      	mov	w9, #0x8e39
   11f90:      	lsr	x8, x8, #2
   11f94:      	movk	w9, #0x38e3, lsl #16
   11f98:      	mov	w10, #0x1
   11f9c:      	mul	w8, w8, w9
   11fa0:      	ldrb	w9, [x24, #0x9c6]
   11fa4:      	lsl	w8, w10, w8
   11fa8:      	tst	w8, w9
   11fac:      	b.eq	0x12018 <pd_put_pd_msg_event+0x2e8>
   11fb0:      	bic	w8, w9, w8
   11fb4:      	strb	w8, [x24, #0x9c6]
   11fb8:      	b	0x11fc8 <pd_put_pd_msg_event+0x298>
   11fbc:      	adrp	x0, 0x11000 <pd_get_deferred_tcp_event+0x64>
		0000000000011fbc:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x3503
   11fc0:      	add	x0, x0, #0x0
		0000000000011fc0:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x3503
   11fc4:      	bl	0x11fc4 <pd_put_pd_msg_event+0x294>
		0000000000011fc4:  R_AARCH64_CALL26	pd_dbg_info
   11fc8:      	mov	x0, x19
   11fcc:      	bl	0x11fcc <pd_put_pd_msg_event+0x29c>
		0000000000011fcc:  R_AARCH64_CALL26	mutex_unlock
   11fd0:      	mov	w22, wzr
   11fd4:      	mrs	x8, SP_EL0
   11fd8:      	ldr	x8, [x8, #0x638]
   11fdc:      	ldur	x9, [x29, #-0x8]
   11fe0:      	cmp	x8, x9
   11fe4:      	b.ne	0x12024 <pd_put_pd_msg_event+0x2f4>
   11fe8:      	and	w0, w22, #0x1
   11fec:      	ldp	x20, x19, [sp, #0x60]
   11ff0:      	ldp	x22, x21, [sp, #0x50]
   11ff4:      	ldp	x24, x23, [sp, #0x40]
   11ff8:      	ldp	x26, x25, [sp, #0x30]
   11ffc:      	ldp	x29, x30, [sp, #0x20]
   12000:      	add	sp, sp, #0x70
   12004:      	autiasp
   12008:      	ret
   1200c:      	brk	#0x800
   12010:      	ldrb	w9, [x24, #0x9c6]
   12014:      	b	0x11de4 <pd_put_pd_msg_event+0xb4>
   12018:      	brk	#0x800
   1201c:      	ldrb	w9, [x24, #0x9c6]
   12020:      	b	0x11fb0 <pd_put_pd_msg_event+0x280>
   12024:      	bl	0x12024 <pd_put_pd_msg_event+0x2f4>
		0000000000012024:  R_AARCH64_CALL26	__stack_chk_fail
   12028:      	prfm	pstl1strm, [x24]
   1202c:      	ldxr	w8, [x24]
   12030:      	add	w8, w8, #0x1
   12034:      	stxr	w9, w8, [x24]
   12038:      	cbnz	w9, 0x1202c <pd_put_pd_msg_event+0x2fc>
   1203c:      	b	0x11ef0 <pd_put_pd_msg_event+0x1c0>
   12040:      	prfm	pstl1strm, [x24]
   12044:      	ldxr	w8, [x24]
   12048:      	add	w8, w8, #0x1
   1204c:      	stxr	w9, w8, [x24]
   12050:      	cbnz	w9, 0x12044 <pd_put_pd_msg_event+0x314>
   12054:      	b	0x11e50 <pd_put_pd_msg_event+0x120>
