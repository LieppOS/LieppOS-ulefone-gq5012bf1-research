source pd_dpm_snk_standby_power section=.text address=0x174a4 size=272
   174a4:      	paciasp
   174a8:      	stp	x29, x30, [sp, #-0x30]!
   174ac:      	str	x21, [sp, #0x10]
   174b0:      	stp	x20, x19, [sp, #0x20]
   174b4:      	mov	x29, sp
   174b8:      	ldr	w10, [x0, #0x190]
   174bc:      	mov	w9, #0x1388
   174c0:      	ldr	w8, [x0, #0x198]
   174c4:      	mov	x19, x0
   174c8:      	cmp	w10, w8
   174cc:      	csel	w20, w10, w8, gt
   174d0:      	cmp	w8, w9
   174d4:      	ldrb	w9, [x0, #0x4d]
   174d8:      	cset	w21, gt
   174dc:      	cbnz	w9, 0x17524 <pd_dpm_snk_standby_power+0x80>
   174e0:      	mov	w9, #0x1389
   174e4:      	cmp	w8, w9
   174e8:      	b.lt	0x17524 <pd_dpm_snk_standby_power+0x80>
   174ec:      	mov	w8, #0x2c8c
   174f0:      	ldr	x9, [x19]
   174f4:      	ldrb	w8, [x9, x8]
   174f8:      	tbz	w8, #0x6, 0x17524 <pd_dpm_snk_standby_power+0x80>
   174fc:      	adrp	x0, 0x17000 <pd_dpm_build_rdo+0x4>
		00000000000174fc:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x810
   17500:      	add	x0, x0, #0x0
		0000000000017500:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x810
   17504:      	mov	w1, #0x1
   17508:      	bl	0x17508 <pd_dpm_snk_standby_power+0x64>
		0000000000017508:  R_AARCH64_CALL26	pd_dbg_info
   1750c:      	ldrb	w8, [x19, #0x40]
   17510:      	mov	x0, x19
   17514:      	mov	w1, wzr
   17518:      	strb	w8, [x19, #0x4e]
   1751c:      	bl	0x1751c <pd_dpm_snk_standby_power+0x78>
		000000000001751c:  R_AARCH64_CALL26	pd_set_vconn
   17520:      	strb	w21, [x19, #0x4d]
   17524:      	ldr	w8, [x19, #0x15c]
   17528:      	ldr	w9, [x19, #0x160]
   1752c:      	cmp	w8, w9
   17530:      	b.ne	0x1753c <pd_dpm_snk_standby_power+0x98>
   17534:      	ldrb	w8, [x19, #0x1b0]
   17538:      	cbnz	w8, 0x175a0 <pd_dpm_snk_standby_power+0xfc>
   1753c:      	mov	w8, #0x25a0
   17540:      	ldr	w2, [x19, #0x198]
   17544:      	movk	w8, #0x26, lsl #16
   17548:      	ldr	w10, [x19, #0x190]
   1754c:      	sdiv	w9, w8, w20
   17550:      	ldr	w8, [x19, #0x19c]
   17554:      	cmp	w9, w8
   17558:      	csel	w3, w9, w8, lt
   1755c:      	cmp	w2, w10
   17560:      	b.le	0x17570 <pd_dpm_snk_standby_power+0xcc>
   17564:      	mov	w1, #0x6
   17568:      	tbz	w3, #0x1f, 0x17598 <pd_dpm_snk_standby_power+0xf4>
   1756c:      	b	0x175a0 <pd_dpm_snk_standby_power+0xfc>
   17570:      	b.ge	0x17580 <pd_dpm_snk_standby_power+0xdc>
   17574:      	mov	w1, #0x7
   17578:      	tbz	w3, #0x1f, 0x17598 <pd_dpm_snk_standby_power+0xf4>
   1757c:      	b	0x175a0 <pd_dpm_snk_standby_power+0xfc>
   17580:      	ldr	w9, [x19, #0x194]
   17584:      	cmp	w8, w9
   17588:      	b.ge	0x175a0 <pd_dpm_snk_standby_power+0xfc>
   1758c:      	mov	w1, #0x5
   17590:      	mov	w3, w8
   17594:      	tbnz	w3, #0x1f, 0x175a0 <pd_dpm_snk_standby_power+0xfc>
   17598:      	ldr	x0, [x19]
   1759c:      	bl	0x1759c <pd_dpm_snk_standby_power+0xf8>
		000000000001759c:  R_AARCH64_CALL26	tcpci_sink_vbus
   175a0:      	ldp	x20, x19, [sp, #0x20]
   175a4:      	ldr	x21, [sp, #0x10]
   175a8:      	ldp	x29, x30, [sp], #0x30
   175ac:      	autiasp
   175b0:      	ret
