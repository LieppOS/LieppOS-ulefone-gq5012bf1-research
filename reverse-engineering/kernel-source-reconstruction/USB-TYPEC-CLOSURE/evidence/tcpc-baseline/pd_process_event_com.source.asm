source pd_process_event_com section=.text address=0x1e2b8 size=1844
   1e2b8:      	paciasp
   1e2bc:      	sub	sp, sp, #0x50
   1e2c0:      	stp	x29, x30, [sp, #0x20]
   1e2c4:      	str	x21, [sp, #0x30]
   1e2c8:      	stp	x20, x19, [sp, #0x40]
   1e2cc:      	add	x29, sp, #0x20
   1e2d0:      	mrs	x8, SP_EL0
   1e2d4:      	mov	x19, x0
   1e2d8:      	ldr	x8, [x8, #0x638]
   1e2dc:      	mov	w0, wzr
   1e2e0:      	stur	x8, [x29, #-0x8]
   1e2e4:      	ldrb	w8, [x1]
   1e2e8:      	sub	w8, w8, #0x1
   1e2ec:      	cmp	w8, #0x6
   1e2f0:      	b.hi	0x1e9b8 <pd_process_event_com+0x700>
   1e2f4:      	adrp	x9, 0x1e000 <pd_process_event_tcp+0x200>
		000000000001e2f4:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x1c62
   1e2f8:      	add	x9, x9, #0x0
		000000000001e2f8:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x1c62
   1e2fc:      	mov	x20, x1
   1e300:      	adr	x10, #0x10
   1e304:      	ldrh	w11, [x9, x8, lsl #1]
   1e308:      	add	x10, x10, x11, lsl #2
   1e30c:      	br	x10
   1e310:      	ldrb	w10, [x19, #0x13d]
   1e314:      	ldrb	w8, [x19, #0x324]
   1e318:      	ldrb	w9, [x20, #0x1]
   1e31c:      	cmp	w10, #0x1
   1e320:      	b.hi	0x1e4b0 <pd_process_event_com+0x1f8>
   1e324:      	cmp	w9, #0x10
   1e328:      	b.lo	0x1e4b0 <pd_process_event_com+0x1f8>
   1e32c:      	mov	w8, #0x19
   1e330:      	b	0x1e4a4 <pd_process_event_com+0x1ec>
   1e334:      	ldrb	w10, [x19, #0x13d]
   1e338:      	ldrb	w8, [x19, #0x324]
   1e33c:      	ldrb	w9, [x20, #0x1]
   1e340:      	cmp	w10, #0x1
   1e344:      	b.hi	0x1e350 <pd_process_event_com+0x98>
   1e348:      	cmp	w9, #0x5
   1e34c:      	b.hs	0x1e4a0 <pd_process_event_com+0x1e8>
   1e350:      	mov	w0, wzr
   1e354:      	sub	w9, w9, #0x3
   1e358:      	cmp	w9, #0x9
   1e35c:      	b.hi	0x1e9b8 <pd_process_event_com+0x700>
   1e360:      	adrp	x10, 0x1e000 <pd_process_event_tcp+0x200>
		000000000001e360:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x1ccc
   1e364:      	add	x10, x10, #0x0
		000000000001e364:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x1ccc
   1e368:      	adr	x11, #0x10
   1e36c:      	ldrh	w12, [x10, x9, lsl #1]
   1e370:      	add	x11, x11, x12, lsl #2
   1e374:      	br	x11
   1e378:      	ldrb	w9, [x19, #0x3d]
   1e37c:      	cmp	w9, w8
   1e380:      	b.ne	0x1e960 <pd_process_event_com+0x6a8>
   1e384:      	ldr	w8, [x19, #0x190]
   1e388:      	mov	w9, #0x1389
   1e38c:      	cmp	w8, w9
   1e390:      	b.lt	0x1e90c <pd_process_event_com+0x654>
   1e394:      	adrp	x0, 0x1e000 <pd_process_event_tcp+0x200>
		000000000001e394:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x1de2
   1e398:      	add	x0, x0, #0x0
		000000000001e398:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x1de2
   1e39c:      	bl	0x1e39c <pd_process_event_com+0xe4>
		000000000001e39c:  R_AARCH64_CALL26	pd_dbg_info
   1e3a0:      	b	0x1e960 <pd_process_event_com+0x6a8>
   1e3a4:      	ldrb	w8, [x19, #0x13d]
   1e3a8:      	cmp	w8, #0x1
   1e3ac:      	b.ls	0x1e4a0 <pd_process_event_com+0x1e8>
   1e3b0:      	ldrb	w21, [x19, #0x324]
   1e3b4:      	ldrb	w8, [x19, #0x3d]
   1e3b8:      	cmp	w8, w21
   1e3bc:      	b.ne	0x1e508 <pd_process_event_com+0x250>
   1e3c0:      	mov	x0, x19
   1e3c4:      	bl	0x1e3c4 <pd_process_event_com+0x10c>
		000000000001e3c4:  R_AARCH64_CALL26	pd_is_multi_chunk_msg
   1e3c8:      	tbz	w0, #0x0, 0x1e508 <pd_process_event_com+0x250>
   1e3cc:      	mov	w8, #0x1
   1e3d0:      	mov	x0, x19
   1e3d4:      	mov	x1, x20
   1e3d8:      	strb	w8, [x19, #0x327]
   1e3dc:      	bl	0x1e3dc <pd_process_event_com+0x124>
		000000000001e3dc:  R_AARCH64_CALL26	pd_process_protocol_error
   1e3e0:      	b	0x1e9b8 <pd_process_event_com+0x700>
   1e3e4:      	ldrb	w8, [x20, #0x1]
   1e3e8:      	cmp	w8, #0x3
   1e3ec:      	b.eq	0x1e550 <pd_process_event_com+0x298>
   1e3f0:      	cmp	w8, #0x2
   1e3f4:      	b.eq	0x1e560 <pd_process_event_com+0x2a8>
   1e3f8:      	cbnz	w8, 0x1e960 <pd_process_event_com+0x6a8>
   1e3fc:      	ldrh	w8, [x19, #0x6a]
   1e400:      	tbz	w8, #0xa, 0x1e960 <pd_process_event_com+0x6a8>
   1e404:      	ldrb	w8, [x19, #0x324]
   1e408:      	b	0x1e9b0 <pd_process_event_com+0x6f8>
   1e40c:      	ldrb	w8, [x20, #0x1]
   1e410:      	sub	w9, w8, #0x7
   1e414:      	cmp	w9, #0x2
   1e418:      	b.lo	0x1e4e8 <pd_process_event_com+0x230>
   1e41c:      	cmp	w8, #0xa
   1e420:      	b.eq	0x1e574 <pd_process_event_com+0x2bc>
   1e424:      	cmp	w8, #0x2
   1e428:      	b.ne	0x1e960 <pd_process_event_com+0x6a8>
   1e42c:      	mov	w8, #0x2ff3
   1e430:      	ldr	x9, [x19]
   1e434:      	ldrb	w8, [x9, x8]
   1e438:      	cbz	w8, 0x1e448 <pd_process_event_com+0x190>
   1e43c:      	ldrb	w8, [x19, #0x78]
   1e440:      	add	w8, w8, #0x1
   1e444:      	strb	w8, [x19, #0x78]
   1e448:      	ldrb	w8, [x19, #0x3f]
   1e44c:      	mov	w9, #0x25
   1e450:      	cmp	w8, #0x0
   1e454:      	mov	w8, #0xa
   1e458:      	csel	w8, w9, w8, eq
   1e45c:      	b	0x1e9b0 <pd_process_event_com+0x6f8>
   1e460:      	ldrb	w8, [x20, #0x1]
   1e464:      	mov	w0, wzr
   1e468:      	sub	w8, w8, #0x1
   1e46c:      	cmp	w8, #0x21
   1e470:      	b.hi	0x1e9b8 <pd_process_event_com+0x700>
   1e474:      	adrp	x9, 0x1e000 <pd_process_event_tcp+0x200>
		000000000001e474:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x1c70
   1e478:      	add	x9, x9, #0x0
		000000000001e478:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x1c70
   1e47c:      	ldrb	w20, [x19, #0x324]
   1e480:      	adr	x10, #0x10
   1e484:      	ldrh	w11, [x9, x8, lsl #1]
   1e488:      	add	x10, x10, x11, lsl #2
   1e48c:      	br	x10
   1e490:      	ldrb	w8, [x19, #0x3d]
   1e494:      	cmp	w8, #0x9b
   1e498:      	b.eq	0x1e6f0 <pd_process_event_com+0x438>
   1e49c:      	b	0x1e960 <pd_process_event_com+0x6a8>
   1e4a0:      	mov	w8, #0x10
   1e4a4:      	mov	w0, wzr
   1e4a8:      	strb	w8, [x20, #0x1]
   1e4ac:      	b	0x1e9b8 <pd_process_event_com+0x700>
   1e4b0:      	mov	w0, wzr
   1e4b4:      	sub	w9, w9, #0x1
   1e4b8:      	cmp	w9, #0x17
   1e4bc:      	b.hi	0x1e9b8 <pd_process_event_com+0x700>
   1e4c0:      	adrp	x10, 0x1e000 <pd_process_event_tcp+0x200>
		000000000001e4c0:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x1ce0
   1e4c4:      	add	x10, x10, #0x0
		000000000001e4c4:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x1ce0
   1e4c8:      	adr	x11, #0x10
   1e4cc:      	ldrh	w12, [x10, x9, lsl #1]
   1e4d0:      	add	x11, x11, x12, lsl #2
   1e4d4:      	br	x11
   1e4d8:      	ldrh	w9, [x19, #0x6a]
   1e4dc:      	tbnz	w9, #0x9, 0x1e9b0 <pd_process_event_com+0x6f8>
   1e4e0:      	tbnz	w9, #0x8, 0x1e5bc <pd_process_event_com+0x304>
   1e4e4:      	b	0x1e960 <pd_process_event_com+0x6a8>
   1e4e8:      	ldrb	w8, [x19, #0x78]
   1e4ec:      	cmp	w8, #0x3
   1e4f0:      	b.lo	0x1e584 <pd_process_event_com+0x2cc>
   1e4f4:      	adrp	x0, 0x1e000 <pd_process_event_tcp+0x200>
		000000000001e4f4:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x2bd8
   1e4f8:      	add	x0, x0, #0x0
		000000000001e4f8:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x2bd8
   1e4fc:      	bl	0x1e4fc <pd_process_event_com+0x244>
		000000000001e4fc:  R_AARCH64_CALL26	pd_dbg_info
   1e500:      	mov	w8, #0x98
   1e504:      	b	0x1e9b0 <pd_process_event_com+0x6f8>
   1e508:      	ldrb	w8, [x20, #0x1]
   1e50c:      	mov	w0, wzr
   1e510:      	sub	w8, w8, #0x3
   1e514:      	cmp	w8, #0xb
   1e518:      	b.hi	0x1e9b8 <pd_process_event_com+0x700>
   1e51c:      	adrp	x9, 0x1e000 <pd_process_event_tcp+0x200>
		000000000001e51c:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x1cb4
   1e520:      	add	x9, x9, #0x0
		000000000001e520:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x1cb4
   1e524:      	adr	x10, #0x10
   1e528:      	ldrh	w11, [x9, x8, lsl #1]
   1e52c:      	add	x10, x10, x11, lsl #2
   1e530:      	br	x10
   1e534:      	ldrb	w8, [x19, #0x380]
   1e538:      	cbz	w8, 0x1e960 <pd_process_event_com+0x6a8>
   1e53c:      	ldrb	w8, [x19, #0x3d]
   1e540:      	cmp	w8, w21
   1e544:      	b.ne	0x1e960 <pd_process_event_com+0x6a8>
   1e548:      	mov	w8, #0x8a
   1e54c:      	b	0x1e9b0 <pd_process_event_com+0x6f8>
   1e550:      	ldrb	w8, [x19, #0x13e]
   1e554:      	cmp	w8, #0x2
   1e558:      	b.hs	0x1e56c <pd_process_event_com+0x2b4>
   1e55c:      	b	0x1e960 <pd_process_event_com+0x6a8>
   1e560:      	ldrb	w8, [x19, #0x13d]
   1e564:      	cmp	w8, #0x1
   1e568:      	b.ls	0x1e960 <pd_process_event_com+0x6a8>
   1e56c:      	mov	w8, #0x93
   1e570:      	b	0x1e9b0 <pd_process_event_com+0x6f8>
   1e574:      	ldr	x0, [x19]
   1e578:      	bl	0x1e578 <pd_process_event_com+0x2c0>
		000000000001e578:  R_AARCH64_CALL26	tcpci_retransmit
   1e57c:      	mov	w0, #0x1
   1e580:      	b	0x1e9b8 <pd_process_event_com+0x700>
   1e584:      	ldrh	w8, [x19, #0x6a]
   1e588:      	tbnz	w8, #0x3, 0x1e698 <pd_process_event_com+0x3e0>
   1e58c:      	tbnz	w8, #0x5, 0x1e794 <pd_process_event_com+0x4dc>
   1e590:      	tbz	w8, #0x6, 0x1e960 <pd_process_event_com+0x6a8>
   1e594:      	mov	w8, #0x98
   1e598:      	b	0x1e9b0 <pd_process_event_com+0x6f8>
   1e59c:      	ldr	x8, [x19]
   1e5a0:      	mov	w9, #0x3510
   1e5a4:      	add	x0, x8, x9
   1e5a8:      	bl	0x1e5a8 <pd_process_event_com+0x2f0>
		000000000001e5a8:  R_AARCH64_CALL26	mutex_is_locked
   1e5ac:      	tbz	w0, #0x0, 0x1e6ac <pd_process_event_com+0x3f4>
   1e5b0:      	adrp	x0, 0x1e000 <pd_process_event_tcp+0x200>
		000000000001e5b0:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x329f
   1e5b4:      	add	x0, x0, #0x0
		000000000001e5b4:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x329f
   1e5b8:      	bl	0x1e5b8 <pd_process_event_com+0x300>
		000000000001e5b8:  R_AARCH64_CALL26	pd_dbg_info
   1e5bc:      	ldr	x0, [x19]
   1e5c0:      	mov	w1, #0x7
   1e5c4:      	bl	0x1e5c4 <pd_process_event_com+0x30c>
		000000000001e5c4:  R_AARCH64_CALL26	tcpc_enable_timer
   1e5c8:      	b	0x1e960 <pd_process_event_com+0x6a8>
   1e5cc:      	ldrb	w8, [x19, #0x40]
   1e5d0:      	cmp	w8, #0x3
   1e5d4:      	b.ne	0x1e960 <pd_process_event_com+0x6a8>
   1e5d8:      	mov	x0, x19
   1e5dc:      	mov	w1, #0x1
   1e5e0:      	bl	0x1e5e0 <pd_process_event_com+0x328>
		000000000001e5e0:  R_AARCH64_CALL26	pd_set_vconn
   1e5e4:      	ldr	w8, [x19, #0x64]
   1e5e8:      	ldrb	w9, [x19, #0x61]
   1e5ec:      	and	w8, w8, #0xfffffbff
   1e5f0:      	orr	w8, w8, #0x20000000
   1e5f4:      	str	w8, [x19, #0x64]
   1e5f8:      	tbz	w9, #0x2, 0x1e600 <pd_process_event_com+0x348>
   1e5fc:      	strb	wzr, [x19, #0x5a]
   1e600:      	ldr	x0, [x19]
   1e604:      	bl	0x1e604 <pd_process_event_com+0x34c>
		000000000001e604:  R_AARCH64_CALL26	tcpc_event_thread_wake_up
   1e608:      	b	0x1e960 <pd_process_event_com+0x6a8>
   1e60c:      	ldrb	w8, [x19, #0x3d]
   1e610:      	cmp	w8, w20
   1e614:      	b.ne	0x1e960 <pd_process_event_com+0x6a8>
   1e618:      	ldrb	w8, [x19, #0x3e]
   1e61c:      	cmp	w8, #0x1
   1e620:      	b.ne	0x1e960 <pd_process_event_com+0x6a8>
   1e624:      	ldr	w8, [x19, #0x64]
   1e628:      	mov	w9, #0xfbff
   1e62c:      	movk	w9, #0xdfff, lsl #16
   1e630:      	add	w9, w9, #0x300
   1e634:      	and	w8, w8, w9
   1e638:      	ldrb	w9, [x19, #0x61]
   1e63c:      	orr	w8, w8, #0x20000000
   1e640:      	str	w8, [x19, #0x64]
   1e644:      	tbnz	w9, #0x0, 0x1e5fc <pd_process_event_com+0x344>
   1e648:      	b	0x1e600 <pd_process_event_com+0x348>
   1e64c:      	mov	x0, x19
   1e650:      	mov	w1, #0x13
   1e654:      	bl	0x1e654 <pd_process_event_com+0x39c>
		000000000001e654:  R_AARCH64_CALL26	pd_notify_tcp_event_buf_reset
   1e658:      	b	0x1e960 <pd_process_event_com+0x6a8>
   1e65c:      	ldrb	w9, [x19, #0x3d]
   1e660:      	cmp	w9, #0x8b
   1e664:      	b.ne	0x1e960 <pd_process_event_com+0x6a8>
   1e668:      	b	0x1e9b0 <pd_process_event_com+0x6f8>
   1e66c:      	ldrb	w9, [x19, #0x39c]
   1e670:      	cbz	w9, 0x1e960 <pd_process_event_com+0x6a8>
   1e674:      	ldrb	w9, [x19, #0x3d]
   1e678:      	cmp	w9, w8
   1e67c:      	b.ne	0x1e960 <pd_process_event_com+0x6a8>
   1e680:      	mov	w8, #0x92
   1e684:      	b	0x1e9b0 <pd_process_event_com+0x6f8>
   1e688:      	ldrb	w9, [x19, #0x3d]
   1e68c:      	cmp	w9, #0x94
   1e690:      	b.ne	0x1e960 <pd_process_event_com+0x6a8>
   1e694:      	b	0x1e9b0 <pd_process_event_com+0x6f8>
   1e698:      	mov	x0, x19
   1e69c:      	mov	w1, #0x1c
   1e6a0:      	bl	0x1e6a0 <pd_process_event_com+0x3e8>
		000000000001e6a0:  R_AARCH64_CALL26	pd_notify_tcp_event_2nd_result
   1e6a4:      	ldrb	w8, [x19, #0x324]
   1e6a8:      	b	0x1e9b0 <pd_process_event_com+0x6f8>
   1e6ac:      	ldr	w8, [x19, #0x60]
   1e6b0:      	cmp	w8, #0x7f
   1e6b4:      	b.hi	0x1e6cc <pd_process_event_com+0x414>
   1e6b8:      	ldr	w9, [x19, #0x64]
   1e6bc:      	bic	w9, w9, w8
   1e6c0:      	str	w9, [x19, #0x64]
   1e6c4:      	cbz	w8, 0x1e6cc <pd_process_event_com+0x414>
   1e6c8:      	strb	wzr, [x19, #0x5a]
   1e6cc:      	mov	x0, x19
   1e6d0:      	bl	0x1e6d0 <pd_process_event_com+0x418>
		000000000001e6d0:  R_AARCH64_CALL26	pd_notify_pe_cancel_pr_swap
   1e6d4:      	mov	x0, x19
   1e6d8:      	mov	w1, #0x18
   1e6dc:      	bl	0x1e6dc <pd_process_event_com+0x424>
		000000000001e6dc:  R_AARCH64_CALL26	pd_notify_tcp_event_2nd_result
   1e6e0:      	ldrh	w8, [x19, #0x6a]
   1e6e4:      	tbnz	w8, #0x2, 0x1e6f0 <pd_process_event_com+0x438>
   1e6e8:      	tbnz	w8, #0x4, 0x1e794 <pd_process_event_com+0x4dc>
   1e6ec:      	b	0x1e960 <pd_process_event_com+0x6a8>
   1e6f0:      	mov	w0, #0x1
   1e6f4:      	strb	w20, [x19, #0x3c]
   1e6f8:      	b	0x1e9b8 <pd_process_event_com+0x700>
   1e6fc:      	ldrb	w8, [x19, #0x380]
   1e700:      	cbz	w8, 0x1e960 <pd_process_event_com+0x6a8>
   1e704:      	ldrb	w8, [x19, #0x3d]
   1e708:      	cmp	w8, w21
   1e70c:      	b.ne	0x1e960 <pd_process_event_com+0x6a8>
   1e710:      	mov	w8, #0x8c
   1e714:      	b	0x1e9b0 <pd_process_event_com+0x6f8>
   1e718:      	ldrb	w8, [x19, #0x3d]
   1e71c:      	cmp	w8, #0x89
   1e720:      	b.eq	0x1e768 <pd_process_event_com+0x4b0>
   1e724:      	b	0x1e960 <pd_process_event_com+0x6a8>
   1e728:      	ldrb	w8, [x19, #0x3d]
   1e72c:      	cmp	w8, w21
   1e730:      	b.ne	0x1e960 <pd_process_event_com+0x6a8>
   1e734:      	mov	w8, #0x8e
   1e738:      	b	0x1e9b0 <pd_process_event_com+0x6f8>
   1e73c:      	ldrb	w8, [x19, #0x3d]
   1e740:      	cmp	w8, #0x8d
   1e744:      	b.eq	0x1e768 <pd_process_event_com+0x4b0>
   1e748:      	b	0x1e960 <pd_process_event_com+0x6a8>
   1e74c:      	ldrb	w8, [x19, #0x3d]
   1e750:      	cmp	w8, #0x91
   1e754:      	b.eq	0x1e768 <pd_process_event_com+0x4b0>
   1e758:      	b	0x1e960 <pd_process_event_com+0x6a8>
   1e75c:      	ldrb	w8, [x19, #0x3d]
   1e760:      	cmp	w8, #0x8f
   1e764:      	b.ne	0x1e960 <pd_process_event_com+0x6a8>
   1e768:      	mov	w0, #0x1
   1e76c:      	strb	w21, [x19, #0x3c]
   1e770:      	b	0x1e9b8 <pd_process_event_com+0x700>
   1e774:      	mov	x0, x19
   1e778:      	mov	w1, #0x17
   1e77c:      	bl	0x1e77c <pd_process_event_com+0x4c4>
		000000000001e77c:  R_AARCH64_CALL26	pd_notify_tcp_event_2nd_result
   1e780:      	ldrh	w8, [x19, #0x6a]
   1e784:      	tbnz	w8, #0x1, 0x1e810 <pd_process_event_com+0x558>
   1e788:      	b	0x1e960 <pd_process_event_com+0x6a8>
   1e78c:      	ldrb	w9, [x19, #0x48]
   1e790:      	cbz	w9, 0x1e938 <pd_process_event_com+0x680>
   1e794:      	ldrb	w8, [x19, #0x325]
   1e798:      	b	0x1e9b0 <pd_process_event_com+0x6f8>
   1e79c:      	ldrb	w9, [x19, #0x3d]
   1e7a0:      	cmp	w9, w8
   1e7a4:      	b.ne	0x1e960 <pd_process_event_com+0x6a8>
   1e7a8:      	ldr	x8, [x19]
   1e7ac:      	ldr	w8, [x8, #0x3550]
   1e7b0:      	and	w8, w8, #0xfffffffe
   1e7b4:      	cmp	w8, #0x8
   1e7b8:      	b.eq	0x1e9ac <pd_process_event_com+0x6f4>
   1e7bc:      	ldr	w9, [x19, #0x220]
   1e7c0:      	tbz	w9, #0x0, 0x1e9ac <pd_process_event_com+0x6f4>
   1e7c4:      	ldrb	w8, [x19, #0x3f]
   1e7c8:      	cmp	w8, #0x1
   1e7cc:      	b.ne	0x1e970 <pd_process_event_com+0x6b8>
   1e7d0:      	tbz	w9, #0x15, 0x1e974 <pd_process_event_com+0x6bc>
   1e7d4:      	b	0x1e9ac <pd_process_event_com+0x6f4>
   1e7d8:      	ldrb	w9, [x19, #0x3d]
   1e7dc:      	cmp	w9, w8
   1e7e0:      	b.ne	0x1e960 <pd_process_event_com+0x6a8>
   1e7e4:      	mov	w8, #0x4
   1e7e8:      	mov	w9, #0x55
   1e7ec:      	mov	w0, #0x1
   1e7f0:      	strb	w8, [x19, #0x38]
   1e7f4:      	strb	w9, [x19, #0x3c]
   1e7f8:      	b	0x1e9b8 <pd_process_event_com+0x700>
   1e7fc:      	mov	x0, x19
   1e800:      	mov	w1, #0x16
   1e804:      	bl	0x1e804 <pd_process_event_com+0x54c>
		000000000001e804:  R_AARCH64_CALL26	pd_notify_tcp_event_2nd_result
   1e808:      	ldrh	w8, [x19, #0x6a]
   1e80c:      	tbz	w8, #0x0, 0x1e960 <pd_process_event_com+0x6a8>
   1e810:      	ldr	w8, [x19, #0x60]
   1e814:      	cmp	w8, #0x7f
   1e818:      	b.hi	0x1e830 <pd_process_event_com+0x578>
   1e81c:      	ldr	w9, [x19, #0x64]
   1e820:      	bic	w9, w9, w8
   1e824:      	str	w9, [x19, #0x64]
   1e828:      	cbz	w8, 0x1e830 <pd_process_event_com+0x578>
   1e82c:      	strb	wzr, [x19, #0x5a]
   1e830:      	ldrb	w8, [x19, #0x38]
   1e834:      	cmp	w8, #0x3
   1e838:      	b.ne	0x1e404 <pd_process_event_com+0x14c>
   1e83c:      	mov	x0, x19
   1e840:      	bl	0x1e840 <pd_process_event_com+0x588>
		000000000001e840:  R_AARCH64_CALL26	pd_notify_pe_cancel_pr_swap
   1e844:      	b	0x1e404 <pd_process_event_com+0x14c>
   1e848:      	ldrb	w8, [x19, #0x4b]
   1e84c:      	cbnz	w8, 0x1e960 <pd_process_event_com+0x6a8>
   1e850:      	mov	w8, #0x2ff3
   1e854:      	ldr	x9, [x19]
   1e858:      	ldrb	w8, [x9, x8]
   1e85c:      	cbnz	w8, 0x1e960 <pd_process_event_com+0x6a8>
   1e860:      	ldrb	w8, [x19, #0x3f]
   1e864:      	mov	w9, #0x29
   1e868:      	cmp	w8, #0x0
   1e86c:      	mov	w8, #0xf
   1e870:      	csel	w8, w9, w8, eq
   1e874:      	b	0x1e9b0 <pd_process_event_com+0x6f8>
   1e878:      	ldr	w8, [x19, #0x60]
   1e87c:      	cmp	w8, #0x7f
   1e880:      	b.hi	0x1e898 <pd_process_event_com+0x5e0>
   1e884:      	ldr	w9, [x19, #0x64]
   1e888:      	bic	w9, w9, w8
   1e88c:      	str	w9, [x19, #0x64]
   1e890:      	cbz	w8, 0x1e898 <pd_process_event_com+0x5e0>
   1e894:      	strb	wzr, [x19, #0x5a]
   1e898:      	mov	x0, x19
   1e89c:      	bl	0x1e89c <pd_process_event_com+0x5e4>
		000000000001e89c:  R_AARCH64_CALL26	pd_notify_pe_reset_protocol
   1e8a0:      	mov	x0, x19
   1e8a4:      	mov	w1, #0x1a
   1e8a8:      	bl	0x1e8a8 <pd_process_event_com+0x5f0>
		000000000001e8a8:  R_AARCH64_CALL26	pd_notify_tcp_event_2nd_result
   1e8ac:      	ldrh	w8, [x19, #0x6a]
   1e8b0:      	tbnz	w8, #0x2, 0x1e404 <pd_process_event_com+0x14c>
   1e8b4:      	ldr	w8, [x19, #0x74]
   1e8b8:      	cmp	w8, #0x35
   1e8bc:      	b.hi	0x1e960 <pd_process_event_com+0x6a8>
   1e8c0:      	mov	w8, #0x506
   1e8c4:      	ldr	x0, [x19]
   1e8c8:      	add	x1, sp, #0x8
   1e8cc:      	mov	w2, wzr
   1e8d0:      	stp	x8, xzr, [sp, #0x8]
   1e8d4:      	bl	0x1e8d4 <pd_process_event_com+0x61c>
		000000000001e8d4:  R_AARCH64_CALL26	pd_put_vdm_event
   1e8d8:      	b	0x1e960 <pd_process_event_com+0x6a8>
   1e8dc:      	ldrb	w9, [x19, #0x39c]
   1e8e0:      	cbz	w9, 0x1e960 <pd_process_event_com+0x6a8>
   1e8e4:      	ldrb	w9, [x19, #0x3d]
   1e8e8:      	cmp	w9, w8
   1e8ec:      	b.ne	0x1e960 <pd_process_event_com+0x6a8>
   1e8f0:      	mov	w8, #0x90
   1e8f4:      	b	0x1e9b0 <pd_process_event_com+0x6f8>
   1e8f8:      	ldrb	w9, [x19, #0x3d]
   1e8fc:      	cmp	w9, w8
   1e900:      	b.ne	0x1e960 <pd_process_event_com+0x6a8>
   1e904:      	mov	w8, #0x95
   1e908:      	b	0x1e9b0 <pd_process_event_com+0x6f8>
   1e90c:      	ldr	x8, [x20, #0x8]
   1e910:      	mov	w9, #0x50000000
   1e914:      	ldr	w8, [x8, #0x8]
   1e918:      	and	w8, w8, #0xf0000000
   1e91c:      	cmp	w8, w9
   1e920:      	b.eq	0x1e968 <pd_process_event_com+0x6b0>
   1e924:      	mov	w9, #-0x80000000
   1e928:      	cmp	w8, w9
   1e92c:      	b.ne	0x1e960 <pd_process_event_com+0x6a8>
   1e930:      	mov	w8, #0x9a
   1e934:      	b	0x1e9b0 <pd_process_event_com+0x6f8>
   1e938:      	ldrb	w9, [x19, #0x3d]
   1e93c:      	cmp	w9, w8
   1e940:      	b.ne	0x1e960 <pd_process_event_com+0x6a8>
   1e944:      	ldr	w9, [x19, #0x220]
   1e948:      	tbz	w9, #0x1, 0x1e9ac <pd_process_event_com+0x6f4>
   1e94c:      	ldrb	w8, [x19, #0x3e]
   1e950:      	cmp	w8, #0x1
   1e954:      	b.ne	0x1e988 <pd_process_event_com+0x6d0>
   1e958:      	tbnz	w9, #0x1b, 0x1e9ac <pd_process_event_com+0x6f4>
   1e95c:      	b	0x1e98c <pd_process_event_com+0x6d4>
   1e960:      	mov	w0, wzr
   1e964:      	b	0x1e9b8 <pd_process_event_com+0x700>
   1e968:      	mov	w8, #0x9b
   1e96c:      	b	0x1e9b0 <pd_process_event_com+0x6f8>
   1e970:      	tbnz	w9, #0x14, 0x1e9ac <pd_process_event_com+0x6f4>
   1e974:      	mov	w9, #0x3
   1e978:      	cmp	w8, #0x0
   1e97c:      	mov	w8, #0x3e
   1e980:      	mov	w10, #0x45
   1e984:      	b	0x1e99c <pd_process_event_com+0x6e4>
   1e988:      	tbnz	w9, #0x1a, 0x1e9ac <pd_process_event_com+0x6f4>
   1e98c:      	mov	w9, #0x2
   1e990:      	cmp	w8, #0x0
   1e994:      	mov	w8, #0x34
   1e998:      	mov	w10, #0x39
   1e99c:      	csel	w8, w10, w8, eq
   1e9a0:      	strb	wzr, [x19, #0x4b]
   1e9a4:      	strb	w9, [x19, #0x38]
   1e9a8:      	b	0x1e9b0 <pd_process_event_com+0x6f8>
   1e9ac:      	mov	w8, #0x97
   1e9b0:      	mov	w0, #0x1
   1e9b4:      	strb	w8, [x19, #0x3c]
   1e9b8:      	mrs	x8, SP_EL0
   1e9bc:      	ldr	x8, [x8, #0x638]
   1e9c0:      	ldur	x9, [x29, #-0x8]
   1e9c4:      	cmp	x8, x9
   1e9c8:      	b.ne	0x1e9e8 <pd_process_event_com+0x730>
   1e9cc:      	and	w0, w0, #0x1
   1e9d0:      	ldp	x20, x19, [sp, #0x40]
   1e9d4:      	ldp	x29, x30, [sp, #0x20]
   1e9d8:      	ldr	x21, [sp, #0x30]
   1e9dc:      	add	sp, sp, #0x50
   1e9e0:      	autiasp
   1e9e4:      	ret
   1e9e8:      	bl	0x1e9e8 <pd_process_event_com+0x730>
		000000000001e9e8:  R_AARCH64_CALL26	__stack_chk_fail
