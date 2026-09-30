/*
 * Reconstructed InfiRay/InfiSense AC020 API — GQ5012BF1 stock stack.
 * Documentation/specification only; not a drop-in vendor header.
 *
 * Tags:
 *   EXACT_SYMBOL                    exported symbol or Java name/value exists in stock
 *   RECONSTRUCTED_HIGH_CONFIDENCE   signature/layout follows stock JNI + independent trace
 *   RECONSTRUCTED_MEDIUM_CONFIDENCE plausible C ABI; native packing not verified
 *   INFERRED                        semantic inference
 *   UNKNOWN                         requires native decompilation/live passive capture
 */
#ifndef RECONSTRUCTED_AC020_API_H
#define RECONSTRUCTED_AC020_API_H
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct ircmd_handle ircmd_handle_t;       /* EXACT_SYMBOL opaque */
typedef struct ir_video_handle ir_video_handle_t; /* EXACT_SYMBOL opaque */
typedef struct ir_control_handle ir_control_handle_t;

typedef enum { /* EXACT Java CommonParams.DriverType */
    AC020_DRIVER_USB=0, AC020_DRIVER_SPI=1, AC020_DRIVER_MIPI_I2C=2,
    AC020_DRIVER_USB_DUAL=3, AC020_DRIVER_MIPI_I2C_DUAL=4,
    AC020_DRIVER_USB_DUAL_NATIVE_CAM=5, AC020_DRIVER_USB_OMNI=10
} ac020_driver_type_t;

typedef enum { /* EXACT Java CommonParams.FrameOutputFormat */
    AC020_FRAME_YUYV=0, AC020_FRAME_NV12=1,
    AC020_FRAME_NV12_AND_TEMP=2, AC020_FRAME_YUYV_AND_TEMP=3
} ac020_frame_output_t;

typedef enum { /* EXACT Java irutilslibrary.GainMode/GainStatus */
    AC020_GAIN_MODE_LOW=0, AC020_GAIN_MODE_HIGH=1, AC020_GAIN_MODE_HIGH_LOW=2
} ac020_gain_mode_t;
typedef enum { AC020_LOW_GAIN=0, AC020_HIGH_GAIN=1 } ac020_gain_status_t;

typedef enum { /* EXACT Java ProductType */
    AC020_PRODUCT_TC1B=0, AC020_PRODUCT_TC1C=1, AC020_PRODUCT_TC1BE=2,
    AC020_PRODUCT_WN256=3, AC020_PRODUCT_WN384=4, AC020_PRODUCT_WN640=5,
    AC020_PRODUCT_P2=6, AC020_PRODUCT_WN_ADVANCED=7
} ac020_product_type_t;

typedef enum { /* EXACT Java IRCMDType ordinal */
    AC020_IRCMD_USB_IR_256_384=0, AC020_IRCMD_SPI_IR_256_384=1,
    AC020_IRCMD_USB_WN_640_512=2, AC020_IRCMD_USB_WN_384_288=3,
    AC020_IRCMD_USB_WN_640_512_V2=4, AC020_IRCMD_USB_WN_384_288_V2=5
} ac020_ircmd_type_t;

typedef enum { /* EXACT Java CommonParams.AdvStreamSourceMode */
    AC020_SRC_IR=0, AC020_SRC_KBC=1, AC020_SRC_TNR=2,
    AC020_SRC_HBC_DPC=3, AC020_SRC_VBC=4, AC020_SRC_SNR=5,
    AC020_SRC_DDE=6, AC020_SRC_AGC=7, AC020_SRC_GAMMA=8,
    AC020_SRC_TPD=9, AC020_SRC_MIRROR=10, AC020_SRC_PICTURE=11
} ac020_stream_source_t;

typedef enum { AC020_FFC_AUTO_DISABLED=0, AC020_FFC_AUTO_ENABLED=1 } ac020_auto_ffc_t;
typedef enum { AC020_FFC_TEMP_THRESHOLD=0, AC020_FFC_MIN_INTERVAL=1,
               AC020_FFC_MAX_INTERVAL=2 } ac020_auto_ffc_param_t;
typedef enum { AC020_SHUTTER_CLOSED=0, AC020_SHUTTER_OPEN=1,
               AC020_SHUTTER_UNKNOWN=2 } ac020_shutter_status_t;
typedef enum { AC020_FFC_UPDATE_B=0, AC020_FFC_UPDATE_OOC=1,
               AC020_FFC_UPDATE_B_AND_OOC=2 } ac020_ffc_behavior_t;

typedef enum { /* EXACT Java DeviceStatus */
    AC020_STATE_STARTUP=0, AC020_STATE_PREVIEW=1, AC020_STATE_VIDEO_OUT=2,
    AC020_STATE_UPDATE=3, AC020_STATE_ERROR=4
} ac020_device_status_t;

typedef enum { /* EXACT Java UpgradeMode */
    AC020_UPGRADE_WHOLE_ZIP=0, AC020_UPGRADE_UPDATE_ZIP=1,
    AC020_UPGRADE_SINGLE_FIRMWARE=2, AC020_UPGRADE_SYSTEM_CONFIG=3
} ac020_upgrade_mode_t;

typedef enum { /* EXACT Java FirmwareUpgradeCode */
    AC020_UPGRADE_NONE=-2, AC020_UPGRADE_FAIL=-1, AC020_UPGRADE_INIT_OK=0,
    AC020_UPGRADE_INIT_FAIL=1, AC020_UPGRADE_RESET_ROM=2,
    AC020_UPGRADE_START_FW=3, AC020_UPGRADE_FINISH_FW=4,
    AC020_UPGRADE_START_ALL_DATA=5, AC020_UPGRADE_FINISH_ALL_DATA=6
} ac020_upgrade_status_t;

typedef enum { /* EXACT Java AdvSecondCalibFlagStatus */
    AC020_CAL_INVALID=-1, AC020_CAL_TEC_K=0, AC020_CAL_KT=1,
    AC020_CAL_BT=2, AC020_CAL_RMVC=3, AC020_CAL_NUC_T=4,
    AC020_CAL_DPC=5, AC020_CAL_MAX=6
} ac020_second_cal_flag_t;

/* Java ABI field names are EXACT; C width/packing is RECONSTRUCTED_MEDIUM_CONFIDENCE. */
typedef struct { int32_t EMS, TAU, Ta, Tu; } ac020_env_param_t;
typedef struct { int32_t K_E, B_E; } ac020_env_factor_t;
typedef struct { int32_t P0, P1, P2; } ac020_nuc_factor_t;
typedef struct { int32_t Kn, Bn; } ac020_cal_factor_t;
typedef struct { int32_t K, B; } ac020_recal_factor_t;
typedef struct { uint16_t width, height; } ac020_temp_resolution_t;
typedef struct { int32_t x, y; } ac020_point_t;
typedef struct {
    uint16_t min_temp, max_temp, avg_temp; /* 1/64 kelvin on classic path */
    ac020_point_t min_coord, max_coord;
} ac020_temp_info_t;

/* Exact conversion used by stock LibIRTemp. */
static inline float ac020_u16_to_celsius(uint16_t raw) {
    return (float)raw / 64.0f - 273.15f;
}

/* RECONSTRUCTED_HIGH_CONFIDENCE: combined classic frame. Actual shipping mode must be probed. */
typedef struct {
    const uint8_t *yuyv;       /* width * image_height * 2 */
    const uint16_t *temp_le;   /* width * image_height, 1/64 K */
    const uint8_t *meta_lines; /* optional two lines in 256x386 factory/SOP mode */
} ac020_combined_frame_view_t;

/* Donor-derived vdcmd wire layout, corroborated by OEM UVC immediates. */
enum {
    AC020_USB_REQ_OUT=0x41, AC020_USB_REQ_IN=0xC1,
    AC020_USB_BREQ_SET=0x45, AC020_USB_BREQ_GET=0x44,
    AC020_USB_WVALUE_VENDOR=0x78,
    AC020_VDCMD_STATUS=0x0200,
    AC020_VDCMD_STD_HEADER=0x1d00, AC020_VDCMD_STD_DATA=0x1d08,
    AC020_VDCMD_LONG_HEADER=0x9d00, AC020_VDCMD_LONG_DATA=0x9d08,
    AC020_VDCMD_LONG_RESULT=0x1d10,
    AC020_CMD_SET_BIT=0x4000
};
#pragma pack(push,1)
typedef struct { uint16_t command_le; uint32_t parameter_be; uint16_t length_be; }
    ac020_vdcmd_std_header_t; /* HIGH_CONFIDENCE donor; verify on Armor */
typedef struct { uint16_t command_le; uint16_t p1_be; uint32_t p2_be; }
    ac020_vdcmd_long_header_t;
#pragma pack(pop)

/* Donor Mini/P2-family opcodes; INFERRED for this AC020 firmware until captured. */
enum {
    AC020_CMD_SYS_RESET_TO_ROM=0x0805, AC020_CMD_SPI_TRANSFER=0x8201,
    AC020_CMD_GET_DEVICE_INFO=0x8405, AC020_CMD_PSEUDO_COLOR=0x8409,
    AC020_CMD_SHUTTER_VTEMP=0x840c, AC020_CMD_PROP_TPD_PARAMS=0x8514,
    AC020_CMD_CURRENT_VTEMP=0x8b0d, AC020_CMD_Y16_PREVIEW_START=0x010a,
    AC020_CMD_PREVIEW_START=0xc10f, AC020_CMD_PREVIEW_STOP=0x020f
};

/* EXACT_SYMBOL names. Parameters are intentionally opaque where ABI was not proven. */
ircmd_handle_t *ircmd_create_handle(void *driver_handle, ...); /* MEDIUM */
void ircmd_delete_handle(ircmd_handle_t *);                    /* MEDIUM */
int vdcmd_set_polling_wait_time(ircmd_handle_t *, uint32_t);   /* MEDIUM */
int standard_cmd_read(ircmd_handle_t *, ...);                  /* UNKNOWN prototype */
int standard_cmd_write(ircmd_handle_t *, ...);
int standard_cmd_write_without_read_return_status(ircmd_handle_t *, ...);
int long_cmd_read(ircmd_handle_t *, ...);
int long_cmd_write(ircmd_handle_t *, ...);

/* EXACT_SYMBOL semantic surface; signatures represented by stock JNI Java ABI. */
int adv_manual_ffc_switch_set(ircmd_handle_t *, int status, ...);
int adv_manual_ffc_switch_get(ircmd_handle_t *, int *status, ...);
int adv_manual_ffc_update(ircmd_handle_t *, ...);
int basic_auto_ffc_status_get(ircmd_handle_t *, int *status, ...);
int basic_auto_ffc_status_set(ircmd_handle_t *, int status, ...);
int basic_all_ffc_function_status_get(ircmd_handle_t *, int *status, ...);
int adv_edge_enhance_get(ircmd_handle_t *, int *level, ...);
int adv_edge_enhance_set(ircmd_handle_t *, int level, ...);
int adv_device_realtime_status_get(ircmd_handle_t *, int type, int *value, ...);
int adv_algorithm_parameters_read(ircmd_handle_t *, int type, int *values, ...);
int adv_algorithm_parameters_write(ircmd_handle_t *, int type, const int *values, ...);
int adv_dpc_calib_data_clear(ircmd_handle_t *, ...); /* destructive */
int adv_rmcover_calib_clear(ircmd_handle_t *, ...); /* destructive */

/* Exact native radiometry symbols; pointer types reconstructed from Java nested classes. */
int calculate_tau(uint8_t a, uint8_t b, uint8_t c, uint8_t d);
int calculate_nuc_with_nuc_factor(const ac020_nuc_factor_t *, float, int32_t *out);
int calculate_KE_and_BE(const ac020_env_param_t *, const ac020_nuc_factor_t *,
                        int32_t, ac020_env_factor_t *out);
int get_point_temp(const uint8_t *plane, const ac020_temp_resolution_t *,
                   const ac020_point_t *, uint16_t *raw_out);
int temp_correct(float input, int mode, float emissivity, float distance, float *out);

/* Java-facing WN V2 rule: both NUC arrays MUST have 8192 int16 entries. */
int64_t get_tempinfo_wn640_v2(int gain_mode, int gain_status,
    const int16_t nuc_high[8192], const int16_t nuc_low[8192],
    int p0, int p1, int p2);

/* File identifiers are exact module-relative paths. */
#define AC020_FILE_USER_EEPROM "user_data/user_eeprom_data.bin"
#define AC020_FILE_SYSTEM_CFG "system_cfg.bin"
#define AC020_FILE_DEFAULT_CFG "default_cfg.bin"
#define AC020_FILE_SECOND_CAL_STATUS "secd_cali_data/manufacturer_temporary_data.bin"
#define AC020_FILE_KT_HIGH "secd_cali_data/high_gain/tpd_kt1.bin"
#define AC020_FILE_KT_LOW "secd_cali_data/low_gain/tpd_kt1.bin"
#define AC020_FILE_BT_HIGH "secd_cali_data/high_gain/tpd_bt1.bin"
#define AC020_FILE_BT_LOW "secd_cali_data/low_gain/tpd_bt1.bin"
#define AC020_FILE_NUCT_HIGH "secd_cali_data/high_gain/tpd_nuc_t.bin"
#define AC020_FILE_NUCT_LOW "secd_cali_data/low_gain/tpd_nuc_t.bin"

/* Safe default policy: allow open/stream/read/measurement; deny these outside expert mode. */
#define AC020_UNSAFE_ROM_ENTRY       0x0001u
#define AC020_UNSAFE_FIRMWARE_WRITE  0x0002u
#define AC020_UNSAFE_FLASH_RAW       0x0004u
#define AC020_UNSAFE_CALIB_WRITE     0x0008u
#define AC020_UNSAFE_CALIB_CLEAR     0x0010u
#define AC020_UNSAFE_FORCED_SHUTTER  0x0020u

#ifdef __cplusplus
}
#endif
#endif
