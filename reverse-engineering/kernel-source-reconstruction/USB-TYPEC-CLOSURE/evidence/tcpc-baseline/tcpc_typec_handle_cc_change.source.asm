source tcpc_typec_handle_cc_change section=.text address=0x1458 size=1312
    1458:      	paciasp
    145c:      	sub	sp, sp, #0x60
    1460:      	stp	x29, x30, [sp, #0x20]
    1464:      	str	x23, [sp, #0x30]
    1468:      	stp	x22, x21, [sp, #0x40]
    146c:      	stp	x20, x19, [sp, #0x50]
    1470:      	add	x29, sp, #0x20
    1474:      	mrs	x8, SP_EL0
    1478:      	mov	x19, x0
    147c:      	ldr	x8, [x8, #0x638]
    1480:      	stur	x8, [x29, #-0x8]
    1484:      	bl	0x1484 <tcpc_typec_handle_cc_change+0x2c>
		0000000000001484:  R_AARCH64_CALL26	tcpci_get_cc
    1488:      	tbnz	w0, #0x1f, 0x14e8 <tcpc_typec_handle_cc_change+0x90>
    148c:      	mov	w8, #0x2c70
    1490:      	adrp	x0, 0x1000 <tcpc_show_property+0x3c4>
		0000000000001490:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x2193
    1494:      	add	x0, x0, #0x0
		0000000000001494:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x2193
    1498:      	add	x22, x19, x8
    149c:      	ldrb	w1, [x22, #0x7]
    14a0:      	ldrb	w2, [x22, #0x8]
    14a4:      	bl	0x14a4 <tcpc_typec_handle_cc_change+0x4c>
		00000000000014a4:  R_AARCH64_CALL26	pd_dbg_info
    14a8:      	mov	x0, x19
    14ac:      	bl	0x1978 <typec_try_norp_src>
    14b0:      	tbnz	w0, #0x0, 0x14e4 <tcpc_typec_handle_cc_change+0x8c>
    14b4:      	ldrb	w8, [x22, #0x7]
    14b8:      	cmp	w8, #0xf
    14bc:      	b.eq	0x14e4 <tcpc_typec_handle_cc_change+0x8c>
    14c0:      	ldrb	w9, [x22]
    14c4:      	cmp	w9, #0x12
    14c8:      	b.hi	0x1518 <tcpc_typec_handle_cc_change+0xc0>
    14cc:      	mov	w10, #0x1
    14d0:      	mov	w11, #0x3
    14d4:      	lsl	w10, w10, w9
    14d8:      	movk	w11, #0x4, lsl #16
    14dc:      	tst	w10, w11
    14e0:      	b.eq	0x1518 <tcpc_typec_handle_cc_change+0xc0>
    14e4:      	mov	w0, wzr
    14e8:      	mrs	x8, SP_EL0
    14ec:      	ldr	x8, [x8, #0x638]
    14f0:      	ldur	x9, [x29, #-0x8]
    14f4:      	cmp	x8, x9
    14f8:      	b.ne	0x1974 <tcpc_typec_handle_cc_change+0x51c>
    14fc:      	ldp	x20, x19, [sp, #0x50]
    1500:      	ldp	x22, x21, [sp, #0x40]
    1504:      	ldp	x29, x30, [sp, #0x20]
    1508:      	ldr	x23, [sp, #0x30]
    150c:      	add	sp, sp, #0x60
    1510:      	autiasp
    1514:      	ret
    1518:      	ldr	w10, [x19, #0x2c8c]
    151c:      	cmp	w9, #0x13
    1520:      	b.ne	0x1528 <tcpc_typec_handle_cc_change+0xd0>
    1524:      	tbnz	w10, #0x8, 0x14e4 <tcpc_typec_handle_cc_change+0x8c>
    1528:      	cmp	w9, #0x14
    152c:      	b.ne	0x1534 <tcpc_typec_handle_cc_change+0xdc>
    1530:      	tbnz	w10, #0x9, 0x14e4 <tcpc_typec_handle_cc_change+0x8c>
    1534:      	mov	w0, wzr
    1538:      	cmp	w9, #0xa
    153c:      	b.eq	0x14e8 <tcpc_typec_handle_cc_change+0x90>
    1540:      	ldrb	w10, [x22, #0x384]
    1544:      	cbnz	w10, 0x14e8 <tcpc_typec_handle_cc_change+0x90>
    1548:      	sub	w9, w9, #0x6
    154c:      	cmp	w9, #0xb
    1550:      	b.hi	0x15cc <tcpc_typec_handle_cc_change+0x174>
    1554:      	adrp	x10, 0x1000 <tcpc_show_property+0x3c4>
		0000000000001554:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x30
    1558:      	add	x10, x10, #0x0
		0000000000001558:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x30
    155c:      	adr	x11, #0x10
    1560:      	ldrb	w12, [x10, x9]
    1564:      	add	x11, x11, x12, lsl #2
    1568:      	br	x11
    156c:      	ldrb	w8, [x22, #0xb]
    1570:      	cmp	w8, #0x0
    1574:      	mov	w8, #0x7
    1578:      	cinc	x8, x8, ne
    157c:      	ldrb	w8, [x22, x8]
    1580:      	cbnz	w8, 0x163c <tcpc_typec_handle_cc_change+0x1e4>
    1584:      	b	0x1878 <tcpc_typec_handle_cc_change+0x420>
    1588:      	cbz	w8, 0x1630 <tcpc_typec_handle_cc_change+0x1d8>
    158c:      	cmp	w8, #0x1
    1590:      	b.eq	0x1630 <tcpc_typec_handle_cc_change+0x1d8>
    1594:      	cmp	w8, #0x2
    1598:      	b.ne	0x1878 <tcpc_typec_handle_cc_change+0x420>
    159c:      	ldrb	w8, [x22, #0x8]
    15a0:      	cmp	w8, #0x2
    15a4:      	b.lo	0x163c <tcpc_typec_handle_cc_change+0x1e4>
    15a8:      	b	0x1878 <tcpc_typec_handle_cc_change+0x420>
    15ac:      	ldrb	w9, [x22, #0x8]
    15b0:      	add	w8, w8, w9
    15b4:      	sub	w8, w8, #0x5
    15b8:      	cmp	w8, #0x3
    15bc:      	b.lo	0x163c <tcpc_typec_handle_cc_change+0x1e4>
    15c0:      	b	0x1878 <tcpc_typec_handle_cc_change+0x420>
    15c4:      	cbnz	w8, 0x15f0 <tcpc_typec_handle_cc_change+0x198>
    15c8:      	b	0x1878 <tcpc_typec_handle_cc_change+0x420>
    15cc:      	ldrb	w9, [x22, #0x8]
    15d0:      	add	w10, w9, w8
    15d4:      	cmp	w10, #0x1
    15d8:      	b.ne	0x17a8 <tcpc_typec_handle_cc_change+0x350>
    15dc:      	adrp	x0, 0x1000 <tcpc_show_property+0x3c4>
		00000000000015dc:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x1e52
    15e0:      	add	x0, x0, #0x0
		00000000000015e0:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x1e52
    15e4:      	bl	0x15e4 <tcpc_typec_handle_cc_change+0x18c>
		00000000000015e4:  R_AARCH64_CALL26	pd_dbg_info
    15e8:      	b	0x1878 <tcpc_typec_handle_cc_change+0x420>
    15ec:      	cbnz	w8, 0x163c <tcpc_typec_handle_cc_change+0x1e4>
    15f0:      	ldrb	w8, [x22, #0x8]
    15f4:      	cbnz	w8, 0x163c <tcpc_typec_handle_cc_change+0x1e4>
    15f8:      	b	0x1878 <tcpc_typec_handle_cc_change+0x420>
    15fc:      	ldrb	w9, [x22, #0x8]
    1600:      	add	w10, w8, w9
    1604:      	sub	w10, w10, #0x5
    1608:      	cmp	w10, #0x3
    160c:      	b.lo	0x163c <tcpc_typec_handle_cc_change+0x1e4>
    1610:      	cbz	w8, 0x1870 <tcpc_typec_handle_cc_change+0x418>
    1614:      	cmp	w8, #0x1
    1618:      	b.eq	0x1870 <tcpc_typec_handle_cc_change+0x418>
    161c:      	cmp	w8, #0x2
    1620:      	b.ne	0x1878 <tcpc_typec_handle_cc_change+0x420>
    1624:      	cmp	w9, #0x2
    1628:      	b.lo	0x163c <tcpc_typec_handle_cc_change+0x1e4>
    162c:      	b	0x1878 <tcpc_typec_handle_cc_change+0x420>
    1630:      	ldrb	w8, [x22, #0x8]
    1634:      	cmp	w8, #0x2
    1638:      	b.ne	0x1878 <tcpc_typec_handle_cc_change+0x420>
    163c:      	mov	x0, x19
    1640:      	mov	w1, wzr
    1644:      	bl	0x1644 <tcpc_typec_handle_cc_change+0x1ec>
		0000000000001644:  R_AARCH64_CALL26	tcpc_enable_lpm_timer
    1648:      	mov	x0, x19
    164c:      	mov	w1, wzr
    1650:      	bl	0x1650 <tcpc_typec_handle_cc_change+0x1f8>
		0000000000001650:  R_AARCH64_CALL26	tcpci_set_low_power_mode
    1654:      	ldrb	w8, [x22, #0x5]
    1658:      	and	w8, w8, #0x7
    165c:      	cmp	w8, #0x4
    1660:      	b.eq	0x1674 <tcpc_typec_handle_cc_change+0x21c>
    1664:      	cmp	w8, #0x1
    1668:      	b.ne	0x168c <tcpc_typec_handle_cc_change+0x234>
    166c:      	mov	w20, wzr
    1670:      	b	0x1690 <tcpc_typec_handle_cc_change+0x238>
    1674:      	ldrb	w8, [x22, #0x7]
    1678:      	ldrb	w9, [x22, #0x8]
    167c:      	add	w8, w9, w8
    1680:      	cmp	w8, #0x4
    1684:      	cset	w20, hi
    1688:      	b	0x1690 <tcpc_typec_handle_cc_change+0x238>
    168c:      	mov	w20, #0x1
    1690:      	ldrb	w8, [x22, #0xb]
    1694:      	cmp	w8, #0x0
    1698:      	mov	w8, #0x7
    169c:      	cinc	x9, x8, ne
    16a0:      	ldrb	w8, [x22]
    16a4:      	ldrb	w23, [x22, x9]
    16a8:      	cmp	w8, #0x7
    16ac:      	b.eq	0x171c <tcpc_typec_handle_cc_change+0x2c4>
    16b0:      	cmp	w8, #0xe
    16b4:      	b.eq	0x171c <tcpc_typec_handle_cc_change+0x2c4>
    16b8:      	ldrb	w8, [x22, #0xa]
    16bc:      	cbz	w8, 0x1714 <tcpc_typec_handle_cc_change+0x2bc>
    16c0:      	adrp	x0, 0x1000 <tcpc_show_property+0x3c4>
		00000000000016c0:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x1c9e
    16c4:      	add	x0, x0, #0x0
		00000000000016c4:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x1c9e
    16c8:      	adrp	x1, 0x1000 <tcpc_show_property+0x3c4>
		00000000000016c8:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0xc34
    16cc:      	add	x1, x1, #0x0
		00000000000016cc:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0xc34
    16d0:      	bl	0x16d0 <tcpc_typec_handle_cc_change+0x278>
		00000000000016d0:  R_AARCH64_CALL26	pd_dbg_info
    16d4:      	ldrb	w8, [x22, #0xa]
    16d8:      	cmp	w8, #0x1
    16dc:      	b.ne	0x1714 <tcpc_typec_handle_cc_change+0x2bc>
    16e0:      	mov	w8, #0x2248
    16e4:      	add	x21, x19, x8
    16e8:      	mov	x0, x21
    16ec:      	bl	0x16ec <tcpc_typec_handle_cc_change+0x294>
		00000000000016ec:  R_AARCH64_CALL26	mutex_lock
    16f0:      	mov	x0, x19
    16f4:      	mov	w1, #0x26
    16f8:      	bl	0x16f8 <tcpc_typec_handle_cc_change+0x2a0>
		00000000000016f8:  R_AARCH64_CALL26	tcpc_disable_timer
    16fc:      	mov	x0, x19
    1700:      	mov	w1, wzr
    1704:      	mov	w2, wzr
    1708:      	bl	0x1708 <tcpc_typec_handle_cc_change+0x2b0>
		0000000000001708:  R_AARCH64_CALL26	tcpci_enable_discharge
    170c:      	mov	x0, x21
    1710:      	bl	0x1710 <tcpc_typec_handle_cc_change+0x2b8>
		0000000000001710:  R_AARCH64_CALL26	mutex_unlock
    1714:      	ldrb	w8, [x22]
    1718:      	strb	wzr, [x22, #0xa]
    171c:      	sub	w8, w8, #0x6
    1720:      	cmp	w8, #0xf
    1724:      	b.hi	0x1814 <tcpc_typec_handle_cc_change+0x3bc>
    1728:      	adrp	x9, 0x1000 <tcpc_show_property+0x3c4>
		0000000000001728:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x3c
    172c:      	add	x9, x9, #0x0
		000000000000172c:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x3c
    1730:      	adr	x10, #0x10
    1734:      	ldrb	w11, [x9, x8]
    1738:      	add	x10, x10, x11, lsl #2
    173c:      	br	x10
    1740:      	mov	x0, x19
    1744:      	mov	w1, w20
    1748:      	bl	0x1748 <tcpc_typec_handle_cc_change+0x2f0>
		0000000000001748:  R_AARCH64_CALL26	tcpci_notify_attachwait_state
    174c:      	b	0x1908 <tcpc_typec_handle_cc_change+0x4b0>
    1750:      	adrp	x0, 0x1000 <tcpc_show_property+0x3c4>
		0000000000001750:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x484
    1754:      	add	x0, x0, #0x0
		0000000000001754:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x484
    1758:      	mov	w8, #0x3044
    175c:      	add	x20, x19, x8
    1760:      	bl	0x1760 <tcpc_typec_handle_cc_change+0x308>
		0000000000001760:  R_AARCH64_CALL26	pd_dbg_info
    1764:      	ldrb	w8, [x20]
    1768:      	cbz	w8, 0x1958 <tcpc_typec_handle_cc_change+0x500>
    176c:      	ldrb	w8, [x20, #0xf9]
    1770:      	cmp	w8, #0x2
    1774:      	b.lo	0x1958 <tcpc_typec_handle_cc_change+0x500>
    1778:      	cmp	w23, #0x7
    177c:      	b.eq	0x1958 <tcpc_typec_handle_cc_change+0x500>
    1780:      	adrp	x8, 0x1000 <tcpc_show_property+0x3c4>
		0000000000001780:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.cst16+0x30
    1784:      	add	x8, x8, #0x0
		0000000000001784:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.cst16+0x30
    1788:      	add	x1, sp, #0x8
    178c:      	mov	x0, x19
    1790:      	mov	w2, wzr
    1794:      	ldp	x9, x8, [x8]
    1798:      	stp	x9, x8, [sp, #0x8]
    179c:      	strb	wzr, [sp, #0xa]
    17a0:      	bl	0x17a0 <tcpc_typec_handle_cc_change+0x348>
		00000000000017a0:  R_AARCH64_CALL26	pd_put_event
    17a4:      	b	0x1958 <tcpc_typec_handle_cc_change+0x500>
    17a8:      	cbnz	w8, 0x163c <tcpc_typec_handle_cc_change+0x1e4>
    17ac:      	cbz	w9, 0x1878 <tcpc_typec_handle_cc_change+0x420>
    17b0:      	b	0x163c <tcpc_typec_handle_cc_change+0x1e4>
    17b4:      	ldrb	w8, [x22, #0x7]
    17b8:      	ldrb	w9, [x22, #0x8]
    17bc:      	add	w8, w9, w8
    17c0:      	cmp	w8, #0x3
    17c4:      	b.ne	0x1914 <tcpc_typec_handle_cc_change+0x4bc>
    17c8:      	ldrb	w8, [x22, #0x18]
    17cc:      	cbz	w8, 0x1914 <tcpc_typec_handle_cc_change+0x4bc>
    17d0:      	mov	x0, x19
    17d4:      	mov	w1, #0x1
    17d8:      	bl	0x17d8 <tcpc_typec_handle_cc_change+0x380>
		00000000000017d8:  R_AARCH64_CALL26	tcpci_set_vconn
    17dc:      	b	0x1914 <tcpc_typec_handle_cc_change+0x4bc>
    17e0:      	mov	x0, x19
    17e4:      	mov	w1, #0x1
    17e8:      	bl	0x17e8 <tcpc_typec_handle_cc_change+0x390>
		00000000000017e8:  R_AARCH64_CALL26	tcpci_notify_attachwait_state
    17ec:      	b	0x1920 <tcpc_typec_handle_cc_change+0x4c8>
    17f0:      	adrp	x0, 0x1000 <tcpc_show_property+0x3c4>
		00000000000017f0:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x1721
    17f4:      	add	x0, x0, #0x0
		00000000000017f4:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x1721
    17f8:      	bl	0x17f8 <tcpc_typec_handle_cc_change+0x3a0>
		00000000000017f8:  R_AARCH64_CALL26	pd_dbg_info
    17fc:      	mov	x0, x19
    1800:      	mov	w1, #0x2b
    1804:      	strb	wzr, [x22, #0x381]
    1808:      	bl	0x1808 <tcpc_typec_handle_cc_change+0x3b0>
		0000000000001808:  R_AARCH64_CALL26	tcpc_disable_timer
    180c:      	mov	x0, x19
    1810:      	bl	0x3c7c <typec_unattached_power_entry>
    1814:      	mov	x0, x19
    1818:      	mov	w1, w20
    181c:      	bl	0x181c <tcpc_typec_handle_cc_change+0x3c4>
		000000000000181c:  R_AARCH64_CALL26	tcpci_notify_attachwait_state
    1820:      	adrp	x0, 0x1000 <tcpc_show_property+0x3c4>
		0000000000001820:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x381e
    1824:      	add	x0, x0, #0x0
		0000000000001824:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x381e
    1828:      	cbz	w20, 0x1844 <tcpc_typec_handle_cc_change+0x3ec>
    182c:      	adrp	x1, 0x1000 <tcpc_show_property+0x3c4>
		000000000000182c:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x2a08
    1830:      	add	x1, x1, #0x0
		0000000000001830:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x2a08
    1834:      	bl	0x1834 <tcpc_typec_handle_cc_change+0x3dc>
		0000000000001834:  R_AARCH64_CALL26	pd_dbg_info
    1838:      	mov	w8, #0x4
    183c:      	strb	w8, [x22]
    1840:      	b	0x1920 <tcpc_typec_handle_cc_change+0x4c8>
    1844:      	adrp	x1, 0x1000 <tcpc_show_property+0x3c4>
		0000000000001844:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x2c7
    1848:      	add	x1, x1, #0x0
		0000000000001848:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x2c7
    184c:      	bl	0x184c <tcpc_typec_handle_cc_change+0x3f4>
		000000000000184c:  R_AARCH64_CALL26	pd_dbg_info
    1850:      	ldrb	w8, [x22, #0x6]
    1854:      	mov	w1, #0x1
    1858:      	mov	w9, #0x5
    185c:      	mov	x0, x19
    1860:      	bfi	w1, w8, #3, #2
    1864:      	strb	w9, [x22]
    1868:      	bl	0x1868 <tcpc_typec_handle_cc_change+0x410>
		0000000000001868:  R_AARCH64_CALL26	tcpci_set_cc
    186c:      	b	0x1920 <tcpc_typec_handle_cc_change+0x4c8>
    1870:      	cmp	w9, #0x2
    1874:      	b.eq	0x163c <tcpc_typec_handle_cc_change+0x1e4>
    1878:      	ldrb	w8, [x22, #0xa]
    187c:      	cbz	w8, 0x18d4 <tcpc_typec_handle_cc_change+0x47c>
    1880:      	adrp	x0, 0x1000 <tcpc_show_property+0x3c4>
		0000000000001880:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x1c9e
    1884:      	add	x0, x0, #0x0
		0000000000001884:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x1c9e
    1888:      	adrp	x1, 0x1000 <tcpc_show_property+0x3c4>
		0000000000001888:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0xc34
    188c:      	add	x1, x1, #0x0
		000000000000188c:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0xc34
    1890:      	bl	0x1890 <tcpc_typec_handle_cc_change+0x438>
		0000000000001890:  R_AARCH64_CALL26	pd_dbg_info
    1894:      	ldrb	w8, [x22, #0xa]
    1898:      	cmp	w8, #0x1
    189c:      	b.ne	0x18d4 <tcpc_typec_handle_cc_change+0x47c>
    18a0:      	mov	w8, #0x2248
    18a4:      	add	x20, x19, x8
    18a8:      	mov	x0, x20
    18ac:      	bl	0x18ac <tcpc_typec_handle_cc_change+0x454>
		00000000000018ac:  R_AARCH64_CALL26	mutex_lock
    18b0:      	mov	x0, x19
    18b4:      	mov	w1, #0x26
    18b8:      	bl	0x18b8 <tcpc_typec_handle_cc_change+0x460>
		00000000000018b8:  R_AARCH64_CALL26	tcpc_disable_timer
    18bc:      	mov	x0, x19
    18c0:      	mov	w1, wzr
    18c4:      	mov	w2, wzr
    18c8:      	bl	0x18c8 <tcpc_typec_handle_cc_change+0x470>
		00000000000018c8:  R_AARCH64_CALL26	tcpci_enable_discharge
    18cc:      	mov	x0, x20
    18d0:      	bl	0x18d0 <tcpc_typec_handle_cc_change+0x478>
		00000000000018d0:  R_AARCH64_CALL26	mutex_unlock
    18d4:      	ldrb	w8, [x22]
    18d8:      	strb	wzr, [x22, #0xa]
    18dc:      	sub	w8, w8, #0x6
    18e0:      	cmp	w8, #0x9
    18e4:      	b.hi	0x1958 <tcpc_typec_handle_cc_change+0x500>
    18e8:      	adrp	x9, 0x1000 <tcpc_show_property+0x3c4>
		00000000000018e8:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x4c
    18ec:      	add	x9, x9, #0x0
		00000000000018ec:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x4c
    18f0:      	adr	x10, #0x10
    18f4:      	ldrb	w11, [x9, x8]
    18f8:      	add	x10, x10, x11, lsl #2
    18fc:      	br	x10
    1900:      	ldrb	w8, [x22, #0xc]
    1904:      	cbz	w8, 0x1914 <tcpc_typec_handle_cc_change+0x4bc>
    1908:      	mov	x0, x19
    190c:      	mov	w1, #0x32
    1910:      	b	0x1960 <tcpc_typec_handle_cc_change+0x508>
    1914:      	mov	x0, x19
    1918:      	bl	0x1918 <tcpc_typec_handle_cc_change+0x4c0>
		0000000000001918:  R_AARCH64_CALL26	tcpc_reset_typec_debounce_timer
    191c:      	b	0x14e4 <tcpc_typec_handle_cc_change+0x8c>
    1920:      	mov	x0, x19
    1924:      	mov	w1, #0x30
    1928:      	b	0x1960 <tcpc_typec_handle_cc_change+0x508>
    192c:      	ldrb	w8, [x22, #0x7]
    1930:      	cbnz	w8, 0x1958 <tcpc_typec_handle_cc_change+0x500>
    1934:      	ldrb	w8, [x22, #0x8]
    1938:      	cbnz	w8, 0x1958 <tcpc_typec_handle_cc_change+0x500>
    193c:      	mov	w8, #0x2248
    1940:      	add	x20, x19, x8
    1944:      	mov	x0, x20
    1948:      	bl	0x1948 <tcpc_typec_handle_cc_change+0x4f0>
		0000000000001948:  R_AARCH64_CALL26	mutex_lock
    194c:      	mov	x0, x20
    1950:      	strb	wzr, [x22, #0x388]
    1954:      	bl	0x1954 <tcpc_typec_handle_cc_change+0x4fc>
		0000000000001954:  R_AARCH64_CALL26	mutex_unlock
    1958:      	mov	x0, x19
    195c:      	mov	w1, #0x31
    1960:      	bl	0x1960 <tcpc_typec_handle_cc_change+0x508>
		0000000000001960:  R_AARCH64_CALL26	tcpc_enable_timer
    1964:      	b	0x14e4 <tcpc_typec_handle_cc_change+0x8c>
    1968:      	mov	x0, x19
    196c:      	mov	w1, #0x33
    1970:      	b	0x1960 <tcpc_typec_handle_cc_change+0x508>
    1974:      	bl	0x1974 <tcpc_typec_handle_cc_change+0x51c>
		0000000000001974:  R_AARCH64_CALL26	__stack_chk_fail
