source pd_process_protocol_error section=.text address=0x15ba4 size=332
   15ba4:      	paciasp
   15ba8:      	stp	x29, x30, [sp, #-0x40]!
   15bac:      	str	x23, [sp, #0x10]
   15bb0:      	stp	x22, x21, [sp, #0x20]
   15bb4:      	stp	x20, x19, [sp, #0x30]
   15bb8:      	mov	x29, sp
   15bbc:      	ldrb	w19, [x1]
   15bc0:      	ldrb	w20, [x1, #0x1]
   15bc4:      	ldrh	w8, [x0, #0x6a]
   15bc8:      	ldrh	w23, [x0, #0x31c]
   15bcc:      	tbnz	w8, #0x7, 0x15bf0 <pd_process_protocol_error+0x4c>
   15bd0:      	mov	w8, #0x2ff3
   15bd4:      	ldr	x9, [x0]
   15bd8:      	mov	x21, x0
   15bdc:      	ldrb	w8, [x9, x8]
   15be0:      	cbz	w8, 0x15c34 <pd_process_protocol_error+0x90>
   15be4:      	adrp	x0, 0x15000 <pd_send_soft_reset+0xa8>
		0000000000015be4:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x3901
   15be8:      	add	x0, x0, #0x0
		0000000000015be8:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x3901
   15bec:      	b	0x15bf8 <pd_process_protocol_error+0x54>
   15bf0:      	adrp	x0, 0x15000 <pd_send_soft_reset+0xa8>
		0000000000015bf0:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x2e1a
   15bf4:      	add	x0, x0, #0x0
		0000000000015bf4:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x2e1a
   15bf8:      	bl	0x15bf8 <pd_process_protocol_error+0x54>
		0000000000015bf8:  R_AARCH64_CALL26	pd_dbg_info
   15bfc:      	mov	w22, wzr
   15c00:      	ubfx	w3, w23, #9, #3
   15c04:      	adrp	x0, 0x15000 <pd_send_soft_reset+0xa8>
		0000000000015c04:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x17eb
   15c08:      	add	x0, x0, #0x0
		0000000000015c08:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x17eb
   15c0c:      	mov	w1, w19
   15c10:      	mov	w2, w20
   15c14:      	bl	0x15c14 <pd_process_protocol_error+0x70>
		0000000000015c14:  R_AARCH64_CALL26	pd_dbg_info
   15c18:      	mov	w0, w22
   15c1c:      	ldp	x20, x19, [sp, #0x30]
   15c20:      	ldp	x22, x21, [sp, #0x20]
   15c24:      	ldr	x23, [sp, #0x10]
   15c28:      	ldp	x29, x30, [sp], #0x40
   15c2c:      	autiasp
   15c30:      	ret
   15c34:      	ldrb	w8, [x21, #0x3d]
   15c38:      	cmp	w8, #0x23
   15c3c:      	b.hi	0x15cb4 <pd_process_protocol_error+0x110>
   15c40:      	mov	w9, #0x1
   15c44:      	mov	x10, #0x30
   15c48:      	lsl	x9, x9, x8
   15c4c:      	movk	x10, #0x4, lsl #32
   15c50:      	tst	x9, x10
   15c54:      	b.eq	0x15c68 <pd_process_protocol_error+0xc4>
   15c58:      	ldrb	w8, [x21, #0x4b]
   15c5c:      	cbnz	w8, 0x15cbc <pd_process_protocol_error+0x118>
   15c60:      	ldrb	w8, [x21, #0x325]
   15c64:      	b	0x15ce4 <pd_process_protocol_error+0x140>
   15c68:      	mov	w9, #0x1
   15c6c:      	lsl	x8, x9, x8
   15c70:      	mov	x9, #0x40
   15c74:      	movk	x9, #0x8, lsl #32
   15c78:      	tst	x8, x9
   15c7c:      	b.eq	0x15cb4 <pd_process_protocol_error+0x110>
   15c80:      	ldrb	w8, [x21, #0x327]
   15c84:      	cbz	w8, 0x15cc4 <pd_process_protocol_error+0x120>
   15c88:      	ldrb	w8, [x21, #0x13d]
   15c8c:      	cmp	w8, #0x1
   15c90:      	b.ls	0x15ccc <pd_process_protocol_error+0x128>
   15c94:      	mov	x0, x21
   15c98:      	bl	0x15c98 <pd_process_protocol_error+0xf4>
		0000000000015c98:  R_AARCH64_CALL26	pd_is_multi_chunk_msg
   15c9c:      	ldrb	w8, [x21, #0x3f]
   15ca0:      	cbz	w8, 0x15cd4 <pd_process_protocol_error+0x130>
   15ca4:      	tst	w0, #0x1
   15ca8:      	mov	w8, #0x14
   15cac:      	mov	w9, #0x16
   15cb0:      	b	0x15ce0 <pd_process_protocol_error+0x13c>
   15cb4:      	ldrb	w8, [x21, #0x4b]
   15cb8:      	cbz	w8, 0x15cc4 <pd_process_protocol_error+0x120>
   15cbc:      	mov	w8, #0x98
   15cc0:      	b	0x15ce4 <pd_process_protocol_error+0x140>
   15cc4:      	ldrb	w8, [x21, #0x326]
   15cc8:      	b	0x15ce4 <pd_process_protocol_error+0x140>
   15ccc:      	mov	w8, #0x97
   15cd0:      	b	0x15ce4 <pd_process_protocol_error+0x140>
   15cd4:      	tst	w0, #0x1
   15cd8:      	mov	w8, #0x2a
   15cdc:      	mov	w9, #0x2c
   15ce0:      	csel	w8, w9, w8, ne
   15ce4:      	mov	w22, #0x1
   15ce8:      	strb	w8, [x21, #0x3c]
   15cec:      	b	0x15c00 <pd_process_protocol_error+0x5c>
