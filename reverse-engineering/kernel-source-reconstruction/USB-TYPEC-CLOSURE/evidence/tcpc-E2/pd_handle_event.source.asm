source pd_handle_event section=.text address=0x158d0 size=568
   158d0:      	paciasp
   158d4:      	stp	x29, x30, [sp, #-0x40]!
   158d8:      	stp	x24, x23, [sp, #0x10]
   158dc:      	stp	x22, x21, [sp, #0x20]
   158e0:      	stp	x20, x19, [sp, #0x30]
   158e4:      	mov	x29, sp
   158e8:      	mov	x20, x0
   158ec:      	ldrb	w8, [x0, #0x2f0]
   158f0:      	mov	x19, x1
   158f4:      	cbz	w8, 0x15948 <pd_handle_event+0x78>
   158f8:      	ldrb	w8, [x20, #0x4a]
   158fc:      	cbz	w8, 0x15908 <pd_handle_event+0x38>
   15900:      	ldrb	w8, [x20, #0x6c]
   15904:      	tbz	w8, #0x1, 0x15914 <pd_handle_event+0x44>
   15908:      	ldrb	w8, [x19]
   1590c:      	cmp	w8, #0x8
   15910:      	b.ne	0x15940 <pd_handle_event+0x70>
   15914:      	ldr	w1, [x20, #0x74]
   15918:      	strb	wzr, [x20, #0x4a]
   1591c:      	ldrb	w8, [x20, #0x3a]
   15920:      	strb	wzr, [x20, #0x6c]
   15924:      	cmp	w1, #0x35
   15928:      	strb	w8, [x20, #0x3b]
   1592c:      	b.hi	0x15940 <pd_handle_event+0x70>
   15930:      	ldr	x0, [x20]
   15934:      	bl	0x15934 <pd_handle_event+0x64>
		0000000000015934:  R_AARCH64_CALL26	tcpc_disable_timer
   15938:      	mov	w8, #0x36
   1593c:      	str	w8, [x20, #0x74]
   15940:      	add	x8, x20, #0x3b
   15944:      	b	0x1594c <pd_handle_event+0x7c>
   15948:      	add	x8, x20, #0x3a
   1594c:      	ldrb	w8, [x8]
   15950:      	mov	x0, x20
   15954:      	mov	x1, x19
   15958:      	strb	w8, [x20, #0x3d]
   1595c:      	bl	0x1595c <pd_handle_event+0x8c>
		000000000001595c:  R_AARCH64_CALL26	pd_process_event
   15960:      	tbz	w0, #0x0, 0x15ae0 <pd_handle_event+0x210>
   15964:      	ldrb	w0, [x20, #0x3d]
   15968:      	cmp	w0, #0x9d
   1596c:      	b.hi	0x15abc <pd_handle_event+0x1ec>
   15970:      	ldrb	w22, [x20, #0x3c]
   15974:      	cmp	w22, #0x9e
   15978:      	b.hs	0x15abc <pd_handle_event+0x1ec>
   1597c:      	mov	x21, xzr
   15980:      	cmp	w22, #0x9b
   15984:      	b.hi	0x15998 <pd_handle_event+0xc8>
   15988:      	cmp	w22, #0x98
   1598c:      	b.eq	0x15998 <pd_handle_event+0xc8>
   15990:      	bl	0x15990 <pd_handle_event+0xc0>
		0000000000015990:  R_AARCH64_CALL26	pe_get_exit_action
   15994:      	mov	x21, x0
   15998:      	cmp	w22, #0x9d
   1599c:      	b.hi	0x15b04 <pd_handle_event+0x234>
   159a0:      	lsl	x8, x22, #3
   159a4:      	adrp	x9, 0x15000 <pd_send_soft_reset+0xc4>
		00000000000159a4:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x8a8
   159a8:      	add	x9, x9, #0x0
		00000000000159a8:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x8a8
   159ac:      	adrp	x10, 0x15000 <pd_send_soft_reset+0xc4>
		00000000000159ac:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0xd98
   159b0:      	add	x10, x10, #0x0
		00000000000159b0:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0xd98
   159b4:      	ldrb	w11, [x20, #0x2f0]
   159b8:      	ldrb	w13, [x20, #0x3f]
   159bc:      	adrp	x12, 0x15000 <pd_send_soft_reset+0xc4>
		00000000000159bc:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x28f5
   159c0:      	add	x12, x12, #0x0
		00000000000159c0:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x28f5
   159c4:      	ldr	x23, [x9, x8]
   159c8:      	ldr	x2, [x10, x8]
   159cc:      	adrp	x9, 0x15000 <pd_send_soft_reset+0xc4>
		00000000000159cc:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0xd3b
   159d0:      	add	x9, x9, #0x0
		00000000000159d0:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0xd3b
   159d4:      	ldrb	w8, [x20, #0x3e]
   159d8:      	cmp	w11, #0x0
   159dc:      	ldrb	w11, [x20, #0x40]
   159e0:      	csel	x1, x12, x9, eq
   159e4:      	cmp	w13, #0x0
   159e8:      	mov	w9, #0x50
   159ec:      	mov	w10, #0x43
   159f0:      	csel	w3, w10, w9, eq
   159f4:      	cmp	w8, #0x0
   159f8:      	mov	w8, #0x44
   159fc:      	mov	w9, #0x55
   15a00:      	csel	w4, w9, w8, eq
   15a04:      	cmp	w11, #0x0
   15a08:      	mov	w8, #0x59
   15a0c:      	mov	w9, #0x4e
   15a10:      	csel	w5, w9, w8, eq
   15a14:      	adrp	x0, 0x15000 <pd_send_soft_reset+0xc4>
		0000000000015a14:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0xaa9
   15a18:      	add	x0, x0, #0x0
		0000000000015a18:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0xaa9
   15a1c:      	bl	0x15a1c <pd_handle_event+0x14c>
		0000000000015a1c:  R_AARCH64_CALL26	pd_dbg_info
   15a20:      	ldrh	w8, [x20, #0x6a]
   15a24:      	tbz	w8, #0x8, 0x15a34 <pd_handle_event+0x164>
   15a28:      	ldr	x0, [x20]
   15a2c:      	mov	w1, #0x7
   15a30:      	bl	0x15a30 <pd_handle_event+0x160>
		0000000000015a30:  R_AARCH64_CALL26	tcpc_disable_timer
   15a34:      	ldrb	w8, [x20, #0x2f0]
   15a38:      	cbz	w8, 0x15ac4 <pd_handle_event+0x1f4>
   15a3c:      	mov	x24, x20
   15a40:      	ldr	w1, [x24, #0x74]!
   15a44:      	sturb	wzr, [x24, #-0x8]
   15a48:      	cmp	w1, #0x35
   15a4c:      	b.hi	0x15a60 <pd_handle_event+0x190>
   15a50:      	ldr	x0, [x20]
   15a54:      	bl	0x15a54 <pd_handle_event+0x184>
		0000000000015a54:  R_AARCH64_CALL26	tcpc_disable_timer
   15a58:      	mov	w8, #0x36
   15a5c:      	str	w8, [x24]
   15a60:      	strh	wzr, [x20, #0x6a]
   15a64:      	cbz	x21, 0x15a88 <pd_handle_event+0x1b8>
   15a68:      	mov	x0, x20
   15a6c:      	ldur	w16, [x21, #-0x4]
   15a70:      	movk	w17, #0xc3b8
   15a74:      	movk	w17, #0xa866, lsl #16
   15a78:      	cmp	w16, w17
   15a7c:      	b.eq	0x15a84 <pd_handle_event+0x1b4>
   15a80:      	brk	#0x8235
   15a84:      	blr	x21
   15a88:      	cbz	x23, 0x15aac <pd_handle_event+0x1dc>
   15a8c:      	mov	x0, x20
   15a90:      	ldur	w16, [x23, #-0x4]
   15a94:      	movk	w17, #0xc3b8
   15a98:      	movk	w17, #0xa866, lsl #16
   15a9c:      	cmp	w16, w17
   15aa0:      	b.eq	0x15aa8 <pd_handle_event+0x1d8>
   15aa4:      	brk	#0x8237
   15aa8:      	blr	x23
   15aac:      	ldrb	w8, [x20, #0x2f0]
   15ab0:      	cbz	w8, 0x15ad8 <pd_handle_event+0x208>
   15ab4:      	strb	w22, [x20, #0x3b]
   15ab8:      	b	0x15adc <pd_handle_event+0x20c>
   15abc:      	brk	#0x800
   15ac0:      	b	0x15ae0 <pd_handle_event+0x210>
   15ac4:      	mov	x24, x20
   15ac8:      	ldr	w1, [x24, #0x70]!
   15acc:      	cmp	w1, #0x35
   15ad0:      	b.ls	0x15a50 <pd_handle_event+0x180>
   15ad4:      	b	0x15a60 <pd_handle_event+0x190>
   15ad8:      	strb	w22, [x20, #0x3a]
   15adc:      	strb	w22, [x20, #0x3d]
   15ae0:      	ldr	x0, [x20]
   15ae4:      	mov	x1, x19
   15ae8:      	bl	0x15ae8 <pd_handle_event+0x218>
		0000000000015ae8:  R_AARCH64_CALL26	pd_free_event
   15aec:      	ldp	x20, x19, [sp, #0x30]
   15af0:      	ldp	x22, x21, [sp, #0x20]
   15af4:      	ldp	x24, x23, [sp, #0x10]
   15af8:      	ldp	x29, x30, [sp], #0x40
   15afc:      	autiasp
   15b00:      	ret
   15b04:      	brk	#0x1
