source tcpc_store_property section=.text address=0x1050 size=676
    1050:      	paciasp
    1054:      	sub	sp, sp, #0x50
    1058:      	stp	x29, x30, [sp, #0x20]
    105c:      	stp	x22, x21, [sp, #0x30]
    1060:      	stp	x20, x19, [sp, #0x40]
    1064:      	add	x29, sp, #0x20
    1068:      	adrp	x9, 0x1000 <tcpc_show_property+0x3c4>
		0000000000001068:  R_AARCH64_ADR_PREL_PG_HI21	.data+0x30
    106c:      	add	x9, x9, #0x0
		000000000000106c:  R_AARCH64_ADD_ABS_LO12_NC	.data+0x30
    1070:      	mrs	x8, SP_EL0
    1074:      	sub	x9, x1, x9
    1078:      	mov	x19, x3
    107c:      	mov	x21, x0
    1080:      	ldr	x8, [x8, #0x638]
    1084:      	sub	x20, x0, #0x50
    1088:      	asr	x22, x9, #5
    108c:      	cmp	x22, #0x3
    1090:      	stur	x8, [x29, #-0x8]
    1094:      	str	xzr, [sp, #0x8]
    1098:      	b.hs	0x10f8 <tcpc_store_property+0xa8>
    109c:      	adrp	x1, 0x1000 <tcpc_show_property+0x3c4>
		000000000000109c:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x29a0
    10a0:      	add	x1, x1, #0x0
		00000000000010a0:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x29a0
    10a4:      	add	x0, sp, #0x10
    10a8:      	str	x2, [sp, #0x10]
    10ac:      	bl	0x10ac <tcpc_store_property+0x5c>
		00000000000010ac:  R_AARCH64_CALL26	strsep
    10b0:      	cbz	x0, 0x11f8 <tcpc_store_property+0x1a8>
    10b4:      	add	x2, sp, #0x8
    10b8:      	mov	w1, wzr
    10bc:      	bl	0x10bc <tcpc_store_property+0x6c>
		00000000000010bc:  R_AARCH64_CALL26	kstrtoull
    10c0:      	cbnz	w0, 0x11f8 <tcpc_store_property+0x1a8>
    10c4:      	adrp	x1, 0x1000 <tcpc_show_property+0x3c4>
		00000000000010c4:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x29a0
    10c8:      	add	x1, x1, #0x0
		00000000000010c8:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x29a0
    10cc:      	add	x0, sp, #0x10
    10d0:      	bl	0x10d0 <tcpc_store_property+0x80>
		00000000000010d0:  R_AARCH64_CALL26	strsep
    10d4:      	cmp	x22, #0x2
    10d8:      	b.eq	0x11c8 <tcpc_store_property+0x178>
    10dc:      	cmp	x22, #0x1
    10e0:      	b.eq	0x11e0 <tcpc_store_property+0x190>
    10e4:      	cbnz	x22, 0x120c <tcpc_store_property+0x1bc>
    10e8:      	ldrb	w1, [sp, #0x8]
    10ec:      	mov	x0, x20
    10f0:      	bl	0x10f0 <tcpc_store_property+0xa0>
		00000000000010f0:  R_AARCH64_CALL26	tcpm_typec_change_role
    10f4:      	b	0x120c <tcpc_store_property+0x1bc>
    10f8:      	b.eq	0x1184 <tcpc_store_property+0x134>
    10fc:      	cmp	x22, #0x6
    1100:      	b.ne	0x120c <tcpc_store_property+0x1bc>
    1104:      	adrp	x1, 0x1000 <tcpc_show_property+0x3c4>
		0000000000001104:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x29a0
    1108:      	add	x1, x1, #0x0
		0000000000001108:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x29a0
    110c:      	add	x0, sp, #0x10
    1110:      	str	x2, [sp, #0x10]
    1114:      	bl	0x1114 <tcpc_store_property+0xc4>
		0000000000001114:  R_AARCH64_CALL26	strsep
    1118:      	cbz	x0, 0x11f8 <tcpc_store_property+0x1a8>
    111c:      	add	x2, sp, #0x8
    1120:      	mov	w1, wzr
    1124:      	bl	0x1124 <tcpc_store_property+0xd4>
		0000000000001124:  R_AARCH64_CALL26	kstrtoull
    1128:      	cbnz	w0, 0x11f8 <tcpc_store_property+0x1a8>
    112c:      	adrp	x1, 0x1000 <tcpc_show_property+0x3c4>
		000000000000112c:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x29a0
    1130:      	add	x1, x1, #0x0
		0000000000001130:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x29a0
    1134:      	add	x0, sp, #0x10
    1138:      	bl	0x1138 <tcpc_store_property+0xe8>
		0000000000001138:  R_AARCH64_CALL26	strsep
    113c:      	ldr	x8, [sp, #0x8]
    1140:      	sub	x8, x8, #0x1
    1144:      	cmp	x8, #0x8
    1148:      	b.hi	0x120c <tcpc_store_property+0x1bc>
    114c:      	adrp	x9, 0x1000 <tcpc_show_property+0x3c4>
		000000000000114c:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x9
    1150:      	add	x9, x9, #0x0
		0000000000001150:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x9
    1154:      	adr	x10, #0x10
    1158:      	ldrb	w11, [x9, x8]
    115c:      	add	x10, x10, x11, lsl #2
    1160:      	br	x10
    1164:      	mov	x0, x20
    1168:      	bl	0x1168 <tcpc_store_property+0x118>
		0000000000001168:  R_AARCH64_CALL26	tcpm_inquire_pd_power_role
    116c:      	tst	w0, #0xff
    1170:      	mov	x0, x20
    1174:      	cset	w1, eq
    1178:      	mov	x2, xzr
    117c:      	bl	0x117c <tcpc_store_property+0x12c>
		000000000000117c:  R_AARCH64_CALL26	tcpm_dpm_pd_power_swap
    1180:      	b	0x120c <tcpc_store_property+0x1bc>
    1184:      	adrp	x1, 0x1000 <tcpc_show_property+0x3c4>
		0000000000001184:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x29a0
    1188:      	add	x1, x1, #0x0
		0000000000001188:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x29a0
    118c:      	add	x0, sp, #0x10
    1190:      	str	x2, [sp, #0x10]
    1194:      	bl	0x1194 <tcpc_store_property+0x144>
		0000000000001194:  R_AARCH64_CALL26	strsep
    1198:      	cbz	x0, 0x123c <tcpc_store_property+0x1ec>
    119c:      	add	x2, sp, #0x8
    11a0:      	mov	w1, wzr
    11a4:      	bl	0x11a4 <tcpc_store_property+0x154>
		00000000000011a4:  R_AARCH64_CALL26	kstrtoull
    11a8:      	cbnz	w0, 0x123c <tcpc_store_property+0x1ec>
    11ac:      	adrp	x1, 0x1000 <tcpc_show_property+0x3c4>
		00000000000011ac:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x29a0
    11b0:      	add	x1, x1, #0x0
		00000000000011b0:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x29a0
    11b4:      	add	x0, sp, #0x10
    11b8:      	bl	0x11b8 <tcpc_store_property+0x168>
		00000000000011b8:  R_AARCH64_CALL26	strsep
    11bc:      	ldr	x8, [sp, #0x8]
    11c0:      	str	w8, [x21, #0x3530]
    11c4:      	b	0x120c <tcpc_store_property+0x1bc>
    11c8:      	ldr	x1, [sp, #0x8]
    11cc:      	cmp	x1, #0x35
    11d0:      	b.hi	0x120c <tcpc_store_property+0x1bc>
    11d4:      	mov	x0, x20
    11d8:      	bl	0x11d8 <tcpc_store_property+0x188>
		00000000000011d8:  R_AARCH64_CALL26	tcpc_enable_timer
    11dc:      	b	0x120c <tcpc_store_property+0x1bc>
    11e0:      	ldr	x8, [sp, #0x8]
    11e4:      	cmp	x8, #0x2
    11e8:      	b.hi	0x120c <tcpc_store_property+0x1bc>
    11ec:      	mov	w9, #0x2c26
    11f0:      	strb	w8, [x21, x9]
    11f4:      	b	0x120c <tcpc_store_property+0x1bc>
    11f8:      	adrp	x1, 0x1000 <tcpc_show_property+0x3c4>
		00000000000011f8:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x1a9c
    11fc:      	add	x1, x1, #0x0
		00000000000011fc:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x1a9c
    1200:      	mov	x0, x21
    1204:      	bl	0x1204 <tcpc_store_property+0x1b4>
		0000000000001204:  R_AARCH64_CALL26	_dev_err
    1208:      	mov	x19, #-0x16
    120c:      	mrs	x8, SP_EL0
    1210:      	ldr	x8, [x8, #0x638]
    1214:      	ldur	x9, [x29, #-0x8]
    1218:      	cmp	x8, x9
    121c:      	b.ne	0x12f0 <tcpc_store_property+0x2a0>
    1220:      	mov	x0, x19
    1224:      	ldp	x20, x19, [sp, #0x40]
    1228:      	ldp	x22, x21, [sp, #0x30]
    122c:      	ldp	x29, x30, [sp, #0x20]
    1230:      	add	sp, sp, #0x50
    1234:      	autiasp
    1238:      	ret
    123c:      	adrp	x1, 0x1000 <tcpc_show_property+0x3c4>
		000000000000123c:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x1a9c
    1240:      	add	x1, x1, #0x0
		0000000000001240:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x1a9c
    1244:      	mov	x0, x21
    1248:      	bl	0x1248 <tcpc_store_property+0x1f8>
		0000000000001248:  R_AARCH64_CALL26	_dev_notice
    124c:      	b	0x1208 <tcpc_store_property+0x1b8>
    1250:      	mov	x0, x20
    1254:      	bl	0x1254 <tcpc_store_property+0x204>
		0000000000001254:  R_AARCH64_CALL26	tcpm_inquire_pd_data_role
    1258:      	tst	w0, #0xff
    125c:      	mov	x0, x20
    1260:      	cset	w1, eq
    1264:      	mov	x2, xzr
    1268:      	bl	0x1268 <tcpc_store_property+0x218>
		0000000000001268:  R_AARCH64_CALL26	tcpm_dpm_pd_data_swap
    126c:      	b	0x120c <tcpc_store_property+0x1bc>
    1270:      	mov	x0, x20
    1274:      	bl	0x1274 <tcpc_store_property+0x224>
		0000000000001274:  R_AARCH64_CALL26	tcpm_inquire_pd_vconn_role
    1278:      	tst	w0, #0xff
    127c:      	mov	x0, x20
    1280:      	cset	w1, eq
    1284:      	mov	x2, xzr
    1288:      	bl	0x1288 <tcpc_store_property+0x238>
		0000000000001288:  R_AARCH64_CALL26	tcpm_dpm_pd_vconn_swap
    128c:      	b	0x120c <tcpc_store_property+0x1bc>
    1290:      	mov	x0, x20
    1294:      	mov	x1, xzr
    1298:      	bl	0x1298 <tcpc_store_property+0x248>
		0000000000001298:  R_AARCH64_CALL26	tcpm_dpm_pd_soft_reset
    129c:      	b	0x120c <tcpc_store_property+0x1bc>
    12a0:      	mov	x0, x20
    12a4:      	mov	x1, xzr
    12a8:      	bl	0x12a8 <tcpc_store_property+0x258>
		00000000000012a8:  R_AARCH64_CALL26	tcpm_dpm_pd_hard_reset
    12ac:      	b	0x120c <tcpc_store_property+0x1bc>
    12b0:      	mov	x0, x20
    12b4:      	mov	x1, xzr
    12b8:      	bl	0x12b8 <tcpc_store_property+0x268>
		00000000000012b8:  R_AARCH64_CALL26	tcpm_dpm_pd_get_source_cap
    12bc:      	b	0x120c <tcpc_store_property+0x1bc>
    12c0:      	mov	x0, x20
    12c4:      	mov	x1, xzr
    12c8:      	bl	0x12c8 <tcpc_store_property+0x278>
		00000000000012c8:  R_AARCH64_CALL26	tcpm_dpm_pd_get_sink_cap
    12cc:      	b	0x120c <tcpc_store_property+0x1bc>
    12d0:      	mov	x0, x20
    12d4:      	mov	x1, xzr
    12d8:      	bl	0x12d8 <tcpc_store_property+0x288>
		00000000000012d8:  R_AARCH64_CALL26	tcpm_dpm_vdm_discover_id
    12dc:      	b	0x120c <tcpc_store_property+0x1bc>
    12e0:      	mov	x0, x20
    12e4:      	mov	x1, xzr
    12e8:      	bl	0x12e8 <tcpc_store_property+0x298>
		00000000000012e8:  R_AARCH64_CALL26	tcpm_dpm_vdm_discover_cable_id
    12ec:      	b	0x120c <tcpc_store_property+0x1bc>
    12f0:      	bl	0x12f0 <tcpc_store_property+0x2a0>
		00000000000012f0:  R_AARCH64_CALL26	__stack_chk_fail
