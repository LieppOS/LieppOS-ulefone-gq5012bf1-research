stock pd_dpm_snk_standby_power section=.text address=0x173ec size=280
   173ec:      	paciasp
   173f0:      	stp	x29, x30, [sp, #-0x30]!
   173f4:      	str	x21, [sp, #0x10]
   173f8:      	stp	x20, x19, [sp, #0x20]
   173fc:      	mov	x29, sp
   17400:      	ldr	w10, [x0, #0x190]
   17404:      	mov	w9, #0x1388
   17408:      	ldr	w8, [x0, #0x198]
   1740c:      	mov	x19, x0
   17410:      	cmp	w10, w8
   17414:      	csel	w20, w10, w8, gt
   17418:      	cmp	w8, w9
   1741c:      	ldrb	w9, [x0, #0x4d]
   17420:      	cset	w21, gt
   17424:      	cbnz	w9, 0x1746c <pd_dpm_snk_standby_power+0x80>
   17428:      	mov	w9, #0x1389
   1742c:      	cmp	w8, w9
   17430:      	b.lt	0x1746c <pd_dpm_snk_standby_power+0x80>
   17434:      	mov	w8, #0x2c8c
   17438:      	ldr	x9, [x19]
   1743c:      	ldrb	w8, [x9, x8]
   17440:      	tbz	w8, #0x6, 0x1746c <pd_dpm_snk_standby_power+0x80>
   17444:      	adrp	x0, 0x17000 <pd_dpm_build_rdo+0xbc>
		0000000000017444:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x874
   17448:      	add	x0, x0, #0x0
		0000000000017448:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x874
   1744c:      	mov	w1, #0x1
   17450:      	bl	0x17450 <pd_dpm_snk_standby_power+0x64>
		0000000000017450:  R_AARCH64_CALL26	pd_dbg_info
   17454:      	ldrb	w8, [x19, #0x40]
   17458:      	mov	x0, x19
   1745c:      	mov	w1, wzr
   17460:      	strb	w8, [x19, #0x4e]
   17464:      	bl	0x17464 <pd_dpm_snk_standby_power+0x78>
		0000000000017464:  R_AARCH64_CALL26	pd_set_vconn
   17468:      	strb	w21, [x19, #0x4d]
   1746c:      	ldr	w8, [x19, #0x15c]
   17470:      	ldr	w9, [x19, #0x160]
   17474:      	cmp	w8, w9
   17478:      	b.ne	0x17484 <pd_dpm_snk_standby_power+0x98>
   1747c:      	ldrb	w8, [x19, #0x1b0]
   17480:      	cbnz	w8, 0x174f0 <pd_dpm_snk_standby_power+0x104>
   17484:      	ldr	w2, [x19, #0x198]
   17488:      	ldr	w8, [x19, #0x190]
   1748c:      	cmp	w2, w8
   17490:      	b.ne	0x174a8 <pd_dpm_snk_standby_power+0xbc>
   17494:      	ldr	w10, [x19, #0x19c]
   17498:      	ldr	w9, [x19, #0x194]
   1749c:      	cmp	w10, w9
   174a0:      	b.ne	0x174ac <pd_dpm_snk_standby_power+0xc0>
   174a4:      	b	0x174f0 <pd_dpm_snk_standby_power+0x104>
   174a8:      	ldr	w9, [x19, #0x194]
   174ac:      	mov	w10, #0x25a0
   174b0:      	ldr	w11, [x19, #0x19c]
   174b4:      	movk	w10, #0x26, lsl #16
   174b8:      	sdiv	w10, w10, w20
   174bc:      	cmp	w9, w10
   174c0:      	ccmp	w9, w11, #0x0, le
   174c4:      	b.le	0x174f0 <pd_dpm_snk_standby_power+0x104>
   174c8:      	cmp	w10, w11
   174cc:      	mov	w9, #0x7
   174d0:      	csel	w3, w10, w11, lt
   174d4:      	cmp	w2, w8
   174d8:      	mov	w8, #0x5
   174dc:      	ldr	x0, [x19]
   174e0:      	csel	w8, w9, w8, lt
   174e4:      	mov	w9, #0x6
   174e8:      	csel	w1, w9, w8, gt
   174ec:      	bl	0x174ec <pd_dpm_snk_standby_power+0x100>
		00000000000174ec:  R_AARCH64_CALL26	tcpci_sink_vbus
   174f0:      	ldp	x20, x19, [sp, #0x20]
   174f4:      	ldr	x21, [sp, #0x10]
   174f8:      	ldp	x29, x30, [sp], #0x30
   174fc:      	autiasp
   17500:      	ret
