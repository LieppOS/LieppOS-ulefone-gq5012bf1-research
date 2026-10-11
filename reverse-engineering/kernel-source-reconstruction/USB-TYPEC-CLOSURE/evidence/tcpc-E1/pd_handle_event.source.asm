source pd_handle_event section=.text address=0x158ec size=568
   158ec:      	paciasp
   158f0:      	stp	x29, x30, [sp, #-0x40]!
   158f4:      	stp	x24, x23, [sp, #0x10]
   158f8:      	stp	x22, x21, [sp, #0x20]
   158fc:      	stp	x20, x19, [sp, #0x30]
   15900:      	mov	x29, sp
   15904:      	mov	x20, x0
   15908:      	ldrb	w8, [x0, #0x2f0]
   1590c:      	mov	x19, x1
   15910:      	cbz	w8, 0x15964 <pd_handle_event+0x78>
   15914:      	ldrb	w8, [x20, #0x4a]
   15918:      	cbz	w8, 0x15924 <pd_handle_event+0x38>
   1591c:      	ldrb	w8, [x20, #0x6c]
   15920:      	tbz	w8, #0x1, 0x15930 <pd_handle_event+0x44>
   15924:      	ldrb	w8, [x19]
   15928:      	cmp	w8, #0x8
   1592c:      	b.ne	0x1595c <pd_handle_event+0x70>
   15930:      	ldr	w1, [x20, #0x74]
   15934:      	strb	wzr, [x20, #0x4a]
   15938:      	ldrb	w8, [x20, #0x3a]
   1593c:      	strb	wzr, [x20, #0x6c]
   15940:      	cmp	w1, #0x35
   15944:      	strb	w8, [x20, #0x3b]
   15948:      	b.hi	0x1595c <pd_handle_event+0x70>
   1594c:      	ldr	x0, [x20]
   15950:      	bl	0x15950 <pd_handle_event+0x64>
		0000000000015950:  R_AARCH64_CALL26	tcpc_disable_timer
   15954:      	mov	w8, #0x36
   15958:      	str	w8, [x20, #0x74]
   1595c:      	add	x8, x20, #0x3b
   15960:      	b	0x15968 <pd_handle_event+0x7c>
   15964:      	add	x8, x20, #0x3a
   15968:      	ldrb	w8, [x8]
   1596c:      	mov	x0, x20
   15970:      	mov	x1, x19
   15974:      	strb	w8, [x20, #0x3d]
   15978:      	bl	0x15978 <pd_handle_event+0x8c>
		0000000000015978:  R_AARCH64_CALL26	pd_process_event
   1597c:      	tbz	w0, #0x0, 0x15afc <pd_handle_event+0x210>
   15980:      	ldrb	w0, [x20, #0x3d]
   15984:      	cmp	w0, #0x9d
   15988:      	b.hi	0x15ad8 <pd_handle_event+0x1ec>
   1598c:      	ldrb	w22, [x20, #0x3c]
   15990:      	cmp	w22, #0x9e
   15994:      	b.hs	0x15ad8 <pd_handle_event+0x1ec>
   15998:      	mov	x21, xzr
   1599c:      	cmp	w22, #0x9b
   159a0:      	b.hi	0x159b4 <pd_handle_event+0xc8>
   159a4:      	cmp	w22, #0x98
   159a8:      	b.eq	0x159b4 <pd_handle_event+0xc8>
   159ac:      	bl	0x159ac <pd_handle_event+0xc0>
		00000000000159ac:  R_AARCH64_CALL26	pe_get_exit_action
   159b0:      	mov	x21, x0
   159b4:      	cmp	w22, #0x9d
   159b8:      	b.hi	0x15b20 <pd_handle_event+0x234>
   159bc:      	lsl	x8, x22, #3
   159c0:      	adrp	x9, 0x15000 <pd_send_soft_reset+0xa8>
		00000000000159c0:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x8a8
   159c4:      	add	x9, x9, #0x0
		00000000000159c4:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x8a8
   159c8:      	adrp	x10, 0x15000 <pd_send_soft_reset+0xa8>
		00000000000159c8:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0xd98
   159cc:      	add	x10, x10, #0x0
		00000000000159cc:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0xd98
   159d0:      	ldrb	w11, [x20, #0x2f0]
   159d4:      	ldrb	w13, [x20, #0x3f]
   159d8:      	adrp	x12, 0x15000 <pd_send_soft_reset+0xa8>
		00000000000159d8:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x28f5
   159dc:      	add	x12, x12, #0x0
		00000000000159dc:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x28f5
   159e0:      	ldr	x23, [x9, x8]
   159e4:      	ldr	x2, [x10, x8]
   159e8:      	adrp	x9, 0x15000 <pd_send_soft_reset+0xa8>
		00000000000159e8:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0xd3b
   159ec:      	add	x9, x9, #0x0
		00000000000159ec:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0xd3b
   159f0:      	ldrb	w8, [x20, #0x3e]
   159f4:      	cmp	w11, #0x0
   159f8:      	ldrb	w11, [x20, #0x40]
   159fc:      	csel	x1, x12, x9, eq
   15a00:      	cmp	w13, #0x0
   15a04:      	mov	w9, #0x50
   15a08:      	mov	w10, #0x43
   15a0c:      	csel	w3, w10, w9, eq
   15a10:      	cmp	w8, #0x0
   15a14:      	mov	w8, #0x44
   15a18:      	mov	w9, #0x55
   15a1c:      	csel	w4, w9, w8, eq
   15a20:      	cmp	w11, #0x0
   15a24:      	mov	w8, #0x59
   15a28:      	mov	w9, #0x4e
   15a2c:      	csel	w5, w9, w8, eq
   15a30:      	adrp	x0, 0x15000 <pd_send_soft_reset+0xa8>
		0000000000015a30:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0xaa9
   15a34:      	add	x0, x0, #0x0
		0000000000015a34:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0xaa9
   15a38:      	bl	0x15a38 <pd_handle_event+0x14c>
		0000000000015a38:  R_AARCH64_CALL26	pd_dbg_info
   15a3c:      	ldrh	w8, [x20, #0x6a]
   15a40:      	tbz	w8, #0x8, 0x15a50 <pd_handle_event+0x164>
   15a44:      	ldr	x0, [x20]
   15a48:      	mov	w1, #0x7
   15a4c:      	bl	0x15a4c <pd_handle_event+0x160>
		0000000000015a4c:  R_AARCH64_CALL26	tcpc_disable_timer
   15a50:      	ldrb	w8, [x20, #0x2f0]
   15a54:      	cbz	w8, 0x15ae0 <pd_handle_event+0x1f4>
   15a58:      	mov	x24, x20
   15a5c:      	ldr	w1, [x24, #0x74]!
   15a60:      	sturb	wzr, [x24, #-0x8]
   15a64:      	cmp	w1, #0x35
   15a68:      	b.hi	0x15a7c <pd_handle_event+0x190>
   15a6c:      	ldr	x0, [x20]
   15a70:      	bl	0x15a70 <pd_handle_event+0x184>
		0000000000015a70:  R_AARCH64_CALL26	tcpc_disable_timer
   15a74:      	mov	w8, #0x36
   15a78:      	str	w8, [x24]
   15a7c:      	strh	wzr, [x20, #0x6a]
   15a80:      	cbz	x21, 0x15aa4 <pd_handle_event+0x1b8>
   15a84:      	mov	x0, x20
   15a88:      	ldur	w16, [x21, #-0x4]
   15a8c:      	movk	w17, #0xc3b8
   15a90:      	movk	w17, #0xa866, lsl #16
   15a94:      	cmp	w16, w17
   15a98:      	b.eq	0x15aa0 <pd_handle_event+0x1b4>
   15a9c:      	brk	#0x8235
   15aa0:      	blr	x21
   15aa4:      	cbz	x23, 0x15ac8 <pd_handle_event+0x1dc>
   15aa8:      	mov	x0, x20
   15aac:      	ldur	w16, [x23, #-0x4]
   15ab0:      	movk	w17, #0xc3b8
   15ab4:      	movk	w17, #0xa866, lsl #16
   15ab8:      	cmp	w16, w17
   15abc:      	b.eq	0x15ac4 <pd_handle_event+0x1d8>
   15ac0:      	brk	#0x8237
   15ac4:      	blr	x23
   15ac8:      	ldrb	w8, [x20, #0x2f0]
   15acc:      	cbz	w8, 0x15af4 <pd_handle_event+0x208>
   15ad0:      	strb	w22, [x20, #0x3b]
   15ad4:      	b	0x15af8 <pd_handle_event+0x20c>
   15ad8:      	brk	#0x800
   15adc:      	b	0x15afc <pd_handle_event+0x210>
   15ae0:      	mov	x24, x20
   15ae4:      	ldr	w1, [x24, #0x70]!
   15ae8:      	cmp	w1, #0x35
   15aec:      	b.ls	0x15a6c <pd_handle_event+0x180>
   15af0:      	b	0x15a7c <pd_handle_event+0x190>
   15af4:      	strb	w22, [x20, #0x3a]
   15af8:      	strb	w22, [x20, #0x3d]
   15afc:      	ldr	x0, [x20]
   15b00:      	mov	x1, x19
   15b04:      	bl	0x15b04 <pd_handle_event+0x218>
		0000000000015b04:  R_AARCH64_CALL26	pd_free_event
   15b08:      	ldp	x20, x19, [sp, #0x30]
   15b0c:      	ldp	x22, x21, [sp, #0x20]
   15b10:      	ldp	x24, x23, [sp, #0x10]
   15b14:      	ldp	x29, x30, [sp], #0x40
   15b18:      	autiasp
   15b1c:      	ret
   15b20:      	brk	#0x1
