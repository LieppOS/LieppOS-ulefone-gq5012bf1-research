#!/usr/bin/env python3
"""Generate the s5kgm2sp / s5kgn1sp sub-driver sources (GQ5012BF1 parity build).

No public source exists for either driver in this form.  Shared boiler-plate
(init_ctx, vsync_notify, *_seamless_switch, set_group_hold, test-pattern,
get_gain2reg, open) is byte-identical to the reconstructed s5kjn1 driver and
the source-backed imx989 driver; the sensor-init register list comes from
stock-imgsensor-oracle/inline/<v>_sensor_init.tsv (scripts/inline_writes.py)
and the vendor ID-probe / AWB functions were written from stock disassembly.

usage: mk_s5kgx.py <imx989mipiraw_Sensor.c> <init.tsv> <variant> <outdir>
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mk_s5kjn1 as J  # noqa: E402

VARIANTS = {
    "s5kgm2sp": dict(dphy="4", awb=False),
    "s5kgn1sp": dict(dphy="3", awb=True),
}


def get_id_gm2sp(v):
    return f"""static int get_imgsensor_id(struct subdrv_ctx *ctx, u32 *sensor_id)
{{
	u8 i = 0;
	u8 retry = 2;
	u32 addr_l = ctx->s_ctx.reg_addr_sensor_id.addr[1];
	u32 addr_h = ctx->s_ctx.reg_addr_sensor_id.addr[0];

	while (ctx->s_ctx.i2c_addr_table[i] != 0xFF) {{
		ctx->i2c_write_id = ctx->s_ctx.i2c_addr_table[i];
		do {{
			*sensor_id = (subdrv_i2c_rd_u8(ctx, addr_l) << 8) |
				subdrv_i2c_rd_u8(ctx, addr_h);
			printk("xqadd0 {v} i2c_write_id(0x%x) sensor_id(0x%x/0x%x)\\n",
				ctx->i2c_write_id, *sensor_id, ctx->s_ctx.sensor_id);
			if (*sensor_id == {v.upper()}_SENSOR_ID) {{
				*sensor_id = ctx->s_ctx.sensor_id;
				return ERROR_NONE;
			}}
			retry--;
		}} while (retry > 0);
		i++;
		retry = 2;
	}}
	if (*sensor_id != ctx->s_ctx.sensor_id) {{
		*sensor_id = 0xFFFFFFFF;
		return ERROR_SENSOR_CONNECT_FAIL;
	}}
	printk("xqadd0 {v} okss i2c_write_id(0x%x) sensor_id(0x%x/0x%x)\\n",
		ctx->i2c_write_id, *sensor_id, ctx->s_ctx.sensor_id);
	return ERROR_NONE;
}}

"""


def get_id_gn1sp(v):
    return f"""static int get_imgsensor_id(struct subdrv_ctx *ctx, u32 *sensor_id)
{{
	u8 i = 0;
	u8 retry = 2;
	u32 addr_h = ctx->s_ctx.reg_addr_sensor_id.addr[0];
	u32 addr_l = ctx->s_ctx.reg_addr_sensor_id.addr[1];

	DRV_LOG_MUST(ctx, "error: #######  cb {v}  get_imgsensor_id enter \\n");
	while (ctx->s_ctx.i2c_addr_table[i] != 0xFF) {{
		ctx->i2c_write_id = ctx->s_ctx.i2c_addr_table[i];
		do {{
			*sensor_id = (subdrv_i2c_rd_u8(ctx, addr_h) << 8) |
				subdrv_i2c_rd_u8(ctx, addr_l);
			DRV_LOG_MUST(ctx, "xqadd0 {v} i2c_write_id(0x%x) sensor_id(0x%x/0x%x)\\n",
				ctx->i2c_write_id, *sensor_id, ctx->s_ctx.sensor_id);
			DRV_LOG_MUST(ctx, "error: #######  cb {v} i2c_write_id(0x%x) sensor_id(0x%x/0x%x)\\n",
				ctx->i2c_write_id, *sensor_id, ctx->s_ctx.sensor_id);
			if (*sensor_id == {v.upper()}_SENSOR_ID) {{
				*sensor_id = ctx->s_ctx.sensor_id;
				return ERROR_NONE;
			}}
			retry--;
		}} while (retry > 0);
		i++;
		retry = 2;
	}}
	if (*sensor_id != ctx->s_ctx.sensor_id) {{
		*sensor_id = 0xFFFFFFFF;
		return ERROR_SENSOR_CONNECT_FAIL;
	}}
	DRV_LOG_MUST(ctx, "xqadd0 {v} okss i2c_write_id(0x%x) sensor_id(0x%x/0x%x)\\n",
		ctx->i2c_write_id, *sensor_id, ctx->s_ctx.sensor_id);
	DRV_LOG_MUST(ctx, "error: #######  cb {v}  get_imgsensor_id out \\n");
	return ERROR_NONE;
}}

"""


AWB = """static int {v}_awb_gain(struct subdrv_ctx *ctx, u8 *para, u32 *len)
{{
	struct SET_SENSOR_AWB_GAIN *pSetSensorAWB = (struct SET_SENSOR_AWB_GAIN *)para;
	u32 rgain_32, grgain_32, gbgain_32, bgain_32;

	grgain_32 = (pSetSensorAWB->ABS_GAIN_GR + 1) >> 1;
	rgain_32 = (pSetSensorAWB->ABS_GAIN_R + 1) >> 1;
	bgain_32 = (pSetSensorAWB->ABS_GAIN_B + 1) >> 1;
	gbgain_32 = (pSetSensorAWB->ABS_GAIN_GB + 1) >> 1;

	printk("ABS_GAIN_GR:%d, grgain_32:%d\\n, ABS_GAIN_R:%d, rgain_32:%d\\n, ABS_GAIN_B:%d, bgain_32:%d,ABS_GAIN_GB:%d, gbgain_32:%d\\n",
		pSetSensorAWB->ABS_GAIN_GR, grgain_32,
		pSetSensorAWB->ABS_GAIN_R, rgain_32,
		pSetSensorAWB->ABS_GAIN_B, bgain_32,
		pSetSensorAWB->ABS_GAIN_GB, gbgain_32);

	subdrv_i2c_wr_u16(ctx, 0x0D82, rgain_32);
	subdrv_i2c_wr_u16(ctx, 0x0D84, grgain_32);
	subdrv_i2c_wr_u16(ctx, 0x0D86, bgain_32);
	return ERROR_NONE;
}}

"""


def main():
    imx, tsv, v, out = sys.argv[1:5]
    cfg = VARIANTS[v]
    src = open(imx).read()
    head = src[:src.index('#include "imx989mipiraw_Sensor.h"')].replace("imx989", v)
    init = subprocess.run([sys.executable, os.path.join(J.SCRIPTS, "inline_to_c.py"), tsv],
                          capture_output=True, text=True, check=True).stdout.rstrip("\n")
    openf = J.grab(src, "open").replace("""	/* initail setting */
	sensor_init(ctx);

	if (ctx->s_ctx.s_cali != NULL)
		ctx->s_ctx.s_cali((void *) ctx);
	else
		write_sensor_Cali(ctx);
""", f"""	/* initail setting */
	{v}_sensor_init(ctx);
""")
    k = openf.index("\tif (ctx->s_ctx.mode[ctx->current_scenario_id].hdr_mode == HDR_RAW_LBMF)")
    openf = openf[:k].rstrip("\n") + "\n\n\treturn ERROR_NONE;\n}\n"
    jn1 = J.__dict__  # noqa: F841

    protos = ["static int get_imgsensor_id(struct subdrv_ctx *ctx, u32 *sensor_id);",
              "static int open(struct subdrv_ctx *ctx);",
              "static void set_group_hold(void *arg, u8 en);",
              "static u16 get_gain2reg(u32 gain);",
              f"static int {v}_seamless_switch(struct subdrv_ctx *ctx, u8 *para, u32 *len);",
              f"static int {v}_set_test_pattern(struct subdrv_ctx *ctx, u8 *para, u32 *len);",
              f"static int {v}_set_test_pattern_data(struct subdrv_ctx *ctx, u8 *para, u32 *len);"]
    if cfg["awb"]:
        protos.append(f"static int {v}_awb_gain(struct subdrv_ctx *ctx, u8 *para, u32 *len);")
    protos += [f"static void {v}_sensor_init(struct subdrv_ctx *ctx);",
               "static int init_ctx(struct subdrv_ctx *ctx,\tstruct i2c_client *i2c_client, u8 i2c_write_id);",
               "static int vsync_notify(struct subdrv_ctx *ctx,\tunsigned int sof_cnt);"]

    c = head + f'#include "{v}mipiraw_Sensor.h"\n\n' + "\n".join(protos) + "\n\n"
    c += "/* STOCK-PARITY data: regenerated byte-exact from the GQ5012BF1 stock module */\n"
    c += f'#ifdef GQ5012BF1_CAM_CORRECTED\n/* CORRECTED: mode/frame-descriptor geometry fixed (reconstruction/imgsensor/corrected/) */\n#include "{v}_corrected_data.h"\n#else\n#include "{v}_stock_data.h"\n#endif\n\n/* FUNCTION */\n\n'
    c += get_id_gn1sp(v) if v == "s5kgn1sp" else get_id_gm2sp(v)
    c += J.grab(src, "init_ctx") + "\n" + openf + "\n" + J.grab(src, "vsync_notify") + "\n"
    c += "static u16 get_gain2reg(u32 gain)\n{\n\treturn gain * 32 / BASEGAIN;\n}\n\n"
    c += J.grab(src, "set_group_hold") + "\n"
    # test pattern functions: same as s5kjn1 (u16 0x0600.. writes)
    jsrc = open(os.path.join(os.path.dirname(os.path.dirname(imx)), "s5kjn1_mipi_raw",
                             "s5kjn1mipiraw_Sensor.c")).read()
    c += J.grab(jsrc, "s5kjn1_set_test_pattern").replace("s5kjn1", v) + "\n"
    c += J.grab(jsrc, "s5kjn1_set_test_pattern_data").replace("s5kjn1", v) + "\n"
    c += J.grab(src, "imx989_seamless_switch").replace("imx989", v) + "\n"
    if cfg["awb"]:
        c += AWB.format(v=v)
    c += f"""static void {v}_sensor_init(struct subdrv_ctx *ctx)
{{
	DRV_LOG(ctx, "E\\n");
	DRV_LOG(ctx, "Dphy-{cfg['dphy']}lane setting\\n");
{init}
	DRV_LOG(ctx, "X\\n");
}}
"""
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, f"{v}mipiraw_Sensor.c"), "w").write(c)


if __name__ == "__main__":
    main()
