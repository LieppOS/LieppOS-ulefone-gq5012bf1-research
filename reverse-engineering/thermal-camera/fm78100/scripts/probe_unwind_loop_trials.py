W='/home/armol/kernel-work/gki-12901745-workspace/lieppos/thermal-fm78100'
exec(open(W+'/fast.py').read())
s=open(W+'/yft_tiny2c_usb.B5.c').read()
a=s.index('static int tiny2c_usb_init_sysfs'); b=s.index('static int tiny2c_usb_probe(')
H='static int tiny2c_usb_init_sysfs(struct device *dev)\n{\n'
P='\tprintk("tiny2c_usb_init_sysfs. begin. \\n");\n'
V={}
V['v4']=H+'\tint i, ret = 0;\n\n'+P+'\tfor (i = 0; mt_sysfs_attributes[i]; i++) {\n\t\tret = device_create_file(dev, mt_sysfs_attributes[i]);\n\t\tif (ret)\n\t\t\tbreak;\n\t}\n\tif (ret) {\n\t\tfor (; i >= 0; i--)\n\t\t\tdevice_remove_file(dev, mt_sysfs_attributes[i]);\n\t}\n\treturn ret;\n}\n\n'
V['v5']=H+'\tint i, ret = 0;\n\n'+P+'\tfor (i = 0; mt_sysfs_attributes[i]; i++) {\n\t\tret = device_create_file(dev, mt_sysfs_attributes[i]);\n\t\tif (ret) {\n\t\t\tfor (; i >= 0; i--)\n\t\t\t\tdevice_remove_file(dev, mt_sysfs_attributes[i]);\n\t\t\tbreak;\n\t\t}\n\t}\n\treturn ret;\n}\n\n'
V['v6']=H+'\tint i, ret = 0;\n\n'+P+'\tfor (i = 0; mt_sysfs_attributes[i]; i++) {\n\t\tret = device_create_file(dev, mt_sysfs_attributes[i]);\n\t\tif (ret) {\n\t\t\twhile (i >= 0) {\n\t\t\t\tdevice_remove_file(dev, mt_sysfs_attributes[i]);\n\t\t\t\ti--;\n\t\t\t}\n\t\t\treturn ret;\n\t\t}\n\t}\n\treturn ret;\n}\n\n'
V['v7']=H+'\tint i, ret = 0;\n\tint num = ARRAY_SIZE(mt_sysfs_attributes) - 1;\n\n'+P+'\tfor (i = 0; i < num; i++) {\n\t\tret = device_create_file(dev, mt_sysfs_attributes[i]);\n\t\tif (ret)\n\t\t\tbreak;\n\t}\n\tif (ret) {\n\t\tfor (; i >= 0; i--)\n\t\t\tdevice_remove_file(dev, mt_sysfs_attributes[i]);\n\t}\n\treturn ret;\n}\n\n'
V['v8']=H+'\tint i, ret = 0;\n\n'+P+'\tfor (i = 0; mt_sysfs_attributes[i]; i++) {\n\t\tret = device_create_file(dev, mt_sysfs_attributes[i]);\n\t\tif (ret)\n\t\t\tgoto exit;\n\t}\n\treturn 0;\nexit:\n\tfor (; i >= 0; i--)\n\t\tdevice_remove_file(dev, mt_sysfs_attributes[i]);\n\treturn ret;\n}\n\n'
V['v9']=H+'\tint i = 0, ret = 0;\n\n'+P+'\twhile (mt_sysfs_attributes[i]) {\n\t\tret = device_create_file(dev, mt_sysfs_attributes[i]);\n\t\tif (ret)\n\t\t\tbreak;\n\t\ti++;\n\t}\n\tif (ret)\n\t\tfor (; i >= 0; i--)\n\t\t\tdevice_remove_file(dev, mt_sysfs_attributes[i]);\n\treturn ret;\n}\n\n'
import sys
for k,v in V.items():
    t=s[:a]+v+s[b:]
    print(k,score(t,'tiny2c_usb_probe',tag=k),flush=True)
W='/home/armol/kernel-work/gki-12901745-workspace/lieppos/thermal-fm78100'
exec(open(W+'/fast.py').read())
s=open(W+'/yft_tiny2c_usb.B5.c').read()
a=s.index('static int tiny2c_usb_init_sysfs'); b=s.index('static int tiny2c_usb_probe(')
H='static int tiny2c_usb_init_sysfs(struct device *dev)\n{\n'
P='\tprintk("tiny2c_usb_init_sysfs. begin. \\n");\n'
CREATE={
 'null':'\tfor (i = 0; mt_sysfs_attributes[i]; i++) {\n\t\tret = device_create_file(dev, mt_sysfs_attributes[i]);\n\t\tif (ret)\n\t\t\tbreak;\n\t}\n',
 'num':'\tfor (i = 0; i < num; i++) {\n\t\tret = device_create_file(dev, mt_sysfs_attributes[i]);\n\t\tif (ret)\n\t\t\tbreak;\n\t}\n',
 'num_null':'\tfor (i = 0; i < num; i++) {\n\t\tif (!mt_sysfs_attributes[i])\n\t\t\tbreak;\n\t\tret = device_create_file(dev, mt_sysfs_attributes[i]);\n\t\tif (ret)\n\t\t\tbreak;\n\t}\n',
}
REMOVE={
 'for':'\tif (ret)\n\t\tfor (; i >= 0; i--)\n\t\t\tdevice_remove_file(dev, mt_sysfs_attributes[i]);\n',
 'do':'\tif (ret) {\n\t\tdo {\n\t\t\tdevice_remove_file(dev, mt_sysfs_attributes[i]);\n\t\t} while (--i >= 0);\n\t}\n',
 'postdec':'\tif (ret)\n\t\twhile (i >= 0)\n\t\t\tdevice_remove_file(dev, mt_sysfs_attributes[i--]);\n',
}
NUM={'n3':'\tint num = ARRAY_SIZE(mt_sysfs_attributes);\n','n2':'\tint num = ARRAY_SIZE(mt_sysfs_attributes) - 1;\n','none':''}
TY={'int':'\tint i, ret = 0;\n','long':'\tlong i;\n\tint ret = 0;\n','uint_ret':'\tint i;\n\tint ret = 0;\n'}
res=[]
for cn,c in CREATE.items():
  for rn,r in REMOVE.items():
    for nn,n in NUM.items():
      if ('num' in cn)!=(nn!='none'): continue
      for tn,t in TY.items():
        if tn=='uint_ret': continue
        body=H+t+n+'\n'+P+c+r+'\treturn ret;\n}\n\n'
        sc=score(s[:a]+body+s[b:],'tiny2c_usb_probe',tag='x')
        res.append((sc,cn,rn,nn,tn)); print(sc,cn,rn,nn,tn,flush=True)
print(sorted(res)[:3])
W='/home/armol/kernel-work/gki-12901745-workspace/lieppos/thermal-fm78100'
exec(open(W+'/fast.py').read())
s=open(W+'/yft_tiny2c_usb.B5.c').read()
a=s.index('static int tiny2c_usb_init_sysfs'); b=s.index('static int tiny2c_usb_probe(')
H='static int tiny2c_usb_init_sysfs(struct device *dev)\n{\n'
P='\tprintk("tiny2c_usb_init_sysfs. begin. \\n");\n'
V={
'uint_cast':H+'\tunsigned int i;\n\tint ret = 0;\n'+P+'\tfor (i = 0; mt_sysfs_attributes[i]; i++) {\n\t\tret = device_create_file(dev, mt_sysfs_attributes[i]);\n\t\tif (ret)\n\t\t\tbreak;\n\t}\n\tif (ret)\n\t\tfor (; (int)i >= 0; i--)\n\t\t\tdevice_remove_file(dev, mt_sysfs_attributes[i]);\n\treturn ret;\n}\n\n',
'arrsize':H+'\tint i, ret = 0;\n'+P+'\tfor (i = 0; i < ARRAY_SIZE(mt_sysfs_attributes); i++) {\n\t\tif (!mt_sysfs_attributes[i])\n\t\t\tbreak;\n\t\tret = device_create_file(dev, mt_sysfs_attributes[i]);\n\t\tif (ret)\n\t\t\tbreak;\n\t}\n\tif (ret)\n\t\tfor (; i >= 0; i--)\n\t\t\tdevice_remove_file(dev, mt_sysfs_attributes[i]);\n\treturn ret;\n}\n\n',
'jcount':H+'\tint i, j, ret = 0;\n'+P+'\tfor (i = 0; mt_sysfs_attributes[i]; i++) {\n\t\tret = device_create_file(dev, mt_sysfs_attributes[i]);\n\t\tif (ret)\n\t\t\tbreak;\n\t}\n\tif (ret)\n\t\tfor (j = i; j >= 0; j--)\n\t\t\tdevice_remove_file(dev, mt_sysfs_attributes[j]);\n\treturn ret;\n}\n\n',
'noinit_ret_goto':H+'\tint i, ret;\n'+P+'\tfor (i = 0; mt_sysfs_attributes[i] != NULL; i++) {\n\t\tret = device_create_file(dev, mt_sysfs_attributes[i]);\n\t\tif (ret)\n\t\t\tgoto err;\n\t}\n\treturn 0;\nerr:\n\tfor (; i >= 0; i--)\n\t\tdevice_remove_file(dev, mt_sysfs_attributes[i]);\n\treturn ret;\n}\n\n',
}
# also variant: removal done in probe (init_sysfs returns idx via pointer)
for k,v in V.items():
    print(k,score(s[:a]+v+s[b:],'tiny2c_usb_probe',tag='z'),flush=True)
W='/home/armol/kernel-work/gki-12901745-workspace/lieppos/thermal-fm78100'
exec(open(W+'/fast.py').read())
s=open(W+'/yft_tiny2c_usb.B5.c').read()
a=s.index('static int tiny2c_usb_init_sysfs'); b=s.index('static int tiny2c_usb_probe(')
P='\tprintk("tiny2c_usb_init_sysfs. begin. \\n");\n'
CR='\tfor (i = 0; attrs[i]; i++) {\n\t\tret = device_create_file(dev, attrs[i]);\n\t\tif (ret)\n\t\t\tbreak;\n\t}\n'
CRn='\tfor (i = 0; i < num; i++) {\n\t\tret = device_create_file(dev, attrs[i]);\n\t\tif (ret)\n\t\t\tbreak;\n\t}\n'
RM='\tif (ret)\n\t\tfor (; i >= 0; i--)\n\t\t\tdevice_remove_file(dev, attrs[i]);\n'
RMw='\tif (ret) {\n\t\twhile (i >= 0) {\n\t\t\tdevice_remove_file(dev, attrs[i]);\n\t\t\ti--;\n\t\t}\n\t}\n'
V={
'p_attrs':'static int tiny2c_usb_init_sysfs(struct device *dev, struct device_attribute **attrs)\n{\n\tint i, ret = 0;\n\n'+P+CR+RM+'\treturn ret;\n}\n\n',
'p_attrs_w':'static int tiny2c_usb_init_sysfs(struct device *dev, struct device_attribute **attrs)\n{\n\tint i, ret = 0;\n\n'+P+CR+RMw+'\treturn ret;\n}\n\n',
'p_num':'static int tiny2c_usb_init_sysfs(struct device *dev, struct device_attribute **attrs, int num)\n{\n\tint i, ret = 0;\n\n'+P+CRn+RM+'\treturn ret;\n}\n\n',
}
CALL={'p_attrs':'tiny2c_usb_init_sysfs(&pdev->dev, mt_sysfs_attributes)','p_attrs_w':'tiny2c_usb_init_sysfs(&pdev->dev, mt_sysfs_attributes)','p_num':'tiny2c_usb_init_sysfs(&pdev->dev, mt_sysfs_attributes, ARRAY_SIZE(mt_sysfs_attributes) - 1)'}
for k,v in V.items():
    t=s[:a]+v+s[b:]; t=t.replace('tiny2c_usb_init_sysfs(&pdev->dev)',CALL[k])
    print(k,score(t,'tiny2c_usb_probe',tag='w'),flush=True)
