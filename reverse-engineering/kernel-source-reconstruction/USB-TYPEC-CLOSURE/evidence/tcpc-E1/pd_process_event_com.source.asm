source pd_process_event_com section=.text address=0x1e21c size=1844
   1e21c:      	paciasp
   1e220:      	sub	sp, sp, #0x50
   1e224:      	stp	x29, x30, [sp, #0x20]
   1e228:      	str	x21, [sp, #0x30]
   1e22c:      	stp	x20, x19, [sp, #0x40]
   1e230:      	add	x29, sp, #0x20
   1e234:      	mrs	x8, SP_EL0
   1e238:      	mov	x19, x0
   1e23c:      	ldr	x8, [x8, #0x638]
   1e240:      	mov	w0, wzr
   1e244:      	stur	x8, [x29, #-0x8]
   1e248:      	ldrb	w8, [x1]
   1e24c:      	sub	w8, w8, #0x1
   1e250:      	cmp	w8, #0x6
   1e254:      	b.hi	0x1e91c <pd_process_event_com+0x700>
   1e258:      	adrp	x9, 0x1e000 <pd_process_event_tcp+0x29c>
		000000000001e258:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x1c62
   1e25c:      	add	x9, x9, #0x0
		000000000001e25c:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x1c62
   1e260:      	mov	x20, x1
   1e264:      	adr	x10, #0x10
   1e268:      	ldrh	w11, [x9, x8, lsl #1]
   1e26c:      	add	x10, x10, x11, lsl #2
   1e270:      	br	x10
   1e274:      	ldrb	w10, [x19, #0x13d]
   1e278:      	ldrb	w8, [x19, #0x324]
   1e27c:      	ldrb	w9, [x20, #0x1]
   1e280:      	cmp	w10, #0x1
   1e284:      	b.hi	0x1e414 <pd_process_event_com+0x1f8>
   1e288:      	cmp	w9, #0x10
   1e28c:      	b.lo	0x1e414 <pd_process_event_com+0x1f8>
   1e290:      	mov	w8, #0x19
   1e294:      	b	0x1e408 <pd_process_event_com+0x1ec>
   1e298:      	ldrb	w10, [x19, #0x13d]
   1e29c:      	ldrb	w8, [x19, #0x324]
   1e2a0:      	ldrb	w9, [x20, #0x1]
   1e2a4:      	cmp	w10, #0x1
   1e2a8:      	b.hi	0x1e2b4 <pd_process_event_com+0x98>
   1e2ac:      	cmp	w9, #0x5
   1e2b0:      	b.hs	0x1e404 <pd_process_event_com+0x1e8>
   1e2b4:      	mov	w0, wzr
   1e2b8:      	sub	w9, w9, #0x3
   1e2bc:      	cmp	w9, #0x9
   1e2c0:      	b.hi	0x1e91c <pd_process_event_com+0x700>
   1e2c4:      	adrp	x10, 0x1e000 <pd_process_event_tcp+0x29c>
		000000000001e2c4:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x1ccc
   1e2c8:      	add	x10, x10, #0x0
		000000000001e2c8:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x1ccc
   1e2cc:      	adr	x11, #0x10
   1e2d0:      	ldrh	w12, [x10, x9, lsl #1]
   1e2d4:      	add	x11, x11, x12, lsl #2
   1e2d8:      	br	x11
   1e2dc:      	ldrb	w9, [x19, #0x3d]
   1e2e0:      	cmp	w9, w8
   1e2e4:      	b.ne	0x1e8c4 <pd_process_event_com+0x6a8>
   1e2e8:      	ldr	w8, [x19, #0x190]
   1e2ec:      	mov	w9, #0x1389
   1e2f0:      	cmp	w8, w9
   1e2f4:      	b.lt	0x1e870 <pd_process_event_com+0x654>
   1e2f8:      	adrp	x0, 0x1e000 <pd_process_event_tcp+0x29c>
		000000000001e2f8:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x1dca
   1e2fc:      	add	x0, x0, #0x0
		000000000001e2fc:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x1dca
   1e300:      	bl	0x1e300 <pd_process_event_com+0xe4>
		000000000001e300:  R_AARCH64_CALL26	pd_dbg_info
   1e304:      	b	0x1e8c4 <pd_process_event_com+0x6a8>
   1e308:      	ldrb	w8, [x19, #0x13d]
   1e30c:      	cmp	w8, #0x1
   1e310:      	b.ls	0x1e404 <pd_process_event_com+0x1e8>
   1e314:      	ldrb	w21, [x19, #0x324]
   1e318:      	ldrb	w8, [x19, #0x3d]
   1e31c:      	cmp	w8, w21
   1e320:      	b.ne	0x1e46c <pd_process_event_com+0x250>
   1e324:      	mov	x0, x19
   1e328:      	bl	0x1e328 <pd_process_event_com+0x10c>
		000000000001e328:  R_AARCH64_CALL26	pd_is_multi_chunk_msg
   1e32c:      	tbz	w0, #0x0, 0x1e46c <pd_process_event_com+0x250>
   1e330:      	mov	w8, #0x1
   1e334:      	mov	x0, x19
   1e338:      	mov	x1, x20
   1e33c:      	strb	w8, [x19, #0x327]
   1e340:      	bl	0x1e340 <pd_process_event_com+0x124>
		000000000001e340:  R_AARCH64_CALL26	pd_process_protocol_error
   1e344:      	b	0x1e91c <pd_process_event_com+0x700>
   1e348:      	ldrb	w8, [x20, #0x1]
   1e34c:      	cmp	w8, #0x3
   1e350:      	b.eq	0x1e4b4 <pd_process_event_com+0x298>
   1e354:      	cmp	w8, #0x2
   1e358:      	b.eq	0x1e4c4 <pd_process_event_com+0x2a8>
   1e35c:      	cbnz	w8, 0x1e8c4 <pd_process_event_com+0x6a8>
   1e360:      	ldrh	w8, [x19, #0x6a]
   1e364:      	tbz	w8, #0xa, 0x1e8c4 <pd_process_event_com+0x6a8>
   1e368:      	ldrb	w8, [x19, #0x324]
   1e36c:      	b	0x1e914 <pd_process_event_com+0x6f8>
   1e370:      	ldrb	w8, [x20, #0x1]
   1e374:      	sub	w9, w8, #0x7
   1e378:      	cmp	w9, #0x2
   1e37c:      	b.lo	0x1e44c <pd_process_event_com+0x230>
   1e380:      	cmp	w8, #0xa
   1e384:      	b.eq	0x1e4d8 <pd_process_event_com+0x2bc>
   1e388:      	cmp	w8, #0x2
   1e38c:      	b.ne	0x1e8c4 <pd_process_event_com+0x6a8>
   1e390:      	mov	w8, #0x2ff3
   1e394:      	ldr	x9, [x19]
   1e398:      	ldrb	w8, [x9, x8]
   1e39c:      	cbz	w8, 0x1e3ac <pd_process_event_com+0x190>
   1e3a0:      	ldrb	w8, [x19, #0x78]
   1e3a4:      	add	w8, w8, #0x1
   1e3a8:      	strb	w8, [x19, #0x78]
   1e3ac:      	ldrb	w8, [x19, #0x3f]
   1e3b0:      	mov	w9, #0x25
   1e3b4:      	cmp	w8, #0x0
   1e3b8:      	mov	w8, #0xa
   1e3bc:      	csel	w8, w9, w8, eq
   1e3c0:      	b	0x1e914 <pd_process_event_com+0x6f8>
   1e3c4:      	ldrb	w8, [x20, #0x1]
   1e3c8:      	mov	w0, wzr
   1e3cc:      	sub	w8, w8, #0x1
   1e3d0:      	cmp	w8, #0x21
   1e3d4:      	b.hi	0x1e91c <pd_process_event_com+0x700>
   1e3d8:      	adrp	x9, 0x1e000 <pd_process_event_tcp+0x29c>
		000000000001e3d8:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x1c70
   1e3dc:      	add	x9, x9, #0x0
		000000000001e3dc:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x1c70
   1e3e0:      	ldrb	w20, [x19, #0x324]
   1e3e4:      	adr	x10, #0x10
   1e3e8:      	ldrh	w11, [x9, x8, lsl #1]
   1e3ec:      	add	x10, x10, x11, lsl #2
   1e3f0:      	br	x10
   1e3f4:      	ldrb	w8, [x19, #0x3d]
   1e3f8:      	cmp	w8, #0x9b
   1e3fc:      	b.eq	0x1e654 <pd_process_event_com+0x438>
   1e400:      	b	0x1e8c4 <pd_process_event_com+0x6a8>
   1e404:      	mov	w8, #0x10
   1e408:      	mov	w0, wzr
   1e40c:      	strb	w8, [x20, #0x1]
   1e410:      	b	0x1e91c <pd_process_event_com+0x700>
   1e414:      	mov	w0, wzr
   1e418:      	sub	w9, w9, #0x1
   1e41c:      	cmp	w9, #0x17
   1e420:      	b.hi	0x1e91c <pd_process_event_com+0x700>
   1e424:      	adrp	x10, 0x1e000 <pd_process_event_tcp+0x29c>
		000000000001e424:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x1ce0
   1e428:      	add	x10, x10, #0x0
		000000000001e428:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x1ce0
   1e42c:      	adr	x11, #0x10
   1e430:      	ldrh	w12, [x10, x9, lsl #1]
   1e434:      	add	x11, x11, x12, lsl #2
   1e438:      	br	x11
   1e43c:      	ldrh	w9, [x19, #0x6a]
   1e440:      	tbnz	w9, #0x9, 0x1e914 <pd_process_event_com+0x6f8>
   1e444:      	tbnz	w9, #0x8, 0x1e520 <pd_process_event_com+0x304>
   1e448:      	b	0x1e8c4 <pd_process_event_com+0x6a8>
   1e44c:      	ldrb	w8, [x19, #0x78]
   1e450:      	cmp	w8, #0x3
   1e454:      	b.lo	0x1e4e8 <pd_process_event_com+0x2cc>
   1e458:      	adrp	x0, 0x1e000 <pd_process_event_tcp+0x29c>
		000000000001e458:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x2bc0
   1e45c:      	add	x0, x0, #0x0
		000000000001e45c:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x2bc0
   1e460:      	bl	0x1e460 <pd_process_event_com+0x244>
		000000000001e460:  R_AARCH64_CALL26	pd_dbg_info
   1e464:      	mov	w8, #0x98
   1e468:      	b	0x1e914 <pd_process_event_com+0x6f8>
   1e46c:      	ldrb	w8, [x20, #0x1]
   1e470:      	mov	w0, wzr
   1e474:      	sub	w8, w8, #0x3
   1e478:      	cmp	w8, #0xb
   1e47c:      	b.hi	0x1e91c <pd_process_event_com+0x700>
   1e480:      	adrp	x9, 0x1e000 <pd_process_event_tcp+0x29c>
		000000000001e480:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x1cb4
   1e484:      	add	x9, x9, #0x0
		000000000001e484:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x1cb4
   1e488:      	adr	x10, #0x10
   1e48c:      	ldrh	w11, [x9, x8, lsl #1]
   1e490:      	add	x10, x10, x11, lsl #2
   1e494:      	br	x10
   1e498:      	ldrb	w8, [x19, #0x380]
   1e49c:      	cbz	w8, 0x1e8c4 <pd_process_event_com+0x6a8>
   1e4a0:      	ldrb	w8, [x19, #0x3d]
   1e4a4:      	cmp	w8, w21
   1e4a8:      	b.ne	0x1e8c4 <pd_process_event_com+0x6a8>
   1e4ac:      	mov	w8, #0x8a
   1e4b0:      	b	0x1e914 <pd_process_event_com+0x6f8>
   1e4b4:      	ldrb	w8, [x19, #0x13e]
   1e4b8:      	cmp	w8, #0x2
   1e4bc:      	b.hs	0x1e4d0 <pd_process_event_com+0x2b4>
   1e4c0:      	b	0x1e8c4 <pd_process_event_com+0x6a8>
   1e4c4:      	ldrb	w8, [x19, #0x13d]
   1e4c8:      	cmp	w8, #0x1
   1e4cc:      	b.ls	0x1e8c4 <pd_process_event_com+0x6a8>
   1e4d0:      	mov	w8, #0x93
   1e4d4:      	b	0x1e914 <pd_process_event_com+0x6f8>
   1e4d8:      	ldr	x0, [x19]
   1e4dc:      	bl	0x1e4dc <pd_process_event_com+0x2c0>
		000000000001e4dc:  R_AARCH64_CALL26	tcpci_retransmit
   1e4e0:      	mov	w0, #0x1
   1e4e4:      	b	0x1e91c <pd_process_event_com+0x700>
   1e4e8:      	ldrh	w8, [x19, #0x6a]
   1e4ec:      	tbnz	w8, #0x3, 0x1e5fc <pd_process_event_com+0x3e0>
   1e4f0:      	tbnz	w8, #0x5, 0x1e6f8 <pd_process_event_com+0x4dc>
   1e4f4:      	tbz	w8, #0x6, 0x1e8c4 <pd_process_event_com+0x6a8>
   1e4f8:      	mov	w8, #0x98
   1e4fc:      	b	0x1e914 <pd_process_event_com+0x6f8>
   1e500:      	ldr	x8, [x19]
   1e504:      	mov	w9, #0x3510
   1e508:      	add	x0, x8, x9
   1e50c:      	bl	0x1e50c <pd_process_event_com+0x2f0>
		000000000001e50c:  R_AARCH64_CALL26	mutex_is_locked
   1e510:      	tbz	w0, #0x0, 0x1e610 <pd_process_event_com+0x3f4>
   1e514:      	adrp	x0, 0x1e000 <pd_process_event_tcp+0x29c>
		000000000001e514:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x3272
   1e518:      	add	x0, x0, #0x0
		000000000001e518:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x3272
   1e51c:      	bl	0x1e51c <pd_process_event_com+0x300>
		000000000001e51c:  R_AARCH64_CALL26	pd_dbg_info
   1e520:      	ldr	x0, [x19]
   1e524:      	mov	w1, #0x7
   1e528:      	bl	0x1e528 <pd_process_event_com+0x30c>
		000000000001e528:  R_AARCH64_CALL26	tcpc_enable_timer
   1e52c:      	b	0x1e8c4 <pd_process_event_com+0x6a8>
   1e530:      	ldrb	w8, [x19, #0x40]
   1e534:      	cmp	w8, #0x3
   1e538:      	b.ne	0x1e8c4 <pd_process_event_com+0x6a8>
   1e53c:      	mov	x0, x19
   1e540:      	mov	w1, #0x1
   1e544:      	bl	0x1e544 <pd_process_event_com+0x328>
		000000000001e544:  R_AARCH64_CALL26	pd_set_vconn
   1e548:      	ldr	w8, [x19, #0x64]
   1e54c:      	ldrb	w9, [x19, #0x61]
   1e550:      	and	w8, w8, #0xfffffbff
   1e554:      	orr	w8, w8, #0x20000000
   1e558:      	str	w8, [x19, #0x64]
   1e55c:      	tbz	w9, #0x2, 0x1e564 <pd_process_event_com+0x348>
   1e560:      	strb	wzr, [x19, #0x5a]
   1e564:      	ldr	x0, [x19]
   1e568:      	bl	0x1e568 <pd_process_event_com+0x34c>
		000000000001e568:  R_AARCH64_CALL26	tcpc_event_thread_wake_up
   1e56c:      	b	0x1e8c4 <pd_process_event_com+0x6a8>
   1e570:      	ldrb	w8, [x19, #0x3d]
   1e574:      	cmp	w8, w20
   1e578:      	b.ne	0x1e8c4 <pd_process_event_com+0x6a8>
   1e57c:      	ldrb	w8, [x19, #0x3e]
   1e580:      	cmp	w8, #0x1
   1e584:      	b.ne	0x1e8c4 <pd_process_event_com+0x6a8>
   1e588:      	ldr	w8, [x19, #0x64]
   1e58c:      	mov	w9, #0xfbff
   1e590:      	movk	w9, #0xdfff, lsl #16
   1e594:      	add	w9, w9, #0x300
   1e598:      	and	w8, w8, w9
   1e59c:      	ldrb	w9, [x19, #0x61]
   1e5a0:      	orr	w8, w8, #0x20000000
   1e5a4:      	str	w8, [x19, #0x64]
   1e5a8:      	tbnz	w9, #0x0, 0x1e560 <pd_process_event_com+0x344>
   1e5ac:      	b	0x1e564 <pd_process_event_com+0x348>
   1e5b0:      	mov	x0, x19
   1e5b4:      	mov	w1, #0x13
   1e5b8:      	bl	0x1e5b8 <pd_process_event_com+0x39c>
		000000000001e5b8:  R_AARCH64_CALL26	pd_notify_tcp_event_buf_reset
   1e5bc:      	b	0x1e8c4 <pd_process_event_com+0x6a8>
   1e5c0:      	ldrb	w9, [x19, #0x3d]
   1e5c4:      	cmp	w9, #0x8b
   1e5c8:      	b.ne	0x1e8c4 <pd_process_event_com+0x6a8>
   1e5cc:      	b	0x1e914 <pd_process_event_com+0x6f8>
   1e5d0:      	ldrb	w9, [x19, #0x39c]
   1e5d4:      	cbz	w9, 0x1e8c4 <pd_process_event_com+0x6a8>
   1e5d8:      	ldrb	w9, [x19, #0x3d]
   1e5dc:      	cmp	w9, w8
   1e5e0:      	b.ne	0x1e8c4 <pd_process_event_com+0x6a8>
   1e5e4:      	mov	w8, #0x92
   1e5e8:      	b	0x1e914 <pd_process_event_com+0x6f8>
   1e5ec:      	ldrb	w9, [x19, #0x3d]
   1e5f0:      	cmp	w9, #0x94
   1e5f4:      	b.ne	0x1e8c4 <pd_process_event_com+0x6a8>
   1e5f8:      	b	0x1e914 <pd_process_event_com+0x6f8>
   1e5fc:      	mov	x0, x19
   1e600:      	mov	w1, #0x1c
   1e604:      	bl	0x1e604 <pd_process_event_com+0x3e8>
		000000000001e604:  R_AARCH64_CALL26	pd_notify_tcp_event_2nd_result
   1e608:      	ldrb	w8, [x19, #0x324]
   1e60c:      	b	0x1e914 <pd_process_event_com+0x6f8>
   1e610:      	ldr	w8, [x19, #0x60]
   1e614:      	cmp	w8, #0x7f
   1e618:      	b.hi	0x1e630 <pd_process_event_com+0x414>
   1e61c:      	ldr	w9, [x19, #0x64]
   1e620:      	bic	w9, w9, w8
   1e624:      	str	w9, [x19, #0x64]
   1e628:      	cbz	w8, 0x1e630 <pd_process_event_com+0x414>
   1e62c:      	strb	wzr, [x19, #0x5a]
   1e630:      	mov	x0, x19
   1e634:      	bl	0x1e634 <pd_process_event_com+0x418>
		000000000001e634:  R_AARCH64_CALL26	pd_notify_pe_cancel_pr_swap
   1e638:      	mov	x0, x19
   1e63c:      	mov	w1, #0x18
   1e640:      	bl	0x1e640 <pd_process_event_com+0x424>
		000000000001e640:  R_AARCH64_CALL26	pd_notify_tcp_event_2nd_result
   1e644:      	ldrh	w8, [x19, #0x6a]
   1e648:      	tbnz	w8, #0x2, 0x1e654 <pd_process_event_com+0x438>
   1e64c:      	tbnz	w8, #0x4, 0x1e6f8 <pd_process_event_com+0x4dc>
   1e650:      	b	0x1e8c4 <pd_process_event_com+0x6a8>
   1e654:      	mov	w0, #0x1
   1e658:      	strb	w20, [x19, #0x3c]
   1e65c:      	b	0x1e91c <pd_process_event_com+0x700>
   1e660:      	ldrb	w8, [x19, #0x380]
   1e664:      	cbz	w8, 0x1e8c4 <pd_process_event_com+0x6a8>
   1e668:      	ldrb	w8, [x19, #0x3d]
   1e66c:      	cmp	w8, w21
   1e670:      	b.ne	0x1e8c4 <pd_process_event_com+0x6a8>
   1e674:      	mov	w8, #0x8c
   1e678:      	b	0x1e914 <pd_process_event_com+0x6f8>
   1e67c:      	ldrb	w8, [x19, #0x3d]
   1e680:      	cmp	w8, #0x89
   1e684:      	b.eq	0x1e6cc <pd_process_event_com+0x4b0>
   1e688:      	b	0x1e8c4 <pd_process_event_com+0x6a8>
   1e68c:      	ldrb	w8, [x19, #0x3d]
   1e690:      	cmp	w8, w21
   1e694:      	b.ne	0x1e8c4 <pd_process_event_com+0x6a8>
   1e698:      	mov	w8, #0x8e
   1e69c:      	b	0x1e914 <pd_process_event_com+0x6f8>
   1e6a0:      	ldrb	w8, [x19, #0x3d]
   1e6a4:      	cmp	w8, #0x8d
   1e6a8:      	b.eq	0x1e6cc <pd_process_event_com+0x4b0>
   1e6ac:      	b	0x1e8c4 <pd_process_event_com+0x6a8>
   1e6b0:      	ldrb	w8, [x19, #0x3d]
   1e6b4:      	cmp	w8, #0x91
   1e6b8:      	b.eq	0x1e6cc <pd_process_event_com+0x4b0>
   1e6bc:      	b	0x1e8c4 <pd_process_event_com+0x6a8>
   1e6c0:      	ldrb	w8, [x19, #0x3d]
   1e6c4:      	cmp	w8, #0x8f
   1e6c8:      	b.ne	0x1e8c4 <pd_process_event_com+0x6a8>
   1e6cc:      	mov	w0, #0x1
   1e6d0:      	strb	w21, [x19, #0x3c]
   1e6d4:      	b	0x1e91c <pd_process_event_com+0x700>
   1e6d8:      	mov	x0, x19
   1e6dc:      	mov	w1, #0x17
   1e6e0:      	bl	0x1e6e0 <pd_process_event_com+0x4c4>
		000000000001e6e0:  R_AARCH64_CALL26	pd_notify_tcp_event_2nd_result
   1e6e4:      	ldrh	w8, [x19, #0x6a]
   1e6e8:      	tbnz	w8, #0x1, 0x1e774 <pd_process_event_com+0x558>
   1e6ec:      	b	0x1e8c4 <pd_process_event_com+0x6a8>
   1e6f0:      	ldrb	w9, [x19, #0x48]
   1e6f4:      	cbz	w9, 0x1e89c <pd_process_event_com+0x680>
   1e6f8:      	ldrb	w8, [x19, #0x325]
   1e6fc:      	b	0x1e914 <pd_process_event_com+0x6f8>
   1e700:      	ldrb	w9, [x19, #0x3d]
   1e704:      	cmp	w9, w8
   1e708:      	b.ne	0x1e8c4 <pd_process_event_com+0x6a8>
   1e70c:      	ldr	x8, [x19]
   1e710:      	ldr	w8, [x8, #0x3550]
   1e714:      	and	w8, w8, #0xfffffffe
   1e718:      	cmp	w8, #0x8
   1e71c:      	b.eq	0x1e910 <pd_process_event_com+0x6f4>
   1e720:      	ldr	w9, [x19, #0x220]
   1e724:      	tbz	w9, #0x0, 0x1e910 <pd_process_event_com+0x6f4>
   1e728:      	ldrb	w8, [x19, #0x3f]
   1e72c:      	cmp	w8, #0x1
   1e730:      	b.ne	0x1e8d4 <pd_process_event_com+0x6b8>
   1e734:      	tbz	w9, #0x15, 0x1e8d8 <pd_process_event_com+0x6bc>
   1e738:      	b	0x1e910 <pd_process_event_com+0x6f4>
   1e73c:      	ldrb	w9, [x19, #0x3d]
   1e740:      	cmp	w9, w8
   1e744:      	b.ne	0x1e8c4 <pd_process_event_com+0x6a8>
   1e748:      	mov	w8, #0x4
   1e74c:      	mov	w9, #0x55
   1e750:      	mov	w0, #0x1
   1e754:      	strb	w8, [x19, #0x38]
   1e758:      	strb	w9, [x19, #0x3c]
   1e75c:      	b	0x1e91c <pd_process_event_com+0x700>
   1e760:      	mov	x0, x19
   1e764:      	mov	w1, #0x16
   1e768:      	bl	0x1e768 <pd_process_event_com+0x54c>
		000000000001e768:  R_AARCH64_CALL26	pd_notify_tcp_event_2nd_result
   1e76c:      	ldrh	w8, [x19, #0x6a]
   1e770:      	tbz	w8, #0x0, 0x1e8c4 <pd_process_event_com+0x6a8>
   1e774:      	ldr	w8, [x19, #0x60]
   1e778:      	cmp	w8, #0x7f
   1e77c:      	b.hi	0x1e794 <pd_process_event_com+0x578>
   1e780:      	ldr	w9, [x19, #0x64]
   1e784:      	bic	w9, w9, w8
   1e788:      	str	w9, [x19, #0x64]
   1e78c:      	cbz	w8, 0x1e794 <pd_process_event_com+0x578>
   1e790:      	strb	wzr, [x19, #0x5a]
   1e794:      	ldrb	w8, [x19, #0x38]
   1e798:      	cmp	w8, #0x3
   1e79c:      	b.ne	0x1e368 <pd_process_event_com+0x14c>
   1e7a0:      	mov	x0, x19
   1e7a4:      	bl	0x1e7a4 <pd_process_event_com+0x588>
		000000000001e7a4:  R_AARCH64_CALL26	pd_notify_pe_cancel_pr_swap
   1e7a8:      	b	0x1e368 <pd_process_event_com+0x14c>
   1e7ac:      	ldrb	w8, [x19, #0x4b]
   1e7b0:      	cbnz	w8, 0x1e8c4 <pd_process_event_com+0x6a8>
   1e7b4:      	mov	w8, #0x2ff3
   1e7b8:      	ldr	x9, [x19]
   1e7bc:      	ldrb	w8, [x9, x8]
   1e7c0:      	cbnz	w8, 0x1e8c4 <pd_process_event_com+0x6a8>
   1e7c4:      	ldrb	w8, [x19, #0x3f]
   1e7c8:      	mov	w9, #0x29
   1e7cc:      	cmp	w8, #0x0
   1e7d0:      	mov	w8, #0xf
   1e7d4:      	csel	w8, w9, w8, eq
   1e7d8:      	b	0x1e914 <pd_process_event_com+0x6f8>
   1e7dc:      	ldr	w8, [x19, #0x60]
   1e7e0:      	cmp	w8, #0x7f
   1e7e4:      	b.hi	0x1e7fc <pd_process_event_com+0x5e0>
   1e7e8:      	ldr	w9, [x19, #0x64]
   1e7ec:      	bic	w9, w9, w8
   1e7f0:      	str	w9, [x19, #0x64]
   1e7f4:      	cbz	w8, 0x1e7fc <pd_process_event_com+0x5e0>
   1e7f8:      	strb	wzr, [x19, #0x5a]
   1e7fc:      	mov	x0, x19
   1e800:      	bl	0x1e800 <pd_process_event_com+0x5e4>
		000000000001e800:  R_AARCH64_CALL26	pd_notify_pe_reset_protocol
   1e804:      	mov	x0, x19
   1e808:      	mov	w1, #0x1a
   1e80c:      	bl	0x1e80c <pd_process_event_com+0x5f0>
		000000000001e80c:  R_AARCH64_CALL26	pd_notify_tcp_event_2nd_result
   1e810:      	ldrh	w8, [x19, #0x6a]
   1e814:      	tbnz	w8, #0x2, 0x1e368 <pd_process_event_com+0x14c>
   1e818:      	ldr	w8, [x19, #0x74]
   1e81c:      	cmp	w8, #0x35
   1e820:      	b.hi	0x1e8c4 <pd_process_event_com+0x6a8>
   1e824:      	mov	w8, #0x506
   1e828:      	ldr	x0, [x19]
   1e82c:      	add	x1, sp, #0x8
   1e830:      	mov	w2, wzr
   1e834:      	stp	x8, xzr, [sp, #0x8]
   1e838:      	bl	0x1e838 <pd_process_event_com+0x61c>
		000000000001e838:  R_AARCH64_CALL26	pd_put_vdm_event
   1e83c:      	b	0x1e8c4 <pd_process_event_com+0x6a8>
   1e840:      	ldrb	w9, [x19, #0x39c]
   1e844:      	cbz	w9, 0x1e8c4 <pd_process_event_com+0x6a8>
   1e848:      	ldrb	w9, [x19, #0x3d]
   1e84c:      	cmp	w9, w8
   1e850:      	b.ne	0x1e8c4 <pd_process_event_com+0x6a8>
   1e854:      	mov	w8, #0x90
   1e858:      	b	0x1e914 <pd_process_event_com+0x6f8>
   1e85c:      	ldrb	w9, [x19, #0x3d]
   1e860:      	cmp	w9, w8
   1e864:      	b.ne	0x1e8c4 <pd_process_event_com+0x6a8>
   1e868:      	mov	w8, #0x95
   1e86c:      	b	0x1e914 <pd_process_event_com+0x6f8>
   1e870:      	ldr	x8, [x20, #0x8]
   1e874:      	mov	w9, #0x50000000
   1e878:      	ldr	w8, [x8, #0x8]
   1e87c:      	and	w8, w8, #0xf0000000
   1e880:      	cmp	w8, w9
   1e884:      	b.eq	0x1e8cc <pd_process_event_com+0x6b0>
   1e888:      	mov	w9, #-0x80000000
   1e88c:      	cmp	w8, w9
   1e890:      	b.ne	0x1e8c4 <pd_process_event_com+0x6a8>
   1e894:      	mov	w8, #0x9a
   1e898:      	b	0x1e914 <pd_process_event_com+0x6f8>
   1e89c:      	ldrb	w9, [x19, #0x3d]
   1e8a0:      	cmp	w9, w8
   1e8a4:      	b.ne	0x1e8c4 <pd_process_event_com+0x6a8>
   1e8a8:      	ldr	w9, [x19, #0x220]
   1e8ac:      	tbz	w9, #0x1, 0x1e910 <pd_process_event_com+0x6f4>
   1e8b0:      	ldrb	w8, [x19, #0x3e]
   1e8b4:      	cmp	w8, #0x1
   1e8b8:      	b.ne	0x1e8ec <pd_process_event_com+0x6d0>
   1e8bc:      	tbnz	w9, #0x1b, 0x1e910 <pd_process_event_com+0x6f4>
   1e8c0:      	b	0x1e8f0 <pd_process_event_com+0x6d4>
   1e8c4:      	mov	w0, wzr
   1e8c8:      	b	0x1e91c <pd_process_event_com+0x700>
   1e8cc:      	mov	w8, #0x9b
   1e8d0:      	b	0x1e914 <pd_process_event_com+0x6f8>
   1e8d4:      	tbnz	w9, #0x14, 0x1e910 <pd_process_event_com+0x6f4>
   1e8d8:      	mov	w9, #0x3
   1e8dc:      	cmp	w8, #0x0
   1e8e0:      	mov	w8, #0x3e
   1e8e4:      	mov	w10, #0x45
   1e8e8:      	b	0x1e900 <pd_process_event_com+0x6e4>
   1e8ec:      	tbnz	w9, #0x1a, 0x1e910 <pd_process_event_com+0x6f4>
   1e8f0:      	mov	w9, #0x2
   1e8f4:      	cmp	w8, #0x0
   1e8f8:      	mov	w8, #0x34
   1e8fc:      	mov	w10, #0x39
   1e900:      	csel	w8, w10, w8, eq
   1e904:      	strb	wzr, [x19, #0x4b]
   1e908:      	strb	w9, [x19, #0x38]
   1e90c:      	b	0x1e914 <pd_process_event_com+0x6f8>
   1e910:      	mov	w8, #0x97
   1e914:      	mov	w0, #0x1
   1e918:      	strb	w8, [x19, #0x3c]
   1e91c:      	mrs	x8, SP_EL0
   1e920:      	ldr	x8, [x8, #0x638]
   1e924:      	ldur	x9, [x29, #-0x8]
   1e928:      	cmp	x8, x9
   1e92c:      	b.ne	0x1e94c <pd_process_event_com+0x730>
   1e930:      	and	w0, w0, #0x1
   1e934:      	ldp	x20, x19, [sp, #0x40]
   1e938:      	ldp	x29, x30, [sp, #0x20]
   1e93c:      	ldr	x21, [sp, #0x30]
   1e940:      	add	sp, sp, #0x50
   1e944:      	autiasp
   1e948:      	ret
   1e94c:      	bl	0x1e94c <pd_process_event_com+0x730>
		000000000001e94c:  R_AARCH64_CALL26	__stack_chk_fail
