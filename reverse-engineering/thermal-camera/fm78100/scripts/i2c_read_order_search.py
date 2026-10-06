exec(open('/home/armol/kernel-work/gki-12901745-workspace/lieppos/thermal-fm78100/fast.py').read())
import random
HDR=''
full=open(W+'/yft_tiny2c_usb.B2.c').read(); a=full.index('int tiny2c_usb_i2c_read('); b=full.index('int tiny2c_usb_read_chipid(')
pre,post=full[:a],full[b:]
import sys
decl=sys.argv[1] if len(sys.argv)>1 else 'z'
D={'z':'\tu8 buf[2];\n\tstruct i2c_msg msg[2] = { };\n\tint ret;\n','n':'\tu8 buf[2];\n\tstruct i2c_msg msg[2];\n\tint ret;\n','r':'\tint ret;\n\tu8 buf[2];\n\tstruct i2c_msg msg[2];\n'}
hdr='int tiny2c_usb_i2c_read(struct i2c_client *client, u16 addr, u8 *data)\n{\n'+D[decl]+'\n\tif (!client)\n\t\treturn -ENODEV;\n'
tail='''
	ret = i2c_transfer(client->adapter, msg, 2);
	if (ret < 0) {
		dev_info(&client->dev, "i2c transfer failed (%d)\\n", ret);
		return ret;
	}
	*data = buf[0];
	return 0;
}

'''
S=['\tbuf[0] = addr >> 8;\n','\tbuf[1] = addr & 0xff;\n','\tmsg[0].addr = client->addr;\n','\tmsg[0].flags = client->flags;\n','\tmsg[0].len = 2;\n','\tmsg[0].buf = buf;\n','\tmsg[1].addr = client->addr;\n','\tmsg[1].flags = client->flags | I2C_M_RD;\n','\tmsg[1].len = 1;\n','\tmsg[1].buf = buf;\n']
cache={}
def ev(p):
    k=tuple(p)
    if k not in cache:
        cache[k]=score(pre+hdr+''.join(S[i] for i in p)+tail+post,'tiny2c_usb_i2c_read')
    return cache[k]
random.seed(int(sys.argv[2]) if len(sys.argv)>2 else 1)
best=None
for restart in range(4):
    p=list(range(10)); 
    if restart: random.shuffle(p)
    cur=ev(p); improved=True
    while improved and cur>0:
        improved=False
        for i in range(10):
            for j in range(10):
                if i==j: continue
                q=p[:]; x=q.pop(i); q.insert(j,x); s=ev(q)
                if s<cur: p,cur,improved=q,s,True; break
            if improved: break
    print(decl,'restart',restart,cur,p,flush=True)
    if best is None or cur<best[0]: best=(cur,p)
    if cur==0: break
print('BEST',best, 'evals',len(cache))
