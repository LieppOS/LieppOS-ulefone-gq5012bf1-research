source tcpc_typec_handle_cc_change section=.text address=0x1444 size=1300
    1444:      	paciasp
    1448:      	sub	sp, sp, #0x60
    144c:      	stp	x29, x30, [sp, #0x20]
    1450:      	str	x23, [sp, #0x30]
    1454:      	stp	x22, x21, [sp, #0x40]
    1458:      	stp	x20, x19, [sp, #0x50]
    145c:      	add	x29, sp, #0x20
    1460:      	mrs	x8, SP_EL0
    1464:      	mov	x19, x0
    1468:      	ldr	x8, [x8, #0x638]
    146c:      	stur	x8, [x29, #-0x8]
    1470:      	bl	0x1470 <tcpc_typec_handle_cc_change+0x2c>
		0000000000001470:  R_AARCH64_CALL26	tcpci_get_cc
    1474:      	tbnz	w0, #0x1f, 0x14d4 <tcpc_typec_handle_cc_change+0x90>
    1478:      	mov	w8, #0x2c70
    147c:      	adrp	x0, 0x1000 <tcpc_show_property+0x3c4>
		000000000000147c:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x217b
    1480:      	add	x0, x0, #0x0
		0000000000001480:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x217b
    1484:      	add	x22, x19, x8
    1488:      	ldrb	w1, [x22, #0x7]
    148c:      	ldrb	w2, [x22, #0x8]
    1490:      	bl	0x1490 <tcpc_typec_handle_cc_change+0x4c>
		0000000000001490:  R_AARCH64_CALL26	pd_dbg_info
    1494:      	mov	x0, x19
    1498:      	bl	0x1958 <typec_try_norp_src>
    149c:      	tbnz	w0, #0x0, 0x14d0 <tcpc_typec_handle_cc_change+0x8c>
    14a0:      	ldrb	w8, [x22, #0x7]
    14a4:      	cmp	w8, #0xf
    14a8:      	b.eq	0x14d0 <tcpc_typec_handle_cc_change+0x8c>
    14ac:      	ldrb	w9, [x22]
    14b0:      	cmp	w9, #0x12
    14b4:      	b.hi	0x1504 <tcpc_typec_handle_cc_change+0xc0>
    14b8:      	mov	w10, #0x1
    14bc:      	mov	w11, #0x3
    14c0:      	lsl	w10, w10, w9
    14c4:      	movk	w11, #0x4, lsl #16
    14c8:      	tst	w10, w11
    14cc:      	b.eq	0x1504 <tcpc_typec_handle_cc_change+0xc0>
    14d0:      	mov	w0, wzr
    14d4:      	mrs	x8, SP_EL0
    14d8:      	ldr	x8, [x8, #0x638]
    14dc:      	ldur	x9, [x29, #-0x8]
    14e0:      	cmp	x8, x9
    14e4:      	b.ne	0x1954 <tcpc_typec_handle_cc_change+0x510>
    14e8:      	ldp	x20, x19, [sp, #0x50]
    14ec:      	ldp	x22, x21, [sp, #0x40]
    14f0:      	ldp	x29, x30, [sp, #0x20]
    14f4:      	ldr	x23, [sp, #0x30]
    14f8:      	add	sp, sp, #0x60
    14fc:      	autiasp
    1500:      	ret
    1504:      	ldr	w10, [x19, #0x2c8c]
    1508:      	cmp	w9, #0x13
    150c:      	b.ne	0x1514 <tcpc_typec_handle_cc_change+0xd0>
    1510:      	tbnz	w10, #0x8, 0x14d0 <tcpc_typec_handle_cc_change+0x8c>
    1514:      	cmp	w9, #0x14
    1518:      	b.ne	0x1520 <tcpc_typec_handle_cc_change+0xdc>
    151c:      	tbnz	w10, #0x9, 0x14d0 <tcpc_typec_handle_cc_change+0x8c>
    1520:      	mov	w0, wzr
    1524:      	cmp	w9, #0xa
    1528:      	b.eq	0x14d4 <tcpc_typec_handle_cc_change+0x90>
    152c:      	ldrb	w10, [x22, #0x384]
    1530:      	cbnz	w10, 0x14d4 <tcpc_typec_handle_cc_change+0x90>
    1534:      	sub	w9, w9, #0x6
    1538:      	cmp	w9, #0xb
    153c:      	b.hi	0x15b8 <tcpc_typec_handle_cc_change+0x174>
    1540:      	adrp	x10, 0x1000 <tcpc_show_property+0x3c4>
		0000000000001540:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x30
    1544:      	add	x10, x10, #0x0
		0000000000001544:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x30
    1548:      	adr	x11, #0x10
    154c:      	ldrb	w12, [x10, x9]
    1550:      	add	x11, x11, x12, lsl #2
    1554:      	br	x11
    1558:      	ldrb	w8, [x22, #0xb]
    155c:      	cmp	w8, #0x0
    1560:      	mov	w8, #0x7
    1564:      	cinc	x8, x8, ne
    1568:      	ldrb	w8, [x22, x8]
    156c:      	cbnz	w8, 0x1628 <tcpc_typec_handle_cc_change+0x1e4>
    1570:      	b	0x1858 <tcpc_typec_handle_cc_change+0x414>
    1574:      	cbz	w8, 0x161c <tcpc_typec_handle_cc_change+0x1d8>
    1578:      	cmp	w8, #0x1
    157c:      	b.eq	0x161c <tcpc_typec_handle_cc_change+0x1d8>
    1580:      	cmp	w8, #0x2
    1584:      	b.ne	0x1858 <tcpc_typec_handle_cc_change+0x414>
    1588:      	ldrb	w8, [x22, #0x8]
    158c:      	cmp	w8, #0x2
    1590:      	b.lo	0x1628 <tcpc_typec_handle_cc_change+0x1e4>
    1594:      	b	0x1858 <tcpc_typec_handle_cc_change+0x414>
    1598:      	ldrb	w9, [x22, #0x8]
    159c:      	add	w8, w8, w9
    15a0:      	sub	w8, w8, #0x5
    15a4:      	cmp	w8, #0x3
    15a8:      	b.lo	0x1628 <tcpc_typec_handle_cc_change+0x1e4>
    15ac:      	b	0x1858 <tcpc_typec_handle_cc_change+0x414>
    15b0:      	cbnz	w8, 0x15dc <tcpc_typec_handle_cc_change+0x198>
    15b4:      	b	0x1858 <tcpc_typec_handle_cc_change+0x414>
    15b8:      	ldrb	w9, [x22, #0x8]
    15bc:      	add	w10, w9, w8
    15c0:      	cmp	w10, #0x1
    15c4:      	b.ne	0x1788 <tcpc_typec_handle_cc_change+0x344>
    15c8:      	adrp	x0, 0x1000 <tcpc_show_property+0x3c4>
		00000000000015c8:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x1e3a
    15cc:      	add	x0, x0, #0x0
		00000000000015cc:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x1e3a
    15d0:      	bl	0x15d0 <tcpc_typec_handle_cc_change+0x18c>
		00000000000015d0:  R_AARCH64_CALL26	pd_dbg_info
    15d4:      	b	0x1858 <tcpc_typec_handle_cc_change+0x414>
    15d8:      	cbnz	w8, 0x1628 <tcpc_typec_handle_cc_change+0x1e4>
    15dc:      	ldrb	w8, [x22, #0x8]
    15e0:      	cbnz	w8, 0x1628 <tcpc_typec_handle_cc_change+0x1e4>
    15e4:      	b	0x1858 <tcpc_typec_handle_cc_change+0x414>
    15e8:      	ldrb	w9, [x22, #0x8]
    15ec:      	add	w10, w8, w9
    15f0:      	sub	w10, w10, #0x5
    15f4:      	cmp	w10, #0x3
    15f8:      	b.lo	0x1628 <tcpc_typec_handle_cc_change+0x1e4>
    15fc:      	cbz	w8, 0x1850 <tcpc_typec_handle_cc_change+0x40c>
    1600:      	cmp	w8, #0x1
    1604:      	b.eq	0x1850 <tcpc_typec_handle_cc_change+0x40c>
    1608:      	cmp	w8, #0x2
    160c:      	b.ne	0x1858 <tcpc_typec_handle_cc_change+0x414>
    1610:      	cmp	w9, #0x2
    1614:      	b.lo	0x1628 <tcpc_typec_handle_cc_change+0x1e4>
    1618:      	b	0x1858 <tcpc_typec_handle_cc_change+0x414>
    161c:      	ldrb	w8, [x22, #0x8]
    1620:      	cmp	w8, #0x2
    1624:      	b.ne	0x1858 <tcpc_typec_handle_cc_change+0x414>
    1628:      	mov	x0, x19
    162c:      	mov	w1, wzr
    1630:      	bl	0x1630 <tcpc_typec_handle_cc_change+0x1ec>
		0000000000001630:  R_AARCH64_CALL26	tcpc_enable_lpm_timer
    1634:      	mov	x0, x19
    1638:      	mov	w1, wzr
    163c:      	bl	0x163c <tcpc_typec_handle_cc_change+0x1f8>
		000000000000163c:  R_AARCH64_CALL26	tcpci_set_low_power_mode
    1640:      	ldrb	w8, [x22, #0x5]
    1644:      	and	w8, w8, #0x7
    1648:      	cmp	w8, #0x4
    164c:      	b.eq	0x1660 <tcpc_typec_handle_cc_change+0x21c>
    1650:      	cmp	w8, #0x1
    1654:      	b.ne	0x1678 <tcpc_typec_handle_cc_change+0x234>
    1658:      	mov	w20, wzr
    165c:      	b	0x167c <tcpc_typec_handle_cc_change+0x238>
    1660:      	ldrb	w8, [x22, #0x7]
    1664:      	ldrb	w9, [x22, #0x8]
    1668:      	add	w8, w9, w8
    166c:      	cmp	w8, #0x4
    1670:      	cset	w20, hi
    1674:      	b	0x167c <tcpc_typec_handle_cc_change+0x238>
    1678:      	mov	w20, #0x1
    167c:      	ldrb	w8, [x22, #0xb]
    1680:      	cmp	w8, #0x0
    1684:      	mov	w8, #0x7
    1688:      	cinc	x9, x8, ne
    168c:      	ldrb	w8, [x22]
    1690:      	ldrb	w23, [x22, x9]
    1694:      	cmp	w8, #0x7
    1698:      	b.eq	0x1708 <tcpc_typec_handle_cc_change+0x2c4>
    169c:      	cmp	w8, #0xe
    16a0:      	b.eq	0x1708 <tcpc_typec_handle_cc_change+0x2c4>
    16a4:      	ldrb	w8, [x22, #0xa]
    16a8:      	cbz	w8, 0x1700 <tcpc_typec_handle_cc_change+0x2bc>
    16ac:      	adrp	x0, 0x1000 <tcpc_show_property+0x3c4>
		00000000000016ac:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x1c86
    16b0:      	add	x0, x0, #0x0
		00000000000016b0:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x1c86
    16b4:      	adrp	x1, 0x1000 <tcpc_show_property+0x3c4>
		00000000000016b4:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0xc1c
    16b8:      	add	x1, x1, #0x0
		00000000000016b8:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0xc1c
    16bc:      	bl	0x16bc <tcpc_typec_handle_cc_change+0x278>
		00000000000016bc:  R_AARCH64_CALL26	pd_dbg_info
    16c0:      	ldrb	w8, [x22, #0xa]
    16c4:      	cmp	w8, #0x1
    16c8:      	b.ne	0x1700 <tcpc_typec_handle_cc_change+0x2bc>
    16cc:      	mov	w8, #0x2248
    16d0:      	add	x21, x19, x8
    16d4:      	mov	x0, x21
    16d8:      	bl	0x16d8 <tcpc_typec_handle_cc_change+0x294>
		00000000000016d8:  R_AARCH64_CALL26	mutex_lock
    16dc:      	mov	x0, x19
    16e0:      	mov	w1, #0x26
    16e4:      	bl	0x16e4 <tcpc_typec_handle_cc_change+0x2a0>
		00000000000016e4:  R_AARCH64_CALL26	tcpc_disable_timer
    16e8:      	mov	x0, x19
    16ec:      	mov	w1, wzr
    16f0:      	mov	w2, wzr
    16f4:      	bl	0x16f4 <tcpc_typec_handle_cc_change+0x2b0>
		00000000000016f4:  R_AARCH64_CALL26	tcpci_enable_discharge
    16f8:      	mov	x0, x21
    16fc:      	bl	0x16fc <tcpc_typec_handle_cc_change+0x2b8>
		00000000000016fc:  R_AARCH64_CALL26	mutex_unlock
    1700:      	ldrb	w8, [x22]
    1704:      	strb	wzr, [x22, #0xa]
    1708:      	sub	w8, w8, #0x6
    170c:      	cmp	w8, #0xf
    1710:      	b.hi	0x17f4 <tcpc_typec_handle_cc_change+0x3b0>
    1714:      	adrp	x9, 0x1000 <tcpc_show_property+0x3c4>
		0000000000001714:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x3c
    1718:      	add	x9, x9, #0x0
		0000000000001718:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x3c
    171c:      	adr	x10, #0x10
    1720:      	ldrb	w11, [x9, x8]
    1724:      	add	x10, x10, x11, lsl #2
    1728:      	br	x10
    172c:      	mov	x0, x19
    1730:      	mov	w1, w20
    1734:      	bl	0x1734 <tcpc_typec_handle_cc_change+0x2f0>
		0000000000001734:  R_AARCH64_CALL26	tcpci_notify_attachwait_state
    1738:      	b	0x18e8 <tcpc_typec_handle_cc_change+0x4a4>
    173c:      	mov	w8, #0x3044
    1740:      	add	x8, x19, x8
    1744:      	ldrb	w9, [x8]
    1748:      	cbz	w9, 0x1938 <tcpc_typec_handle_cc_change+0x4f4>
    174c:      	ldrb	w8, [x8, #0xf9]
    1750:      	cmp	w8, #0x2
    1754:      	b.lo	0x1938 <tcpc_typec_handle_cc_change+0x4f4>
    1758:      	cmp	w23, #0x7
    175c:      	b.eq	0x1938 <tcpc_typec_handle_cc_change+0x4f4>
    1760:      	adrp	x8, 0x1000 <tcpc_show_property+0x3c4>
		0000000000001760:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.cst16+0x30
    1764:      	add	x8, x8, #0x0
		0000000000001764:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.cst16+0x30
    1768:      	add	x1, sp, #0x8
    176c:      	mov	x0, x19
    1770:      	mov	w2, wzr
    1774:      	ldp	x9, x8, [x8]
    1778:      	stp	x9, x8, [sp, #0x8]
    177c:      	strb	wzr, [sp, #0xa]
    1780:      	bl	0x1780 <tcpc_typec_handle_cc_change+0x33c>
		0000000000001780:  R_AARCH64_CALL26	pd_put_event
    1784:      	b	0x1938 <tcpc_typec_handle_cc_change+0x4f4>
    1788:      	cbnz	w8, 0x1628 <tcpc_typec_handle_cc_change+0x1e4>
    178c:      	cbz	w9, 0x1858 <tcpc_typec_handle_cc_change+0x414>
    1790:      	b	0x1628 <tcpc_typec_handle_cc_change+0x1e4>
    1794:      	ldrb	w8, [x22, #0x7]
    1798:      	ldrb	w9, [x22, #0x8]
    179c:      	add	w8, w9, w8
    17a0:      	cmp	w8, #0x3
    17a4:      	b.ne	0x18f4 <tcpc_typec_handle_cc_change+0x4b0>
    17a8:      	ldrb	w8, [x22, #0x18]
    17ac:      	cbz	w8, 0x18f4 <tcpc_typec_handle_cc_change+0x4b0>
    17b0:      	mov	x0, x19
    17b4:      	mov	w1, #0x1
    17b8:      	bl	0x17b8 <tcpc_typec_handle_cc_change+0x374>
		00000000000017b8:  R_AARCH64_CALL26	tcpci_set_vconn
    17bc:      	b	0x18f4 <tcpc_typec_handle_cc_change+0x4b0>
    17c0:      	mov	x0, x19
    17c4:      	mov	w1, #0x1
    17c8:      	bl	0x17c8 <tcpc_typec_handle_cc_change+0x384>
		00000000000017c8:  R_AARCH64_CALL26	tcpci_notify_attachwait_state
    17cc:      	b	0x1900 <tcpc_typec_handle_cc_change+0x4bc>
    17d0:      	adrp	x0, 0x1000 <tcpc_show_property+0x3c4>
		00000000000017d0:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x1709
    17d4:      	add	x0, x0, #0x0
		00000000000017d4:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x1709
    17d8:      	bl	0x17d8 <tcpc_typec_handle_cc_change+0x394>
		00000000000017d8:  R_AARCH64_CALL26	pd_dbg_info
    17dc:      	mov	x0, x19
    17e0:      	mov	w1, #0x2b
    17e4:      	strb	wzr, [x22, #0x381]
    17e8:      	bl	0x17e8 <tcpc_typec_handle_cc_change+0x3a4>
		00000000000017e8:  R_AARCH64_CALL26	tcpc_disable_timer
    17ec:      	mov	x0, x19
    17f0:      	bl	0x3c5c <typec_unattached_power_entry>
    17f4:      	mov	x0, x19
    17f8:      	mov	w1, w20
    17fc:      	bl	0x17fc <tcpc_typec_handle_cc_change+0x3b8>
		00000000000017fc:  R_AARCH64_CALL26	tcpci_notify_attachwait_state
    1800:      	adrp	x0, 0x1000 <tcpc_show_property+0x3c4>
		0000000000001800:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x37f1
    1804:      	add	x0, x0, #0x0
		0000000000001804:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x37f1
    1808:      	cbz	w20, 0x1824 <tcpc_typec_handle_cc_change+0x3e0>
    180c:      	adrp	x1, 0x1000 <tcpc_show_property+0x3c4>
		000000000000180c:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x29f0
    1810:      	add	x1, x1, #0x0
		0000000000001810:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x29f0
    1814:      	bl	0x1814 <tcpc_typec_handle_cc_change+0x3d0>
		0000000000001814:  R_AARCH64_CALL26	pd_dbg_info
    1818:      	mov	w8, #0x4
    181c:      	strb	w8, [x22]
    1820:      	b	0x1900 <tcpc_typec_handle_cc_change+0x4bc>
    1824:      	adrp	x1, 0x1000 <tcpc_show_property+0x3c4>
		0000000000001824:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x2c7
    1828:      	add	x1, x1, #0x0
		0000000000001828:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x2c7
    182c:      	bl	0x182c <tcpc_typec_handle_cc_change+0x3e8>
		000000000000182c:  R_AARCH64_CALL26	pd_dbg_info
    1830:      	ldrb	w8, [x22, #0x6]
    1834:      	mov	w1, #0x1
    1838:      	mov	w9, #0x5
    183c:      	mov	x0, x19
    1840:      	bfi	w1, w8, #3, #2
    1844:      	strb	w9, [x22]
    1848:      	bl	0x1848 <tcpc_typec_handle_cc_change+0x404>
		0000000000001848:  R_AARCH64_CALL26	tcpci_set_cc
    184c:      	b	0x1900 <tcpc_typec_handle_cc_change+0x4bc>
    1850:      	cmp	w9, #0x2
    1854:      	b.eq	0x1628 <tcpc_typec_handle_cc_change+0x1e4>
    1858:      	ldrb	w8, [x22, #0xa]
    185c:      	cbz	w8, 0x18b4 <tcpc_typec_handle_cc_change+0x470>
    1860:      	adrp	x0, 0x1000 <tcpc_show_property+0x3c4>
		0000000000001860:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x1c86
    1864:      	add	x0, x0, #0x0
		0000000000001864:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x1c86
    1868:      	adrp	x1, 0x1000 <tcpc_show_property+0x3c4>
		0000000000001868:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0xc1c
    186c:      	add	x1, x1, #0x0
		000000000000186c:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0xc1c
    1870:      	bl	0x1870 <tcpc_typec_handle_cc_change+0x42c>
		0000000000001870:  R_AARCH64_CALL26	pd_dbg_info
    1874:      	ldrb	w8, [x22, #0xa]
    1878:      	cmp	w8, #0x1
    187c:      	b.ne	0x18b4 <tcpc_typec_handle_cc_change+0x470>
    1880:      	mov	w8, #0x2248
    1884:      	add	x20, x19, x8
    1888:      	mov	x0, x20
    188c:      	bl	0x188c <tcpc_typec_handle_cc_change+0x448>
		000000000000188c:  R_AARCH64_CALL26	mutex_lock
    1890:      	mov	x0, x19
    1894:      	mov	w1, #0x26
    1898:      	bl	0x1898 <tcpc_typec_handle_cc_change+0x454>
		0000000000001898:  R_AARCH64_CALL26	tcpc_disable_timer
    189c:      	mov	x0, x19
    18a0:      	mov	w1, wzr
    18a4:      	mov	w2, wzr
    18a8:      	bl	0x18a8 <tcpc_typec_handle_cc_change+0x464>
		00000000000018a8:  R_AARCH64_CALL26	tcpci_enable_discharge
    18ac:      	mov	x0, x20
    18b0:      	bl	0x18b0 <tcpc_typec_handle_cc_change+0x46c>
		00000000000018b0:  R_AARCH64_CALL26	mutex_unlock
    18b4:      	ldrb	w8, [x22]
    18b8:      	strb	wzr, [x22, #0xa]
    18bc:      	sub	w8, w8, #0x6
    18c0:      	cmp	w8, #0x9
    18c4:      	b.hi	0x1938 <tcpc_typec_handle_cc_change+0x4f4>
    18c8:      	adrp	x9, 0x1000 <tcpc_show_property+0x3c4>
		00000000000018c8:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x4c
    18cc:      	add	x9, x9, #0x0
		00000000000018cc:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x4c
    18d0:      	adr	x10, #0x10
    18d4:      	ldrb	w11, [x9, x8]
    18d8:      	add	x10, x10, x11, lsl #2
    18dc:      	br	x10
    18e0:      	ldrb	w8, [x22, #0xc]
    18e4:      	cbz	w8, 0x18f4 <tcpc_typec_handle_cc_change+0x4b0>
    18e8:      	mov	x0, x19
    18ec:      	mov	w1, #0x32
    18f0:      	b	0x1940 <tcpc_typec_handle_cc_change+0x4fc>
    18f4:      	mov	x0, x19
    18f8:      	bl	0x18f8 <tcpc_typec_handle_cc_change+0x4b4>
		00000000000018f8:  R_AARCH64_CALL26	tcpc_reset_typec_debounce_timer
    18fc:      	b	0x14d0 <tcpc_typec_handle_cc_change+0x8c>
    1900:      	mov	x0, x19
    1904:      	mov	w1, #0x30
    1908:      	b	0x1940 <tcpc_typec_handle_cc_change+0x4fc>
    190c:      	ldrb	w8, [x22, #0x7]
    1910:      	cbnz	w8, 0x1938 <tcpc_typec_handle_cc_change+0x4f4>
    1914:      	ldrb	w8, [x22, #0x8]
    1918:      	cbnz	w8, 0x1938 <tcpc_typec_handle_cc_change+0x4f4>
    191c:      	mov	w8, #0x2248
    1920:      	add	x20, x19, x8
    1924:      	mov	x0, x20
    1928:      	bl	0x1928 <tcpc_typec_handle_cc_change+0x4e4>
		0000000000001928:  R_AARCH64_CALL26	mutex_lock
    192c:      	mov	x0, x20
    1930:      	strb	wzr, [x22, #0x388]
    1934:      	bl	0x1934 <tcpc_typec_handle_cc_change+0x4f0>
		0000000000001934:  R_AARCH64_CALL26	mutex_unlock
    1938:      	mov	x0, x19
    193c:      	mov	w1, #0x31
    1940:      	bl	0x1940 <tcpc_typec_handle_cc_change+0x4fc>
		0000000000001940:  R_AARCH64_CALL26	tcpc_enable_timer
    1944:      	b	0x14d0 <tcpc_typec_handle_cc_change+0x8c>
    1948:      	mov	x0, x19
    194c:      	mov	w1, #0x33
    1950:      	b	0x1940 <tcpc_typec_handle_cc_change+0x4fc>
    1954:      	bl	0x1954 <tcpc_typec_handle_cc_change+0x510>
		0000000000001954:  R_AARCH64_CALL26	__stack_chk_fail
