source pd_process_protocol_error section=.text address=0x15b88 size=332
   15b88:      	paciasp
   15b8c:      	stp	x29, x30, [sp, #-0x40]!
   15b90:      	str	x23, [sp, #0x10]
   15b94:      	stp	x22, x21, [sp, #0x20]
   15b98:      	stp	x20, x19, [sp, #0x30]
   15b9c:      	mov	x29, sp
   15ba0:      	ldrb	w19, [x1]
   15ba4:      	ldrb	w20, [x1, #0x1]
   15ba8:      	ldrh	w8, [x0, #0x6a]
   15bac:      	ldrh	w23, [x0, #0x31c]
   15bb0:      	tbnz	w8, #0x7, 0x15bd4 <pd_process_protocol_error+0x4c>
   15bb4:      	mov	w8, #0x2ff3
   15bb8:      	ldr	x9, [x0]
   15bbc:      	mov	x21, x0
   15bc0:      	ldrb	w8, [x9, x8]
   15bc4:      	cbz	w8, 0x15c18 <pd_process_protocol_error+0x90>
   15bc8:      	adrp	x0, 0x15000 <pd_send_soft_reset+0xc4>
		0000000000015bc8:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x3885
   15bcc:      	add	x0, x0, #0x0
		0000000000015bcc:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x3885
   15bd0:      	b	0x15bdc <pd_process_protocol_error+0x54>
   15bd4:      	adrp	x0, 0x15000 <pd_send_soft_reset+0xc4>
		0000000000015bd4:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x2e0d
   15bd8:      	add	x0, x0, #0x0
		0000000000015bd8:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x2e0d
   15bdc:      	bl	0x15bdc <pd_process_protocol_error+0x54>
		0000000000015bdc:  R_AARCH64_CALL26	pd_dbg_info
   15be0:      	mov	w22, wzr
   15be4:      	ubfx	w3, w23, #9, #3
   15be8:      	adrp	x0, 0x15000 <pd_send_soft_reset+0xc4>
		0000000000015be8:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x17e8
   15bec:      	add	x0, x0, #0x0
		0000000000015bec:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x17e8
   15bf0:      	mov	w1, w19
   15bf4:      	mov	w2, w20
   15bf8:      	bl	0x15bf8 <pd_process_protocol_error+0x70>
		0000000000015bf8:  R_AARCH64_CALL26	pd_dbg_info
   15bfc:      	mov	w0, w22
   15c00:      	ldp	x20, x19, [sp, #0x30]
   15c04:      	ldp	x22, x21, [sp, #0x20]
   15c08:      	ldr	x23, [sp, #0x10]
   15c0c:      	ldp	x29, x30, [sp], #0x40
   15c10:      	autiasp
   15c14:      	ret
   15c18:      	ldrb	w8, [x21, #0x3d]
   15c1c:      	cmp	w8, #0x23
   15c20:      	b.hi	0x15c98 <pd_process_protocol_error+0x110>
   15c24:      	mov	w9, #0x1
   15c28:      	mov	x10, #0x30
   15c2c:      	lsl	x9, x9, x8
   15c30:      	movk	x10, #0x4, lsl #32
   15c34:      	tst	x9, x10
   15c38:      	b.eq	0x15c4c <pd_process_protocol_error+0xc4>
   15c3c:      	ldrb	w8, [x21, #0x4b]
   15c40:      	cbnz	w8, 0x15ca0 <pd_process_protocol_error+0x118>
   15c44:      	ldrb	w8, [x21, #0x325]
   15c48:      	b	0x15cc8 <pd_process_protocol_error+0x140>
   15c4c:      	mov	w9, #0x1
   15c50:      	lsl	x8, x9, x8
   15c54:      	mov	x9, #0x40
   15c58:      	movk	x9, #0x8, lsl #32
   15c5c:      	tst	x8, x9
   15c60:      	b.eq	0x15c98 <pd_process_protocol_error+0x110>
   15c64:      	ldrb	w8, [x21, #0x327]
   15c68:      	cbz	w8, 0x15ca8 <pd_process_protocol_error+0x120>
   15c6c:      	ldrb	w8, [x21, #0x13d]
   15c70:      	cmp	w8, #0x1
   15c74:      	b.ls	0x15cb0 <pd_process_protocol_error+0x128>
   15c78:      	mov	x0, x21
   15c7c:      	bl	0x15c7c <pd_process_protocol_error+0xf4>
		0000000000015c7c:  R_AARCH64_CALL26	pd_is_multi_chunk_msg
   15c80:      	ldrb	w8, [x21, #0x3f]
   15c84:      	cbz	w8, 0x15cb8 <pd_process_protocol_error+0x130>
   15c88:      	tst	w0, #0x1
   15c8c:      	mov	w8, #0x14
   15c90:      	mov	w9, #0x16
   15c94:      	b	0x15cc4 <pd_process_protocol_error+0x13c>
   15c98:      	ldrb	w8, [x21, #0x4b]
   15c9c:      	cbz	w8, 0x15ca8 <pd_process_protocol_error+0x120>
   15ca0:      	mov	w8, #0x98
   15ca4:      	b	0x15cc8 <pd_process_protocol_error+0x140>
   15ca8:      	ldrb	w8, [x21, #0x326]
   15cac:      	b	0x15cc8 <pd_process_protocol_error+0x140>
   15cb0:      	mov	w8, #0x97
   15cb4:      	b	0x15cc8 <pd_process_protocol_error+0x140>
   15cb8:      	tst	w0, #0x1
   15cbc:      	mov	w8, #0x2a
   15cc0:      	mov	w9, #0x2c
   15cc4:      	csel	w8, w9, w8, ne
   15cc8:      	mov	w22, #0x1
   15ccc:      	strb	w8, [x21, #0x3c]
   15cd0:      	b	0x15be4 <pd_process_protocol_error+0x5c>
