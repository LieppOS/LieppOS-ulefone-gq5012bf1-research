
recon/sc851x_charger.ko:	file format elf64-littleaarch64

Disassembly of section .text:

0000000000000000 <.text>:
       0: aa 38 f1 5e  	.word	0x5ef138aa

0000000000000004 <sc851x_charger_probe>:
       4: d503233f     	paciasp
       8: a9bb7bfd     	stp	x29, x30, [sp, #-0x50]!
       c: f9000bfc     	str	x28, [sp, #0x10]
      10: a9025ff8     	stp	x24, x23, [sp, #0x20]
      14: a90357f6     	stp	x22, x21, [sp, #0x30]
      18: a9044ff4     	stp	x20, x19, [sp, #0x40]
      1c: 910003fd     	mov	x29, sp
      20: d10903ff     	sub	sp, sp, #0x240
      24: d5384108     	mrs	x8, SP_EL0
      28: 91008013     	add	x19, x0, #0x20
      2c: f9431d08     	ldr	x8, [x8, #0x638]
      30: aa0003f5     	mov	x21, x0
      34: 90000001     	adrp	x1, 0x0 <.text>
		0000000000000034:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x406
      38: 91000021     	add	x1, x1, #0x0
		0000000000000038:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x406
      3c: 90000002     	adrp	x2, 0x0 <.text>
		000000000000003c:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x2a6
      40: 91000042     	add	x2, x2, #0x0
		0000000000000040:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x2a6
      44: 90000003     	adrp	x3, 0x0 <.text>
		0000000000000044:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x40f
      48: 91000063     	add	x3, x3, #0x0
		0000000000000048:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x40f
      4c: aa1303e0     	mov	x0, x19
      50: f81f83a8     	stur	x8, [x29, #-0x8]
      54: 94000000     	bl	0x54 <sc851x_charger_probe+0x50>
		0000000000000054:  R_AARCH64_CALL26	_dev_err
      58: aa1303e0     	mov	x0, x19
      5c: 52804801     	mov	w1, #0x240              // =576
      60: 5281b802     	mov	w2, #0xdc0              // =3520
      64: 94000000     	bl	0x64 <sc851x_charger_probe+0x60>
		0000000000000064:  R_AARCH64_CALL26	devm_kmalloc
      68: b5000200     	cbnz	x0, 0xa8 <sc851x_charger_probe+0xa4>
      6c: 12800175     	mov	w21, #-0xc              // =-12
      70: d5384108     	mrs	x8, SP_EL0
      74: f9431d08     	ldr	x8, [x8, #0x638]
      78: f85f83a9     	ldur	x9, [x29, #-0x8]
      7c: eb09011f     	cmp	x8, x9
      80: 54003821     	b.ne	0x784 <sc851x_charger_probe+0x780>
      84: 2a1503e0     	mov	w0, w21
      88: 910903ff     	add	sp, sp, #0x240
      8c: a9444ff4     	ldp	x20, x19, [sp, #0x40]
      90: a94357f6     	ldp	x22, x21, [sp, #0x30]
      94: a9425ff8     	ldp	x24, x23, [sp, #0x20]
      98: f9400bfc     	ldr	x28, [sp, #0x10]
      9c: a8c57bfd     	ldp	x29, x30, [sp], #0x50
      a0: d50323bf     	autiasp
      a4: d65f03c0     	ret
      a8: aa0003f4     	mov	x20, x0
      ac: a9005413     	stp	x19, x21, [x0]
      b0: 90000001     	adrp	x1, 0x0 <.text>
		00000000000000b0:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0xc0
      b4: 91000021     	add	x1, x1, #0x0
		00000000000000b4:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0xc0
      b8: aa1503e0     	mov	x0, x21
      bc: aa1f03e2     	mov	x2, xzr
      c0: aa1f03e3     	mov	x3, xzr
      c4: 94000000     	bl	0xc4 <sc851x_charger_probe+0xc0>
		00000000000000c4:  R_AARCH64_CALL26	__devm_regmap_init_i2c
      c8: b140041f     	cmn	x0, #0x1, lsl #12       // =0x1000
      cc: f9000a80     	str	x0, [x20, #0x10]
      d0: 540000e9     	b.ls	0xec <sc851x_charger_probe+0xe8>
      d4: f9400280     	ldr	x0, [x20]
      d8: 90000001     	adrp	x1, 0x0 <.text>
		00000000000000d8:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x5e
      dc: 91000021     	add	x1, x1, #0x0
		00000000000000dc:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x5e
      e0: 94000000     	bl	0xe0 <sc851x_charger_probe+0xdc>
		00000000000000e0:  R_AARCH64_CALL26	_dev_err
      e4: b9401295     	ldr	w21, [x20, #0x10]
      e8: 14000178     	b	0x6c8 <sc851x_charger_probe+0x6c4>
      ec: 910023f7     	add	x23, sp, #0x8
      f0: 52800316     	mov	w22, #0x18              // =24
      f4: 90000018     	adrp	x24, 0x0 <.text>
		00000000000000f4:  R_AARCH64_ADR_PREL_PG_HI21	.rodata+0x208
      f8: 91000318     	add	x24, x24, #0x0
		00000000000000f8:  R_AARCH64_ADD_ABS_LO12_NC	.rodata+0x208
      fc: a9402708     	ldp	x8, x9, [x24]
     100: 910023e2     	add	x2, sp, #0x8
     104: f9400a81     	ldr	x1, [x20, #0x10]
     108: b940130a     	ldr	w10, [x24, #0x10]
     10c: f9400280     	ldr	x0, [x20]
     110: a900a7e8     	stp	x8, x9, [sp, #0x8]
     114: b9001bea     	str	w10, [sp, #0x18]
     118: 94000000     	bl	0x118 <sc851x_charger_probe+0x114>
		0000000000000118:  R_AARCH64_CALL26	devm_regmap_field_alloc
     11c: b13ffc1f     	cmn	x0, #0xfff
     120: f8366a80     	str	x0, [x20, x22]
     124: 540029e2     	b.hs	0x660 <sc851x_charger_probe+0x65c>
     128: 910022d6     	add	x22, x22, #0x8
     12c: 91005318     	add	x24, x24, #0x14
     130: f106a2df     	cmp	x22, #0x1a8
     134: 54fffe41     	b.ne	0xfc <sc851x_charger_probe+0xf8>
     138: f9400280     	ldr	x0, [x20]
     13c: 90000001     	adrp	x1, 0x0 <.text>
		000000000000013c:  R_AARCH64_ADR_PREL_PG_HI21	.data+0x438
     140: 91000021     	add	x1, x1, #0x0
		0000000000000140:  R_AARCH64_ADD_ABS_LO12_NC	.data+0x438
     144: f9005eb4     	str	x20, [x21, #0xb8]
     148: 94000000     	bl	0x148 <sc851x_charger_probe+0x144>
		0000000000000148:  R_AARCH64_CALL26	device_create_file
     14c: 9106a288     	add	x8, x20, #0x1a8
     150: 90000009     	adrp	x9, 0x0 <.text>
		0000000000000150:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x39b
     154: 91000129     	add	x9, x9, #0x0
		0000000000000154:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x39b
     158: 9000000a     	adrp	x10, 0x0 <.text>
		0000000000000158:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x104
     15c: 9100014a     	add	x10, x10, #0x0
		000000000000015c:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x104
     160: 9000000b     	adrp	x11, 0x0 <.text>
		0000000000000160:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x27a
     164: 9100016b     	add	x11, x11, #0x0
		0000000000000164:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x27a
     168: aa1f03f8     	mov	x24, xzr
     16c: a900a3e9     	stp	x9, x8, [sp, #0x8]
     170: 91001109     	add	x9, x8, #0x4
     174: f94186b6     	ldr	x22, [x21, #0x308]
     178: a901a7ea     	stp	x10, x9, [sp, #0x18]
     17c: 9106c289     	add	x9, x20, #0x1b0
     180: 9000000a     	adrp	x10, 0x0 <.text>
		0000000000000180:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x3e6
     184: 9100014a     	add	x10, x10, #0x0
		0000000000000184:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x3e6
     188: a902a7eb     	stp	x11, x9, [sp, #0x28]
     18c: 91003109     	add	x9, x8, #0xc
     190: 9000000b     	adrp	x11, 0x0 <.text>
		0000000000000190:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x92
     194: 9100016b     	add	x11, x11, #0x0
		0000000000000194:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x92
     198: a903a7ea     	stp	x10, x9, [sp, #0x38]
     19c: 9106e289     	add	x9, x20, #0x1b8
     1a0: 9000000a     	adrp	x10, 0x0 <.text>
		00000000000001a0:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x162
     1a4: 9100014a     	add	x10, x10, #0x0
		00000000000001a4:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x162
     1a8: a904a7eb     	stp	x11, x9, [sp, #0x48]
     1ac: 91005109     	add	x9, x8, #0x14
     1b0: 9000000b     	adrp	x11, 0x0 <.text>
		00000000000001b0:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1
     1b4: 9100016b     	add	x11, x11, #0x0
		00000000000001b4:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1
     1b8: a905a7ea     	stp	x10, x9, [sp, #0x58]
     1bc: 91072289     	add	x9, x20, #0x1c8
     1c0: 9000000a     	adrp	x10, 0x0 <.text>
		00000000000001c0:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x14
     1c4: 9100014a     	add	x10, x10, #0x0
		00000000000001c4:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x14
     1c8: a90826eb     	stp	x11, x9, [x23, #0x80]
     1cc: 91009109     	add	x9, x8, #0x24
     1d0: 9000000b     	adrp	x11, 0x0 <.text>
		00000000000001d0:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x245
     1d4: 9100016b     	add	x11, x11, #0x0
		00000000000001d4:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x245
     1d8: a90926ea     	stp	x10, x9, [x23, #0x90]
     1dc: 91074289     	add	x9, x20, #0x1d0
     1e0: 9000000a     	adrp	x10, 0x0 <.text>
		00000000000001e0:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0xa5
     1e4: 9100014a     	add	x10, x10, #0x0
		00000000000001e4:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0xa5
     1e8: a90a26eb     	stp	x11, x9, [x23, #0xa0]
     1ec: 9100b109     	add	x9, x8, #0x2c
     1f0: 9000000b     	adrp	x11, 0x0 <.text>
		00000000000001f0:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0xb7
     1f4: 9100016b     	add	x11, x11, #0x0
		00000000000001f4:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0xb7
     1f8: a90b26ea     	stp	x10, x9, [x23, #0xb0]
     1fc: 91076289     	add	x9, x20, #0x1d8
     200: 9000000a     	adrp	x10, 0x0 <.text>
		0000000000000200:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x3f8
     204: 9100014a     	add	x10, x10, #0x0
		0000000000000204:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x3f8
     208: a90c26eb     	stp	x11, x9, [x23, #0xc0]
     20c: 9100d109     	add	x9, x8, #0x34
     210: 9000000b     	adrp	x11, 0x0 <.text>
		0000000000000210:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x541
     214: 9100016b     	add	x11, x11, #0x0
		0000000000000214:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x541
     218: a90d26ea     	stp	x10, x9, [x23, #0xd0]
     21c: 91078289     	add	x9, x20, #0x1e0
     220: 9000000a     	adrp	x10, 0x0 <.text>
		0000000000000220:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x28d
     224: 9100014a     	add	x10, x10, #0x0
		0000000000000224:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x28d
     228: a90e26eb     	stp	x11, x9, [x23, #0xe0]
     22c: 9100f109     	add	x9, x8, #0x3c
     230: 9000000b     	adrp	x11, 0x0 <.text>
		0000000000000230:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x436
     234: 9100016b     	add	x11, x11, #0x0
		0000000000000234:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x436
     238: a90f26ea     	stp	x10, x9, [x23, #0xf0]
     23c: 9107a289     	add	x9, x20, #0x1e8
     240: 9000000a     	adrp	x10, 0x0 <.text>
		0000000000000240:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x332
     244: 9100014a     	add	x10, x10, #0x0
		0000000000000244:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x332
     248: a91026eb     	stp	x11, x9, [x23, #0x100]
     24c: 91011109     	add	x9, x8, #0x44
     250: 9000000b     	adrp	x11, 0x0 <.text>
		0000000000000250:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x37
     254: 9100016b     	add	x11, x11, #0x0
		0000000000000254:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x37
     258: a91126ea     	stp	x10, x9, [x23, #0x110]
     25c: 9107c289     	add	x9, x20, #0x1f0
     260: 9000000a     	adrp	x10, 0x0 <.text>
		0000000000000260:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x116
     264: 9100014a     	add	x10, x10, #0x0
		0000000000000264:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x116
     268: a91226eb     	stp	x11, x9, [x23, #0x120]
     26c: 91013109     	add	x9, x8, #0x4c
     270: 9000000b     	adrp	x11, 0x0 <.text>
		0000000000000270:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x257
     274: 9100016b     	add	x11, x11, #0x0
		0000000000000274:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x257
     278: a91326ea     	stp	x10, x9, [x23, #0x130]
     27c: 9107e289     	add	x9, x20, #0x1f8
     280: 9000000a     	adrp	x10, 0x0 <.text>
		0000000000000280:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x372
     284: 9100014a     	add	x10, x10, #0x0
		0000000000000284:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x372
     288: a91426eb     	stp	x11, x9, [x23, #0x140]
     28c: 91015109     	add	x9, x8, #0x54
     290: 9000000b     	adrp	x11, 0x0 <.text>
		0000000000000290:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x266
     294: 9100016b     	add	x11, x11, #0x0
		0000000000000294:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x266
     298: a91526ea     	stp	x10, x9, [x23, #0x150]
     29c: 91080289     	add	x9, x20, #0x200
     2a0: 9000000a     	adrp	x10, 0x0 <.text>
		00000000000002a0:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x1a4
     2a4: 9100014a     	add	x10, x10, #0x0
		00000000000002a4:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x1a4
     2a8: a91626eb     	stp	x11, x9, [x23, #0x160]
     2ac: 91017109     	add	x9, x8, #0x5c
     2b0: 9000000b     	adrp	x11, 0x0 <.text>
		00000000000002b0:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x48d
     2b4: 9100016b     	add	x11, x11, #0x0
		00000000000002b4:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x48d
     2b8: a91726ea     	stp	x10, x9, [x23, #0x170]
     2bc: 91082289     	add	x9, x20, #0x208
     2c0: 9000000a     	adrp	x10, 0x0 <.text>
		00000000000002c0:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x178
     2c4: 9100014a     	add	x10, x10, #0x0
		00000000000002c4:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x178
     2c8: a91826eb     	stp	x11, x9, [x23, #0x180]
     2cc: 91019109     	add	x9, x8, #0x64
     2d0: 9000000b     	adrp	x11, 0x0 <.text>
		00000000000002d0:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0xc9
     2d4: 9100016b     	add	x11, x11, #0x0
		00000000000002d4:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0xc9
     2d8: a91926ea     	stp	x10, x9, [x23, #0x190]
     2dc: 91084289     	add	x9, x20, #0x210
     2e0: 9000000a     	adrp	x10, 0x0 <.text>
		00000000000002e0:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x55e
     2e4: 9100014a     	add	x10, x10, #0x0
		00000000000002e4:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x55e
     2e8: a91a26eb     	stp	x11, x9, [x23, #0x1a0]
     2ec: 9101b109     	add	x9, x8, #0x6c
     2f0: 9000000b     	adrp	x11, 0x0 <.text>
		00000000000002f0:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0xe0
     2f4: 9100016b     	add	x11, x11, #0x0
		00000000000002f4:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0xe0
     2f8: a91b26ea     	stp	x10, x9, [x23, #0x1b0]
     2fc: 91086289     	add	x9, x20, #0x218
     300: 9000000a     	adrp	x10, 0x0 <.text>
		0000000000000300:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x5af
     304: 9100014a     	add	x10, x10, #0x0
		0000000000000304:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x5af
     308: a91c26eb     	stp	x11, x9, [x23, #0x1c0]
     30c: 9101d109     	add	x9, x8, #0x74
     310: 9000000b     	adrp	x11, 0x0 <.text>
		0000000000000310:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x12e
     314: 9100016b     	add	x11, x11, #0x0
		0000000000000314:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x12e
     318: a91d26ea     	stp	x10, x9, [x23, #0x1d0]
     31c: 91088289     	add	x9, x20, #0x220
     320: 9000000a     	adrp	x10, 0x0 <.text>
		0000000000000320:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x500
     324: 9100014a     	add	x10, x10, #0x0
		0000000000000324:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x500
     328: a91e26eb     	stp	x11, x9, [x23, #0x1e0]
     32c: 9101f109     	add	x9, x8, #0x7c
     330: 9000000b     	adrp	x11, 0x0 <.text>
		0000000000000330:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x1bb
     334: 9100016b     	add	x11, x11, #0x0
		0000000000000334:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x1bb
     338: a91f26ea     	stp	x10, x9, [x23, #0x1f0]
     33c: 9108a289     	add	x9, x20, #0x228
     340: 9000000a     	adrp	x10, 0x0 <.text>
		0000000000000340:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x3b1
     344: 9100014a     	add	x10, x10, #0x0
		0000000000000344:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x3b1
     348: f90102eb     	str	x11, [x23, #0x200]
     34c: 9000000b     	adrp	x11, 0x0 <.text>
		000000000000034c:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x477
     350: 9100016b     	add	x11, x11, #0x0
		0000000000000350:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x477
     354: f90106e9     	str	x9, [x23, #0x208]
     358: 91021109     	add	x9, x8, #0x84
     35c: f9010aea     	str	x10, [x23, #0x210]
     360: 9000000a     	adrp	x10, 0x0 <.text>
		0000000000000360:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x1f4
     364: 9100014a     	add	x10, x10, #0x0
		0000000000000364:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x1f4
     368: 91007108     	add	x8, x8, #0x1c
     36c: f9010ee9     	str	x9, [x23, #0x218]
     370: 9108c289     	add	x9, x20, #0x230
     374: f90112ea     	str	x10, [x23, #0x220]
     378: 9000000a     	adrp	x10, 0x0 <.text>
		0000000000000378:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x4c
     37c: 9100014a     	add	x10, x10, #0x0
		000000000000037c:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x4c
     380: a907a3eb     	stp	x11, x8, [sp, #0x78]
     384: f90116e9     	str	x9, [x23, #0x228]
     388: 91070289     	add	x9, x20, #0x1c0
     38c: 910023f7     	add	x23, sp, #0x8
     390: a906a7ea     	stp	x10, x9, [sp, #0x68]
     394: 8b1802e8     	add	x8, x23, x24
     398: aa1603e0     	mov	x0, x22
     39c: 52800023     	mov	w3, #0x1                // =1
     3a0: aa1f03e4     	mov	x4, xzr
     3a4: a9400901     	ldp	x1, x2, [x8]
     3a8: 94000000     	bl	0x3a8 <sc851x_charger_probe+0x3a4>
		00000000000003a8:  R_AARCH64_CALL26	of_property_read_variable_u32_array
     3ac: 37f81660     	tbnz	w0, #0x1f, 0x678 <sc851x_charger_probe+0x674>
     3b0: 91004318     	add	x24, x24, #0x10
     3b4: f108c31f     	cmp	x24, #0x230
     3b8: 54fffee1     	b.ne	0x394 <sc851x_charger_probe+0x390>
     3bc: 90000001     	adrp	x1, 0x0 <.text>
		00000000000003bc:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x2cd
     3c0: 91000021     	add	x1, x1, #0x0
		00000000000003c0:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x2cd
     3c4: aa1603e0     	mov	x0, x22
     3c8: 2a1f03e2     	mov	w2, wzr
     3cc: aa1f03e3     	mov	x3, xzr
     3d0: 94000000     	bl	0x3d0 <sc851x_charger_probe+0x3cc>
		00000000000003d0:  R_AARCH64_CALL26	of_get_named_gpio_flags
     3d4: 2a0003e2     	mov	w2, w0
     3d8: 7108001f     	cmp	w0, #0x200
     3dc: b9023682     	str	w2, [x20, #0x234]
     3e0: 540015c2     	b.hs	0x698 <sc851x_charger_probe+0x694>
     3e4: b941aa88     	ldr	w8, [x20, #0x1a8]
     3e8: 52800029     	mov	w9, #0x1                // =1
     3ec: b941ae8a     	ldr	w10, [x20, #0x1ac]
     3f0: 5280004b     	mov	w11, #0x2               // =2
     3f4: f9407680     	ldr	x0, [x20, #0xe8]
     3f8: 12800001     	mov	w1, #-0x1               // =-1
     3fc: 290123ff     	stp	wzr, w8, [sp, #0x8]
     400: b941b288     	ldr	w8, [x20, #0x1b0]
     404: 29022be9     	stp	w9, w10, [sp, #0x10]
     408: 52800069     	mov	w9, #0x3                // =3
     40c: b941b68a     	ldr	w10, [x20, #0x1b4]
     410: 52800022     	mov	w2, #0x1                // =1
     414: 290323eb     	stp	w11, w8, [sp, #0x18]
     418: 52800088     	mov	w8, #0x4                // =4
     41c: b941ba8b     	ldr	w11, [x20, #0x1b8]
     420: aa1f03e3     	mov	x3, xzr
     424: 29042be9     	stp	w9, w10, [sp, #0x20]
     428: 528000a9     	mov	w9, #0x5                // =5
     42c: b941be8a     	ldr	w10, [x20, #0x1bc]
     430: 2a1f03e4     	mov	w4, wzr
     434: 29052fe8     	stp	w8, w11, [sp, #0x28]
     438: 528000c8     	mov	w8, #0x6                // =6
     43c: b941c28b     	ldr	w11, [x20, #0x1c0]
     440: 2a1f03e5     	mov	w5, wzr
     444: 29062be9     	stp	w9, w10, [sp, #0x30]
     448: 528000e9     	mov	w9, #0x7                // =7
     44c: b941c68a     	ldr	w10, [x20, #0x1c4]
     450: 29072fe8     	stp	w8, w11, [sp, #0x38]
     454: 52800108     	mov	w8, #0x8                // =8
     458: b941ca8b     	ldr	w11, [x20, #0x1c8]
     45c: 29082be9     	stp	w9, w10, [sp, #0x40]
     460: 52800129     	mov	w9, #0x9                // =9
     464: b941ce8a     	ldr	w10, [x20, #0x1cc]
     468: 29092fe8     	stp	w8, w11, [sp, #0x48]
     46c: 52800148     	mov	w8, #0xa                // =10
     470: b941d28b     	ldr	w11, [x20, #0x1d0]
     474: 290a2be9     	stp	w9, w10, [sp, #0x50]
     478: 528001a9     	mov	w9, #0xd                // =13
     47c: b941d68a     	ldr	w10, [x20, #0x1d4]
     480: 290b2fe8     	stp	w8, w11, [sp, #0x58]
     484: 528001c8     	mov	w8, #0xe                // =14
     488: b941da8b     	ldr	w11, [x20, #0x1d8]
     48c: 290c2be9     	stp	w9, w10, [sp, #0x60]
     490: 528001e9     	mov	w9, #0xf                // =15
     494: b941de8a     	ldr	w10, [x20, #0x1dc]
     498: 290d2fe8     	stp	w8, w11, [sp, #0x68]
     49c: 52800208     	mov	w8, #0x10               // =16
     4a0: b941e28b     	ldr	w11, [x20, #0x1e0]
     4a4: 290e2be9     	stp	w9, w10, [sp, #0x70]
     4a8: 52800229     	mov	w9, #0x11               // =17
     4ac: b941e68a     	ldr	w10, [x20, #0x1e4]
     4b0: 290f2fe8     	stp	w8, w11, [sp, #0x78]
     4b4: 52800248     	mov	w8, #0x12               // =18
     4b8: b941ea8b     	ldr	w11, [x20, #0x1e8]
     4bc: 29102be9     	stp	w9, w10, [sp, #0x80]
     4c0: 52800369     	mov	w9, #0x1b               // =27
     4c4: b941ee8a     	ldr	w10, [x20, #0x1ec]
     4c8: 29112fe8     	stp	w8, w11, [sp, #0x88]
     4cc: 52800388     	mov	w8, #0x1c               // =28
     4d0: b941f28b     	ldr	w11, [x20, #0x1f0]
     4d4: 29122be9     	stp	w9, w10, [sp, #0x90]
     4d8: 528003a9     	mov	w9, #0x1d               // =29
     4dc: b941f68a     	ldr	w10, [x20, #0x1f4]
     4e0: 29132fe8     	stp	w8, w11, [sp, #0x98]
     4e4: 52800408     	mov	w8, #0x20               // =32
     4e8: b941fa8b     	ldr	w11, [x20, #0x1f8]
     4ec: 29142be9     	stp	w9, w10, [sp, #0xa0]
     4f0: 52800429     	mov	w9, #0x21               // =33
     4f4: b941fe8a     	ldr	w10, [x20, #0x1fc]
     4f8: 29152fe8     	stp	w8, w11, [sp, #0xa8]
     4fc: 52800448     	mov	w8, #0x22               // =34
     500: b942028b     	ldr	w11, [x20, #0x200]
     504: 29162be9     	stp	w9, w10, [sp, #0xb0]
     508: 52800469     	mov	w9, #0x23               // =35
     50c: b942068a     	ldr	w10, [x20, #0x204]
     510: 29172fe8     	stp	w8, w11, [sp, #0xb8]
     514: 52800488     	mov	w8, #0x24               // =36
     518: b9420a8b     	ldr	w11, [x20, #0x208]
     51c: 29182be9     	stp	w9, w10, [sp, #0xc0]
     520: 528004a9     	mov	w9, #0x25               // =37
     524: b9420e8a     	ldr	w10, [x20, #0x20c]
     528: 29192fe8     	stp	w8, w11, [sp, #0xc8]
     52c: 528004c8     	mov	w8, #0x26               // =38
     530: b942128b     	ldr	w11, [x20, #0x210]
     534: 291a2be9     	stp	w9, w10, [sp, #0xd0]
     538: 528004e9     	mov	w9, #0x27               // =39
     53c: b942168a     	ldr	w10, [x20, #0x214]
     540: 291b2fe8     	stp	w8, w11, [sp, #0xd8]
     544: 52800508     	mov	w8, #0x28               // =40
     548: b9421a8b     	ldr	w11, [x20, #0x218]
     54c: 291c2be9     	stp	w9, w10, [sp, #0xe0]
     550: 52800529     	mov	w9, #0x29               // =41
     554: b9421e8a     	ldr	w10, [x20, #0x21c]
     558: 291d2fe8     	stp	w8, w11, [sp, #0xe8]
     55c: 52800548     	mov	w8, #0x2a               // =42
     560: b942228b     	ldr	w11, [x20, #0x220]
     564: 291e2be9     	stp	w9, w10, [sp, #0xf0]
     568: 52800569     	mov	w9, #0x2b               // =43
     56c: b942268a     	ldr	w10, [x20, #0x224]
     570: 291f2fe8     	stp	w8, w11, [sp, #0xf8]
     574: 52800588     	mov	w8, #0x2c               // =44
     578: b90103e9     	str	w9, [sp, #0x100]
     57c: 528005e9     	mov	w9, #0x2f               // =47
     580: b9422a8b     	ldr	w11, [x20, #0x228]
     584: b90107ea     	str	w10, [sp, #0x104]
     588: b9010be8     	str	w8, [sp, #0x108]
     58c: b9422e88     	ldr	w8, [x20, #0x22c]
     590: 5280062a     	mov	w10, #0x31              // =49
     594: b90113e9     	str	w9, [sp, #0x110]
     598: b9423289     	ldr	w9, [x20, #0x230]
     59c: b9010feb     	str	w11, [sp, #0x10c]
     5a0: b90117e8     	str	w8, [sp, #0x114]
     5a4: b9011bea     	str	w10, [sp, #0x118]
     5a8: b9011fe9     	str	w9, [sp, #0x11c]
     5ac: 94000000     	bl	0x5ac <sc851x_charger_probe+0x5a8>
		00000000000005ac:  R_AARCH64_CALL26	regmap_field_update_bits_base
     5b0: 36f801e0     	tbz	w0, #0x1f, 0x5ec <sc851x_charger_probe+0x5e8>
     5b4: 2a0003f5     	mov	w21, w0
     5b8: f9400280     	ldr	x0, [x20]
     5bc: 90000001     	adrp	x1, 0x0 <.text>
		00000000000005bc:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x417
     5c0: 91000021     	add	x1, x1, #0x0
		00000000000005c0:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x417
     5c4: 52800342     	mov	w2, #0x1a               // =26
     5c8: 2a1503e3     	mov	w3, w21
     5cc: 94000000     	bl	0x5cc <sc851x_charger_probe+0x5c8>
		00000000000005cc:  R_AARCH64_CALL26	_dev_err
     5d0: f9400280     	ldr	x0, [x20]
     5d4: 90000001     	adrp	x1, 0x0 <.text>
		00000000000005d4:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x575
     5d8: 91000021     	add	x1, x1, #0x0
		00000000000005d8:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x575
     5dc: 90000002     	adrp	x2, 0x0 <.text>
		00000000000005dc:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x5c2
     5e0: 91000042     	add	x2, x2, #0x0
		00000000000005e0:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x5c2
     5e4: 2a1503e3     	mov	w3, w21
     5e8: 94000000     	bl	0x5e8 <sc851x_charger_probe+0x5e4>
		00000000000005e8:  R_AARCH64_CALL26	_dev_err
     5ec: 52800140     	mov	w0, #0xa                // =10
     5f0: 94000000     	bl	0x5f0 <sc851x_charger_probe+0x5ec>
		00000000000005f0:  R_AARCH64_CALL26	msleep
     5f4: aa1f03f7     	mov	x23, xzr
     5f8: 910023f8     	add	x24, sp, #0x8
     5fc: 90000015     	adrp	x21, 0x0 <.text>
		00000000000005fc:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x417
     600: 910002b5     	add	x21, x21, #0x0
		0000000000000600:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x417
     604: 14000004     	b	0x614 <sc851x_charger_probe+0x610>
     608: 910022f7     	add	x23, x23, #0x8
     60c: f10462ff     	cmp	x23, #0x118
     610: 540006c0     	b.eq	0x6e8 <sc851x_charger_probe+0x6e4>
     614: b8776b16     	ldr	w22, [x24, x23]
     618: 7100cadf     	cmp	w22, #0x32
     61c: 54000b22     	b.hs	0x780 <sc851x_charger_probe+0x77c>
     620: 8b170308     	add	x8, x24, x23
     624: 8b160e89     	add	x9, x20, x22, lsl #3
     628: 12800001     	mov	w1, #-0x1               // =-1
     62c: aa1f03e3     	mov	x3, xzr
     630: 2a1f03e4     	mov	w4, wzr
     634: 2a1f03e5     	mov	w5, wzr
     638: b9400502     	ldr	w2, [x8, #0x4]
     63c: f9400d20     	ldr	x0, [x9, #0x18]
     640: 94000000     	bl	0x640 <sc851x_charger_probe+0x63c>
		0000000000000640:  R_AARCH64_CALL26	regmap_field_update_bits_base
     644: 36fffe20     	tbz	w0, #0x1f, 0x608 <sc851x_charger_probe+0x604>
     648: 2a0003e3     	mov	w3, w0
     64c: f9400280     	ldr	x0, [x20]
     650: aa1503e1     	mov	x1, x21
     654: 2a1603e2     	mov	w2, w22
     658: 94000000     	bl	0x658 <sc851x_charger_probe+0x654>
		0000000000000658:  R_AARCH64_CALL26	_dev_err
     65c: 17ffffeb     	b	0x608 <sc851x_charger_probe+0x604>
     660: f9400280     	ldr	x0, [x20]
     664: 90000001     	adrp	x1, 0x0 <.text>
		0000000000000664:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x4e2
     668: 91000021     	add	x1, x1, #0x0
		0000000000000668:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x4e2
     66c: 94000000     	bl	0x66c <sc851x_charger_probe+0x668>
		000000000000066c:  R_AARCH64_CALL26	_dev_err
     670: b8766a95     	ldr	w21, [x20, x22]
     674: 14000015     	b	0x6c8 <sc851x_charger_probe+0x6c4>
     678: 910023e8     	add	x8, sp, #0x8
     67c: 2a0003f5     	mov	w21, w0
     680: f9400280     	ldr	x0, [x20]
     684: 90000001     	adrp	x1, 0x0 <.text>
		0000000000000684:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x2bb
     688: 91000021     	add	x1, x1, #0x0
		0000000000000688:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x2bb
     68c: f8786902     	ldr	x2, [x8, x24]
     690: 94000000     	bl	0x690 <sc851x_charger_probe+0x68c>
		0000000000000690:  R_AARCH64_CALL26	_dev_err
     694: 14000006     	b	0x6ac <sc851x_charger_probe+0x6a8>
     698: f9400280     	ldr	x0, [x20]
     69c: 90000001     	adrp	x1, 0x0 <.text>
		000000000000069c:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x4c9
     6a0: 91000021     	add	x1, x1, #0x0
		00000000000006a0:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x4c9
     6a4: 94000000     	bl	0x6a4 <sc851x_charger_probe+0x6a0>
		00000000000006a4:  R_AARCH64_CALL26	_dev_err
     6a8: 128002b5     	mov	w21, #-0x16             // =-22
     6ac: f9400280     	ldr	x0, [x20]
     6b0: 90000001     	adrp	x1, 0x0 <.text>
		00000000000006b0:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x2e0
     6b4: 91000021     	add	x1, x1, #0x0
		00000000000006b4:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x2e0
     6b8: 90000002     	adrp	x2, 0x0 <.text>
		00000000000006b8:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x2a6
     6bc: 91000042     	add	x2, x2, #0x0
		00000000000006bc:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x2a6
     6c0: 2a1503e3     	mov	w3, w21
     6c4: 94000000     	bl	0x6c4 <sc851x_charger_probe+0x6c0>
		00000000000006c4:  R_AARCH64_CALL26	_dev_err
     6c8: aa1303e0     	mov	x0, x19
     6cc: aa1403e1     	mov	x1, x20
     6d0: 94000000     	bl	0x6d0 <sc851x_charger_probe+0x6cc>
		00000000000006d0:  R_AARCH64_CALL26	devm_kfree
     6d4: 90000001     	adrp	x1, 0x0 <.text>
		00000000000006d4:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x52e
     6d8: 91000021     	add	x1, x1, #0x0
		00000000000006d8:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x52e
     6dc: aa1303e0     	mov	x0, x19
     6e0: 94000000     	bl	0x6e0 <sc851x_charger_probe+0x6dc>
		00000000000006e0:  R_AARCH64_CALL26	_dev_err
     6e4: 17fffe63     	b	0x70 <sc851x_charger_probe+0x6c>
     6e8: 2a1f03f6     	mov	w22, wzr
     6ec: 90000017     	adrp	x23, 0x0 <.text>
		00000000000006ec:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x2f8
     6f0: 910002f7     	add	x23, x23, #0x0
		00000000000006f0:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x2f8
     6f4: 90000018     	adrp	x24, 0x0 <.text>
		00000000000006f4:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x5d5
     6f8: 91000318     	add	x24, x24, #0x0
		00000000000006f8:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x5d5
     6fc: b90007ff     	str	wzr, [sp, #0x4]
     700: f9400a80     	ldr	x0, [x20, #0x10]
     704: 910013e2     	add	x2, sp, #0x4
     708: 2a1603e1     	mov	w1, w22
     70c: 94000000     	bl	0x70c <sc851x_charger_probe+0x708>
		000000000000070c:  R_AARCH64_CALL26	regmap_read
     710: 2a0003f5     	mov	w21, w0
     714: f9400280     	ldr	x0, [x20]
     718: b94007e4     	ldr	w4, [sp, #0x4]
     71c: aa1703e1     	mov	x1, x23
     720: aa1803e2     	mov	x2, x24
     724: 2a1603e3     	mov	w3, w22
     728: 94000000     	bl	0x728 <sc851x_charger_probe+0x724>
		0000000000000728:  R_AARCH64_CALL26	_dev_err
     72c: 110006d6     	add	w22, w22, #0x1
     730: 71005adf     	cmp	w22, #0x16
     734: 54fffe61     	b.ne	0x700 <sc851x_charger_probe+0x6fc>
     738: 36f800b5     	tbz	w21, #0x1f, 0x74c <sc851x_charger_probe+0x748>
     73c: f9400280     	ldr	x0, [x20]
     740: 90000001     	adrp	x1, 0x0 <.text>
		0000000000000740:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x3cb
     744: 91000021     	add	x1, x1, #0x0
		0000000000000744:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x3cb
     748: 17ffffdc     	b	0x6b8 <sc851x_charger_probe+0x6b4>
     74c: aa1403e0     	mov	x0, x20
     750: 94000034     	bl	0x820 <sc851x_register_interrupt>
     754: 2a0003f5     	mov	w21, w0
     758: f9400280     	ldr	x0, [x20]
     75c: 36f80095     	tbz	w21, #0x1f, 0x76c <sc851x_charger_probe+0x768>
     760: 90000001     	adrp	x1, 0x0 <.text>
		0000000000000760:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x1da
     764: 91000021     	add	x1, x1, #0x0
		0000000000000764:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x1da
     768: 17ffffd4     	b	0x6b8 <sc851x_charger_probe+0x6b4>
     76c: 90000001     	adrp	x1, 0x0 <.text>
		000000000000076c:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x356
     770: 91000021     	add	x1, x1, #0x0
		0000000000000770:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x356
     774: 94000000     	bl	0x774 <sc851x_charger_probe+0x770>
		0000000000000774:  R_AARCH64_CALL26	_dev_err
     778: 2a1f03f5     	mov	w21, wzr
     77c: 17fffe3d     	b	0x70 <sc851x_charger_probe+0x6c>
     780: d42aa240     	brk	#0x5512
     784: 94000000     	bl	0x784 <sc851x_charger_probe+0x780>
		0000000000000784:  R_AARCH64_CALL26	__stack_chk_fail
     788: 6d dd ff 8e  	.word	0x8effdd6d

000000000000078c <sc851x_charger_remove>:
     78c: d503233f     	paciasp
     790: a9bf7bfd     	stp	x29, x30, [sp, #-0x10]!
     794: 910003fd     	mov	x29, sp
     798: 91008008     	add	x8, x0, #0x20
     79c: f9405c01     	ldr	x1, [x0, #0xb8]
     7a0: aa0803e0     	mov	x0, x8
     7a4: 94000000     	bl	0x7a4 <sc851x_charger_remove+0x18>
		00000000000007a4:  R_AARCH64_CALL26	devm_kfree
     7a8: a8c17bfd     	ldp	x29, x30, [sp], #0x10
     7ac: d50323bf     	autiasp
     7b0: d65f03c0     	ret
     7b4: 6d dd ff 8e  	.word	0x8effdd6d

00000000000007b8 <sc851x_charger_shutdown>:
     7b8: d503233f     	paciasp
     7bc: a9be7bfd     	stp	x29, x30, [sp, #-0x20]!
     7c0: f9000bf3     	str	x19, [sp, #0x10]
     7c4: 910003fd     	mov	x29, sp
     7c8: f9405c13     	ldr	x19, [x0, #0xb8]
     7cc: 12800001     	mov	w1, #-0x1               // =-1
     7d0: 2a1f03e2     	mov	w2, wzr
     7d4: aa1f03e3     	mov	x3, xzr
     7d8: 2a1f03e4     	mov	w4, wzr
     7dc: 2a1f03e5     	mov	w5, wzr
     7e0: f9407a60     	ldr	x0, [x19, #0xf0]
     7e4: 94000000     	bl	0x7e4 <sc851x_charger_shutdown+0x2c>
		00000000000007e4:  R_AARCH64_CALL26	regmap_field_update_bits_base
     7e8: 36f800e0     	tbz	w0, #0x1f, 0x804 <sc851x_charger_shutdown+0x4c>
     7ec: 2a0003e3     	mov	w3, w0
     7f0: f9400260     	ldr	x0, [x19]
     7f4: 90000001     	adrp	x1, 0x0 <.text>
		00000000000007f4:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x417
     7f8: 91000021     	add	x1, x1, #0x0
		00000000000007f8:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x417
     7fc: 52800362     	mov	w2, #0x1b               // =27
     800: 94000000     	bl	0x800 <sc851x_charger_shutdown+0x48>
		0000000000000800:  R_AARCH64_CALL26	_dev_err
     804: 90000000     	adrp	x0, 0x0 <.text>
		0000000000000804:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x21c
     808: 91000000     	add	x0, x0, #0x0
		0000000000000808:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x21c
     80c: 94000000     	bl	0x80c <sc851x_charger_shutdown+0x54>
		000000000000080c:  R_AARCH64_CALL26	_printk
     810: f9400bf3     	ldr	x19, [sp, #0x10]
     814: a8c27bfd     	ldp	x29, x30, [sp], #0x20
     818: d50323bf     	autiasp
     81c: d65f03c0     	ret

0000000000000820 <sc851x_register_interrupt>:
     820: d503233f     	paciasp
     824: a9be7bfd     	stp	x29, x30, [sp, #-0x20]!
     828: a9014ff4     	stp	x20, x19, [sp, #0x10]
     82c: 910003fd     	mov	x29, sp
     830: aa0003f3     	mov	x19, x0
     834: b9423400     	ldr	w0, [x0, #0x234]
     838: 7108001f     	cmp	w0, #0x200
     83c: 540003e2     	b.hs	0x8b8 <sc851x_register_interrupt+0x98>
     840: 90000002     	adrp	x2, 0x0 <.text>
		0000000000000840:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x1cf
     844: 91000042     	add	x2, x2, #0x0
		0000000000000844:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x1cf
     848: 52800021     	mov	w1, #0x1                // =1
     84c: 94000000     	bl	0x84c <sc851x_register_interrupt+0x2c>
		000000000000084c:  R_AARCH64_CALL26	gpio_request_one
     850: 350003c0     	cbnz	w0, 0x8c8 <sc851x_register_interrupt+0xa8>
     854: b9423660     	ldr	w0, [x19, #0x234]
     858: 94000000     	bl	0x858 <sc851x_register_interrupt+0x38>
		0000000000000858:  R_AARCH64_CALL26	gpio_to_desc
     85c: 94000000     	bl	0x85c <sc851x_register_interrupt+0x3c>
		000000000000085c:  R_AARCH64_CALL26	gpiod_to_irq
     860: b9023a60     	str	w0, [x19, #0x238]
     864: 37f803a0     	tbnz	w0, #0x1f, 0x8d8 <sc851x_register_interrupt+0xb8>
     868: 2a0003e1     	mov	w1, w0
     86c: 34000220     	cbz	w0, 0x8b0 <sc851x_register_interrupt+0x90>
     870: f9400668     	ldr	x8, [x19, #0x8]
     874: 90000003     	adrp	x3, 0x0 <.text>
		0000000000000874:  R_AARCH64_ADR_PREL_PG_HI21	.text+0xae8
     878: 91000063     	add	x3, x3, #0x0
		0000000000000878:  R_AARCH64_ADD_ABS_LO12_NC	.text+0xae8
     87c: 90000005     	adrp	x5, 0x0 <.text>
		000000000000087c:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x311
     880: 910000a5     	add	x5, x5, #0x0
		0000000000000880:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x311
     884: aa1f03e2     	mov	x2, xzr
     888: 91008100     	add	x0, x8, #0x20
     88c: 52840044     	mov	w4, #0x2002             // =8194
     890: aa1303e6     	mov	x6, x19
     894: 94000000     	bl	0x894 <sc851x_register_interrupt+0x74>
		0000000000000894:  R_AARCH64_CALL26	devm_request_threaded_irq
     898: 2a0003f4     	mov	w20, w0
     89c: 37f80320     	tbnz	w0, #0x1f, 0x900 <sc851x_register_interrupt+0xe0>
     8a0: b9423a60     	ldr	w0, [x19, #0x238]
     8a4: 52800021     	mov	w1, #0x1                // =1
     8a8: 94000000     	bl	0x8a8 <sc851x_register_interrupt+0x88>
		00000000000008a8:  R_AARCH64_CALL26	irq_set_irq_wake
     8ac: 14000010     	b	0x8ec <sc851x_register_interrupt+0xcc>
     8b0: 2a1f03f4     	mov	w20, wzr
     8b4: 1400000e     	b	0x8ec <sc851x_register_interrupt+0xcc>
     8b8: f9400260     	ldr	x0, [x19]
     8bc: 90000001     	adrp	x1, 0x0 <.text>
		00000000000008bc:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x7b
     8c0: 91000021     	add	x1, x1, #0x0
		00000000000008c0:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x7b
     8c4: 14000008     	b	0x8e4 <sc851x_register_interrupt+0xc4>
     8c8: f9400260     	ldr	x0, [x19]
     8cc: 90000001     	adrp	x1, 0x0 <.text>
		00000000000008cc:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x144
     8d0: 91000021     	add	x1, x1, #0x0
		00000000000008d0:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x144
     8d4: 14000004     	b	0x8e4 <sc851x_register_interrupt+0xc4>
     8d8: f9400260     	ldr	x0, [x19]
     8dc: 90000001     	adrp	x1, 0x0 <.text>
		00000000000008dc:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x205
     8e0: 91000021     	add	x1, x1, #0x0
		00000000000008e0:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x205
     8e4: 94000000     	bl	0x8e4 <sc851x_register_interrupt+0xc4>
		00000000000008e4:  R_AARCH64_CALL26	_dev_err
     8e8: 128002b4     	mov	w20, #-0x16             // =-22
     8ec: 2a1403e0     	mov	w0, w20
     8f0: a9414ff4     	ldp	x20, x19, [sp, #0x10]
     8f4: a8c27bfd     	ldp	x29, x30, [sp], #0x20
     8f8: d50323bf     	autiasp
     8fc: d65f03c0     	ret
     900: f9400260     	ldr	x0, [x19]
     904: 90000001     	adrp	x1, 0x0 <.text>
		0000000000000904:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x44f
     908: 91000021     	add	x1, x1, #0x0
		0000000000000908:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x44f
     90c: b9423a62     	ldr	w2, [x19, #0x238]
     910: 2a1403e3     	mov	w3, w20
     914: 94000000     	bl	0x914 <sc851x_register_interrupt+0xf4>
		0000000000000914:  R_AARCH64_CALL26	_dev_err
     918: 17fffff5     	b	0x8ec <sc851x_register_interrupt+0xcc>
     91c: 5c c2 43 df  	.word	0xdf43c25c

0000000000000920 <sc851x_show_registers>:
     920: d503233f     	paciasp
     924: d10683ff     	sub	sp, sp, #0x1a0
     928: a9147bfd     	stp	x29, x30, [sp, #0x140]
     92c: f900abfc     	str	x28, [sp, #0x150]
     930: a91667fa     	stp	x26, x25, [sp, #0x160]
     934: a9175ff8     	stp	x24, x23, [sp, #0x170]
     938: a91857f6     	stp	x22, x21, [sp, #0x180]
     93c: a9194ff4     	stp	x20, x19, [sp, #0x190]
     940: 910503fd     	add	x29, sp, #0x140
     944: d5384108     	mrs	x8, SP_EL0
     948: aa0203f3     	mov	x19, x2
     94c: f9431d08     	ldr	x8, [x8, #0x638]
     950: 2a1f03e1     	mov	w1, wzr
     954: 52802582     	mov	w2, #0x12c              // =300
     958: f81f83a8     	stur	x8, [x29, #-0x8]
     95c: f9404c18     	ldr	x24, [x0, #0x98]
     960: 910033e0     	add	x0, sp, #0xc
     964: b9000bff     	str	wzr, [sp, #0x8]
     968: 94000000     	bl	0x968 <sc851x_show_registers+0x48>
		0000000000000968:  R_AARCH64_CALL26	memset
     96c: 90000002     	adrp	x2, 0x0 <.text>
		000000000000096c:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0xff
     970: 91000042     	add	x2, x2, #0x0
		0000000000000970:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0xff
     974: 90000003     	adrp	x3, 0x0 <.text>
		0000000000000974:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x34f
     978: 91000063     	add	x3, x3, #0x0
		0000000000000978:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x34f
     97c: aa1303e0     	mov	x0, x19
     980: 52820001     	mov	w1, #0x1000             // =4096
     984: 52820019     	mov	w25, #0x1000            // =4096
     988: 94000000     	bl	0x988 <sc851x_show_registers+0x68>
		0000000000000988:  R_AARCH64_CALL26	snprintf
     98c: 2a0003f4     	mov	w20, w0
     990: 2a1f03f5     	mov	w21, wzr
     994: 90000016     	adrp	x22, 0x0 <.text>
		0000000000000994:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x387
     998: 910002d6     	add	x22, x22, #0x0
		0000000000000998:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x387
     99c: 1400000a     	b	0x9c4 <sc851x_show_registers+0xa4>
     9a0: 2a0003f7     	mov	w23, w0
     9a4: 8b1a0260     	add	x0, x19, x26
     9a8: 93407ee2     	sxtw	x2, w23
     9ac: 910033e1     	add	x1, sp, #0xc
     9b0: 94000000     	bl	0x9b0 <sc851x_show_registers+0x90>
		00000000000009b0:  R_AARCH64_CALL26	memcpy
     9b4: 0b1402f4     	add	w20, w23, w20
     9b8: 110006b5     	add	w21, w21, #0x1
     9bc: 71005abf     	cmp	w21, #0x16
     9c0: 54000240     	b.eq	0xa08 <sc851x_show_registers+0xe8>
     9c4: f9400b00     	ldr	x0, [x24, #0x10]
     9c8: 910023e2     	add	x2, sp, #0x8
     9cc: 2a1503e1     	mov	w1, w21
     9d0: 94000000     	bl	0x9d0 <sc851x_show_registers+0xb0>
		00000000000009d0:  R_AARCH64_CALL26	regmap_read
     9d4: 35ffff20     	cbnz	w0, 0x9b8 <sc851x_show_registers+0x98>
     9d8: 93407e9a     	sxtw	x26, w20
     9dc: b9400be4     	ldr	w4, [sp, #0x8]
     9e0: cb1a0321     	sub	x1, x25, x26
     9e4: 910033e0     	add	x0, sp, #0xc
     9e8: aa1603e2     	mov	x2, x22
     9ec: 2a1503e3     	mov	w3, w21
     9f0: 94000000     	bl	0x9f0 <sc851x_show_registers+0xd0>
		00000000000009f0:  R_AARCH64_CALL26	snprintf
     9f4: 7104b41f     	cmp	w0, #0x12d
     9f8: 54fffd43     	b.lo	0x9a0 <sc851x_show_registers+0x80>
     9fc: 90000000     	adrp	x0, 0x0 <.text>
		00000000000009fc:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x4c2
     a00: 91000000     	add	x0, x0, #0x0
		0000000000000a00:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x4c2
     a04: 94000000     	bl	0xa04 <sc851x_show_registers+0xe4>
		0000000000000a04:  R_AARCH64_CALL26	fortify_panic
     a08: d5384108     	mrs	x8, SP_EL0
     a0c: f9431d08     	ldr	x8, [x8, #0x638]
     a10: f85f83a9     	ldur	x9, [x29, #-0x8]
     a14: eb09011f     	cmp	x8, x9
     a18: 54000161     	b.ne	0xa44 <sc851x_show_registers+0x124>
     a1c: 93407e80     	sxtw	x0, w20
     a20: a9594ff4     	ldp	x20, x19, [sp, #0x190]
     a24: a95857f6     	ldp	x22, x21, [sp, #0x180]
     a28: a9575ff8     	ldp	x24, x23, [sp, #0x170]
     a2c: a95667fa     	ldp	x26, x25, [sp, #0x160]
     a30: a9547bfd     	ldp	x29, x30, [sp, #0x140]
     a34: f940abfc     	ldr	x28, [sp, #0x150]
     a38: 910683ff     	add	sp, sp, #0x1a0
     a3c: d50323bf     	autiasp
     a40: d65f03c0     	ret
     a44: 94000000     	bl	0xa44 <sc851x_show_registers+0x124>
		0000000000000a44:  R_AARCH64_CALL26	__stack_chk_fail
     a48: 07 ba a8 95  	.word	0x95a8ba07

0000000000000a4c <sc851x_store_register>:
     a4c: d503233f     	paciasp
     a50: d100c3ff     	sub	sp, sp, #0x30
     a54: a9017bfd     	stp	x29, x30, [sp, #0x10]
     a58: a9024ff4     	stp	x20, x19, [sp, #0x20]
     a5c: 910043fd     	add	x29, sp, #0x10
     a60: d5384109     	mrs	x9, SP_EL0
     a64: aa0203e8     	mov	x8, x2
     a68: f9431d29     	ldr	x9, [x9, #0x638]
     a6c: aa0303f3     	mov	x19, x3
     a70: 90000001     	adrp	x1, 0x0 <.text>
		0000000000000a70:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x4a4
     a74: 91000021     	add	x1, x1, #0x0
		0000000000000a74:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x4a4
     a78: 910013e2     	add	x2, sp, #0x4
     a7c: 910003e3     	mov	x3, sp
     a80: f90007e9     	str	x9, [sp, #0x8]
     a84: f9404c14     	ldr	x20, [x0, #0x98]
     a88: aa0803e0     	mov	x0, x8
     a8c: f90003ff     	str	xzr, [sp]
     a90: 94000000     	bl	0xa90 <sc851x_store_register+0x44>
		0000000000000a90:  R_AARCH64_CALL26	sscanf
     a94: 7100081f     	cmp	w0, #0x2
     a98: 540000e1     	b.ne	0xab4 <sc851x_store_register+0x68>
     a9c: b94007e1     	ldr	w1, [sp, #0x4]
     aa0: 7100543f     	cmp	w1, #0x15
     aa4: 54000088     	b.hi	0xab4 <sc851x_store_register+0x68>
     aa8: f9400a80     	ldr	x0, [x20, #0x10]
     aac: b94003e2     	ldr	w2, [sp]
     ab0: 94000000     	bl	0xab0 <sc851x_store_register+0x64>
		0000000000000ab0:  R_AARCH64_CALL26	regmap_write
     ab4: d5384108     	mrs	x8, SP_EL0
     ab8: f9431d08     	ldr	x8, [x8, #0x638]
     abc: f94007e9     	ldr	x9, [sp, #0x8]
     ac0: eb09011f     	cmp	x8, x9
     ac4: 540000e1     	b.ne	0xae0 <sc851x_store_register+0x94>
     ac8: aa1303e0     	mov	x0, x19
     acc: a9424ff4     	ldp	x20, x19, [sp, #0x20]
     ad0: a9417bfd     	ldp	x29, x30, [sp, #0x10]
     ad4: 9100c3ff     	add	sp, sp, #0x30
     ad8: d50323bf     	autiasp
     adc: d65f03c0     	ret
     ae0: 94000000     	bl	0xae0 <sc851x_store_register+0x94>
		0000000000000ae0:  R_AARCH64_CALL26	__stack_chk_fail
     ae4: f6 05 0f f9  	.word	0xf90f05f6

0000000000000ae8 <sc851x_irq_handler>:
     ae8: d503233f     	paciasp
     aec: d100c3ff     	sub	sp, sp, #0x30
     af0: a9017bfd     	stp	x29, x30, [sp, #0x10]
     af4: f90013f3     	str	x19, [sp, #0x20]
     af8: 910043fd     	add	x29, sp, #0x10
     afc: d5384108     	mrs	x8, SP_EL0
     b00: aa0103f3     	mov	x19, x1
     b04: f9431d08     	ldr	x8, [x8, #0x638]
     b08: f90007e8     	str	x8, [sp, #0x8]
     b0c: f9400020     	ldr	x0, [x1]
     b10: 90000001     	adrp	x1, 0x0 <.text>
		0000000000000b10:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x2a
     b14: 91000021     	add	x1, x1, #0x0
		0000000000000b14:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x2a
     b18: 94000000     	bl	0xb18 <sc851x_irq_handler+0x30>
		0000000000000b18:  R_AARCH64_CALL26	_dev_err
     b1c: f9400a60     	ldr	x0, [x19, #0x10]
     b20: 910013e2     	add	x2, sp, #0x4
     b24: 52800181     	mov	w1, #0xc                // =12
     b28: b90007ff     	str	wzr, [sp, #0x4]
     b2c: 94000000     	bl	0xb2c <sc851x_irq_handler+0x44>
		0000000000000b2c:  R_AARCH64_CALL26	regmap_read
     b30: 340002c0     	cbz	w0, 0xb88 <sc851x_irq_handler+0xa0>
     b34: f9400a60     	ldr	x0, [x19, #0x10]
     b38: 910013e2     	add	x2, sp, #0x4
     b3c: 528001a1     	mov	w1, #0xd                // =13
     b40: 94000000     	bl	0xb40 <sc851x_irq_handler+0x58>
		0000000000000b40:  R_AARCH64_CALL26	regmap_read
     b44: 340002e0     	cbz	w0, 0xba0 <sc851x_irq_handler+0xb8>
     b48: f9400a60     	ldr	x0, [x19, #0x10]
     b4c: 910013e2     	add	x2, sp, #0x4
     b50: 528001c1     	mov	w1, #0xe                // =14
     b54: 94000000     	bl	0xb54 <sc851x_irq_handler+0x6c>
		0000000000000b54:  R_AARCH64_CALL26	regmap_read
     b58: 34000300     	cbz	w0, 0xbb8 <sc851x_irq_handler+0xd0>
     b5c: d5384108     	mrs	x8, SP_EL0
     b60: f9431d08     	ldr	x8, [x8, #0x638]
     b64: f94007e9     	ldr	x9, [sp, #0x8]
     b68: eb09011f     	cmp	x8, x9
     b6c: 54000321     	b.ne	0xbd0 <sc851x_irq_handler+0xe8>
     b70: 52800020     	mov	w0, #0x1                // =1
     b74: a9417bfd     	ldp	x29, x30, [sp, #0x10]
     b78: f94013f3     	ldr	x19, [sp, #0x20]
     b7c: 9100c3ff     	add	sp, sp, #0x30
     b80: d50323bf     	autiasp
     b84: d65f03c0     	ret
     b88: f9400260     	ldr	x0, [x19]
     b8c: 90000001     	adrp	x1, 0x0 <.text>
		0000000000000b8c:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x597
     b90: 91000021     	add	x1, x1, #0x0
		0000000000000b90:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x597
     b94: b94007e2     	ldr	w2, [sp, #0x4]
     b98: 94000000     	bl	0xb98 <sc851x_irq_handler+0xb0>
		0000000000000b98:  R_AARCH64_CALL26	_dev_err
     b9c: 17ffffe6     	b	0xb34 <sc851x_irq_handler+0x4c>
     ba0: f9400260     	ldr	x0, [x19]
     ba4: 90000001     	adrp	x1, 0x0 <.text>
		0000000000000ba4:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x516
     ba8: 91000021     	add	x1, x1, #0x0
		0000000000000ba8:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x516
     bac: b94007e2     	ldr	w2, [sp, #0x4]
     bb0: 94000000     	bl	0xbb0 <sc851x_irq_handler+0xc8>
		0000000000000bb0:  R_AARCH64_CALL26	_dev_err
     bb4: 17ffffe5     	b	0xb48 <sc851x_irq_handler+0x60>
     bb8: f9400260     	ldr	x0, [x19]
     bbc: 90000001     	adrp	x1, 0x0 <.text>
		0000000000000bbc:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x4aa
     bc0: 91000021     	add	x1, x1, #0x0
		0000000000000bc0:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x4aa
     bc4: b94007e2     	ldr	w2, [sp, #0x4]
     bc8: 94000000     	bl	0xbc8 <sc851x_irq_handler+0xe0>
		0000000000000bc8:  R_AARCH64_CALL26	_dev_err
     bcc: 17ffffe4     	b	0xb5c <sc851x_irq_handler+0x74>
     bd0: 94000000     	bl	0xbd0 <sc851x_irq_handler+0xe8>
		0000000000000bd0:  R_AARCH64_CALL26	__stack_chk_fail
     bd4: 5f 65 45 3f  	.word	0x3f45655f

0000000000000bd8 <sc851x_suspend>:
     bd8: d503233f     	paciasp
     bdc: a9be7bfd     	stp	x29, x30, [sp, #-0x20]!
     be0: a9014ff4     	stp	x20, x19, [sp, #0x10]
     be4: 910003fd     	mov	x29, sp
     be8: f9404c14     	ldr	x20, [x0, #0x98]
     bec: aa0003f3     	mov	x19, x0
     bf0: 90000001     	adrp	x1, 0x0 <.text>
		0000000000000bf0:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x31c
     bf4: 91000021     	add	x1, x1, #0x0
		0000000000000bf4:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x31c
     bf8: f9400280     	ldr	x0, [x20]
     bfc: 94000000     	bl	0xbfc <sc851x_suspend+0x24>
		0000000000000bfc:  R_AARCH64_CALL26	_dev_info
     c00: 79421a68     	ldrh	w8, [x19, #0x10c]
     c04: 360000c8     	tbz	w8, #0x0, 0xc1c <sc851x_suspend+0x44>
     c08: f940a668     	ldr	x8, [x19, #0x148]
     c0c: b4000088     	cbz	x8, 0xc1c <sc851x_suspend+0x44>
     c10: b9423a80     	ldr	w0, [x20, #0x238]
     c14: 52800021     	mov	w1, #0x1                // =1
     c18: 94000000     	bl	0xc18 <sc851x_suspend+0x40>
		0000000000000c18:  R_AARCH64_CALL26	irq_set_irq_wake
     c1c: b9423a80     	ldr	w0, [x20, #0x238]
     c20: 94000000     	bl	0xc20 <sc851x_suspend+0x48>
		0000000000000c20:  R_AARCH64_CALL26	disable_irq
     c24: 2a1f03e0     	mov	w0, wzr
     c28: a9414ff4     	ldp	x20, x19, [sp, #0x10]
     c2c: a8c27bfd     	ldp	x29, x30, [sp], #0x20
     c30: d50323bf     	autiasp
     c34: d65f03c0     	ret
     c38: 5f 65 45 3f  	.word	0x3f45655f

0000000000000c3c <sc851x_resume>:
     c3c: d503233f     	paciasp
     c40: a9be7bfd     	stp	x29, x30, [sp, #-0x20]!
     c44: a9014ff4     	stp	x20, x19, [sp, #0x10]
     c48: 910003fd     	mov	x29, sp
     c4c: f9404c14     	ldr	x20, [x0, #0x98]
     c50: aa0003f3     	mov	x19, x0
     c54: 90000001     	adrp	x1, 0x0 <.text>
		0000000000000c54:  R_AARCH64_ADR_PREL_PG_HI21	.rodata.str1.1+0x18f
     c58: 91000021     	add	x1, x1, #0x0
		0000000000000c58:  R_AARCH64_ADD_ABS_LO12_NC	.rodata.str1.1+0x18f
     c5c: f9400280     	ldr	x0, [x20]
     c60: 94000000     	bl	0xc60 <sc851x_resume+0x24>
		0000000000000c60:  R_AARCH64_CALL26	_dev_info
     c64: 79421a68     	ldrh	w8, [x19, #0x10c]
     c68: 360000c8     	tbz	w8, #0x0, 0xc80 <sc851x_resume+0x44>
     c6c: f940a668     	ldr	x8, [x19, #0x148]
     c70: b4000088     	cbz	x8, 0xc80 <sc851x_resume+0x44>
     c74: b9423a80     	ldr	w0, [x20, #0x238]
     c78: 2a1f03e1     	mov	w1, wzr
     c7c: 94000000     	bl	0xc7c <sc851x_resume+0x40>
		0000000000000c7c:  R_AARCH64_CALL26	irq_set_irq_wake
     c80: b9423a80     	ldr	w0, [x20, #0x238]
     c84: 94000000     	bl	0xc84 <sc851x_resume+0x48>
		0000000000000c84:  R_AARCH64_CALL26	enable_irq
     c88: 2a1f03e0     	mov	w0, wzr
     c8c: a9414ff4     	ldp	x20, x19, [sp, #0x10]
     c90: a8c27bfd     	ldp	x29, x30, [sp], #0x20
     c94: d50323bf     	autiasp
     c98: d65f03c0     	ret
