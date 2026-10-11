source pd_process_event_com section=.text address=0x1e200 size=1836
   1e200:      	paciasp
   1e204:      	sub	sp, sp, #0x50
   1e208:      	stp	x29, x30, [sp, #0x20]
   1e20c:      	str	x21, [sp, #0x30]
   1e210:      	stp	x20, x19, [sp, #0x40]
   1e214:      	add	x29, sp, #0x20
   1e218:      	mrs	x8, SP_EL0
   1e21c:      	mov	x19, x0
   1e220:      	ldr	x8, [x8, #0x638]
   1e224:      	mov	w0, wzr
   1e228:      	stur	x8, [x29, #-0x8]
   1e22c:      	ldrb	w8, [x1]
   1e230:      	sub	w8, w8, #0x1
   1e234:      	cmp	w8, #0x6
   1e238:      	b.hi	0x1e8f8 <pd_process_event_com+0x6f8>
   1e23c:      	adrp	x9, 0x1e000 <pd_process_event_tcp+0x2b8>
		000000000001e23c:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x1c62
   1e240:      	add	x9, x9, #0x0
		000000000001e240:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x1c62
   1e244:      	mov	x20, x1
   1e248:      	adr	x10, #0x10
   1e24c:      	ldrh	w11, [x9, x8, lsl #1]
   1e250:      	add	x10, x10, x11, lsl #2
   1e254:      	br	x10
   1e258:      	ldrb	w10, [x19, #0x13d]
   1e25c:      	ldrb	w8, [x19, #0x324]
   1e260:      	ldrb	w9, [x20, #0x1]
   1e264:      	cmp	w10, #0x1
   1e268:      	b.hi	0x1e3f8 <pd_process_event_com+0x1f8>
   1e26c:      	cmp	w9, #0x10
   1e270:      	b.lo	0x1e3f8 <pd_process_event_com+0x1f8>
   1e274:      	mov	w8, #0x19
   1e278:      	b	0x1e3ec <pd_process_event_com+0x1ec>
   1e27c:      	ldrb	w10, [x19, #0x13d]
   1e280:      	ldrb	w8, [x19, #0x324]
   1e284:      	ldrb	w9, [x20, #0x1]
   1e288:      	cmp	w10, #0x1
   1e28c:      	b.hi	0x1e298 <pd_process_event_com+0x98>
   1e290:      	cmp	w9, #0x5
   1e294:      	b.hs	0x1e3e8 <pd_process_event_com+0x1e8>
   1e298:      	mov	w0, wzr
   1e29c:      	sub	w9, w9, #0x3
   1e2a0:      	cmp	w9, #0x9
   1e2a4:      	b.hi	0x1e8f8 <pd_process_event_com+0x6f8>
   1e2a8:      	adrp	x10, 0x1e000 <pd_process_event_tcp+0x2b8>
		000000000001e2a8:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x1ccc
   1e2ac:      	add	x10, x10, #0x0
		000000000001e2ac:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x1ccc
   1e2b0:      	adr	x11, #0x10
   1e2b4:      	ldrh	w12, [x10, x9, lsl #1]
   1e2b8:      	add	x11, x11, x12, lsl #2
   1e2bc:      	br	x11
   1e2c0:      	ldrb	w9, [x19, #0x3d]
   1e2c4:      	cmp	w9, w8
   1e2c8:      	b.ne	0x1e8a0 <pd_process_event_com+0x6a0>
   1e2cc:      	ldr	w8, [x19, #0x190]
   1e2d0:      	mov	w9, #0x1389
   1e2d4:      	cmp	w8, w9
   1e2d8:      	b.lt	0x1e84c <pd_process_event_com+0x64c>
   1e2dc:      	adrp	x0, 0x1e000 <pd_process_event_tcp+0x2b8>
		000000000001e2dc:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x1dca
   1e2e0:      	add	x0, x0, #0x0
		000000000001e2e0:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x1dca
   1e2e4:      	bl	0x1e2e4 <pd_process_event_com+0xe4>
		000000000001e2e4:  R_AARCH64_CALL26	pd_dbg_info
   1e2e8:      	b	0x1e8a0 <pd_process_event_com+0x6a0>
   1e2ec:      	ldrb	w8, [x19, #0x13d]
   1e2f0:      	cmp	w8, #0x1
   1e2f4:      	b.ls	0x1e3e8 <pd_process_event_com+0x1e8>
   1e2f8:      	ldrb	w21, [x19, #0x324]
   1e2fc:      	ldrb	w8, [x19, #0x3d]
   1e300:      	cmp	w8, w21
   1e304:      	b.ne	0x1e450 <pd_process_event_com+0x250>
   1e308:      	mov	x0, x19
   1e30c:      	bl	0x1e30c <pd_process_event_com+0x10c>
		000000000001e30c:  R_AARCH64_CALL26	pd_is_multi_chunk_msg
   1e310:      	tbz	w0, #0x0, 0x1e450 <pd_process_event_com+0x250>
   1e314:      	mov	w8, #0x1
   1e318:      	mov	x0, x19
   1e31c:      	mov	x1, x20
   1e320:      	strb	w8, [x19, #0x327]
   1e324:      	bl	0x1e324 <pd_process_event_com+0x124>
		000000000001e324:  R_AARCH64_CALL26	pd_process_protocol_error
   1e328:      	b	0x1e8f8 <pd_process_event_com+0x6f8>
   1e32c:      	ldrb	w8, [x20, #0x1]
   1e330:      	cmp	w8, #0x3
   1e334:      	b.eq	0x1e498 <pd_process_event_com+0x298>
   1e338:      	cmp	w8, #0x2
   1e33c:      	b.eq	0x1e4a8 <pd_process_event_com+0x2a8>
   1e340:      	cbnz	w8, 0x1e8a0 <pd_process_event_com+0x6a0>
   1e344:      	ldrh	w8, [x19, #0x6a]
   1e348:      	tbz	w8, #0xa, 0x1e8a0 <pd_process_event_com+0x6a0>
   1e34c:      	ldrb	w8, [x19, #0x324]
   1e350:      	b	0x1e8f0 <pd_process_event_com+0x6f0>
   1e354:      	ldrb	w8, [x20, #0x1]
   1e358:      	sub	w9, w8, #0x7
   1e35c:      	cmp	w9, #0x2
   1e360:      	b.lo	0x1e430 <pd_process_event_com+0x230>
   1e364:      	cmp	w8, #0xa
   1e368:      	b.eq	0x1e4bc <pd_process_event_com+0x2bc>
   1e36c:      	cmp	w8, #0x2
   1e370:      	b.ne	0x1e8a0 <pd_process_event_com+0x6a0>
   1e374:      	mov	w8, #0x2ff3
   1e378:      	ldr	x9, [x19]
   1e37c:      	ldrb	w8, [x9, x8]
   1e380:      	cbz	w8, 0x1e390 <pd_process_event_com+0x190>
   1e384:      	ldrb	w8, [x19, #0x78]
   1e388:      	add	w8, w8, #0x1
   1e38c:      	strb	w8, [x19, #0x78]
   1e390:      	ldrb	w8, [x19, #0x3f]
   1e394:      	mov	w9, #0x25
   1e398:      	cmp	w8, #0x0
   1e39c:      	mov	w8, #0xa
   1e3a0:      	csel	w8, w9, w8, eq
   1e3a4:      	b	0x1e8f0 <pd_process_event_com+0x6f0>
   1e3a8:      	ldrb	w8, [x20, #0x1]
   1e3ac:      	mov	w0, wzr
   1e3b0:      	sub	w8, w8, #0x1
   1e3b4:      	cmp	w8, #0x21
   1e3b8:      	b.hi	0x1e8f8 <pd_process_event_com+0x6f8>
   1e3bc:      	adrp	x9, 0x1e000 <pd_process_event_tcp+0x2b8>
		000000000001e3bc:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x1c70
   1e3c0:      	add	x9, x9, #0x0
		000000000001e3c0:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x1c70
   1e3c4:      	ldrb	w20, [x19, #0x324]
   1e3c8:      	adr	x10, #0x10
   1e3cc:      	ldrh	w11, [x9, x8, lsl #1]
   1e3d0:      	add	x10, x10, x11, lsl #2
   1e3d4:      	br	x10
   1e3d8:      	ldrb	w8, [x19, #0x3d]
   1e3dc:      	cmp	w8, #0x9b
   1e3e0:      	b.eq	0x1e638 <pd_process_event_com+0x438>
   1e3e4:      	b	0x1e8a0 <pd_process_event_com+0x6a0>
   1e3e8:      	mov	w8, #0x10
   1e3ec:      	mov	w0, wzr
   1e3f0:      	strb	w8, [x20, #0x1]
   1e3f4:      	b	0x1e8f8 <pd_process_event_com+0x6f8>
   1e3f8:      	mov	w0, wzr
   1e3fc:      	sub	w9, w9, #0x1
   1e400:      	cmp	w9, #0x17
   1e404:      	b.hi	0x1e8f8 <pd_process_event_com+0x6f8>
   1e408:      	adrp	x10, 0x1e000 <pd_process_event_tcp+0x2b8>
		000000000001e408:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x1ce0
   1e40c:      	add	x10, x10, #0x0
		000000000001e40c:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x1ce0
   1e410:      	adr	x11, #0x10
   1e414:      	ldrh	w12, [x10, x9, lsl #1]
   1e418:      	add	x11, x11, x12, lsl #2
   1e41c:      	br	x11
   1e420:      	ldrh	w9, [x19, #0x6a]
   1e424:      	tbnz	w9, #0x9, 0x1e8f0 <pd_process_event_com+0x6f0>
   1e428:      	tbnz	w9, #0x8, 0x1e504 <pd_process_event_com+0x304>
   1e42c:      	b	0x1e8a0 <pd_process_event_com+0x6a0>
   1e430:      	ldrb	w8, [x19, #0x78]
   1e434:      	cmp	w8, #0x3
   1e438:      	b.lo	0x1e4cc <pd_process_event_com+0x2cc>
   1e43c:      	adrp	x0, 0x1e000 <pd_process_event_tcp+0x2b8>
		000000000001e43c:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x2bc0
   1e440:      	add	x0, x0, #0x0
		000000000001e440:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x2bc0
   1e444:      	bl	0x1e444 <pd_process_event_com+0x244>
		000000000001e444:  R_AARCH64_CALL26	pd_dbg_info
   1e448:      	mov	w8, #0x98
   1e44c:      	b	0x1e8f0 <pd_process_event_com+0x6f0>
   1e450:      	ldrb	w8, [x20, #0x1]
   1e454:      	mov	w0, wzr
   1e458:      	sub	w8, w8, #0x3
   1e45c:      	cmp	w8, #0xb
   1e460:      	b.hi	0x1e8f8 <pd_process_event_com+0x6f8>
   1e464:      	adrp	x9, 0x1e000 <pd_process_event_tcp+0x2b8>
		000000000001e464:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x1cb4
   1e468:      	add	x9, x9, #0x0
		000000000001e468:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x1cb4
   1e46c:      	adr	x10, #0x10
   1e470:      	ldrh	w11, [x9, x8, lsl #1]
   1e474:      	add	x10, x10, x11, lsl #2
   1e478:      	br	x10
   1e47c:      	ldrb	w8, [x19, #0x380]
   1e480:      	cbz	w8, 0x1e8a0 <pd_process_event_com+0x6a0>
   1e484:      	ldrb	w8, [x19, #0x3d]
   1e488:      	cmp	w8, w21
   1e48c:      	b.ne	0x1e8a0 <pd_process_event_com+0x6a0>
   1e490:      	mov	w8, #0x8a
   1e494:      	b	0x1e8f0 <pd_process_event_com+0x6f0>
   1e498:      	ldrb	w8, [x19, #0x13e]
   1e49c:      	cmp	w8, #0x2
   1e4a0:      	b.hs	0x1e4b4 <pd_process_event_com+0x2b4>
   1e4a4:      	b	0x1e8a0 <pd_process_event_com+0x6a0>
   1e4a8:      	ldrb	w8, [x19, #0x13d]
   1e4ac:      	cmp	w8, #0x1
   1e4b0:      	b.ls	0x1e8a0 <pd_process_event_com+0x6a0>
   1e4b4:      	mov	w8, #0x93
   1e4b8:      	b	0x1e8f0 <pd_process_event_com+0x6f0>
   1e4bc:      	ldr	x0, [x19]
   1e4c0:      	bl	0x1e4c0 <pd_process_event_com+0x2c0>
		000000000001e4c0:  R_AARCH64_CALL26	tcpci_retransmit
   1e4c4:      	mov	w0, #0x1
   1e4c8:      	b	0x1e8f8 <pd_process_event_com+0x6f8>
   1e4cc:      	ldrh	w8, [x19, #0x6a]
   1e4d0:      	tbnz	w8, #0x3, 0x1e5e0 <pd_process_event_com+0x3e0>
   1e4d4:      	tbnz	w8, #0x5, 0x1e6dc <pd_process_event_com+0x4dc>
   1e4d8:      	tbz	w8, #0x6, 0x1e8a0 <pd_process_event_com+0x6a0>
   1e4dc:      	mov	w8, #0x98
   1e4e0:      	b	0x1e8f0 <pd_process_event_com+0x6f0>
   1e4e4:      	ldr	x8, [x19]
   1e4e8:      	mov	w9, #0x3510
   1e4ec:      	add	x0, x8, x9
   1e4f0:      	bl	0x1e4f0 <pd_process_event_com+0x2f0>
		000000000001e4f0:  R_AARCH64_CALL26	mutex_is_locked
   1e4f4:      	tbz	w0, #0x0, 0x1e5f4 <pd_process_event_com+0x3f4>
   1e4f8:      	adrp	x0, 0x1e000 <pd_process_event_tcp+0x2b8>
		000000000001e4f8:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x3272
   1e4fc:      	add	x0, x0, #0x0
		000000000001e4fc:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x3272
   1e500:      	bl	0x1e500 <pd_process_event_com+0x300>
		000000000001e500:  R_AARCH64_CALL26	pd_dbg_info
   1e504:      	ldr	x0, [x19]
   1e508:      	mov	w1, #0x7
   1e50c:      	bl	0x1e50c <pd_process_event_com+0x30c>
		000000000001e50c:  R_AARCH64_CALL26	tcpc_enable_timer
   1e510:      	b	0x1e8a0 <pd_process_event_com+0x6a0>
   1e514:      	ldrb	w8, [x19, #0x40]
   1e518:      	cmp	w8, #0x3
   1e51c:      	b.ne	0x1e8a0 <pd_process_event_com+0x6a0>
   1e520:      	mov	x0, x19
   1e524:      	mov	w1, #0x1
   1e528:      	bl	0x1e528 <pd_process_event_com+0x328>
		000000000001e528:  R_AARCH64_CALL26	pd_set_vconn
   1e52c:      	ldr	w8, [x19, #0x64]
   1e530:      	ldrb	w9, [x19, #0x61]
   1e534:      	and	w8, w8, #0xfffffbff
   1e538:      	orr	w8, w8, #0x20000000
   1e53c:      	str	w8, [x19, #0x64]
   1e540:      	tbz	w9, #0x2, 0x1e548 <pd_process_event_com+0x348>
   1e544:      	strb	wzr, [x19, #0x5a]
   1e548:      	ldr	x0, [x19]
   1e54c:      	bl	0x1e54c <pd_process_event_com+0x34c>
		000000000001e54c:  R_AARCH64_CALL26	tcpc_event_thread_wake_up
   1e550:      	b	0x1e8a0 <pd_process_event_com+0x6a0>
   1e554:      	ldrb	w8, [x19, #0x3d]
   1e558:      	cmp	w8, w20
   1e55c:      	b.ne	0x1e8a0 <pd_process_event_com+0x6a0>
   1e560:      	ldrb	w8, [x19, #0x3e]
   1e564:      	cmp	w8, #0x1
   1e568:      	b.ne	0x1e8a0 <pd_process_event_com+0x6a0>
   1e56c:      	ldr	w8, [x19, #0x64]
   1e570:      	mov	w9, #0xfbff
   1e574:      	movk	w9, #0xdfff, lsl #16
   1e578:      	add	w9, w9, #0x300
   1e57c:      	and	w8, w8, w9
   1e580:      	ldrb	w9, [x19, #0x61]
   1e584:      	orr	w8, w8, #0x20000000
   1e588:      	str	w8, [x19, #0x64]
   1e58c:      	tbnz	w9, #0x0, 0x1e544 <pd_process_event_com+0x344>
   1e590:      	b	0x1e548 <pd_process_event_com+0x348>
   1e594:      	mov	x0, x19
   1e598:      	mov	w1, #0x13
   1e59c:      	bl	0x1e59c <pd_process_event_com+0x39c>
		000000000001e59c:  R_AARCH64_CALL26	pd_notify_tcp_event_buf_reset
   1e5a0:      	b	0x1e8a0 <pd_process_event_com+0x6a0>
   1e5a4:      	ldrb	w9, [x19, #0x3d]
   1e5a8:      	cmp	w9, #0x8b
   1e5ac:      	b.ne	0x1e8a0 <pd_process_event_com+0x6a0>
   1e5b0:      	b	0x1e8f0 <pd_process_event_com+0x6f0>
   1e5b4:      	ldrb	w9, [x19, #0x39c]
   1e5b8:      	cbz	w9, 0x1e8a0 <pd_process_event_com+0x6a0>
   1e5bc:      	ldrb	w9, [x19, #0x3d]
   1e5c0:      	cmp	w9, w8
   1e5c4:      	b.ne	0x1e8a0 <pd_process_event_com+0x6a0>
   1e5c8:      	mov	w8, #0x92
   1e5cc:      	b	0x1e8f0 <pd_process_event_com+0x6f0>
   1e5d0:      	ldrb	w9, [x19, #0x3d]
   1e5d4:      	cmp	w9, #0x94
   1e5d8:      	b.ne	0x1e8a0 <pd_process_event_com+0x6a0>
   1e5dc:      	b	0x1e8f0 <pd_process_event_com+0x6f0>
   1e5e0:      	mov	x0, x19
   1e5e4:      	mov	w1, #0x1c
   1e5e8:      	bl	0x1e5e8 <pd_process_event_com+0x3e8>
		000000000001e5e8:  R_AARCH64_CALL26	pd_notify_tcp_event_2nd_result
   1e5ec:      	ldrb	w8, [x19, #0x324]
   1e5f0:      	b	0x1e8f0 <pd_process_event_com+0x6f0>
   1e5f4:      	ldr	w8, [x19, #0x60]
   1e5f8:      	cmp	w8, #0x7f
   1e5fc:      	b.hi	0x1e614 <pd_process_event_com+0x414>
   1e600:      	ldr	w9, [x19, #0x64]
   1e604:      	bic	w9, w9, w8
   1e608:      	str	w9, [x19, #0x64]
   1e60c:      	cbz	w8, 0x1e614 <pd_process_event_com+0x414>
   1e610:      	strb	wzr, [x19, #0x5a]
   1e614:      	mov	x0, x19
   1e618:      	bl	0x1e618 <pd_process_event_com+0x418>
		000000000001e618:  R_AARCH64_CALL26	pd_notify_pe_cancel_pr_swap
   1e61c:      	mov	x0, x19
   1e620:      	mov	w1, #0x18
   1e624:      	bl	0x1e624 <pd_process_event_com+0x424>
		000000000001e624:  R_AARCH64_CALL26	pd_notify_tcp_event_2nd_result
   1e628:      	ldrh	w8, [x19, #0x6a]
   1e62c:      	tbnz	w8, #0x2, 0x1e638 <pd_process_event_com+0x438>
   1e630:      	tbnz	w8, #0x4, 0x1e6dc <pd_process_event_com+0x4dc>
   1e634:      	b	0x1e8a0 <pd_process_event_com+0x6a0>
   1e638:      	mov	w0, #0x1
   1e63c:      	strb	w20, [x19, #0x3c]
   1e640:      	b	0x1e8f8 <pd_process_event_com+0x6f8>
   1e644:      	ldrb	w8, [x19, #0x380]
   1e648:      	cbz	w8, 0x1e8a0 <pd_process_event_com+0x6a0>
   1e64c:      	ldrb	w8, [x19, #0x3d]
   1e650:      	cmp	w8, w21
   1e654:      	b.ne	0x1e8a0 <pd_process_event_com+0x6a0>
   1e658:      	mov	w8, #0x8c
   1e65c:      	b	0x1e8f0 <pd_process_event_com+0x6f0>
   1e660:      	ldrb	w8, [x19, #0x3d]
   1e664:      	cmp	w8, #0x89
   1e668:      	b.eq	0x1e6b0 <pd_process_event_com+0x4b0>
   1e66c:      	b	0x1e8a0 <pd_process_event_com+0x6a0>
   1e670:      	ldrb	w8, [x19, #0x3d]
   1e674:      	cmp	w8, w21
   1e678:      	b.ne	0x1e8a0 <pd_process_event_com+0x6a0>
   1e67c:      	mov	w8, #0x8e
   1e680:      	b	0x1e8f0 <pd_process_event_com+0x6f0>
   1e684:      	ldrb	w8, [x19, #0x3d]
   1e688:      	cmp	w8, #0x8d
   1e68c:      	b.eq	0x1e6b0 <pd_process_event_com+0x4b0>
   1e690:      	b	0x1e8a0 <pd_process_event_com+0x6a0>
   1e694:      	ldrb	w8, [x19, #0x3d]
   1e698:      	cmp	w8, #0x91
   1e69c:      	b.eq	0x1e6b0 <pd_process_event_com+0x4b0>
   1e6a0:      	b	0x1e8a0 <pd_process_event_com+0x6a0>
   1e6a4:      	ldrb	w8, [x19, #0x3d]
   1e6a8:      	cmp	w8, #0x8f
   1e6ac:      	b.ne	0x1e8a0 <pd_process_event_com+0x6a0>
   1e6b0:      	mov	w0, #0x1
   1e6b4:      	strb	w21, [x19, #0x3c]
   1e6b8:      	b	0x1e8f8 <pd_process_event_com+0x6f8>
   1e6bc:      	mov	x0, x19
   1e6c0:      	mov	w1, #0x17
   1e6c4:      	bl	0x1e6c4 <pd_process_event_com+0x4c4>
		000000000001e6c4:  R_AARCH64_CALL26	pd_notify_tcp_event_2nd_result
   1e6c8:      	ldrh	w8, [x19, #0x6a]
   1e6cc:      	tbnz	w8, #0x1, 0x1e758 <pd_process_event_com+0x558>
   1e6d0:      	b	0x1e8a0 <pd_process_event_com+0x6a0>
   1e6d4:      	ldrb	w9, [x19, #0x48]
   1e6d8:      	cbz	w9, 0x1e878 <pd_process_event_com+0x678>
   1e6dc:      	ldrb	w8, [x19, #0x325]
   1e6e0:      	b	0x1e8f0 <pd_process_event_com+0x6f0>
   1e6e4:      	ldrb	w9, [x19, #0x3d]
   1e6e8:      	cmp	w9, w8
   1e6ec:      	b.ne	0x1e8a0 <pd_process_event_com+0x6a0>
   1e6f0:      	ldr	x8, [x19]
   1e6f4:      	ldr	w8, [x8, #0x3550]
   1e6f8:      	and	w8, w8, #0xfffffffe
   1e6fc:      	cmp	w8, #0x8
   1e700:      	b.eq	0x1e8ec <pd_process_event_com+0x6ec>
   1e704:      	ldr	w9, [x19, #0x220]
   1e708:      	tbz	w9, #0x0, 0x1e8ec <pd_process_event_com+0x6ec>
   1e70c:      	ldrb	w8, [x19, #0x3f]
   1e710:      	cmp	w8, #0x1
   1e714:      	b.ne	0x1e8b0 <pd_process_event_com+0x6b0>
   1e718:      	tbz	w9, #0x15, 0x1e8b4 <pd_process_event_com+0x6b4>
   1e71c:      	b	0x1e8ec <pd_process_event_com+0x6ec>
   1e720:      	ldrb	w9, [x19, #0x3d]
   1e724:      	cmp	w9, w8
   1e728:      	b.ne	0x1e8a0 <pd_process_event_com+0x6a0>
   1e72c:      	mov	w8, #0x4
   1e730:      	mov	w9, #0x55
   1e734:      	mov	w0, #0x1
   1e738:      	strb	w8, [x19, #0x38]
   1e73c:      	strb	w9, [x19, #0x3c]
   1e740:      	b	0x1e8f8 <pd_process_event_com+0x6f8>
   1e744:      	mov	x0, x19
   1e748:      	mov	w1, #0x16
   1e74c:      	bl	0x1e74c <pd_process_event_com+0x54c>
		000000000001e74c:  R_AARCH64_CALL26	pd_notify_tcp_event_2nd_result
   1e750:      	ldrh	w8, [x19, #0x6a]
   1e754:      	tbz	w8, #0x0, 0x1e8a0 <pd_process_event_com+0x6a0>
   1e758:      	ldr	w8, [x19, #0x60]
   1e75c:      	cmp	w8, #0x7f
   1e760:      	b.hi	0x1e778 <pd_process_event_com+0x578>
   1e764:      	ldr	w9, [x19, #0x64]
   1e768:      	bic	w9, w9, w8
   1e76c:      	str	w9, [x19, #0x64]
   1e770:      	cbz	w8, 0x1e778 <pd_process_event_com+0x578>
   1e774:      	strb	wzr, [x19, #0x5a]
   1e778:      	ldrb	w8, [x19, #0x38]
   1e77c:      	cmp	w8, #0x3
   1e780:      	b.ne	0x1e34c <pd_process_event_com+0x14c>
   1e784:      	mov	x0, x19
   1e788:      	bl	0x1e788 <pd_process_event_com+0x588>
		000000000001e788:  R_AARCH64_CALL26	pd_notify_pe_cancel_pr_swap
   1e78c:      	b	0x1e34c <pd_process_event_com+0x14c>
   1e790:      	ldrb	w8, [x19, #0x4b]
   1e794:      	cbnz	w8, 0x1e8a0 <pd_process_event_com+0x6a0>
   1e798:      	mov	w8, #0x2ff3
   1e79c:      	ldr	x9, [x19]
   1e7a0:      	ldrb	w8, [x9, x8]
   1e7a4:      	cbnz	w8, 0x1e8a0 <pd_process_event_com+0x6a0>
   1e7a8:      	ldrb	w8, [x19, #0x3f]
   1e7ac:      	mov	w9, #0x29
   1e7b0:      	cmp	w8, #0x0
   1e7b4:      	mov	w8, #0xf
   1e7b8:      	csel	w8, w9, w8, eq
   1e7bc:      	b	0x1e8f0 <pd_process_event_com+0x6f0>
   1e7c0:      	ldr	w8, [x19, #0x60]
   1e7c4:      	cmp	w8, #0x7f
   1e7c8:      	b.hi	0x1e7e0 <pd_process_event_com+0x5e0>
   1e7cc:      	ldr	w9, [x19, #0x64]
   1e7d0:      	bic	w9, w9, w8
   1e7d4:      	str	w9, [x19, #0x64]
   1e7d8:      	cbz	w8, 0x1e7e0 <pd_process_event_com+0x5e0>
   1e7dc:      	strb	wzr, [x19, #0x5a]
   1e7e0:      	mov	x0, x19
   1e7e4:      	mov	w1, #0x1a
   1e7e8:      	bl	0x1e7e8 <pd_process_event_com+0x5e8>
		000000000001e7e8:  R_AARCH64_CALL26	pd_notify_tcp_event_2nd_result
   1e7ec:      	ldrh	w8, [x19, #0x6a]
   1e7f0:      	tbnz	w8, #0x2, 0x1e34c <pd_process_event_com+0x14c>
   1e7f4:      	ldr	w8, [x19, #0x74]
   1e7f8:      	cmp	w8, #0x35
   1e7fc:      	b.hi	0x1e8a0 <pd_process_event_com+0x6a0>
   1e800:      	mov	w8, #0x506
   1e804:      	ldr	x0, [x19]
   1e808:      	add	x1, sp, #0x8
   1e80c:      	mov	w2, wzr
   1e810:      	stp	x8, xzr, [sp, #0x8]
   1e814:      	bl	0x1e814 <pd_process_event_com+0x614>
		000000000001e814:  R_AARCH64_CALL26	pd_put_vdm_event
   1e818:      	b	0x1e8a0 <pd_process_event_com+0x6a0>
   1e81c:      	ldrb	w9, [x19, #0x39c]
   1e820:      	cbz	w9, 0x1e8a0 <pd_process_event_com+0x6a0>
   1e824:      	ldrb	w9, [x19, #0x3d]
   1e828:      	cmp	w9, w8
   1e82c:      	b.ne	0x1e8a0 <pd_process_event_com+0x6a0>
   1e830:      	mov	w8, #0x90
   1e834:      	b	0x1e8f0 <pd_process_event_com+0x6f0>
   1e838:      	ldrb	w9, [x19, #0x3d]
   1e83c:      	cmp	w9, w8
   1e840:      	b.ne	0x1e8a0 <pd_process_event_com+0x6a0>
   1e844:      	mov	w8, #0x95
   1e848:      	b	0x1e8f0 <pd_process_event_com+0x6f0>
   1e84c:      	ldr	x8, [x20, #0x8]
   1e850:      	mov	w9, #0x50000000
   1e854:      	ldr	w8, [x8, #0x8]
   1e858:      	and	w8, w8, #0xf0000000
   1e85c:      	cmp	w8, w9
   1e860:      	b.eq	0x1e8a8 <pd_process_event_com+0x6a8>
   1e864:      	mov	w9, #-0x80000000
   1e868:      	cmp	w8, w9
   1e86c:      	b.ne	0x1e8a0 <pd_process_event_com+0x6a0>
   1e870:      	mov	w8, #0x9a
   1e874:      	b	0x1e8f0 <pd_process_event_com+0x6f0>
   1e878:      	ldrb	w9, [x19, #0x3d]
   1e87c:      	cmp	w9, w8
   1e880:      	b.ne	0x1e8a0 <pd_process_event_com+0x6a0>
   1e884:      	ldr	w9, [x19, #0x220]
   1e888:      	tbz	w9, #0x1, 0x1e8ec <pd_process_event_com+0x6ec>
   1e88c:      	ldrb	w8, [x19, #0x3e]
   1e890:      	cmp	w8, #0x1
   1e894:      	b.ne	0x1e8c8 <pd_process_event_com+0x6c8>
   1e898:      	tbnz	w9, #0x1b, 0x1e8ec <pd_process_event_com+0x6ec>
   1e89c:      	b	0x1e8cc <pd_process_event_com+0x6cc>
   1e8a0:      	mov	w0, wzr
   1e8a4:      	b	0x1e8f8 <pd_process_event_com+0x6f8>
   1e8a8:      	mov	w8, #0x9b
   1e8ac:      	b	0x1e8f0 <pd_process_event_com+0x6f0>
   1e8b0:      	tbnz	w9, #0x14, 0x1e8ec <pd_process_event_com+0x6ec>
   1e8b4:      	mov	w9, #0x3
   1e8b8:      	cmp	w8, #0x0
   1e8bc:      	mov	w8, #0x3e
   1e8c0:      	mov	w10, #0x45
   1e8c4:      	b	0x1e8dc <pd_process_event_com+0x6dc>
   1e8c8:      	tbnz	w9, #0x1a, 0x1e8ec <pd_process_event_com+0x6ec>
   1e8cc:      	mov	w9, #0x2
   1e8d0:      	cmp	w8, #0x0
   1e8d4:      	mov	w8, #0x34
   1e8d8:      	mov	w10, #0x39
   1e8dc:      	csel	w8, w10, w8, eq
   1e8e0:      	strb	wzr, [x19, #0x4b]
   1e8e4:      	strb	w9, [x19, #0x38]
   1e8e8:      	b	0x1e8f0 <pd_process_event_com+0x6f0>
   1e8ec:      	mov	w8, #0x97
   1e8f0:      	mov	w0, #0x1
   1e8f4:      	strb	w8, [x19, #0x3c]
   1e8f8:      	mrs	x8, SP_EL0
   1e8fc:      	ldr	x8, [x8, #0x638]
   1e900:      	ldur	x9, [x29, #-0x8]
   1e904:      	cmp	x8, x9
   1e908:      	b.ne	0x1e928 <pd_process_event_com+0x728>
   1e90c:      	and	w0, w0, #0x1
   1e910:      	ldp	x20, x19, [sp, #0x40]
   1e914:      	ldp	x29, x30, [sp, #0x20]
   1e918:      	ldr	x21, [sp, #0x30]
   1e91c:      	add	sp, sp, #0x50
   1e920:      	autiasp
   1e924:      	ret
   1e928:      	bl	0x1e928 <pd_process_event_com+0x728>
		000000000001e928:  R_AARCH64_CALL26	__stack_chk_fail
