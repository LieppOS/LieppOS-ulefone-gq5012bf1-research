source pd_put_pd_msg_event section=.text address=0x11cf0 size=812
   11cf0:      	paciasp
   11cf4:      	sub	sp, sp, #0x70
   11cf8:      	stp	x29, x30, [sp, #0x20]
   11cfc:      	stp	x26, x25, [sp, #0x30]
   11d00:      	stp	x24, x23, [sp, #0x40]
   11d04:      	stp	x22, x21, [sp, #0x50]
   11d08:      	stp	x20, x19, [sp, #0x60]
   11d0c:      	add	x29, sp, #0x20
   11d10:      	mrs	x8, SP_EL0
   11d14:      	mov	w9, #0x22dc
   11d18:      	ldr	x8, [x8, #0x638]
   11d1c:      	mov	x20, x0
   11d20:      	add	x24, x0, x9
   11d24:      	mov	x21, x1
   11d28:      	stur	x8, [x29, #-0x8]
   11d2c:      	mov	w8, #0x2248
   11d30:      	add	x19, x0, x8
   11d34:      	ldrh	w25, [x1, #0x4]
   11d38:      	mov	x0, x19
   11d3c:      	stp	xzr, x1, [sp, #0x8]
   11d40:      	bl	0x11d40 <pd_put_pd_msg_event+0x50>
		0000000000011d40:  R_AARCH64_CALL26	mutex_lock
   11d44:      	ldrb	w8, [x24, #0xd19]
   11d48:      	cbz	w8, 0x11d88 <pd_put_pd_msg_event+0x98>
   11d4c:      	cbz	x21, 0x11dec <pd_put_pd_msg_event+0xfc>
   11d50:      	sub	x8, x21, x20
   11d54:      	mov	x9, #-0x2ce0
   11d58:      	add	x8, x8, x9
   11d5c:      	mov	w9, #0x8e39
   11d60:      	lsr	x8, x8, #2
   11d64:      	movk	w9, #0x38e3, lsl #16
   11d68:      	mov	w10, #0x1
   11d6c:      	mul	w8, w8, w9
   11d70:      	ldrb	w9, [x24, #0x9c6]
   11d74:      	lsl	w8, w10, w8
   11d78:      	tst	w8, w9
   11d7c:      	b.ne	0x11de4 <pd_put_pd_msg_event+0xf4>
   11d80:      	brk	#0x800
   11d84:      	b	0x11fec <pd_put_pd_msg_event+0x2fc>
   11d88:      	ldrb	w8, [x24, #0xd1e]
   11d8c:      	ubfx	w23, w25, #12, #3
   11d90:      	and	w22, w25, #0x1f
   11d94:      	cbz	w8, 0x11da0 <pd_put_pd_msg_event+0xb0>
   11d98:      	ldr	w8, [x21]
   11d9c:      	cbz	w8, 0x11e8c <pd_put_pd_msg_event+0x19c>
   11da0:      	mov	w26, wzr
   11da4:      	cbnz	w23, 0x11e30 <pd_put_pd_msg_event+0x140>
   11da8:      	cmp	w22, #0x5
   11dac:      	b.ne	0x11e30 <pd_put_pd_msg_event+0x140>
   11db0:      	cbz	x21, 0x11dec <pd_put_pd_msg_event+0xfc>
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
   11de0:      	b.eq	0x11fe8 <pd_put_pd_msg_event+0x2f8>
   11de4:      	bic	w8, w9, w8
   11de8:      	strb	w8, [x24, #0x9c6]
   11dec:      	mov	x0, x19
   11df0:      	bl	0x11df0 <pd_put_pd_msg_event+0x100>
		0000000000011df0:  R_AARCH64_CALL26	mutex_unlock
   11df4:      	mov	w22, wzr
   11df8:      	mrs	x8, SP_EL0
   11dfc:      	ldr	x8, [x8, #0x638]
   11e00:      	ldur	x9, [x29, #-0x8]
   11e04:      	cmp	x8, x9
   11e08:      	b.ne	0x12000 <pd_put_pd_msg_event+0x310>
   11e0c:      	and	w0, w22, #0x1
   11e10:      	ldp	x20, x19, [sp, #0x60]
   11e14:      	ldp	x22, x21, [sp, #0x50]
   11e18:      	ldp	x24, x23, [sp, #0x40]
   11e1c:      	ldp	x26, x25, [sp, #0x30]
   11e20:      	ldp	x29, x30, [sp, #0x20]
   11e24:      	add	sp, sp, #0x70
   11e28:      	autiasp
   11e2c:      	ret
   11e30:      	sxth	w25, w25
   11e34:      	cbz	w23, 0x11e4c <pd_put_pd_msg_event+0x15c>
   11e38:      	cmp	w22, #0x3
   11e3c:      	b.ne	0x11e4c <pd_put_pd_msg_event+0x15c>
   11e40:      	tbnz	w25, #0x1f, 0x11e4c <pd_put_pd_msg_event+0x15c>
   11e44:      	mov	w8, #0x1
   11e48:      	strb	w8, [x24, #0xd19]
   11e4c:      	mov	x0, x19
   11e50:      	bl	0x11e50 <pd_put_pd_msg_event+0x160>
		0000000000011e50:  R_AARCH64_CALL26	mutex_unlock
   11e54:      	cbz	w26, 0x11e64 <pd_put_pd_msg_event+0x174>
   11e58:      	mov	x0, x20
   11e5c:      	mov	w1, #0x1b
   11e60:      	bl	0x11e60 <pd_put_pd_msg_event+0x170>
		0000000000011e60:  R_AARCH64_CALL26	tcpc_disable_timer
   11e64:      	cbz	w23, 0x11f68 <pd_put_pd_msg_event+0x278>
   11e68:      	cmp	w22, #0xf
   11e6c:      	b.ne	0x11f68 <pd_put_pd_msg_event+0x278>
   11e70:      	tbnz	w25, #0x1f, 0x11f68 <pd_put_pd_msg_event+0x278>
   11e74:      	add	x1, sp, #0x8
   11e78:      	mov	x0, x20
   11e7c:      	mov	w2, #0x1
   11e80:      	bl	0x11e80 <pd_put_pd_msg_event+0x190>
		0000000000011e80:  R_AARCH64_CALL26	pd_put_vdm_event
   11e84:      	mov	w22, w0
   11e88:      	b	0x11df8 <pd_put_pd_msg_event+0x108>
   11e8c:      	mov	w26, #0x1
   11e90:      	strb	wzr, [x24, #0xd1e]
   11e94:      	cbnz	w23, 0x11da4 <pd_put_pd_msg_event+0xb4>
   11e98:      	cmp	w22, #0x1
   11e9c:      	b.ne	0x11da4 <pd_put_pd_msg_event+0xb4>
   11ea0:      	adrp	x0, 0x11000 <pd_get_deferred_tcp_event+0xa4>
		0000000000011ea0:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x1e9d
   11ea4:      	add	x0, x0, #0x0
		0000000000011ea4:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x1e9d
   11ea8:      	bl	0x11ea8 <pd_put_pd_msg_event+0x1b8>
		0000000000011ea8:  R_AARCH64_CALL26	pd_dbg_info
   11eac:      	cbz	x21, 0x11ee8 <pd_put_pd_msg_event+0x1f8>
   11eb0:      	sub	x8, x21, x20
   11eb4:      	mov	x9, #-0x2ce0
   11eb8:      	add	x8, x8, x9
   11ebc:      	mov	w9, #0x8e39
   11ec0:      	lsr	x8, x8, #2
   11ec4:      	movk	w9, #0x38e3, lsl #16
   11ec8:      	mov	w10, #0x1
   11ecc:      	mul	w8, w8, w9
   11ed0:      	ldrb	w9, [x24, #0x9c6]
   11ed4:      	lsl	w8, w10, w8
   11ed8:      	tst	w8, w9
   11edc:      	b.eq	0x11ff4 <pd_put_pd_msg_event+0x304>
   11ee0:      	bic	w8, w9, w8
   11ee4:      	strb	w8, [x24, #0x9c6]
   11ee8:      	mov	x0, x19
   11eec:      	bl	0x11eec <pd_put_pd_msg_event+0x1fc>
		0000000000011eec:  R_AARCH64_CALL26	mutex_unlock
   11ef0:      	mov	x0, x20
   11ef4:      	mov	w1, #0x1b
   11ef8:      	bl	0x11ef8 <pd_put_pd_msg_event+0x208>
		0000000000011ef8:  R_AARCH64_CALL26	tcpc_disable_timer
   11efc:      	mov	x0, x19
   11f00:      	bl	0x11f00 <pd_put_pd_msg_event+0x210>
		0000000000011f00:  R_AARCH64_CALL26	mutex_lock
   11f04:      	ldrb	w8, [x24, #0x9c4]
   11f08:      	cmp	w8, #0x10
   11f0c:      	b.hs	0x11fd8 <pd_put_pd_msg_event+0x2e8>
   11f10:      	ldrb	w9, [x24, #0x9c5]
   11f14:      	mov	w10, #0x2e00
   11f18:      	mov	w11, #0xa05
   11f1c:      	add	w9, w9, w8
   11f20:      	add	w8, w8, #0x1
   11f24:      	and	x9, x9, #0xf
   11f28:      	add	x9, x20, x9, lsl #4
   11f2c:      	strb	w8, [x24, #0x9c4]
   11f30:      	add	x10, x9, x10
   11f34:      	str	xzr, [x9, #0x2e08]
   11f38:      	strh	w11, [x10]
   11f3c:      	stur	xzr, [x10, #0x2]
   11f40:      	b	0x12004 <pd_put_pd_msg_event+0x314>
   11f44:      	mov	w8, #0x1
   11f48:      	stadd	w8, [x24]
   11f4c:      	mov	w8, #0x22f0
   11f50:      	mov	w1, #0x3
   11f54:      	add	x0, x20, x8
   11f58:      	mov	w2, #0x1
   11f5c:      	mov	x3, xzr
   11f60:      	bl	0x11f60 <pd_put_pd_msg_event+0x270>
		0000000000011f60:  R_AARCH64_CALL26	__wake_up
   11f64:      	b	0x11dec <pd_put_pd_msg_event+0xfc>
   11f68:      	mov	x0, x19
   11f6c:      	bl	0x11f6c <pd_put_pd_msg_event+0x27c>
		0000000000011f6c:  R_AARCH64_CALL26	mutex_lock
   11f70:      	add	x1, sp, #0x8
   11f74:      	mov	x0, x20
   11f78:      	mov	w2, #0x1
   11f7c:      	mov	w22, #0x1
   11f80:      	bl	0x10984 <__pd_put_event>
   11f84:      	mov	w23, w0
   11f88:      	mov	x0, x19
   11f8c:      	bl	0x11f8c <pd_put_pd_msg_event+0x29c>
		0000000000011f8c:  R_AARCH64_CALL26	mutex_unlock
   11f90:      	tbnz	w23, #0x0, 0x11df8 <pd_put_pd_msg_event+0x108>
   11f94:      	mov	x0, x19
   11f98:      	bl	0x11f98 <pd_put_pd_msg_event+0x2a8>
		0000000000011f98:  R_AARCH64_CALL26	mutex_lock
   11f9c:      	cbz	x21, 0x11dec <pd_put_pd_msg_event+0xfc>
   11fa0:      	sub	x8, x21, x20
   11fa4:      	mov	x9, #-0x2ce0
   11fa8:      	add	x8, x8, x9
   11fac:      	mov	w9, #0x8e39
   11fb0:      	lsr	x8, x8, #2
   11fb4:      	movk	w9, #0x38e3, lsl #16
   11fb8:      	mov	w10, #0x1
   11fbc:      	mul	w8, w8, w9
   11fc0:      	ldrb	w9, [x24, #0x9c6]
   11fc4:      	lsl	w8, w10, w8
   11fc8:      	tst	w8, w9
   11fcc:      	b.ne	0x11de4 <pd_put_pd_msg_event+0xf4>
   11fd0:      	brk	#0x800
   11fd4:      	b	0x11fec <pd_put_pd_msg_event+0x2fc>
   11fd8:      	adrp	x0, 0x11000 <pd_get_deferred_tcp_event+0xa4>
		0000000000011fd8:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x345a
   11fdc:      	add	x0, x0, #0x0
		0000000000011fdc:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x345a
   11fe0:      	bl	0x11fe0 <pd_put_pd_msg_event+0x2f0>
		0000000000011fe0:  R_AARCH64_CALL26	pd_dbg_info
   11fe4:      	b	0x11dec <pd_put_pd_msg_event+0xfc>
   11fe8:      	brk	#0x800
   11fec:      	ldrb	w9, [x24, #0x9c6]
   11ff0:      	b	0x11de4 <pd_put_pd_msg_event+0xf4>
   11ff4:      	brk	#0x800
   11ff8:      	ldrb	w9, [x24, #0x9c6]
   11ffc:      	b	0x11ee0 <pd_put_pd_msg_event+0x1f0>
   12000:      	bl	0x12000 <pd_put_pd_msg_event+0x310>
		0000000000012000:  R_AARCH64_CALL26	__stack_chk_fail
   12004:      	prfm	pstl1strm, [x24]
   12008:      	ldxr	w8, [x24]
   1200c:      	add	w8, w8, #0x1
   12010:      	stxr	w9, w8, [x24]
   12014:      	cbnz	w9, 0x12008 <pd_put_pd_msg_event+0x318>
   12018:      	b	0x11f4c <pd_put_pd_msg_event+0x25c>
