source pd_process_event_com section=.text address=0x1e208 size=1836
   1e208:      	paciasp
   1e20c:      	sub	sp, sp, #0x50
   1e210:      	stp	x29, x30, [sp, #0x20]
   1e214:      	str	x21, [sp, #0x30]
   1e218:      	stp	x20, x19, [sp, #0x40]
   1e21c:      	add	x29, sp, #0x20
   1e220:      	mrs	x8, SP_EL0
   1e224:      	mov	x19, x0
   1e228:      	ldr	x8, [x8, #0x638]
   1e22c:      	mov	w0, wzr
   1e230:      	stur	x8, [x29, #-0x8]
   1e234:      	ldrb	w8, [x1]
   1e238:      	sub	w8, w8, #0x1
   1e23c:      	cmp	w8, #0x6
   1e240:      	b.hi	0x1e900 <pd_process_event_com+0x6f8>
   1e244:      	adrp	x9, 0x1e000 <pd_process_event_tcp+0x2b0>
		000000000001e244:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x1c62
   1e248:      	add	x9, x9, #0x0
		000000000001e248:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x1c62
   1e24c:      	mov	x20, x1
   1e250:      	adr	x10, #0x10
   1e254:      	ldrh	w11, [x9, x8, lsl #1]
   1e258:      	add	x10, x10, x11, lsl #2
   1e25c:      	br	x10
   1e260:      	ldrb	w10, [x19, #0x13d]
   1e264:      	ldrb	w8, [x19, #0x324]
   1e268:      	ldrb	w9, [x20, #0x1]
   1e26c:      	cmp	w10, #0x1
   1e270:      	b.hi	0x1e400 <pd_process_event_com+0x1f8>
   1e274:      	cmp	w9, #0x10
   1e278:      	b.lo	0x1e400 <pd_process_event_com+0x1f8>
   1e27c:      	mov	w8, #0x19
   1e280:      	b	0x1e3f4 <pd_process_event_com+0x1ec>
   1e284:      	ldrb	w10, [x19, #0x13d]
   1e288:      	ldrb	w8, [x19, #0x324]
   1e28c:      	ldrb	w9, [x20, #0x1]
   1e290:      	cmp	w10, #0x1
   1e294:      	b.hi	0x1e2a0 <pd_process_event_com+0x98>
   1e298:      	cmp	w9, #0x5
   1e29c:      	b.hs	0x1e3f0 <pd_process_event_com+0x1e8>
   1e2a0:      	mov	w0, wzr
   1e2a4:      	sub	w9, w9, #0x3
   1e2a8:      	cmp	w9, #0x9
   1e2ac:      	b.hi	0x1e900 <pd_process_event_com+0x6f8>
   1e2b0:      	adrp	x10, 0x1e000 <pd_process_event_tcp+0x2b0>
		000000000001e2b0:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x1ccc
   1e2b4:      	add	x10, x10, #0x0
		000000000001e2b4:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x1ccc
   1e2b8:      	adr	x11, #0x10
   1e2bc:      	ldrh	w12, [x10, x9, lsl #1]
   1e2c0:      	add	x11, x11, x12, lsl #2
   1e2c4:      	br	x11
   1e2c8:      	ldrb	w9, [x19, #0x3d]
   1e2cc:      	cmp	w9, w8
   1e2d0:      	b.ne	0x1e8a8 <pd_process_event_com+0x6a0>
   1e2d4:      	ldr	w8, [x19, #0x190]
   1e2d8:      	mov	w9, #0x1389
   1e2dc:      	cmp	w8, w9
   1e2e0:      	b.lt	0x1e854 <pd_process_event_com+0x64c>
   1e2e4:      	adrp	x0, 0x1e000 <pd_process_event_tcp+0x2b0>
		000000000001e2e4:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x1dc7
   1e2e8:      	add	x0, x0, #0x0
		000000000001e2e8:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x1dc7
   1e2ec:      	bl	0x1e2ec <pd_process_event_com+0xe4>
		000000000001e2ec:  R_AARCH64_CALL26	pd_dbg_info
   1e2f0:      	b	0x1e8a8 <pd_process_event_com+0x6a0>
   1e2f4:      	ldrb	w8, [x19, #0x13d]
   1e2f8:      	cmp	w8, #0x1
   1e2fc:      	b.ls	0x1e3f0 <pd_process_event_com+0x1e8>
   1e300:      	ldrb	w21, [x19, #0x324]
   1e304:      	ldrb	w8, [x19, #0x3d]
   1e308:      	cmp	w8, w21
   1e30c:      	b.ne	0x1e458 <pd_process_event_com+0x250>
   1e310:      	mov	x0, x19
   1e314:      	bl	0x1e314 <pd_process_event_com+0x10c>
		000000000001e314:  R_AARCH64_CALL26	pd_is_multi_chunk_msg
   1e318:      	tbz	w0, #0x0, 0x1e458 <pd_process_event_com+0x250>
   1e31c:      	mov	w8, #0x1
   1e320:      	mov	x0, x19
   1e324:      	mov	x1, x20
   1e328:      	strb	w8, [x19, #0x327]
   1e32c:      	bl	0x1e32c <pd_process_event_com+0x124>
		000000000001e32c:  R_AARCH64_CALL26	pd_process_protocol_error
   1e330:      	b	0x1e900 <pd_process_event_com+0x6f8>
   1e334:      	ldrb	w8, [x20, #0x1]
   1e338:      	cmp	w8, #0x3
   1e33c:      	b.eq	0x1e4a0 <pd_process_event_com+0x298>
   1e340:      	cmp	w8, #0x2
   1e344:      	b.eq	0x1e4b0 <pd_process_event_com+0x2a8>
   1e348:      	cbnz	w8, 0x1e8a8 <pd_process_event_com+0x6a0>
   1e34c:      	ldrh	w8, [x19, #0x6a]
   1e350:      	tbz	w8, #0xa, 0x1e8a8 <pd_process_event_com+0x6a0>
   1e354:      	ldrb	w8, [x19, #0x324]
   1e358:      	b	0x1e8f8 <pd_process_event_com+0x6f0>
   1e35c:      	ldrb	w8, [x20, #0x1]
   1e360:      	sub	w9, w8, #0x7
   1e364:      	cmp	w9, #0x2
   1e368:      	b.lo	0x1e438 <pd_process_event_com+0x230>
   1e36c:      	cmp	w8, #0xa
   1e370:      	b.eq	0x1e4c4 <pd_process_event_com+0x2bc>
   1e374:      	cmp	w8, #0x2
   1e378:      	b.ne	0x1e8a8 <pd_process_event_com+0x6a0>
   1e37c:      	mov	w8, #0x2ff3
   1e380:      	ldr	x9, [x19]
   1e384:      	ldrb	w8, [x9, x8]
   1e388:      	cbz	w8, 0x1e398 <pd_process_event_com+0x190>
   1e38c:      	ldrb	w8, [x19, #0x78]
   1e390:      	add	w8, w8, #0x1
   1e394:      	strb	w8, [x19, #0x78]
   1e398:      	ldrb	w8, [x19, #0x3f]
   1e39c:      	mov	w9, #0x25
   1e3a0:      	cmp	w8, #0x0
   1e3a4:      	mov	w8, #0xa
   1e3a8:      	csel	w8, w9, w8, eq
   1e3ac:      	b	0x1e8f8 <pd_process_event_com+0x6f0>
   1e3b0:      	ldrb	w8, [x20, #0x1]
   1e3b4:      	mov	w0, wzr
   1e3b8:      	sub	w8, w8, #0x1
   1e3bc:      	cmp	w8, #0x21
   1e3c0:      	b.hi	0x1e900 <pd_process_event_com+0x6f8>
   1e3c4:      	adrp	x9, 0x1e000 <pd_process_event_tcp+0x2b0>
		000000000001e3c4:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x1c70
   1e3c8:      	add	x9, x9, #0x0
		000000000001e3c8:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x1c70
   1e3cc:      	ldrb	w20, [x19, #0x324]
   1e3d0:      	adr	x10, #0x10
   1e3d4:      	ldrh	w11, [x9, x8, lsl #1]
   1e3d8:      	add	x10, x10, x11, lsl #2
   1e3dc:      	br	x10
   1e3e0:      	ldrb	w8, [x19, #0x3d]
   1e3e4:      	cmp	w8, #0x9b
   1e3e8:      	b.eq	0x1e640 <pd_process_event_com+0x438>
   1e3ec:      	b	0x1e8a8 <pd_process_event_com+0x6a0>
   1e3f0:      	mov	w8, #0x10
   1e3f4:      	mov	w0, wzr
   1e3f8:      	strb	w8, [x20, #0x1]
   1e3fc:      	b	0x1e900 <pd_process_event_com+0x6f8>
   1e400:      	mov	w0, wzr
   1e404:      	sub	w9, w9, #0x1
   1e408:      	cmp	w9, #0x17
   1e40c:      	b.hi	0x1e900 <pd_process_event_com+0x6f8>
   1e410:      	adrp	x10, 0x1e000 <pd_process_event_tcp+0x2b0>
		000000000001e410:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x1ce0
   1e414:      	add	x10, x10, #0x0
		000000000001e414:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x1ce0
   1e418:      	adr	x11, #0x10
   1e41c:      	ldrh	w12, [x10, x9, lsl #1]
   1e420:      	add	x11, x11, x12, lsl #2
   1e424:      	br	x11
   1e428:      	ldrh	w9, [x19, #0x6a]
   1e42c:      	tbnz	w9, #0x9, 0x1e8f8 <pd_process_event_com+0x6f0>
   1e430:      	tbnz	w9, #0x8, 0x1e50c <pd_process_event_com+0x304>
   1e434:      	b	0x1e8a8 <pd_process_event_com+0x6a0>
   1e438:      	ldrb	w8, [x19, #0x78]
   1e43c:      	cmp	w8, #0x3
   1e440:      	b.lo	0x1e4d4 <pd_process_event_com+0x2cc>
   1e444:      	adrp	x0, 0x1e000 <pd_process_event_tcp+0x2b0>
		000000000001e444:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x2bb3
   1e448:      	add	x0, x0, #0x0
		000000000001e448:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x2bb3
   1e44c:      	bl	0x1e44c <pd_process_event_com+0x244>
		000000000001e44c:  R_AARCH64_CALL26	pd_dbg_info
   1e450:      	mov	w8, #0x98
   1e454:      	b	0x1e8f8 <pd_process_event_com+0x6f0>
   1e458:      	ldrb	w8, [x20, #0x1]
   1e45c:      	mov	w0, wzr
   1e460:      	sub	w8, w8, #0x3
   1e464:      	cmp	w8, #0xb
   1e468:      	b.hi	0x1e900 <pd_process_event_com+0x6f8>
   1e46c:      	adrp	x9, 0x1e000 <pd_process_event_tcp+0x2b0>
		000000000001e46c:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x1cb4
   1e470:      	add	x9, x9, #0x0
		000000000001e470:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x1cb4
   1e474:      	adr	x10, #0x10
   1e478:      	ldrh	w11, [x9, x8, lsl #1]
   1e47c:      	add	x10, x10, x11, lsl #2
   1e480:      	br	x10
   1e484:      	ldrb	w8, [x19, #0x380]
   1e488:      	cbz	w8, 0x1e8a8 <pd_process_event_com+0x6a0>
   1e48c:      	ldrb	w8, [x19, #0x3d]
   1e490:      	cmp	w8, w21
   1e494:      	b.ne	0x1e8a8 <pd_process_event_com+0x6a0>
   1e498:      	mov	w8, #0x8a
   1e49c:      	b	0x1e8f8 <pd_process_event_com+0x6f0>
   1e4a0:      	ldrb	w8, [x19, #0x13e]
   1e4a4:      	cmp	w8, #0x2
   1e4a8:      	b.hs	0x1e4bc <pd_process_event_com+0x2b4>
   1e4ac:      	b	0x1e8a8 <pd_process_event_com+0x6a0>
   1e4b0:      	ldrb	w8, [x19, #0x13d]
   1e4b4:      	cmp	w8, #0x1
   1e4b8:      	b.ls	0x1e8a8 <pd_process_event_com+0x6a0>
   1e4bc:      	mov	w8, #0x93
   1e4c0:      	b	0x1e8f8 <pd_process_event_com+0x6f0>
   1e4c4:      	ldr	x0, [x19]
   1e4c8:      	bl	0x1e4c8 <pd_process_event_com+0x2c0>
		000000000001e4c8:  R_AARCH64_CALL26	tcpci_retransmit
   1e4cc:      	mov	w0, #0x1
   1e4d0:      	b	0x1e900 <pd_process_event_com+0x6f8>
   1e4d4:      	ldrh	w8, [x19, #0x6a]
   1e4d8:      	tbnz	w8, #0x3, 0x1e5e8 <pd_process_event_com+0x3e0>
   1e4dc:      	tbnz	w8, #0x5, 0x1e6e4 <pd_process_event_com+0x4dc>
   1e4e0:      	tbz	w8, #0x6, 0x1e8a8 <pd_process_event_com+0x6a0>
   1e4e4:      	mov	w8, #0x98
   1e4e8:      	b	0x1e8f8 <pd_process_event_com+0x6f0>
   1e4ec:      	ldr	x8, [x19]
   1e4f0:      	mov	w9, #0x3510
   1e4f4:      	add	x0, x8, x9
   1e4f8:      	bl	0x1e4f8 <pd_process_event_com+0x2f0>
		000000000001e4f8:  R_AARCH64_CALL26	mutex_is_locked
   1e4fc:      	tbz	w0, #0x0, 0x1e5fc <pd_process_event_com+0x3f4>
   1e500:      	adrp	x0, 0x1e000 <pd_process_event_tcp+0x2b0>
		000000000001e500:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x31f6
   1e504:      	add	x0, x0, #0x0
		000000000001e504:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x31f6
   1e508:      	bl	0x1e508 <pd_process_event_com+0x300>
		000000000001e508:  R_AARCH64_CALL26	pd_dbg_info
   1e50c:      	ldr	x0, [x19]
   1e510:      	mov	w1, #0x7
   1e514:      	bl	0x1e514 <pd_process_event_com+0x30c>
		000000000001e514:  R_AARCH64_CALL26	tcpc_enable_timer
   1e518:      	b	0x1e8a8 <pd_process_event_com+0x6a0>
   1e51c:      	ldrb	w8, [x19, #0x40]
   1e520:      	cmp	w8, #0x3
   1e524:      	b.ne	0x1e8a8 <pd_process_event_com+0x6a0>
   1e528:      	mov	x0, x19
   1e52c:      	mov	w1, #0x1
   1e530:      	bl	0x1e530 <pd_process_event_com+0x328>
		000000000001e530:  R_AARCH64_CALL26	pd_set_vconn
   1e534:      	ldr	w8, [x19, #0x64]
   1e538:      	ldrb	w9, [x19, #0x61]
   1e53c:      	and	w8, w8, #0xfffffbff
   1e540:      	orr	w8, w8, #0x20000000
   1e544:      	str	w8, [x19, #0x64]
   1e548:      	tbz	w9, #0x2, 0x1e550 <pd_process_event_com+0x348>
   1e54c:      	strb	wzr, [x19, #0x5a]
   1e550:      	ldr	x0, [x19]
   1e554:      	bl	0x1e554 <pd_process_event_com+0x34c>
		000000000001e554:  R_AARCH64_CALL26	tcpc_event_thread_wake_up
   1e558:      	b	0x1e8a8 <pd_process_event_com+0x6a0>
   1e55c:      	ldrb	w8, [x19, #0x3d]
   1e560:      	cmp	w8, w20
   1e564:      	b.ne	0x1e8a8 <pd_process_event_com+0x6a0>
   1e568:      	ldrb	w8, [x19, #0x3e]
   1e56c:      	cmp	w8, #0x1
   1e570:      	b.ne	0x1e8a8 <pd_process_event_com+0x6a0>
   1e574:      	ldr	w8, [x19, #0x64]
   1e578:      	mov	w9, #0xfbff
   1e57c:      	movk	w9, #0xdfff, lsl #16
   1e580:      	add	w9, w9, #0x300
   1e584:      	and	w8, w8, w9
   1e588:      	ldrb	w9, [x19, #0x61]
   1e58c:      	orr	w8, w8, #0x20000000
   1e590:      	str	w8, [x19, #0x64]
   1e594:      	tbnz	w9, #0x0, 0x1e54c <pd_process_event_com+0x344>
   1e598:      	b	0x1e550 <pd_process_event_com+0x348>
   1e59c:      	mov	x0, x19
   1e5a0:      	mov	w1, #0x13
   1e5a4:      	bl	0x1e5a4 <pd_process_event_com+0x39c>
		000000000001e5a4:  R_AARCH64_CALL26	pd_notify_tcp_event_buf_reset
   1e5a8:      	b	0x1e8a8 <pd_process_event_com+0x6a0>
   1e5ac:      	ldrb	w9, [x19, #0x3d]
   1e5b0:      	cmp	w9, #0x8b
   1e5b4:      	b.ne	0x1e8a8 <pd_process_event_com+0x6a0>
   1e5b8:      	b	0x1e8f8 <pd_process_event_com+0x6f0>
   1e5bc:      	ldrb	w9, [x19, #0x39c]
   1e5c0:      	cbz	w9, 0x1e8a8 <pd_process_event_com+0x6a0>
   1e5c4:      	ldrb	w9, [x19, #0x3d]
   1e5c8:      	cmp	w9, w8
   1e5cc:      	b.ne	0x1e8a8 <pd_process_event_com+0x6a0>
   1e5d0:      	mov	w8, #0x92
   1e5d4:      	b	0x1e8f8 <pd_process_event_com+0x6f0>
   1e5d8:      	ldrb	w9, [x19, #0x3d]
   1e5dc:      	cmp	w9, #0x94
   1e5e0:      	b.ne	0x1e8a8 <pd_process_event_com+0x6a0>
   1e5e4:      	b	0x1e8f8 <pd_process_event_com+0x6f0>
   1e5e8:      	mov	x0, x19
   1e5ec:      	mov	w1, #0x1c
   1e5f0:      	bl	0x1e5f0 <pd_process_event_com+0x3e8>
		000000000001e5f0:  R_AARCH64_CALL26	pd_notify_tcp_event_2nd_result
   1e5f4:      	ldrb	w8, [x19, #0x324]
   1e5f8:      	b	0x1e8f8 <pd_process_event_com+0x6f0>
   1e5fc:      	ldr	w8, [x19, #0x60]
   1e600:      	cmp	w8, #0x7f
   1e604:      	b.hi	0x1e61c <pd_process_event_com+0x414>
   1e608:      	ldr	w9, [x19, #0x64]
   1e60c:      	bic	w9, w9, w8
   1e610:      	str	w9, [x19, #0x64]
   1e614:      	cbz	w8, 0x1e61c <pd_process_event_com+0x414>
   1e618:      	strb	wzr, [x19, #0x5a]
   1e61c:      	mov	x0, x19
   1e620:      	bl	0x1e620 <pd_process_event_com+0x418>
		000000000001e620:  R_AARCH64_CALL26	pd_notify_pe_cancel_pr_swap
   1e624:      	mov	x0, x19
   1e628:      	mov	w1, #0x18
   1e62c:      	bl	0x1e62c <pd_process_event_com+0x424>
		000000000001e62c:  R_AARCH64_CALL26	pd_notify_tcp_event_2nd_result
   1e630:      	ldrh	w8, [x19, #0x6a]
   1e634:      	tbnz	w8, #0x2, 0x1e640 <pd_process_event_com+0x438>
   1e638:      	tbnz	w8, #0x4, 0x1e6e4 <pd_process_event_com+0x4dc>
   1e63c:      	b	0x1e8a8 <pd_process_event_com+0x6a0>
   1e640:      	mov	w0, #0x1
   1e644:      	strb	w20, [x19, #0x3c]
   1e648:      	b	0x1e900 <pd_process_event_com+0x6f8>
   1e64c:      	ldrb	w8, [x19, #0x380]
   1e650:      	cbz	w8, 0x1e8a8 <pd_process_event_com+0x6a0>
   1e654:      	ldrb	w8, [x19, #0x3d]
   1e658:      	cmp	w8, w21
   1e65c:      	b.ne	0x1e8a8 <pd_process_event_com+0x6a0>
   1e660:      	mov	w8, #0x8c
   1e664:      	b	0x1e8f8 <pd_process_event_com+0x6f0>
   1e668:      	ldrb	w8, [x19, #0x3d]
   1e66c:      	cmp	w8, #0x89
   1e670:      	b.eq	0x1e6b8 <pd_process_event_com+0x4b0>
   1e674:      	b	0x1e8a8 <pd_process_event_com+0x6a0>
   1e678:      	ldrb	w8, [x19, #0x3d]
   1e67c:      	cmp	w8, w21
   1e680:      	b.ne	0x1e8a8 <pd_process_event_com+0x6a0>
   1e684:      	mov	w8, #0x8e
   1e688:      	b	0x1e8f8 <pd_process_event_com+0x6f0>
   1e68c:      	ldrb	w8, [x19, #0x3d]
   1e690:      	cmp	w8, #0x8d
   1e694:      	b.eq	0x1e6b8 <pd_process_event_com+0x4b0>
   1e698:      	b	0x1e8a8 <pd_process_event_com+0x6a0>
   1e69c:      	ldrb	w8, [x19, #0x3d]
   1e6a0:      	cmp	w8, #0x91
   1e6a4:      	b.eq	0x1e6b8 <pd_process_event_com+0x4b0>
   1e6a8:      	b	0x1e8a8 <pd_process_event_com+0x6a0>
   1e6ac:      	ldrb	w8, [x19, #0x3d]
   1e6b0:      	cmp	w8, #0x8f
   1e6b4:      	b.ne	0x1e8a8 <pd_process_event_com+0x6a0>
   1e6b8:      	mov	w0, #0x1
   1e6bc:      	strb	w21, [x19, #0x3c]
   1e6c0:      	b	0x1e900 <pd_process_event_com+0x6f8>
   1e6c4:      	mov	x0, x19
   1e6c8:      	mov	w1, #0x17
   1e6cc:      	bl	0x1e6cc <pd_process_event_com+0x4c4>
		000000000001e6cc:  R_AARCH64_CALL26	pd_notify_tcp_event_2nd_result
   1e6d0:      	ldrh	w8, [x19, #0x6a]
   1e6d4:      	tbnz	w8, #0x1, 0x1e760 <pd_process_event_com+0x558>
   1e6d8:      	b	0x1e8a8 <pd_process_event_com+0x6a0>
   1e6dc:      	ldrb	w9, [x19, #0x48]
   1e6e0:      	cbz	w9, 0x1e880 <pd_process_event_com+0x678>
   1e6e4:      	ldrb	w8, [x19, #0x325]
   1e6e8:      	b	0x1e8f8 <pd_process_event_com+0x6f0>
   1e6ec:      	ldrb	w9, [x19, #0x3d]
   1e6f0:      	cmp	w9, w8
   1e6f4:      	b.ne	0x1e8a8 <pd_process_event_com+0x6a0>
   1e6f8:      	ldr	x8, [x19]
   1e6fc:      	ldr	w8, [x8, #0x3550]
   1e700:      	and	w8, w8, #0xfffffffe
   1e704:      	cmp	w8, #0x8
   1e708:      	b.eq	0x1e8f4 <pd_process_event_com+0x6ec>
   1e70c:      	ldr	w9, [x19, #0x220]
   1e710:      	tbz	w9, #0x0, 0x1e8f4 <pd_process_event_com+0x6ec>
   1e714:      	ldrb	w8, [x19, #0x3f]
   1e718:      	cmp	w8, #0x1
   1e71c:      	b.ne	0x1e8b8 <pd_process_event_com+0x6b0>
   1e720:      	tbz	w9, #0x15, 0x1e8bc <pd_process_event_com+0x6b4>
   1e724:      	b	0x1e8f4 <pd_process_event_com+0x6ec>
   1e728:      	ldrb	w9, [x19, #0x3d]
   1e72c:      	cmp	w9, w8
   1e730:      	b.ne	0x1e8a8 <pd_process_event_com+0x6a0>
   1e734:      	mov	w8, #0x4
   1e738:      	mov	w9, #0x55
   1e73c:      	mov	w0, #0x1
   1e740:      	strb	w8, [x19, #0x38]
   1e744:      	strb	w9, [x19, #0x3c]
   1e748:      	b	0x1e900 <pd_process_event_com+0x6f8>
   1e74c:      	mov	x0, x19
   1e750:      	mov	w1, #0x16
   1e754:      	bl	0x1e754 <pd_process_event_com+0x54c>
		000000000001e754:  R_AARCH64_CALL26	pd_notify_tcp_event_2nd_result
   1e758:      	ldrh	w8, [x19, #0x6a]
   1e75c:      	tbz	w8, #0x0, 0x1e8a8 <pd_process_event_com+0x6a0>
   1e760:      	ldr	w8, [x19, #0x60]
   1e764:      	cmp	w8, #0x7f
   1e768:      	b.hi	0x1e780 <pd_process_event_com+0x578>
   1e76c:      	ldr	w9, [x19, #0x64]
   1e770:      	bic	w9, w9, w8
   1e774:      	str	w9, [x19, #0x64]
   1e778:      	cbz	w8, 0x1e780 <pd_process_event_com+0x578>
   1e77c:      	strb	wzr, [x19, #0x5a]
   1e780:      	ldrb	w8, [x19, #0x38]
   1e784:      	cmp	w8, #0x3
   1e788:      	b.ne	0x1e354 <pd_process_event_com+0x14c>
   1e78c:      	mov	x0, x19
   1e790:      	bl	0x1e790 <pd_process_event_com+0x588>
		000000000001e790:  R_AARCH64_CALL26	pd_notify_pe_cancel_pr_swap
   1e794:      	b	0x1e354 <pd_process_event_com+0x14c>
   1e798:      	ldrb	w8, [x19, #0x4b]
   1e79c:      	cbnz	w8, 0x1e8a8 <pd_process_event_com+0x6a0>
   1e7a0:      	mov	w8, #0x2ff3
   1e7a4:      	ldr	x9, [x19]
   1e7a8:      	ldrb	w8, [x9, x8]
   1e7ac:      	cbnz	w8, 0x1e8a8 <pd_process_event_com+0x6a0>
   1e7b0:      	ldrb	w8, [x19, #0x3f]
   1e7b4:      	mov	w9, #0x29
   1e7b8:      	cmp	w8, #0x0
   1e7bc:      	mov	w8, #0xf
   1e7c0:      	csel	w8, w9, w8, eq
   1e7c4:      	b	0x1e8f8 <pd_process_event_com+0x6f0>
   1e7c8:      	ldr	w8, [x19, #0x60]
   1e7cc:      	cmp	w8, #0x7f
   1e7d0:      	b.hi	0x1e7e8 <pd_process_event_com+0x5e0>
   1e7d4:      	ldr	w9, [x19, #0x64]
   1e7d8:      	bic	w9, w9, w8
   1e7dc:      	str	w9, [x19, #0x64]
   1e7e0:      	cbz	w8, 0x1e7e8 <pd_process_event_com+0x5e0>
   1e7e4:      	strb	wzr, [x19, #0x5a]
   1e7e8:      	mov	x0, x19
   1e7ec:      	mov	w1, #0x1a
   1e7f0:      	bl	0x1e7f0 <pd_process_event_com+0x5e8>
		000000000001e7f0:  R_AARCH64_CALL26	pd_notify_tcp_event_2nd_result
   1e7f4:      	ldrh	w8, [x19, #0x6a]
   1e7f8:      	tbnz	w8, #0x2, 0x1e354 <pd_process_event_com+0x14c>
   1e7fc:      	ldr	w8, [x19, #0x74]
   1e800:      	cmp	w8, #0x35
   1e804:      	b.hi	0x1e8a8 <pd_process_event_com+0x6a0>
   1e808:      	mov	w8, #0x506
   1e80c:      	ldr	x0, [x19]
   1e810:      	add	x1, sp, #0x8
   1e814:      	mov	w2, wzr
   1e818:      	stp	x8, xzr, [sp, #0x8]
   1e81c:      	bl	0x1e81c <pd_process_event_com+0x614>
		000000000001e81c:  R_AARCH64_CALL26	pd_put_vdm_event
   1e820:      	b	0x1e8a8 <pd_process_event_com+0x6a0>
   1e824:      	ldrb	w9, [x19, #0x39c]
   1e828:      	cbz	w9, 0x1e8a8 <pd_process_event_com+0x6a0>
   1e82c:      	ldrb	w9, [x19, #0x3d]
   1e830:      	cmp	w9, w8
   1e834:      	b.ne	0x1e8a8 <pd_process_event_com+0x6a0>
   1e838:      	mov	w8, #0x90
   1e83c:      	b	0x1e8f8 <pd_process_event_com+0x6f0>
   1e840:      	ldrb	w9, [x19, #0x3d]
   1e844:      	cmp	w9, w8
   1e848:      	b.ne	0x1e8a8 <pd_process_event_com+0x6a0>
   1e84c:      	mov	w8, #0x95
   1e850:      	b	0x1e8f8 <pd_process_event_com+0x6f0>
   1e854:      	ldr	x8, [x20, #0x8]
   1e858:      	mov	w9, #0x50000000
   1e85c:      	ldr	w8, [x8, #0x8]
   1e860:      	and	w8, w8, #0xf0000000
   1e864:      	cmp	w8, w9
   1e868:      	b.eq	0x1e8b0 <pd_process_event_com+0x6a8>
   1e86c:      	mov	w9, #-0x80000000
   1e870:      	cmp	w8, w9
   1e874:      	b.ne	0x1e8a8 <pd_process_event_com+0x6a0>
   1e878:      	mov	w8, #0x9a
   1e87c:      	b	0x1e8f8 <pd_process_event_com+0x6f0>
   1e880:      	ldrb	w9, [x19, #0x3d]
   1e884:      	cmp	w9, w8
   1e888:      	b.ne	0x1e8a8 <pd_process_event_com+0x6a0>
   1e88c:      	ldr	w9, [x19, #0x220]
   1e890:      	tbz	w9, #0x1, 0x1e8f4 <pd_process_event_com+0x6ec>
   1e894:      	ldrb	w8, [x19, #0x3e]
   1e898:      	cmp	w8, #0x1
   1e89c:      	b.ne	0x1e8d0 <pd_process_event_com+0x6c8>
   1e8a0:      	tbnz	w9, #0x1b, 0x1e8f4 <pd_process_event_com+0x6ec>
   1e8a4:      	b	0x1e8d4 <pd_process_event_com+0x6cc>
   1e8a8:      	mov	w0, wzr
   1e8ac:      	b	0x1e900 <pd_process_event_com+0x6f8>
   1e8b0:      	mov	w8, #0x9b
   1e8b4:      	b	0x1e8f8 <pd_process_event_com+0x6f0>
   1e8b8:      	tbnz	w9, #0x14, 0x1e8f4 <pd_process_event_com+0x6ec>
   1e8bc:      	mov	w9, #0x3
   1e8c0:      	cmp	w8, #0x0
   1e8c4:      	mov	w8, #0x3e
   1e8c8:      	mov	w10, #0x45
   1e8cc:      	b	0x1e8e4 <pd_process_event_com+0x6dc>
   1e8d0:      	tbnz	w9, #0x1a, 0x1e8f4 <pd_process_event_com+0x6ec>
   1e8d4:      	mov	w9, #0x2
   1e8d8:      	cmp	w8, #0x0
   1e8dc:      	mov	w8, #0x34
   1e8e0:      	mov	w10, #0x39
   1e8e4:      	csel	w8, w10, w8, eq
   1e8e8:      	strb	wzr, [x19, #0x4b]
   1e8ec:      	strb	w9, [x19, #0x38]
   1e8f0:      	b	0x1e8f8 <pd_process_event_com+0x6f0>
   1e8f4:      	mov	w8, #0x97
   1e8f8:      	mov	w0, #0x1
   1e8fc:      	strb	w8, [x19, #0x3c]
   1e900:      	mrs	x8, SP_EL0
   1e904:      	ldr	x8, [x8, #0x638]
   1e908:      	ldur	x9, [x29, #-0x8]
   1e90c:      	cmp	x8, x9
   1e910:      	b.ne	0x1e930 <pd_process_event_com+0x728>
   1e914:      	and	w0, w0, #0x1
   1e918:      	ldp	x20, x19, [sp, #0x40]
   1e91c:      	ldp	x29, x30, [sp, #0x20]
   1e920:      	ldr	x21, [sp, #0x30]
   1e924:      	add	sp, sp, #0x50
   1e928:      	autiasp
   1e92c:      	ret
   1e930:      	bl	0x1e930 <pd_process_event_com+0x728>
		000000000001e930:  R_AARCH64_CALL26	__stack_chk_fail
