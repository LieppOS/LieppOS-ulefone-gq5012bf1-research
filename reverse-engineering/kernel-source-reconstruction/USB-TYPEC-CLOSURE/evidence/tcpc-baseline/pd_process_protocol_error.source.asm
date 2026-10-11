source pd_process_protocol_error section=.text address=0x15c08 size=388
   15c08:      	paciasp
   15c0c:      	stp	x29, x30, [sp, #-0x40]!
   15c10:      	str	x23, [sp, #0x10]
   15c14:      	stp	x22, x21, [sp, #0x20]
   15c18:      	stp	x20, x19, [sp, #0x30]
   15c1c:      	mov	x29, sp
   15c20:      	ldrb	w19, [x1]
   15c24:      	ldrb	w20, [x1, #0x1]
   15c28:      	ldrh	w8, [x0, #0x6a]
   15c2c:      	ldrh	w23, [x0, #0x31c]
   15c30:      	tbnz	w8, #0x7, 0x15c54 <pd_process_protocol_error+0x4c>
   15c34:      	mov	w8, #0x2ff3
   15c38:      	ldr	x9, [x0]
   15c3c:      	mov	x21, x0
   15c40:      	ldrb	w8, [x9, x8]
   15c44:      	cbz	w8, 0x15c98 <pd_process_protocol_error+0x90>
   15c48:      	adrp	x0, 0x15000 <pd_send_soft_reset+0x88>
		0000000000015c48:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x392e
   15c4c:      	add	x0, x0, #0x0
		0000000000015c4c:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x392e
   15c50:      	b	0x15c5c <pd_process_protocol_error+0x54>
   15c54:      	adrp	x0, 0x15000 <pd_send_soft_reset+0x88>
		0000000000015c54:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x2e47
   15c58:      	add	x0, x0, #0x0
		0000000000015c58:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x2e47
   15c5c:      	bl	0x15c5c <pd_process_protocol_error+0x54>
		0000000000015c5c:  R_AARCH64_CALL26	pd_dbg_info
   15c60:      	mov	w22, wzr
   15c64:      	ubfx	w3, w23, #9, #3
   15c68:      	adrp	x0, 0x15000 <pd_send_soft_reset+0x88>
		0000000000015c68:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x1803
   15c6c:      	add	x0, x0, #0x0
		0000000000015c6c:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x1803
   15c70:      	mov	w1, w19
   15c74:      	mov	w2, w20
   15c78:      	bl	0x15c78 <pd_process_protocol_error+0x70>
		0000000000015c78:  R_AARCH64_CALL26	pd_dbg_info
   15c7c:      	mov	w0, w22
   15c80:      	ldp	x20, x19, [sp, #0x30]
   15c84:      	ldp	x22, x21, [sp, #0x20]
   15c88:      	ldr	x23, [sp, #0x10]
   15c8c:      	ldp	x29, x30, [sp], #0x40
   15c90:      	autiasp
   15c94:      	ret
   15c98:      	ldrb	w8, [x21, #0x3d]
   15c9c:      	sub	w8, w8, #0x4
   15ca0:      	cmp	w8, #0x3e
   15ca4:      	b.hi	0x15d50 <pd_process_protocol_error+0x148>
   15ca8:      	mov	w9, #0x1
   15cac:      	mov	w10, #0x3
   15cb0:      	lsl	x9, x9, x8
   15cb4:      	movk	w10, #0x4000, lsl #16
   15cb8:      	tst	x9, x10
   15cbc:      	b.ne	0x15d0c <pd_process_protocol_error+0x104>
   15cc0:      	mov	w9, #0x1
   15cc4:      	mov	w10, #0x4
   15cc8:      	lsl	x9, x9, x8
   15ccc:      	movk	w10, #0x8000, lsl #16
   15cd0:      	tst	x9, x10
   15cd4:      	b.eq	0x15d2c <pd_process_protocol_error+0x124>
   15cd8:      	ldrb	w8, [x21, #0x327]
   15cdc:      	cbz	w8, 0x15d60 <pd_process_protocol_error+0x158>
   15ce0:      	ldrb	w8, [x21, #0x13d]
   15ce4:      	cmp	w8, #0x1
   15ce8:      	b.ls	0x15d68 <pd_process_protocol_error+0x160>
   15cec:      	mov	x0, x21
   15cf0:      	bl	0x15cf0 <pd_process_protocol_error+0xe8>
		0000000000015cf0:  R_AARCH64_CALL26	pd_is_multi_chunk_msg
   15cf4:      	ldrb	w8, [x21, #0x3f]
   15cf8:      	cbz	w8, 0x15d70 <pd_process_protocol_error+0x168>
   15cfc:      	tst	w0, #0x1
   15d00:      	mov	w8, #0x14
   15d04:      	mov	w9, #0x16
   15d08:      	b	0x15d7c <pd_process_protocol_error+0x174>
   15d0c:      	cmp	w19, #0x1
   15d10:      	b.ne	0x15d1c <pd_process_protocol_error+0x114>
   15d14:      	cmp	w20, #0x5
   15d18:      	b.eq	0x15d44 <pd_process_protocol_error+0x13c>
   15d1c:      	ldrb	w8, [x21, #0x4b]
   15d20:      	cbnz	w8, 0x15d58 <pd_process_protocol_error+0x150>
   15d24:      	ldrb	w8, [x21, #0x325]
   15d28:      	b	0x15d80 <pd_process_protocol_error+0x178>
   15d2c:      	cmp	x8, #0x3e
   15d30:      	b.ne	0x15d50 <pd_process_protocol_error+0x148>
   15d34:      	cmp	w19, #0x1
   15d38:      	b.ne	0x15d50 <pd_process_protocol_error+0x148>
   15d3c:      	cmp	w20, #0x5
   15d40:      	b.ne	0x15d50 <pd_process_protocol_error+0x148>
   15d44:      	adrp	x0, 0x15000 <pd_send_soft_reset+0x88>
		0000000000015d44:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x2cd0
   15d48:      	add	x0, x0, #0x0
		0000000000015d48:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x2cd0
   15d4c:      	b	0x15c5c <pd_process_protocol_error+0x54>
   15d50:      	ldrb	w8, [x21, #0x4b]
   15d54:      	cbz	w8, 0x15d60 <pd_process_protocol_error+0x158>
   15d58:      	mov	w8, #0x98
   15d5c:      	b	0x15d80 <pd_process_protocol_error+0x178>
   15d60:      	ldrb	w8, [x21, #0x326]
   15d64:      	b	0x15d80 <pd_process_protocol_error+0x178>
   15d68:      	mov	w8, #0x97
   15d6c:      	b	0x15d80 <pd_process_protocol_error+0x178>
   15d70:      	tst	w0, #0x1
   15d74:      	mov	w8, #0x2a
   15d78:      	mov	w9, #0x2c
   15d7c:      	csel	w8, w9, w8, ne
   15d80:      	mov	w22, #0x1
   15d84:      	strb	w8, [x21, #0x3c]
   15d88:      	b	0x15c64 <pd_process_protocol_error+0x5c>
