source pd_dpm_snk_standby_power section=.text address=0x17408 size=272
   17408:      	paciasp
   1740c:      	stp	x29, x30, [sp, #-0x30]!
   17410:      	str	x21, [sp, #0x10]
   17414:      	stp	x20, x19, [sp, #0x20]
   17418:      	mov	x29, sp
   1741c:      	ldr	w10, [x0, #0x190]
   17420:      	mov	w9, #0x1388
   17424:      	ldr	w8, [x0, #0x198]
   17428:      	mov	x19, x0
   1742c:      	cmp	w10, w8
   17430:      	csel	w20, w10, w8, gt
   17434:      	cmp	w8, w9
   17438:      	ldrb	w9, [x0, #0x4d]
   1743c:      	cset	w21, gt
   17440:      	cbnz	w9, 0x17488 <pd_dpm_snk_standby_power+0x80>
   17444:      	mov	w9, #0x1389
   17448:      	cmp	w8, w9
   1744c:      	b.lt	0x17488 <pd_dpm_snk_standby_power+0x80>
   17450:      	mov	w8, #0x2c8c
   17454:      	ldr	x9, [x19]
   17458:      	ldrb	w8, [x9, x8]
   1745c:      	tbz	w8, #0x6, 0x17488 <pd_dpm_snk_standby_power+0x80>
   17460:      	adrp	x0, 0x17000 <pd_dpm_build_rdo+0xa0>
		0000000000017460:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x7f8
   17464:      	add	x0, x0, #0x0
		0000000000017464:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x7f8
   17468:      	mov	w1, #0x1
   1746c:      	bl	0x1746c <pd_dpm_snk_standby_power+0x64>
		000000000001746c:  R_AARCH64_CALL26	pd_dbg_info
   17470:      	ldrb	w8, [x19, #0x40]
   17474:      	mov	x0, x19
   17478:      	mov	w1, wzr
   1747c:      	strb	w8, [x19, #0x4e]
   17480:      	bl	0x17480 <pd_dpm_snk_standby_power+0x78>
		0000000000017480:  R_AARCH64_CALL26	pd_set_vconn
   17484:      	strb	w21, [x19, #0x4d]
   17488:      	ldr	w8, [x19, #0x15c]
   1748c:      	ldr	w9, [x19, #0x160]
   17490:      	cmp	w8, w9
   17494:      	b.ne	0x174a0 <pd_dpm_snk_standby_power+0x98>
   17498:      	ldrb	w8, [x19, #0x1b0]
   1749c:      	cbnz	w8, 0x17504 <pd_dpm_snk_standby_power+0xfc>
   174a0:      	mov	w8, #0x25a0
   174a4:      	ldr	w2, [x19, #0x198]
   174a8:      	movk	w8, #0x26, lsl #16
   174ac:      	ldr	w10, [x19, #0x190]
   174b0:      	sdiv	w9, w8, w20
   174b4:      	ldr	w8, [x19, #0x19c]
   174b8:      	cmp	w9, w8
   174bc:      	csel	w3, w9, w8, lt
   174c0:      	cmp	w2, w10
   174c4:      	b.le	0x174d4 <pd_dpm_snk_standby_power+0xcc>
   174c8:      	mov	w1, #0x6
   174cc:      	tbz	w3, #0x1f, 0x174fc <pd_dpm_snk_standby_power+0xf4>
   174d0:      	b	0x17504 <pd_dpm_snk_standby_power+0xfc>
   174d4:      	b.ge	0x174e4 <pd_dpm_snk_standby_power+0xdc>
   174d8:      	mov	w1, #0x7
   174dc:      	tbz	w3, #0x1f, 0x174fc <pd_dpm_snk_standby_power+0xf4>
   174e0:      	b	0x17504 <pd_dpm_snk_standby_power+0xfc>
   174e4:      	ldr	w9, [x19, #0x194]
   174e8:      	cmp	w8, w9
   174ec:      	b.ge	0x17504 <pd_dpm_snk_standby_power+0xfc>
   174f0:      	mov	w1, #0x5
   174f4:      	mov	w3, w8
   174f8:      	tbnz	w3, #0x1f, 0x17504 <pd_dpm_snk_standby_power+0xfc>
   174fc:      	ldr	x0, [x19]
   17500:      	bl	0x17500 <pd_dpm_snk_standby_power+0xf8>
		0000000000017500:  R_AARCH64_CALL26	tcpci_sink_vbus
   17504:      	ldp	x20, x19, [sp, #0x20]
   17508:      	ldr	x21, [sp, #0x10]
   1750c:      	ldp	x29, x30, [sp], #0x30
   17510:      	autiasp
   17514:      	ret
