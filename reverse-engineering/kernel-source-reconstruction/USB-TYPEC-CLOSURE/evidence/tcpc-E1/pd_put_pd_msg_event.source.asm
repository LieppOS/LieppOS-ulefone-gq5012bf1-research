source pd_put_pd_msg_event section=.text address=0x11d10 size=808
   11d10:      	paciasp
   11d14:      	sub	sp, sp, #0x70
   11d18:      	stp	x29, x30, [sp, #0x20]
   11d1c:      	stp	x26, x25, [sp, #0x30]
   11d20:      	stp	x24, x23, [sp, #0x40]
   11d24:      	stp	x22, x21, [sp, #0x50]
   11d28:      	stp	x20, x19, [sp, #0x60]
   11d2c:      	add	x29, sp, #0x20
   11d30:      	mrs	x8, SP_EL0
   11d34:      	mov	w9, #0x2248
   11d38:      	ldr	x8, [x8, #0x638]
   11d3c:      	add	x19, x0, x9
   11d40:      	mov	x20, x0
   11d44:      	mov	x21, x1
   11d48:      	stur	x8, [x29, #-0x8]
   11d4c:      	mov	w8, #0x22dc
   11d50:      	ldrh	w25, [x1, #0x4]
   11d54:      	add	x24, x0, x8
   11d58:      	mov	x0, x19
   11d5c:      	stp	xzr, x1, [sp, #0x8]
   11d60:      	ubfx	w23, w25, #12, #3
   11d64:      	and	w22, w25, #0x1f
   11d68:      	bl	0x11d68 <pd_put_pd_msg_event+0x58>
		0000000000011d68:  R_AARCH64_CALL26	mutex_lock
   11d6c:      	ldrb	w26, [x24, #0xd1e]
   11d70:      	cbz	w26, 0x11e4c <pd_put_pd_msg_event+0x13c>
   11d74:      	strb	wzr, [x24, #0xd1e]
   11d78:      	cbnz	w23, 0x11e4c <pd_put_pd_msg_event+0x13c>
   11d7c:      	cmp	w22, #0x1
   11d80:      	b.ne	0x11e4c <pd_put_pd_msg_event+0x13c>
   11d84:      	adrp	x0, 0x11000 <pd_get_deferred_tcp_event+0x84>
		0000000000011d84:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x1ea0
   11d88:      	add	x0, x0, #0x0
		0000000000011d88:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x1ea0
   11d8c:      	bl	0x11d8c <pd_put_pd_msg_event+0x7c>
		0000000000011d8c:  R_AARCH64_CALL26	pd_dbg_info
   11d90:      	cbz	x21, 0x11dcc <pd_put_pd_msg_event+0xbc>
   11d94:      	sub	x8, x21, x20
   11d98:      	mov	x9, #-0x2ce0
   11d9c:      	add	x8, x8, x9
   11da0:      	mov	w9, #0x8e39
   11da4:      	lsr	x8, x8, #2
   11da8:      	movk	w9, #0x38e3, lsl #16
   11dac:      	mov	w10, #0x1
   11db0:      	mul	w8, w8, w9
   11db4:      	ldrb	w9, [x24, #0x9c6]
   11db8:      	lsl	w8, w10, w8
   11dbc:      	tst	w8, w9
   11dc0:      	b.eq	0x11fec <pd_put_pd_msg_event+0x2dc>
   11dc4:      	bic	w8, w9, w8
   11dc8:      	strb	w8, [x24, #0x9c6]
   11dcc:      	mov	x0, x19
   11dd0:      	bl	0x11dd0 <pd_put_pd_msg_event+0xc0>
		0000000000011dd0:  R_AARCH64_CALL26	mutex_unlock
   11dd4:      	mov	x0, x20
   11dd8:      	mov	w1, #0x1b
   11ddc:      	bl	0x11ddc <pd_put_pd_msg_event+0xcc>
		0000000000011ddc:  R_AARCH64_CALL26	tcpc_disable_timer
   11de0:      	mov	x0, x19
   11de4:      	bl	0x11de4 <pd_put_pd_msg_event+0xd4>
		0000000000011de4:  R_AARCH64_CALL26	mutex_lock
   11de8:      	ldrb	w8, [x24, #0x9c4]
   11dec:      	cmp	w8, #0x10
   11df0:      	b.hs	0x11f9c <pd_put_pd_msg_event+0x28c>
   11df4:      	ldrb	w9, [x24, #0x9c5]
   11df8:      	mov	w10, #0x2e00
   11dfc:      	mov	w11, #0xa05
   11e00:      	add	w9, w9, w8
   11e04:      	add	w8, w8, #0x1
   11e08:      	and	x9, x9, #0xf
   11e0c:      	add	x9, x20, x9, lsl #4
   11e10:      	strb	w8, [x24, #0x9c4]
   11e14:      	add	x10, x9, x10
   11e18:      	str	xzr, [x9, #0x2e08]
   11e1c:      	strh	w11, [x10]
   11e20:      	stur	xzr, [x10, #0x2]
   11e24:      	b	0x12020 <pd_put_pd_msg_event+0x310>
   11e28:      	mov	w8, #0x1
   11e2c:      	stadd	w8, [x24]
   11e30:      	mov	w8, #0x22f0
   11e34:      	mov	w1, #0x3
   11e38:      	add	x0, x20, x8
   11e3c:      	mov	w2, #0x1
   11e40:      	mov	x3, xzr
   11e44:      	bl	0x11e44 <pd_put_pd_msg_event+0x134>
		0000000000011e44:  R_AARCH64_CALL26	__wake_up
   11e48:      	b	0x11fa8 <pd_put_pd_msg_event+0x298>
   11e4c:      	sxth	w25, w25
   11e50:      	cbz	w23, 0x11e68 <pd_put_pd_msg_event+0x158>
   11e54:      	cmp	w22, #0x3
   11e58:      	b.ne	0x11e68 <pd_put_pd_msg_event+0x158>
   11e5c:      	tbnz	w25, #0x1f, 0x11e68 <pd_put_pd_msg_event+0x158>
   11e60:      	mov	w8, #0x1
   11e64:      	strb	w8, [x24, #0xd19]
   11e68:      	mov	x0, x19
   11e6c:      	bl	0x11e6c <pd_put_pd_msg_event+0x15c>
		0000000000011e6c:  R_AARCH64_CALL26	mutex_unlock
   11e70:      	cbz	w26, 0x11f00 <pd_put_pd_msg_event+0x1f0>
   11e74:      	mov	x0, x20
   11e78:      	mov	w1, #0x1b
   11e7c:      	bl	0x11e7c <pd_put_pd_msg_event+0x16c>
		0000000000011e7c:  R_AARCH64_CALL26	tcpc_disable_timer
   11e80:      	mov	x0, x19
   11e84:      	bl	0x11e84 <pd_put_pd_msg_event+0x174>
		0000000000011e84:  R_AARCH64_CALL26	mutex_lock
   11e88:      	ldrb	w8, [x24, #0x9c4]
   11e8c:      	cmp	w8, #0x10
   11e90:      	b.hs	0x11eec <pd_put_pd_msg_event+0x1dc>
   11e94:      	ldrb	w9, [x24, #0x9c5]
   11e98:      	mov	w10, #0x2e00
   11e9c:      	mov	w11, #0x805
   11ea0:      	add	w9, w9, w8
   11ea4:      	add	w8, w8, #0x1
   11ea8:      	and	x9, x9, #0xf
   11eac:      	add	x9, x20, x9, lsl #4
   11eb0:      	strb	w8, [x24, #0x9c4]
   11eb4:      	add	x10, x9, x10
   11eb8:      	str	xzr, [x9, #0x2e08]
   11ebc:      	strh	w11, [x10]
   11ec0:      	stur	xzr, [x10, #0x2]
   11ec4:      	b	0x12008 <pd_put_pd_msg_event+0x2f8>
   11ec8:      	mov	w8, #0x1
   11ecc:      	stadd	w8, [x24]
   11ed0:      	mov	w8, #0x22f0
   11ed4:      	mov	w1, #0x3
   11ed8:      	add	x0, x20, x8
   11edc:      	mov	w2, #0x1
   11ee0:      	mov	x3, xzr
   11ee4:      	bl	0x11ee4 <pd_put_pd_msg_event+0x1d4>
		0000000000011ee4:  R_AARCH64_CALL26	__wake_up
   11ee8:      	b	0x11ef8 <pd_put_pd_msg_event+0x1e8>
   11eec:      	adrp	x0, 0x11000 <pd_get_deferred_tcp_event+0x84>
		0000000000011eec:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x34d6
   11ef0:      	add	x0, x0, #0x0
		0000000000011ef0:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x34d6
   11ef4:      	bl	0x11ef4 <pd_put_pd_msg_event+0x1e4>
		0000000000011ef4:  R_AARCH64_CALL26	pd_dbg_info
   11ef8:      	mov	x0, x19
   11efc:      	bl	0x11efc <pd_put_pd_msg_event+0x1ec>
		0000000000011efc:  R_AARCH64_CALL26	mutex_unlock
   11f00:      	cbz	w23, 0x11f28 <pd_put_pd_msg_event+0x218>
   11f04:      	cmp	w22, #0xf
   11f08:      	b.ne	0x11f28 <pd_put_pd_msg_event+0x218>
   11f0c:      	tbnz	w25, #0x1f, 0x11f28 <pd_put_pd_msg_event+0x218>
   11f10:      	add	x1, sp, #0x8
   11f14:      	mov	x0, x20
   11f18:      	mov	w2, #0x1
   11f1c:      	bl	0x11f1c <pd_put_pd_msg_event+0x20c>
		0000000000011f1c:  R_AARCH64_CALL26	pd_put_vdm_event
   11f20:      	mov	w22, w0
   11f24:      	b	0x11fb4 <pd_put_pd_msg_event+0x2a4>
   11f28:      	mov	x0, x19
   11f2c:      	bl	0x11f2c <pd_put_pd_msg_event+0x21c>
		0000000000011f2c:  R_AARCH64_CALL26	mutex_lock
   11f30:      	add	x1, sp, #0x8
   11f34:      	mov	x0, x20
   11f38:      	mov	w2, #0x1
   11f3c:      	mov	w22, #0x1
   11f40:      	bl	0x109a4 <__pd_put_event>
   11f44:      	mov	w23, w0
   11f48:      	mov	x0, x19
   11f4c:      	bl	0x11f4c <pd_put_pd_msg_event+0x23c>
		0000000000011f4c:  R_AARCH64_CALL26	mutex_unlock
   11f50:      	tbnz	w23, #0x0, 0x11fb4 <pd_put_pd_msg_event+0x2a4>
   11f54:      	mov	x0, x19
   11f58:      	bl	0x11f58 <pd_put_pd_msg_event+0x248>
		0000000000011f58:  R_AARCH64_CALL26	mutex_lock
   11f5c:      	cbz	x21, 0x11fa8 <pd_put_pd_msg_event+0x298>
   11f60:      	sub	x8, x21, x20
   11f64:      	mov	x9, #-0x2ce0
   11f68:      	add	x8, x8, x9
   11f6c:      	mov	w9, #0x8e39
   11f70:      	lsr	x8, x8, #2
   11f74:      	movk	w9, #0x38e3, lsl #16
   11f78:      	mov	w10, #0x1
   11f7c:      	mul	w8, w8, w9
   11f80:      	ldrb	w9, [x24, #0x9c6]
   11f84:      	lsl	w8, w10, w8
   11f88:      	tst	w8, w9
   11f8c:      	b.eq	0x11ff8 <pd_put_pd_msg_event+0x2e8>
   11f90:      	bic	w8, w9, w8
   11f94:      	strb	w8, [x24, #0x9c6]
   11f98:      	b	0x11fa8 <pd_put_pd_msg_event+0x298>
   11f9c:      	adrp	x0, 0x11000 <pd_get_deferred_tcp_event+0x84>
		0000000000011f9c:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x34d6
   11fa0:      	add	x0, x0, #0x0
		0000000000011fa0:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x34d6
   11fa4:      	bl	0x11fa4 <pd_put_pd_msg_event+0x294>
		0000000000011fa4:  R_AARCH64_CALL26	pd_dbg_info
   11fa8:      	mov	x0, x19
   11fac:      	bl	0x11fac <pd_put_pd_msg_event+0x29c>
		0000000000011fac:  R_AARCH64_CALL26	mutex_unlock
   11fb0:      	mov	w22, wzr
   11fb4:      	mrs	x8, SP_EL0
   11fb8:      	ldr	x8, [x8, #0x638]
   11fbc:      	ldur	x9, [x29, #-0x8]
   11fc0:      	cmp	x8, x9
   11fc4:      	b.ne	0x12004 <pd_put_pd_msg_event+0x2f4>
   11fc8:      	and	w0, w22, #0x1
   11fcc:      	ldp	x20, x19, [sp, #0x60]
   11fd0:      	ldp	x22, x21, [sp, #0x50]
   11fd4:      	ldp	x24, x23, [sp, #0x40]
   11fd8:      	ldp	x26, x25, [sp, #0x30]
   11fdc:      	ldp	x29, x30, [sp, #0x20]
   11fe0:      	add	sp, sp, #0x70
   11fe4:      	autiasp
   11fe8:      	ret
   11fec:      	brk	#0x800
   11ff0:      	ldrb	w9, [x24, #0x9c6]
   11ff4:      	b	0x11dc4 <pd_put_pd_msg_event+0xb4>
   11ff8:      	brk	#0x800
   11ffc:      	ldrb	w9, [x24, #0x9c6]
   12000:      	b	0x11f90 <pd_put_pd_msg_event+0x280>
   12004:      	bl	0x12004 <pd_put_pd_msg_event+0x2f4>
		0000000000012004:  R_AARCH64_CALL26	__stack_chk_fail
   12008:      	prfm	pstl1strm, [x24]
   1200c:      	ldxr	w8, [x24]
   12010:      	add	w8, w8, #0x1
   12014:      	stxr	w9, w8, [x24]
   12018:      	cbnz	w9, 0x1200c <pd_put_pd_msg_event+0x2fc>
   1201c:      	b	0x11ed0 <pd_put_pd_msg_event+0x1c0>
   12020:      	prfm	pstl1strm, [x24]
   12024:      	ldxr	w8, [x24]
   12028:      	add	w8, w8, #0x1
   1202c:      	stxr	w9, w8, [x24]
   12030:      	cbnz	w9, 0x12024 <pd_put_pd_msg_event+0x314>
   12034:      	b	0x11e30 <pd_put_pd_msg_event+0x120>
