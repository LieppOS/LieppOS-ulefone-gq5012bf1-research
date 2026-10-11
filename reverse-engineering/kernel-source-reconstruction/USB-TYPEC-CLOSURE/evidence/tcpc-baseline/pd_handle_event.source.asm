source pd_handle_event section=.text address=0x1590c size=636
   1590c:      	paciasp
   15910:      	stp	x29, x30, [sp, #-0x40]!
   15914:      	stp	x24, x23, [sp, #0x10]
   15918:      	stp	x22, x21, [sp, #0x20]
   1591c:      	stp	x20, x19, [sp, #0x30]
   15920:      	mov	x29, sp
   15924:      	mov	x20, x0
   15928:      	ldrb	w8, [x0, #0x2f0]
   1592c:      	mov	x19, x1
   15930:      	cbz	w8, 0x15984 <pd_handle_event+0x78>
   15934:      	ldrb	w8, [x20, #0x4a]
   15938:      	cbz	w8, 0x15944 <pd_handle_event+0x38>
   1593c:      	ldrb	w8, [x20, #0x6c]
   15940:      	tbz	w8, #0x1, 0x15950 <pd_handle_event+0x44>
   15944:      	ldrb	w8, [x19]
   15948:      	cmp	w8, #0x8
   1594c:      	b.ne	0x1597c <pd_handle_event+0x70>
   15950:      	ldr	w1, [x20, #0x74]
   15954:      	strb	wzr, [x20, #0x4a]
   15958:      	ldrb	w8, [x20, #0x3a]
   1595c:      	strb	wzr, [x20, #0x6c]
   15960:      	cmp	w1, #0x35
   15964:      	strb	w8, [x20, #0x3b]
   15968:      	b.hi	0x1597c <pd_handle_event+0x70>
   1596c:      	ldr	x0, [x20]
   15970:      	bl	0x15970 <pd_handle_event+0x64>
		0000000000015970:  R_AARCH64_CALL26	tcpc_disable_timer
   15974:      	mov	w8, #0x36
   15978:      	str	w8, [x20, #0x74]
   1597c:      	add	x8, x20, #0x3b
   15980:      	b	0x15988 <pd_handle_event+0x7c>
   15984:      	add	x8, x20, #0x3a
   15988:      	ldrb	w8, [x8]
   1598c:      	mov	x0, x20
   15990:      	mov	x1, x19
   15994:      	strb	w8, [x20, #0x3d]
   15998:      	bl	0x15998 <pd_handle_event+0x8c>
		0000000000015998:  R_AARCH64_CALL26	pd_process_event
   1599c:      	tbz	w0, #0x0, 0x15b54 <pd_handle_event+0x248>
   159a0:      	ldrb	w0, [x20, #0x3d]
   159a4:      	cmp	w0, #0x9d
   159a8:      	b.hi	0x159d8 <pd_handle_event+0xcc>
   159ac:      	ldrb	w22, [x20, #0x3c]
   159b0:      	cmp	w22, #0x9e
   159b4:      	b.hs	0x159d8 <pd_handle_event+0xcc>
   159b8:      	cmp	w22, #0x9c
   159bc:      	b.lo	0x159e0 <pd_handle_event+0xd4>
   159c0:      	adrp	x8, 0x15000 <pd_send_soft_reset+0x88>
		00000000000159c0:  R_AARCH64_ADR_PREL_PG_HI21	pd_usb_connected
   159c4:      	mov	x21, xzr
   159c8:      	str	wzr, [x8]
		00000000000159c8:  R_AARCH64_LDST32_ABS_LO12_NC	pd_usb_connected
   159cc:      	cmp	w22, #0x9d
   159d0:      	b.ls	0x15a1c <pd_handle_event+0x110>
   159d4:      	b	0x15b84 <pd_handle_event+0x278>
   159d8:      	brk	#0x800
   159dc:      	b	0x15b54 <pd_handle_event+0x248>
   159e0:      	cmp	w22, #0x98
   159e4:      	b.eq	0x15b78 <pd_handle_event+0x26c>
   159e8:      	cmp	w22, #0x23
   159ec:      	b.eq	0x15a00 <pd_handle_event+0xf4>
   159f0:      	cmp	w22, #0x6
   159f4:      	b.ne	0x15a0c <pd_handle_event+0x100>
   159f8:      	mov	w8, #0x2
   159fc:      	b	0x15a04 <pd_handle_event+0xf8>
   15a00:      	mov	w8, #0x1
   15a04:      	adrp	x9, 0x15000 <pd_send_soft_reset+0x88>
		0000000000015a04:  R_AARCH64_ADR_PREL_PG_HI21	pd_usb_connected
   15a08:      	str	w8, [x9]
		0000000000015a08:  R_AARCH64_LDST32_ABS_LO12_NC	pd_usb_connected
   15a0c:      	bl	0x15a0c <pd_handle_event+0x100>
		0000000000015a0c:  R_AARCH64_CALL26	pe_get_exit_action
   15a10:      	mov	x21, x0
   15a14:      	cmp	w22, #0x9d
   15a18:      	b.hi	0x15b84 <pd_handle_event+0x278>
   15a1c:      	lsl	x8, x22, #3
   15a20:      	adrp	x9, 0x15000 <pd_send_soft_reset+0x88>
		0000000000015a20:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x8a8
   15a24:      	add	x9, x9, #0x0
		0000000000015a24:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x8a8
   15a28:      	adrp	x10, 0x15000 <pd_send_soft_reset+0x88>
		0000000000015a28:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0xd98
   15a2c:      	add	x10, x10, #0x0
		0000000000015a2c:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0xd98
   15a30:      	ldrb	w11, [x20, #0x2f0]
   15a34:      	ldrb	w13, [x20, #0x3f]
   15a38:      	adrp	x12, 0x15000 <pd_send_soft_reset+0x88>
		0000000000015a38:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x290d
   15a3c:      	add	x12, x12, #0x0
		0000000000015a3c:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x290d
   15a40:      	ldr	x23, [x9, x8]
   15a44:      	ldr	x2, [x10, x8]
   15a48:      	adrp	x9, 0x15000 <pd_send_soft_reset+0x88>
		0000000000015a48:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0xd53
   15a4c:      	add	x9, x9, #0x0
		0000000000015a4c:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0xd53
   15a50:      	ldrb	w8, [x20, #0x3e]
   15a54:      	cmp	w11, #0x0
   15a58:      	ldrb	w11, [x20, #0x40]
   15a5c:      	csel	x1, x12, x9, eq
   15a60:      	cmp	w13, #0x0
   15a64:      	mov	w9, #0x50
   15a68:      	mov	w10, #0x43
   15a6c:      	csel	w3, w10, w9, eq
   15a70:      	cmp	w8, #0x0
   15a74:      	mov	w8, #0x44
   15a78:      	mov	w9, #0x55
   15a7c:      	csel	w4, w9, w8, eq
   15a80:      	cmp	w11, #0x0
   15a84:      	mov	w8, #0x59
   15a88:      	mov	w9, #0x4e
   15a8c:      	csel	w5, w9, w8, eq
   15a90:      	adrp	x0, 0x15000 <pd_send_soft_reset+0x88>
		0000000000015a90:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0xac1
   15a94:      	add	x0, x0, #0x0
		0000000000015a94:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0xac1
   15a98:      	bl	0x15a98 <pd_handle_event+0x18c>
		0000000000015a98:  R_AARCH64_CALL26	pd_dbg_info
   15a9c:      	ldrh	w8, [x20, #0x6a]
   15aa0:      	tbz	w8, #0x8, 0x15ab0 <pd_handle_event+0x1a4>
   15aa4:      	ldr	x0, [x20]
   15aa8:      	mov	w1, #0x7
   15aac:      	bl	0x15aac <pd_handle_event+0x1a0>
		0000000000015aac:  R_AARCH64_CALL26	tcpc_disable_timer
   15ab0:      	ldrb	w8, [x20, #0x2f0]
   15ab4:      	cbz	w8, 0x15b38 <pd_handle_event+0x22c>
   15ab8:      	mov	x24, x20
   15abc:      	ldr	w1, [x24, #0x74]!
   15ac0:      	sturb	wzr, [x24, #-0x8]
   15ac4:      	cmp	w1, #0x35
   15ac8:      	b.hi	0x15adc <pd_handle_event+0x1d0>
   15acc:      	ldr	x0, [x20]
   15ad0:      	bl	0x15ad0 <pd_handle_event+0x1c4>
		0000000000015ad0:  R_AARCH64_CALL26	tcpc_disable_timer
   15ad4:      	mov	w8, #0x36
   15ad8:      	str	w8, [x24]
   15adc:      	strh	wzr, [x20, #0x6a]
   15ae0:      	cbz	x21, 0x15b04 <pd_handle_event+0x1f8>
   15ae4:      	mov	x0, x20
   15ae8:      	ldur	w16, [x21, #-0x4]
   15aec:      	movk	w17, #0xc3b8
   15af0:      	movk	w17, #0xa866, lsl #16
   15af4:      	cmp	w16, w17
   15af8:      	b.eq	0x15b00 <pd_handle_event+0x1f4>
   15afc:      	brk	#0x8235
   15b00:      	blr	x21
   15b04:      	cbz	x23, 0x15b28 <pd_handle_event+0x21c>
   15b08:      	mov	x0, x20
   15b0c:      	ldur	w16, [x23, #-0x4]
   15b10:      	movk	w17, #0xc3b8
   15b14:      	movk	w17, #0xa866, lsl #16
   15b18:      	cmp	w16, w17
   15b1c:      	b.eq	0x15b24 <pd_handle_event+0x218>
   15b20:      	brk	#0x8237
   15b24:      	blr	x23
   15b28:      	ldrb	w8, [x20, #0x2f0]
   15b2c:      	cbz	w8, 0x15b4c <pd_handle_event+0x240>
   15b30:      	strb	w22, [x20, #0x3b]
   15b34:      	b	0x15b50 <pd_handle_event+0x244>
   15b38:      	mov	x24, x20
   15b3c:      	ldr	w1, [x24, #0x70]!
   15b40:      	cmp	w1, #0x35
   15b44:      	b.ls	0x15acc <pd_handle_event+0x1c0>
   15b48:      	b	0x15adc <pd_handle_event+0x1d0>
   15b4c:      	strb	w22, [x20, #0x3a]
   15b50:      	strb	w22, [x20, #0x3d]
   15b54:      	ldr	x0, [x20]
   15b58:      	mov	x1, x19
   15b5c:      	bl	0x15b5c <pd_handle_event+0x250>
		0000000000015b5c:  R_AARCH64_CALL26	pd_free_event
   15b60:      	ldp	x20, x19, [sp, #0x30]
   15b64:      	ldp	x22, x21, [sp, #0x20]
   15b68:      	ldp	x24, x23, [sp, #0x10]
   15b6c:      	ldp	x29, x30, [sp], #0x40
   15b70:      	autiasp
   15b74:      	ret
   15b78:      	mov	x21, xzr
   15b7c:      	cmp	w22, #0x9d
   15b80:      	b.ls	0x15a1c <pd_handle_event+0x110>
   15b84:      	brk	#0x1
