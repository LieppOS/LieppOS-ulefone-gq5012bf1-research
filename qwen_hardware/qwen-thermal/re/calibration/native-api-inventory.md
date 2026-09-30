# Native radiometry / calibration / ISP API inventory (AC020 stack, arm64)

Source: `nm -D --defined-only\| c++filt` per-library exports (see evidence/binaries/symbols/).

## libadvirtempac020
_143 exports_

advanced_ktbt_recal_double_point_calculate
advanced_ktbt_recal_double_point_calculate_version3
advanced_ktbt_recal_double_point_calculate_with_version
calc_env_factor_with_dist_and_env_temp
calculate_coef
calculate_KE_and_BE
calculate_Kn_and_Bn
calculate_ktbt_index_according_vtemp_in_change_lens
calculate_new_KE_and_BE
calculate_new_KE_and_BE_with_nuc_t
calculate_new_value_index_in_orgtable
calculate_nuc_with_nuc_factor
calculate_org_KE_and_BE_with_nuc_t
calculate_tau
calculate_vapor_pressure
distance_calculate
dist_table
dist_table_v3
double_point_recalibrate_KB
ems_correct_table_v1
ems_correct_table_v2
enhance_distance_temp_correct
env_temp_calculate
find_start_and_end_addr
generate_distance_table
generate_high_gain_nuc_t
generate_low_gain_nuc_t
generate_new_distance_table
get_array_average_value
get_compatible_dist_read_index
get_compatible_ems_read_index_of_ems_table
get_compatible_target_temp_read_index
get_compatible_target_temp_read_index_of_ems_table
get_dist_read_index
get_dist_write_index
get_horz_line_temp
get_hum_index
get_irtemp_ac020_version(_JNIEnv*, _jclass*)
get_line_temp
get_NUC_value
get_pixel_horz_neighb_array
get_pixel_slope_neighb_array
get_pixel_square_array
get_pixel_vert_neighb_array
get_point_num
get_point_set
get_point_temp
get_rect_temp
get_slope
get_slope_line_temp
get_target_temp_read_index
get_target_temp_write_index
get_temp_read_index
get_temp_write_index
get_vert_line_temp
hotmode_calc
hotmode_reverse
irtemp_debug_info
irtemp_debug_print
irtemp_debug_void
irtemp_error_info
irtemp_error_print
irtemp_error_void
irtemp_log_register
irtemp_version
_JavaVM::GetEnv(void**, int)
_JNIEnv::FindClass(char const*)
_JNIEnv::GetByteArrayElements(_jbyteArray*, unsigned char*)
_JNIEnv::NewStringUTF(char const*)
_JNIEnv::RegisterNatives(_jclass*, JNINativeMethod const*, int)
_JNIEnv::ReleaseByteArrayElements(_jbyteArray*, signed char*, int)
JNI_OnLoad
KcBc_KdBd_calculate
ktbt_correct_process
ktbt_correct_process_with_version3
LinearInterp
line_rect_over_threshold_alarm
multi_point_calc_new_kt_bt
multi_point_calc_new_kt_bt_intermediate_param
multi_point_calc_new_nuc_table
multi_point_calc_new_nuc_table_in_change_lens
multi_point_calc_new_nuc_table_with_version
multi_point_calc_new_nuc_table_with_version3
multi_point_calc_one_point_correct
multi_point_calc_user_defined_nuc
multi_point_calc_user_defined_nuc_in_change_lens
multi_point_calc_user_defined_nuc_with_version
multi_point_calc_user_defined_nuc_with_version1
multi_point_calc_user_defined_nuc_with_version2
multi_point_calc_user_defined_nuc_with_version3
nativeMethods
new_distance_calculate
new_dist_table
new_ktbt_recal_double_point_calculate
new_ktbt_recal_double_point_calculate_in_change_lens
new_ktbt_recal_double_point_calculate_with_version
new_kt_bt_table_interpolate
new_target_temp_table
ordinary_least_squares
org_ems_list_of_ems_table_v1
org_ems_list_of_ems_table_v2
point_over_threshold_alarm
read_compatible_ems_version1
read_compatible_ems_version2
read_compatible_ems_version3
read_compatible_ems_with_target_temp_and_org_ems
read_compatible_tau_with_target_temp_and_dist
read_tau
read_tau_with_target_temp_and_dist
recalc_NUC_with_env_correct
recalc_tau
recalc_tau_under_influence_of_hum
recalc_tau_with_hum_version
registerNativeMethod(_JNIEnv*)
remap_temp
reverse_calc_NUC_with_env_correct
reverse_calc_NUC_with_nuc_t
reverse_calc_NUC_with_nuc_t_table_len
reverse_calc_NUC_without_env_correct
reverse_enhance_distance_temp_correct
reverse_ktbt_correct
reverse_ktbt_correct_with_version3
reverse_temp_correct
reverse_temp_correct_with_env_param
reverse_temp_correct_with_reflected_temp
select_pixel
single_point_recalibrate_KB
sort_multi_point_kt
sort_multi_point_nuc
target_temp_list_of_ems_table_v1
target_temp_list_of_ems_table_v2
target_temp_table
target_temp_table_v3
tau_data_read
tau_data_write
temp_correct
temp_correction_with_new_method(_JNIEnv*, _jclass*, float, _jbyteArray*, float, float, float, float, float)
temp_correct_with_env_param
temp_correct_with_reflected_temp
temp_measure_with_NUC_value
temp_table
write_tau
write_tau_with_target_temp_and_dist

## libadvirtemp
_152 exports_

advanced_ktbt_recal_double_point_calculate
calc_env_factor_with_dist_and_env_temp
calculate_coef
calculate_KE_and_BE
calculate_Kn_and_Bn
calculate_new_KE_and_BE
calculate_new_KE_and_BE_with_nuc_t
calculate_nuc_with_nuc_factor
calculate_org_KE_and_BE_with_nuc_t
calculate_tau
calculate_vapor_pressure
distance_calculate
dist_squre
dist_table
dist_table_v3
double_point_recalibrate_KB
ems_correct_table_v1
ems_correct_table_v2
enhance_distance_temp_correct
env_temp_calculate
find_start_and_end_addr
generate_distance_table
generate_high_gain_nuc_t
generate_low_gain_nuc_t
generate_new_distance_table
get_array_average_value
get_circle_temp
get_compatible_dist_read_index
get_compatible_ems_read_index_of_ems_table
get_compatible_target_temp_read_index
get_compatible_target_temp_read_index_of_ems_table
get_dist_read_index
get_dist_write_index
get_horz_line_temp
get_hum_index
get_line_temp
get_NUC_value
get_pixel_horz_neighb_array
get_pixel_slope_neighb_array
get_pixel_square_array
get_pixel_vert_neighb_array
get_point_num
get_point_set
get_point_temp
get_rect_temp
get_rect_temp_consistent
get_side_length
get_slope
get_slope_line_temp
get_target_temp_read_index
get_target_temp_write_index
get_temp_read_index
get_temp_write_index
get_vert_line_temp
global_first
hotmode_calc
hotmode_reverse
irtemp_debug_info
irtemp_debug_print
irtemp_debug_void
irtemp_error_info
irtemp_error_print
irtemp_error_void
irtemp_log_register
irtemp_version
Java_com_energy_irutilslibrary_LibIRTemp_calculate_1KE_1and_1BE
Java_com_energy_irutilslibrary_LibIRTemp_calculate_1Kn_1and_1Bn
Java_com_energy_irutilslibrary_LibIRTemp_calculate_1new_1KE_1and_1BE
Java_com_energy_irutilslibrary_LibIRTemp_calculate_1new_1KE_1and_1BE_1with_1nuc_1t
Java_com_energy_irutilslibrary_LibIRTemp_calculate_1nuc_1with_1nuc_1factor
Java_com_energy_irutilslibrary_LibIRTemp_calculate_1org_1KE_1and_1BE_1with_1nuc_1t
Java_com_energy_irutilslibrary_LibIRTemp_calculate_1tau
Java_com_energy_irutilslibrary_LibIRTemp_double_1point_1recalibrate_1KB
Java_com_energy_irutilslibrary_LibIRTemp_env_1temp_1calculate
Java_com_energy_irutilslibrary_LibIRTemp_find_1start_1and_1end_1addr
Java_com_energy_irutilslibrary_LibIRTemp_get_1circle_1temp
Java_com_energy_irutilslibrary_LibIRTemp_get_1line_1temp
Java_com_energy_irutilslibrary_LibIRTemp_get_1NUC_1value
Java_com_energy_irutilslibrary_LibIRTemp_get_1point_1temp
Java_com_energy_irutilslibrary_LibIRTemp_get_1rect_1temp
Java_com_energy_irutilslibrary_LibIRTemp_get_1side_1length
Java_com_energy_irutilslibrary_LibIRTemp_irtemp_1log_1register
Java_com_energy_irutilslibrary_LibIRTemp_irtemp_1version
Java_com_energy_irutilslibrary_LibIRTemp_line_1rect_1over_1threshold_1alarm
Java_com_energy_irutilslibrary_LibIRTemp_point_1over_1threshold_1alarm
Java_com_energy_irutilslibrary_LibIRTemp_read_1tau
Java_com_energy_irutilslibrary_LibIRTemp_read_1tau_1with_1target_1temp_1and_1dist
Java_com_energy_irutilslibrary_LibIRTemp_recalc_1NUC_1with_1env_1correct
Java_com_energy_irutilslibrary_LibIRTemp_remap_1temp
Java_com_energy_irutilslibrary_LibIRTemp_reverse_1calc_1NUC_1with_1env_1correct
Java_com_energy_irutilslibrary_LibIRTemp_reverse_1calc_1NUC_1with_1nuc_1t
Java_com_energy_irutilslibrary_LibIRTemp_reverse_1calc_1NUC_1without_1env_1correct
Java_com_energy_irutilslibrary_LibIRTemp_reverse_1enhance_1distance_1temp_1correct
Java_com_energy_irutilslibrary_LibIRTemp_reverse_1temp_1correct
Java_com_energy_irutilslibrary_LibIRTemp_set_1side_1length
Java_com_energy_irutilslibrary_LibIRTemp_single_1point_1recalibrate_1KB
Java_com_energy_irutilslibrary_LibIRTemp_temp_1correct
Java_com_energy_irutilslibrary_LibIRTemp_write_1tau
ktbt_correct_process
lastTempInfo
LinearInterp
line_rect_over_threshold_alarm
mSideLength
multi_point_calc_new_nuc_table
multi_point_calc_one_point_correct
multi_point_calc_user_defined_nuc
new_distance_calculate
new_dist_table
new_ktbt_recal_double_point_calculate
new_target_temp_table
org_ems_list_of_ems_table_v1
org_ems_list_of_ems_table_v2
point_over_threshold_alarm
read_compatible_ems_version1
read_compatible_ems_version2
read_compatible_ems_version3
read_compatible_ems_with_target_temp_and_org_ems
read_compatible_tau_with_target_temp_and_dist
read_tau
read_tau_with_target_temp_and_dist
recalc_NUC_with_env_correct
recalc_tau
recalc_tau_under_influence_of_hum
recalc_tau_with_hum_version1
remap_temp
returnstates
reverse_calc_NUC_with_env_correct
reverse_calc_NUC_with_nuc_t
reverse_calc_NUC_without_env_correct
reverse_enhance_distance_temp_correct
reverse_ktbt_correct
reverse_temp_correct
reverse_temp_correct_with_env_param
reverse_temp_correct_with_reflected_temp
select_pixel
set_side_length
setTempInfo
single_point_recalibrate_KB
sort_multi_point_nuc
target_temp_list_of_ems_table_v1
target_temp_list_of_ems_table_v2
target_temp_table
target_temp_table_v3
tau_data_read
tau_data_write
temp_correct
temp_correct_with_env_param
temp_correct_with_reflected_temp
temp_measure_with_NUC_value
temp_table
write_tau
write_tau_with_target_temp_and_dist

## libcommonsdk
_2 exports_

_edata
_end

## libdualcalibration
_627 exports_

_bss_end__
callstackDump()
callstackLogcat(char const*)
construction vtable for std::__ndk1::basic_istream<char, std::__ndk1::char_traits<char> >-in-std::__ndk1::basic_iostream<char, std::__ndk1::char_traits<char> >
construction vtable for std::__ndk1::basic_ostream<char, std::__ndk1::char_traits<char> >-in-std::__ndk1::basic_iostream<char, std::__ndk1::char_traits<char> >
.data.rel.ro
dual_cal_camera::~dual_cal_camera()
dual_cal_camera::dual_cal_camera()
dual_cal_camera::dual_calibration_camera_fixed()
dual_cal_camera::dual_calibration_get_data(unsigned char*)
dual_cal_camera::dual_calibration_next_pos()
dual_cal_camera::dual_calibration_recog_analysed()
dual_cal_camera::dual_calibration_reset(int)
dual_cal_camera::dual_calibration_save_data(int, unsigned char*)
dual_cal_camera::dual_calibration_start(int, int, double, int, bool, double, bool, double, double)
dual_cal_camera::dual_calibration_version(char*)
dual_cal_camera::get_dual_calib_save_data(int, unsigned char*)
dual_cal_camera::get_dual_cal_progress()
dual_cal_camera::init_dual_calib_camera(int, int, int, int)
dual_cal_camera::proc_calib_frames(unsigned char*, unsigned int*, unsigned char*, unsigned int*, unsigned char*)
dual_cal_camera::save_dual_calib_data(unsigned char*)
dual_calib_running
dual_calib_save_data
dual_calib_save_data_size
dual_debug_info
dual_debug_print
dual_debug_void
dual_error_info
dual_error_print
dual_error_void
dual_log_register
_edata
_end
handler(int)
JNI_OnLoad
long long std::__ndk1::__num_get_signed_integral<long long>(char const*, char const*, unsigned int&, int)
long std::__ndk1::__num_get_signed_integral<long>(char const*, char const*, unsigned int&, int)
non-virtual thunk to std::__ndk1::basic_iostream<char, std::__ndk1::char_traits<char> >::~basic_iostream()
operator delete(void*)
operator delete[](void*)
operator delete(void*, std::align_val_t)
operator delete[](void*, std::align_val_t)
operator delete(void*, std::align_val_t, std::nothrow_t const&)
operator delete[](void*, std::align_val_t, std::nothrow_t const&)
operator delete(void*, std::nothrow_t const&)
operator delete[](void*, std::nothrow_t const&)
operator delete(void*, unsigned long)
operator delete[](void*, unsigned long)
operator delete(void*, unsigned long, std::align_val_t)
operator delete[](void*, unsigned long, std::align_val_t)
operator new(unsigned long)
operator new[](unsigned long)
operator new(unsigned long, std::align_val_t)
operator new[](unsigned long, std::align_val_t)
operator new(unsigned long, std::align_val_t, std::nothrow_t const&)
operator new[](unsigned long, std::align_val_t, std::nothrow_t const&)
operator new(unsigned long, std::nothrow_t const&)
operator new[](unsigned long, std::nothrow_t const&)
register_dual_cal_camera(_JNIEnv*)
registerNativeMethods(_JNIEnv*, char const*, JNINativeMethod*, int)
savevm
.text
typeinfo for bool
typeinfo for bool*
typeinfo for bool const*
typeinfo for char
typeinfo for char*
typeinfo for char16_t
typeinfo for char16_t*
typeinfo for char16_t const*
typeinfo for char32_t
typeinfo for char32_t*
typeinfo for char32_t const*
typeinfo for char8_t
typeinfo for char8_t*
typeinfo for char8_t const*
typeinfo for char const*
typeinfo for __cxxabiv1::__array_type_info
typeinfo for __cxxabiv1::__class_type_info
typeinfo for __cxxabiv1::__enum_type_info
typeinfo for __cxxabiv1::__function_type_info
typeinfo for __cxxabiv1::__fundamental_type_info
typeinfo for __cxxabiv1::__pbase_type_info
typeinfo for __cxxabiv1::__pointer_to_member_type_info
typeinfo for __cxxabiv1::__pointer_type_info
typeinfo for __cxxabiv1::__shim_type_info
typeinfo for __cxxabiv1::__si_class_type_info
typeinfo for __cxxabiv1::__vmi_class_type_info
typeinfo for decltype(nullptr)
typeinfo for decltype(nullptr)*
typeinfo for decltype(nullptr) const*
typeinfo for double
typeinfo for double*
typeinfo for double const*
typeinfo for float
typeinfo for float*
typeinfo for __float128
typeinfo for __float128*
typeinfo for __float128 const*
typeinfo for float const*
typeinfo for half
typeinfo for half*
typeinfo for half const*
typeinfo for int
typeinfo for int*
typeinfo for __int128
typeinfo for __int128*
typeinfo for __int128 const*
typeinfo for int const*
typeinfo for long
typeinfo for long*
typeinfo for long const*
typeinfo for long double
typeinfo for long double*
typeinfo for long double const*
typeinfo for long long
typeinfo for long long*
typeinfo for long long const*
typeinfo for short
typeinfo for short*
typeinfo for short const*
typeinfo for signed char
typeinfo for signed char*
typeinfo for signed char const*
typeinfo for std::bad_alloc
typeinfo for std::bad_array_length
typeinfo for std::bad_array_new_length
typeinfo for std::bad_cast
typeinfo for std::bad_exception
typeinfo for std::bad_typeid
typeinfo for std::domain_error
typeinfo for std::exception
typeinfo for std::invalid_argument
typeinfo for std::length_error
typeinfo for std::logic_error
typeinfo for std::__ndk1::__assoc_sub_state
typeinfo for std::__ndk1::bad_weak_ptr
typeinfo for std::__ndk1::basic_ios<char, std::__ndk1::char_traits<char> >
typeinfo for std::__ndk1::basic_iostream<char, std::__ndk1::char_traits<char> >
typeinfo for std::__ndk1::basic_ios<wchar_t, std::__ndk1::char_traits<wchar_t> >
typeinfo for std::__ndk1::basic_istream<char, std::__ndk1::char_traits<char> >
typeinfo for std::__ndk1::basic_istream<wchar_t, std::__ndk1::char_traits<wchar_t> >
typeinfo for std::__ndk1::basic_ostream<char, std::__ndk1::char_traits<char> >
typeinfo for std::__ndk1::basic_ostream<wchar_t, std::__ndk1::char_traits<wchar_t> >
typeinfo for std::__ndk1::basic_streambuf<char, std::__ndk1::char_traits<char> >
typeinfo for std::__ndk1::basic_streambuf<wchar_t, std::__ndk1::char_traits<wchar_t> >
typeinfo for std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> >
typeinfo for std::__ndk1::__basic_string_common<true>
typeinfo for std::__ndk1::codecvt_base
typeinfo for std::__ndk1::codecvt_byname<char16_t, char, mbstate_t>
typeinfo for std::__ndk1::codecvt_byname<char32_t, char, mbstate_t>
typeinfo for std::__ndk1::codecvt_byname<char, char, mbstate_t>
typeinfo for std::__ndk1::codecvt_byname<wchar_t, char, mbstate_t>
typeinfo for std::__ndk1::codecvt<char16_t, char, mbstate_t>
typeinfo for std::__ndk1::codecvt<char32_t, char, mbstate_t>
typeinfo for std::__ndk1::codecvt<char, char, mbstate_t>
typeinfo for std::__ndk1::__codecvt_utf16<char16_t, false>
typeinfo for std::__ndk1::__codecvt_utf16<char16_t, true>
typeinfo for std::__ndk1::__codecvt_utf16<char32_t, false>
typeinfo for std::__ndk1::__codecvt_utf16<char32_t, true>
typeinfo for std::__ndk1::__codecvt_utf16<wchar_t, false>
typeinfo for std::__ndk1::__codecvt_utf16<wchar_t, true>
typeinfo for std::__ndk1::__codecvt_utf8<char16_t>
typeinfo for std::__ndk1::__codecvt_utf8<char32_t>
typeinfo for std::__ndk1::__codecvt_utf8_utf16<char16_t>
typeinfo for std::__ndk1::__codecvt_utf8_utf16<char32_t>
typeinfo for std::__ndk1::__codecvt_utf8_utf16<wchar_t>
typeinfo for std::__ndk1::__codecvt_utf8<wchar_t>
typeinfo for std::__ndk1::codecvt<wchar_t, char, mbstate_t>
typeinfo for std::__ndk1::collate_byname<char>
typeinfo for std::__ndk1::collate_byname<wchar_t>
typeinfo for std::__ndk1::collate<char>
typeinfo for std::__ndk1::collate<wchar_t>
typeinfo for std::__ndk1::ctype_base
typeinfo for std::__ndk1::ctype_byname<char>
typeinfo for std::__ndk1::ctype_byname<wchar_t>
typeinfo for std::__ndk1::ctype<char>
typeinfo for std::__ndk1::ctype<wchar_t>
typeinfo for std::__ndk1::error_category
typeinfo for std::__ndk1::future_error
typeinfo for std::__ndk1::ios_base
typeinfo for std::__ndk1::ios_base::failure
typeinfo for std::__ndk1::locale::facet
typeinfo for std::__ndk1::messages_base
typeinfo for std::__ndk1::messages_byname<char>
typeinfo for std::__ndk1::messages_byname<wchar_t>
typeinfo for std::__ndk1::messages<char>
typeinfo for std::__ndk1::messages<wchar_t>
typeinfo for std::__ndk1::money_base
typeinfo for std::__ndk1::__money_get<char>
typeinfo for std::__ndk1::money_get<char, std::__ndk1::istreambuf_iterator<char, std::__ndk1::char_traits<char> > >
typeinfo for std::__ndk1::__money_get<wchar_t>
typeinfo for std::__ndk1::money_get<wchar_t, std::__ndk1::istreambuf_iterator<wchar_t, std::__ndk1::char_traits<wchar_t> > >
typeinfo for std::__ndk1::moneypunct_byname<char, false>
typeinfo for std::__ndk1::moneypunct_byname<char, true>
typeinfo for std::__ndk1::moneypunct_byname<wchar_t, false>
typeinfo for std::__ndk1::moneypunct_byname<wchar_t, true>
typeinfo for std::__ndk1::moneypunct<char, false>
typeinfo for std::__ndk1::moneypunct<char, true>
typeinfo for std::__ndk1::moneypunct<wchar_t, false>
typeinfo for std::__ndk1::moneypunct<wchar_t, true>
typeinfo for std::__ndk1::__money_put<char>
typeinfo for std::__ndk1::money_put<char, std::__ndk1::ostreambuf_iterator<char, std::__ndk1::char_traits<char> > >
typeinfo for std::__ndk1::__money_put<wchar_t>
typeinfo for std::__ndk1::money_put<wchar_t, std::__ndk1::ostreambuf_iterator<wchar_t, std::__ndk1::char_traits<wchar_t> > >
typeinfo for std::__ndk1::__narrow_to_utf8<16ul>
typeinfo for std::__ndk1::__narrow_to_utf8<32ul>
typeinfo for std::__ndk1::__num_get_base
typeinfo for std::__ndk1::__num_get<char>
typeinfo for std::__ndk1::num_get<char, std::__ndk1::istreambuf_iterator<char, std::__ndk1::char_traits<char> > >
typeinfo for std::__ndk1::__num_get<wchar_t>
typeinfo for std::__ndk1::num_get<wchar_t, std::__ndk1::istreambuf_iterator<wchar_t, std::__ndk1::char_traits<wchar_t> > >
typeinfo for std::__ndk1::numpunct_byname<char>
typeinfo for std::__ndk1::numpunct_byname<wchar_t>
typeinfo for std::__ndk1::numpunct<char>
typeinfo for std::__ndk1::numpunct<wchar_t>
typeinfo for std::__ndk1::__num_put_base
typeinfo for std::__ndk1::__num_put<char>
typeinfo for std::__ndk1::num_put<char, std::__ndk1::ostreambuf_iterator<char, std::__ndk1::char_traits<char> > >
typeinfo for std::__ndk1::__num_put<wchar_t>
typeinfo for std::__ndk1::num_put<wchar_t, std::__ndk1::ostreambuf_iterator<wchar_t, std::__ndk1::char_traits<wchar_t> > >
typeinfo for std::__ndk1::__shared_count
typeinfo for std::__ndk1::__shared_weak_count
typeinfo for std::__ndk1::system_error
typeinfo for std::__ndk1::time_base
typeinfo for std::__ndk1::__time_get
typeinfo for std::__ndk1::time_get_byname<char, std::__ndk1::istreambuf_iterator<char, std::__ndk1::char_traits<char> > >
typeinfo for std::__ndk1::time_get_byname<wchar_t, std::__ndk1::istreambuf_iterator<wchar_t, std::__ndk1::char_traits<wchar_t> > >
typeinfo for std::__ndk1::time_get<char, std::__ndk1::istreambuf_iterator<char, std::__ndk1::char_traits<char> > >
typeinfo for std::__ndk1::__time_get_c_storage<char>
typeinfo for std::__ndk1::__time_get_c_storage<wchar_t>
typeinfo for std::__ndk1::__time_get_storage<char>
typeinfo for std::__ndk1::__time_get_storage<wchar_t>
typeinfo for std::__ndk1::time_get<wchar_t, std::__ndk1::istreambuf_iterator<wchar_t, std::__ndk1::char_traits<wchar_t> > >
typeinfo for std::__ndk1::__time_put
typeinfo for std::__ndk1::time_put_byname<char, std::__ndk1::ostreambuf_iterator<char, std::__ndk1::char_traits<char> > >
typeinfo for std::__ndk1::time_put_byname<wchar_t, std::__ndk1::ostreambuf_iterator<wchar_t, std::__ndk1::char_traits<wchar_t> > >
typeinfo for std::__ndk1::time_put<char, std::__ndk1::ostreambuf_iterator<char, std::__ndk1::char_traits<char> > >
typeinfo for std::__ndk1::time_put<wchar_t, std::__ndk1::ostreambuf_iterator<wchar_t, std::__ndk1::char_traits<wchar_t> > >
typeinfo for std::__ndk1::__widen_from_utf8<16ul>
typeinfo for std::__ndk1::__widen_from_utf8<32ul>
typeinfo for std::nested_exception
typeinfo for std::out_of_range
typeinfo for std::overflow_error
typeinfo for std::range_error
typeinfo for std::runtime_error
typeinfo for std::type_info
typeinfo for std::underflow_error
typeinfo for unsigned char
typeinfo for unsigned char*
typeinfo for unsigned char const*
typeinfo for unsigned int
typeinfo for unsigned int*
typeinfo for unsigned __int128
typeinfo for unsigned __int128*
typeinfo for unsigned __int128 const*
typeinfo for unsigned int const*
typeinfo for unsigned long
typeinfo for unsigned long*
typeinfo for unsigned long const*
typeinfo for unsigned long long
typeinfo for unsigned long long*
typeinfo for unsigned long long const*
typeinfo for unsigned short
typeinfo for unsigned short*
typeinfo for unsigned short const*
typeinfo for void
typeinfo for void*
typeinfo for void const*
typeinfo for wchar_t
typeinfo for wchar_t*
typeinfo for wchar_t const*
typeinfo name for bool
typeinfo name for bool*
typeinfo name for bool const*
typeinfo name for char
typeinfo name for char*
typeinfo name for char16_t
typeinfo name for char16_t*
typeinfo name for char16_t const*
typeinfo name for char32_t
typeinfo name for char32_t*
typeinfo name for char32_t const*
typeinfo name for char8_t
typeinfo name for char8_t*
typeinfo name for char8_t const*
typeinfo name for char const*
typeinfo name for __cxxabiv1::__array_type_info
typeinfo name for __cxxabiv1::__class_type_info
typeinfo name for __cxxabiv1::__enum_type_info
typeinfo name for __cxxabiv1::__function_type_info
typeinfo name for __cxxabiv1::__fundamental_type_info
typeinfo name for __cxxabiv1::__pbase_type_info
typeinfo name for __cxxabiv1::__pointer_to_member_type_info
typeinfo name for __cxxabiv1::__pointer_type_info
typeinfo name for __cxxabiv1::__shim_type_info
typeinfo name for __cxxabiv1::__si_class_type_info
typeinfo name for __cxxabiv1::__vmi_class_type_info
typeinfo name for decltype(nullptr)
typeinfo name for decltype(nullptr)*
typeinfo name for decltype(nullptr) const*
typeinfo name for double
typeinfo name for double*
typeinfo name for double const*
typeinfo name for float
typeinfo name for float*
typeinfo name for __float128
typeinfo name for __float128*
typeinfo name for __float128 const*
typeinfo name for float const*
typeinfo name for half
typeinfo name for half*
typeinfo name for half const*
typeinfo name for int
typeinfo name for int*
typeinfo name for __int128
typeinfo name for __int128*
typeinfo name for __int128 const*
typeinfo name for int const*
typeinfo name for long
typeinfo name for long*
typeinfo name for long const*
typeinfo name for long double
typeinfo name for long double*
typeinfo name for long double const*
typeinfo name for long long
typeinfo name for long long*
typeinfo name for long long const*
typeinfo name for short
typeinfo name for short*
typeinfo name for short const*
typeinfo name for signed char
typeinfo name for signed char*
typeinfo name for signed char const*
typeinfo name for std::bad_alloc
typeinfo name for std::bad_array_length
typeinfo name for std::bad_array_new_length
typeinfo name for std::bad_cast
typeinfo name for std::bad_exception
typeinfo name for std::bad_typeid
typeinfo name for std::domain_error
typeinfo name for std::exception
typeinfo name for std::invalid_argument
typeinfo name for std::length_error
typeinfo name for std::logic_error
typeinfo name for std::__ndk1::__assoc_sub_state
typeinfo name for std::__ndk1::bad_weak_ptr
typeinfo name for std::__ndk1::basic_ios<char, std::__ndk1::char_traits<char> >
typeinfo name for std::__ndk1::basic_iostream<char, std::__ndk1::char_traits<char> >
typeinfo name for std::__ndk1::basic_ios<wchar_t, std::__ndk1::char_traits<wchar_t> >
typeinfo name for std::__ndk1::basic_istream<char, std::__ndk1::char_traits<char> >
typeinfo name for std::__ndk1::basic_istream<wchar_t, std::__ndk1::char_traits<wchar_t> >
typeinfo name for std::__ndk1::basic_ostream<char, std::__ndk1::char_traits<char> >
typeinfo name for std::__ndk1::basic_ostream<wchar_t, std::__ndk1::char_traits<wchar_t> >
typeinfo name for std::__ndk1::basic_streambuf<char, std::__ndk1::char_traits<char> >
typeinfo name for std::__ndk1::basic_streambuf<wchar_t, std::__ndk1::char_traits<wchar_t> >
typeinfo name for std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> >
typeinfo name for std::__ndk1::__basic_string_common<true>
typeinfo name for std::__ndk1::codecvt_base
typeinfo name for std::__ndk1::codecvt_byname<char16_t, char, mbstate_t>
typeinfo name for std::__ndk1::codecvt_byname<char32_t, char, mbstate_t>
typeinfo name for std::__ndk1::codecvt_byname<char, char, mbstate_t>
typeinfo name for std::__ndk1::codecvt_byname<wchar_t, char, mbstate_t>
typeinfo name for std::__ndk1::codecvt<char16_t, char, mbstate_t>
typeinfo name for std::__ndk1::codecvt<char32_t, char, mbstate_t>
typeinfo name for std::__ndk1::codecvt<char, char, mbstate_t>
typeinfo name for std::__ndk1::__codecvt_utf16<char16_t, false>
typeinfo name for std::__ndk1::__codecvt_utf16<char16_t, true>
typeinfo name for std::__ndk1::__codecvt_utf16<char32_t, false>
typeinfo name for std::__ndk1::__codecvt_utf16<char32_t, true>
typeinfo name for std::__ndk1::__codecvt_utf16<wchar_t, false>
typeinfo name for std::__ndk1::__codecvt_utf16<wchar_t, true>
typeinfo name for std::__ndk1::__codecvt_utf8<char16_t>
typeinfo name for std::__ndk1::__codecvt_utf8<char32_t>
typeinfo name for std::__ndk1::__codecvt_utf8_utf16<char16_t>
typeinfo name for std::__ndk1::__codecvt_utf8_utf16<char32_t>
typeinfo name for std::__ndk1::__codecvt_utf8_utf16<wchar_t>
typeinfo name for std::__ndk1::__codecvt_utf8<wchar_t>
typeinfo name for std::__ndk1::codecvt<wchar_t, char, mbstate_t>
typeinfo name for std::__ndk1::collate_byname<char>
typeinfo name for std::__ndk1::collate_byname<wchar_t>
typeinfo name for std::__ndk1::collate<char>
typeinfo name for std::__ndk1::collate<wchar_t>
typeinfo name for std::__ndk1::ctype_base
typeinfo name for std::__ndk1::ctype_byname<char>
typeinfo name for std::__ndk1::ctype_byname<wchar_t>
typeinfo name for std::__ndk1::ctype<char>
typeinfo name for std::__ndk1::ctype<wchar_t>
typeinfo name for std::__ndk1::error_category
typeinfo name for std::__ndk1::future_error
typeinfo name for std::__ndk1::ios_base
typeinfo name for std::__ndk1::ios_base::failure
typeinfo name for std::__ndk1::locale::facet
typeinfo name for std::__ndk1::messages_base
typeinfo name for std::__ndk1::messages_byname<char>
typeinfo name for std::__ndk1::messages_byname<wchar_t>
typeinfo name for std::__ndk1::messages<char>
typeinfo name for std::__ndk1::messages<wchar_t>
typeinfo name for std::__ndk1::money_base
typeinfo name for std::__ndk1::__money_get<char>
typeinfo name for std::__ndk1::money_get<char, std::__ndk1::istreambuf_iterator<char, std::__ndk1::char_traits<char> > >
typeinfo name for std::__ndk1::__money_get<wchar_t>
typeinfo name for std::__ndk1::money_get<wchar_t, std::__ndk1::istreambuf_iterator<wchar_t, std::__ndk1::char_traits<wchar_t> > >
typeinfo name for std::__ndk1::moneypunct_byname<char, false>
typeinfo name for std::__ndk1::moneypunct_byname<char, true>
typeinfo name for std::__ndk1::moneypunct_byname<wchar_t, false>
typeinfo name for std::__ndk1::moneypunct_byname<wchar_t, true>
typeinfo name for std::__ndk1::moneypunct<char, false>
typeinfo name for std::__ndk1::moneypunct<char, true>
typeinfo name for std::__ndk1::moneypunct<wchar_t, false>
typeinfo name for std::__ndk1::moneypunct<wchar_t, true>
typeinfo name for std::__ndk1::__money_put<char>
typeinfo name for std::__ndk1::money_put<char, std::__ndk1::ostreambuf_iterator<char, std::__ndk1::char_traits<char> > >
typeinfo name for std::__ndk1::__money_put<wchar_t>
typeinfo name for std::__ndk1::money_put<wchar_t, std::__ndk1::ostreambuf_iterator<wchar_t, std::__ndk1::char_traits<wchar_t> > >
typeinfo name for std::__ndk1::__narrow_to_utf8<16ul>
typeinfo name for std::__ndk1::__narrow_to_utf8<32ul>
typeinfo name for std::__ndk1::__num_get_base
typeinfo name for std::__ndk1::__num_get<char>
typeinfo name for std::__ndk1::num_get<char, std::__ndk1::istreambuf_iterator<char, std::__ndk1::char_traits<char> > >
typeinfo name for std::__ndk1::__num_get<wchar_t>
typeinfo name for std::__ndk1::num_get<wchar_t, std::__ndk1::istreambuf_iterator<wchar_t, std::__ndk1::char_traits<wchar_t> > >
typeinfo name for std::__ndk1::numpunct_byname<char>
typeinfo name for std::__ndk1::numpunct_byname<wchar_t>
typeinfo name for std::__ndk1::numpunct<char>
typeinfo name for std::__ndk1::numpunct<wchar_t>
typeinfo name for std::__ndk1::__num_put_base
typeinfo name for std::__ndk1::__num_put<char>
typeinfo name for std::__ndk1::num_put<char, std::__ndk1::ostreambuf_iterator<char, std::__ndk1::char_traits<char> > >
typeinfo name for std::__ndk1::__num_put<wchar_t>
typeinfo name for std::__ndk1::num_put<wchar_t, std::__ndk1::ostreambuf_iterator<wchar_t, std::__ndk1::char_traits<wchar_t> > >
typeinfo name for std::__ndk1::__shared_count
typeinfo name for std::__ndk1::__shared_weak_count
typeinfo name for std::__ndk1::system_error
typeinfo name for std::__ndk1::time_base
typeinfo name for std::__ndk1::__time_get
typeinfo name for std::__ndk1::time_get_byname<char, std::__ndk1::istreambuf_iterator<char, std::__ndk1::char_traits<char> > >
typeinfo name for std::__ndk1::time_get_byname<wchar_t, std::__ndk1::istreambuf_iterator<wchar_t, std::__ndk1::char_traits<wchar_t> > >
typeinfo name for std::__ndk1::time_get<char, std::__ndk1::istreambuf_iterator<char, std::__ndk1::char_traits<char> > >
typeinfo name for std::__ndk1::__time_get_c_storage<char>
typeinfo name for std::__ndk1::__time_get_c_storage<wchar_t>
typeinfo name for std::__ndk1::__time_get_storage<char>
typeinfo name for std::__ndk1::__time_get_storage<wchar_t>
typeinfo name for std::__ndk1::time_get<wchar_t, std::__ndk1::istreambuf_iterator<wchar_t, std::__ndk1::char_traits<wchar_t> > >
typeinfo name for std::__ndk1::__time_put
typeinfo name for std::__ndk1::time_put_byname<char, std::__ndk1::ostreambuf_iterator<char, std::__ndk1::char_traits<char> > >
typeinfo name for std::__ndk1::time_put_byname<wchar_t, std::__ndk1::ostreambuf_iterator<wchar_t, std::__ndk1::char_traits<wchar_t> > >
typeinfo name for std::__ndk1::time_put<char, std::__ndk1::ostreambuf_iterator<char, std::__ndk1::char_traits<char> > >
typeinfo name for std::__ndk1::time_put<wchar_t, std::__ndk1::ostreambuf_iterator<wchar_t, std::__ndk1::char_traits<wchar_t> > >
typeinfo name for std::__ndk1::__widen_from_utf8<16ul>
typeinfo name for std::__ndk1::__widen_from_utf8<32ul>
typeinfo name for std::nested_exception
typeinfo name for std::out_of_range
typeinfo name for std::overflow_error
typeinfo name for std::range_error
typeinfo name for std::runtime_error
typeinfo name for std::type_info
typeinfo name for std::underflow_error
typeinfo name for unsigned char
typeinfo name for unsigned char*
typeinfo name for unsigned char const*
typeinfo name for unsigned int
typeinfo name for unsigned int*
typeinfo name for unsigned __int128
typeinfo name for unsigned __int128*
typeinfo name for unsigned __int128 const*
typeinfo name for unsigned int const*
typeinfo name for unsigned long
typeinfo name for unsigned long*
typeinfo name for unsigned long const*
typeinfo name for unsigned long long
typeinfo name for unsigned long long*
typeinfo name for unsigned long long const*
typeinfo name for unsigned short
typeinfo name for unsigned short*
typeinfo name for unsigned short const*
typeinfo name for void
typeinfo name for void*
typeinfo name for void const*
typeinfo name for wchar_t
typeinfo name for wchar_t*
typeinfo name for wchar_t const*
unsigned int std::__ndk1::__num_get_unsigned_integral<unsigned int>(char const*, char const*, unsigned int&, int)
unsigned long long std::__ndk1::__num_get_unsigned_integral<unsigned long long>(char const*, char const*, unsigned int&, int)
unsigned long std::__ndk1::__num_get_unsigned_integral<unsigned long>(char const*, char const*, unsigned int&, int)
unsigned short std::__ndk1::__num_get_unsigned_integral<unsigned short>(char const*, char const*, unsigned int&, int)
_Unwind_Backtrace
_Unwind_DeleteException
_Unwind_FindEnclosingFunction
_Unwind_Find_FDE
_Unwind_ForcedUnwind
_Unwind_GetCFA
_Unwind_GetDataRelBase
_Unwind_GetGR
_Unwind_GetIP
_Unwind_GetIPInfo
_Unwind_GetLanguageSpecificData
_Unwind_GetRegionStart
_Unwind_GetTextRelBase
_Unwind_RaiseException
_Unwind_Resume
_Unwind_Resume_or_Rethrow
_Unwind_SetGR
_Unwind_SetIP
virtual thunk to std::__ndk1::basic_iostream<char, std::__ndk1::char_traits<char> >::~basic_iostream()
virtual thunk to std::__ndk1::basic_istream<char, std::__ndk1::char_traits<char> >::~basic_istream()
virtual thunk to std::__ndk1::basic_istream<wchar_t, std::__ndk1::char_traits<wchar_t> >::~basic_istream()
virtual thunk to std::__ndk1::basic_ostream<char, std::__ndk1::char_traits<char> >::~basic_ostream()
virtual thunk to std::__ndk1::basic_ostream<wchar_t, std::__ndk1::char_traits<wchar_t> >::~basic_ostream()
void std::__ndk1::vector<unsigned long, std::__ndk1::allocator<unsigned long> >::__push_back_slow_path<unsigned long>(unsigned long&&)
vtable for __cxxabiv1::__array_type_info
vtable for __cxxabiv1::__class_type_info
vtable for __cxxabiv1::__enum_type_info
vtable for __cxxabiv1::__function_type_info
vtable for __cxxabiv1::__fundamental_type_info
vtable for __cxxabiv1::__pbase_type_info
vtable for __cxxabiv1::__pointer_to_member_type_info
vtable for __cxxabiv1::__pointer_type_info
vtable for __cxxabiv1::__shim_type_info
vtable for __cxxabiv1::__si_class_type_info
vtable for __cxxabiv1::__vmi_class_type_info
vtable for std::bad_alloc
vtable for std::bad_array_length
vtable for std::bad_array_new_length
vtable for std::bad_cast
vtable for std::bad_exception
vtable for std::bad_typeid
vtable for std::domain_error
vtable for std::exception
vtable for std::invalid_argument
vtable for std::length_error
vtable for std::logic_error
vtable for std::__ndk1::__assoc_sub_state
vtable for std::__ndk1::bad_weak_ptr
vtable for std::__ndk1::basic_ios<char, std::__ndk1::char_traits<char> >
vtable for std::__ndk1::basic_iostream<char, std::__ndk1::char_traits<char> >
vtable for std::__ndk1::basic_ios<wchar_t, std::__ndk1::char_traits<wchar_t> >
vtable for std::__ndk1::basic_istream<char, std::__ndk1::char_traits<char> >
vtable for std::__ndk1::basic_istream<wchar_t, std::__ndk1::char_traits<wchar_t> >
vtable for std::__ndk1::basic_ostream<char, std::__ndk1::char_traits<char> >
vtable for std::__ndk1::basic_ostream<wchar_t, std::__ndk1::char_traits<wchar_t> >
vtable for std::__ndk1::basic_streambuf<char, std::__ndk1::char_traits<char> >
vtable for std::__ndk1::basic_streambuf<wchar_t, std::__ndk1::char_traits<wchar_t> >
vtable for std::__ndk1::codecvt_byname<char16_t, char, mbstate_t>
vtable for std::__ndk1::codecvt_byname<char32_t, char, mbstate_t>
vtable for std::__ndk1::codecvt_byname<char, char, mbstate_t>
vtable for std::__ndk1::codecvt_byname<wchar_t, char, mbstate_t>
vtable for std::__ndk1::codecvt<char16_t, char, mbstate_t>
vtable for std::__ndk1::codecvt<char32_t, char, mbstate_t>
vtable for std::__ndk1::codecvt<char, char, mbstate_t>
vtable for std::__ndk1::__codecvt_utf16<char16_t, false>
vtable for std::__ndk1::__codecvt_utf16<char16_t, true>
vtable for std::__ndk1::__codecvt_utf16<char32_t, false>
vtable for std::__ndk1::__codecvt_utf16<char32_t, true>
vtable for std::__ndk1::__codecvt_utf16<wchar_t, false>
vtable for std::__ndk1::__codecvt_utf16<wchar_t, true>
vtable for std::__ndk1::__codecvt_utf8<char16_t>
vtable for std::__ndk1::__codecvt_utf8<char32_t>
vtable for std::__ndk1::__codecvt_utf8_utf16<char16_t>
vtable for std::__ndk1::__codecvt_utf8_utf16<char32_t>
vtable for std::__ndk1::__codecvt_utf8_utf16<wchar_t>
vtable for std::__ndk1::__codecvt_utf8<wchar_t>
vtable for std::__ndk1::codecvt<wchar_t, char, mbstate_t>
vtable for std::__ndk1::collate_byname<char>
vtable for std::__ndk1::collate_byname<wchar_t>
vtable for std::__ndk1::collate<char>
vtable for std::__ndk1::collate<wchar_t>
vtable for std::__ndk1::ctype_byname<char>
vtable for std::__ndk1::ctype_byname<wchar_t>
vtable for std::__ndk1::ctype<char>
vtable for std::__ndk1::ctype<wchar_t>
vtable for std::__ndk1::error_category
vtable for std::__ndk1::future_error
vtable for std::__ndk1::ios_base
vtable for std::__ndk1::ios_base::failure
vtable for std::__ndk1::locale::facet
vtable for std::__ndk1::messages_byname<char>
vtable for std::__ndk1::messages_byname<wchar_t>
vtable for std::__ndk1::messages<char>
vtable for std::__ndk1::messages<wchar_t>
vtable for std::__ndk1::money_get<char, std::__ndk1::istreambuf_iterator<char, std::__ndk1::char_traits<char> > >
vtable for std::__ndk1::money_get<wchar_t, std::__ndk1::istreambuf_iterator<wchar_t, std::__ndk1::char_traits<wchar_t> > >
vtable for std::__ndk1::moneypunct_byname<char, false>
vtable for std::__ndk1::moneypunct_byname<char, true>
vtable for std::__ndk1::moneypunct_byname<wchar_t, false>
vtable for std::__ndk1::moneypunct_byname<wchar_t, true>
vtable for std::__ndk1::moneypunct<char, false>
vtable for std::__ndk1::moneypunct<char, true>
vtable for std::__ndk1::moneypunct<wchar_t, false>
vtable for std::__ndk1::moneypunct<wchar_t, true>
vtable for std::__ndk1::money_put<char, std::__ndk1::ostreambuf_iterator<char, std::__ndk1::char_traits<char> > >
vtable for std::__ndk1::money_put<wchar_t, std::__ndk1::ostreambuf_iterator<wchar_t, std::__ndk1::char_traits<wchar_t> > >
vtable for std::__ndk1::__narrow_to_utf8<16ul>
vtable for std::__ndk1::__narrow_to_utf8<32ul>
vtable for std::__ndk1::num_get<char, std::__ndk1::istreambuf_iterator<char, std::__ndk1::char_traits<char> > >
vtable for std::__ndk1::num_get<wchar_t, std::__ndk1::istreambuf_iterator<wchar_t, std::__ndk1::char_traits<wchar_t> > >
vtable for std::__ndk1::numpunct_byname<char>
vtable for std::__ndk1::numpunct_byname<wchar_t>
vtable for std::__ndk1::numpunct<char>
vtable for std::__ndk1::numpunct<wchar_t>
vtable for std::__ndk1::num_put<char, std::__ndk1::ostreambuf_iterator<char, std::__ndk1::char_traits<char> > >
vtable for std::__ndk1::num_put<wchar_t, std::__ndk1::ostreambuf_iterator<wchar_t, std::__ndk1::char_traits<wchar_t> > >
vtable for std::__ndk1::__shared_count
vtable for std::__ndk1::__shared_weak_count
vtable for std::__ndk1::system_error
vtable for std::__ndk1::time_get_byname<char, std::__ndk1::istreambuf_iterator<char, std::__ndk1::char_traits<char> > >
vtable for std::__ndk1::time_get_byname<wchar_t, std::__ndk1::istreambuf_iterator<wchar_t, std::__ndk1::char_traits<wchar_t> > >
vtable for std::__ndk1::time_get<char, std::__ndk1::istreambuf_iterator<char, std::__ndk1::char_traits<char> > >
vtable for std::__ndk1::time_get<wchar_t, std::__ndk1::istreambuf_iterator<wchar_t, std::__ndk1::char_traits<wchar_t> > >
vtable for std::__ndk1::time_put_byname<char, std::__ndk1::ostreambuf_iterator<char, std::__ndk1::char_traits<char> > >
vtable for std::__ndk1::time_put_byname<wchar_t, std::__ndk1::ostreambuf_iterator<wchar_t, std::__ndk1::char_traits<wchar_t> > >
vtable for std::__ndk1::time_put<char, std::__ndk1::ostreambuf_iterator<char, std::__ndk1::char_traits<char> > >
vtable for std::__ndk1::time_put<wchar_t, std::__ndk1::ostreambuf_iterator<wchar_t, std::__ndk1::char_traits<wchar_t> > >
vtable for std::__ndk1::__widen_from_utf8<16ul>
vtable for std::__ndk1::__widen_from_utf8<32ul>
vtable for std::nested_exception
vtable for std::out_of_range
vtable for std::overflow_error
vtable for std::range_error
vtable for std::runtime_error
vtable for std::type_info
vtable for std::underflow_error
VTT for std::__ndk1::basic_iostream<char, std::__ndk1::char_traits<char> >
VTT for std::__ndk1::basic_istream<char, std::__ndk1::char_traits<char> >
VTT for std::__ndk1::basic_istream<wchar_t, std::__ndk1::char_traits<wchar_t> >
VTT for std::__ndk1::basic_ostream<char, std::__ndk1::char_traits<char> >
VTT for std::__ndk1::basic_ostream<wchar_t, std::__ndk1::char_traits<wchar_t> >

## libadvirprocess
_51 exports_

check_stretch_param
dde_coefficient_calculate
flip
gain_switch_detect
gaussian_filter
get_gau_kernel
get_rgba_color_map_table_m2
get_yuv_color_map_table
get_yuv_color_map_table_m2
gray_map_to_argb_pseudocolor
gray_map_to_argb_pseudocolor_m2
irproc_debug_info
irproc_debug_print
irproc_debug_void
irproc_error_info
irproc_error_print
irproc_error_void
irproc_log_register
irproc_version
Java_com_energy_irutilslibrary_LibIRProcess_flip
Java_com_energy_irutilslibrary_LibIRProcess_gray_1map_1to_1argb_1pseudocolor
Java_com_energy_irutilslibrary_LibIRProcess_gray_1map_1to_1argb_1pseudocolor_1m2
Java_com_energy_irutilslibrary_LibIRProcess_irproc_1version
Java_com_energy_irutilslibrary_LibIRProcess_irprocess_1log_1register
Java_com_energy_irutilslibrary_LibIRProcess_mirror
Java_com_energy_irutilslibrary_LibIRProcess_rotate_1180
Java_com_energy_irutilslibrary_LibIRProcess_rotate_1left_190
Java_com_energy_irutilslibrary_LibIRProcess_rotate_1right_190
Java_com_energy_irutilslibrary_LibIRProcess_y14_1image_1enhance
Java_com_energy_irutilslibrary_LibIRProcess_y14_1map_1to_1yuyv_1pseudocolor
Java_com_energy_irutilslibrary_LibIRProcess_yuyv_1map_1to_1argb_1custom_1pseudocolor
Java_com_energy_irutilslibrary_LibIRProcess_yuyv_1map_1to_1argb_1pseudocolor
Java_com_energy_irutilslibrary_LibIRProcess_yuyv_1map_1to_1argb_1pseudocolor_1m2
mirror
overexposure_detect
rotate_180
rotate_left_90
rotate_right_90
snr_one_pixel_process
snr_weight_get
stretch_frame
y14_image_auto_gain_control
y14_image_digital_detail_enhance
y14_image_enhance
y14_image_extract_detail
y14_image_spatial_noise_reduction
y14_map_to_yuyv_pseudocolor
yuyv_map_to_argb_custom_pseudocolor
yuyv_map_to_argb_pseudocolor
yuyv_map_to_argb_pseudocolor_m2
yuyv_map_to_yuyv_pseudocolor

## libadvirparse
_31 exports_

irparse_debug_info
irparse_debug_print
irparse_debug_void
irparse_error_info
irparse_error_print
irparse_error_void
irparse_log_register
irparse_version
Java_com_energy_irutilslibrary_LibIRParse_irparse_1log_1register
Java_com_energy_irutilslibrary_LibIRParse_irparse_1version
Java_com_energy_irutilslibrary_LibIRParse_raw_1data_1cut
Java_com_energy_irutilslibrary_LibIRParse_rgb_1to_1bgr
Java_com_energy_irutilslibrary_LibIRParse_y14_1to_1rgb
Java_com_energy_irutilslibrary_LibIRParse_y14_1to_1y8
Java_com_energy_irutilslibrary_LibIRParse_y14_1to_1yuv444
Java_com_energy_irutilslibrary_LibIRParse_y16_1to_1y14
Java_com_energy_irutilslibrary_LibIRParse_yuv422_1add_1y
Java_com_energy_irutilslibrary_LibIRParse_yuv422_1to_1rgb
Java_com_energy_irutilslibrary_LibIRParse_yuv444_1to_1rgb
Java_com_energy_irutilslibrary_LibIRParse_yuv444_1to_1yuv422
num_y14_to_y8
raw_data_cut
rgb_to_bgr
y14_to_rgb
y14_to_y8
y14_to_yuv444
y16_to_y14
yuv422_add_y
yuv422_to_rgb
yuv444_to_rgb
yuv444_to_yuv422

## libadvirutils
_16 exports_

get_org_env_factor(TempCalInfo_t*)
get_tempinfo(_JNIEnv*, _jclass*, int, int, _jshortArray*, _jshortArray*, int, int, int, int)
get_tempinfo_wn640_v2(_JNIEnv*, _jclass*, int, int, _jshortArray*, _jshortArray*, int, int, int)
_JavaVM::GetEnv(void**, int)
_JNIEnv::FindClass(char const*)
_JNIEnv::GetByteArrayElements(_jbyteArray*, unsigned char*)
_JNIEnv::GetShortArrayElements(_jshortArray*, unsigned char*)
_JNIEnv::RegisterNatives(_jclass*, JNINativeMethod const*, int)
_JNIEnv::ReleaseByteArrayElements(_jbyteArray*, signed char*, int)
_JNIEnv::ReleaseShortArrayElements(_jshortArray*, short*, int)
JNI_OnLoad
nativeMethods
registerNativeMethod(_JNIEnv*)
temp_correction_release(_JNIEnv*, _jclass*, long, unsigned char)
temp_correction_with_new_method(_JNIEnv*, _jclass*, float, _jbyteArray*, float, float, float, float, float)
temp_correction_with_origin_method(_JNIEnv*, _jclass*, float, _jbyteArray*, float, float, float, float, float, long, int)

## libirpack_tool
_284 exports_

add_file_to_closed_zip_using_file_buffer
add_file_to_open_zip_using_file_buffer
add_file_to_zip_using_file_path
add_file_with_specified_name_from_one_zip_to_another
adler32
adler32_combine
adler32_combine64
adler32_z
_bss_end__
cjson_add_string_to_object
crc32
crc32_combine
crc32_combine64
crc32_z
.data.rel.ro
deflate
deflateBound
deflateCopy
deflate_copyright
deflateEnd
deflateGetDictionary
deflateInit_
deflateInit2_
deflateParams
deflatePending
deflatePrime
deflateReset
deflateResetKeep
deflateSetDictionary
deflateSetHeader
deflateTune
delete_file_in_zip
_dist_code
_edata
_end
get_crc_table
get_file_data_from_closed_zip
get_file_data_from_open_zip
get_file_info_in_folder_from_zip
get_folder_info_in_zip
inflate
inflateCodesUsed
inflateCopy
inflate_copyright
inflateEnd
inflate_fast
inflateGetDictionary
inflateGetHeader
inflateInit_
inflateInit2_
inflateMark
inflatePrime
inflateReset
inflateReset2
inflateResetKeep
inflateSetDictionary
inflateSync
inflateSyncPoint
inflate_table
inflateUndermine
inflateValidate
_length_code
merge_files_between_two_folders_in_zip
modify_org_path_to_dst_path(char const*, char*, char*)
packtool_debug_info(char const*, ...)
packtool_debug_print
packtool_debug_void(char const*, ...)
packtool_error_info(char const*, ...)
packtool_error_print
packtool_error_void(char const*, ...)
packtool_log_register
.text
_tr_align
_tr_flush_bits
_tr_flush_block
_tr_init
_tr_stored_block
_tr_tally
zcalloc
zcfree
z_errmsg
zError
zip_add
zip_add_dir
_zip_add_entry
zip_archive_set_tempdir
_zip_buffer_data
_zip_buffer_eof
_zip_buffer_free
_zip_buffer_get
_zip_buffer_get_16
_zip_buffer_get_32
_zip_buffer_get_64
_zip_buffer_get_8
_zip_buffer_left
_zip_buffer_new
_zip_buffer_new_from_source
_zip_buffer_offset
_zip_buffer_ok
_zip_buffer_put
_zip_buffer_put_16
_zip_buffer_put_32
_zip_buffer_put_64
_zip_buffer_put_8
_zip_buffer_set_offset
_zip_buffer_size
_zip_cdir_free
_zip_cdir_new
_zip_cdir_write
_zip_changed
zip_close
_zip_cp437_to_utf8
zip_delete
_zip_deregister_source
zip_dir_add
_zip_dirent_clone
_zip_dirent_finalize
_zip_dirent_free
_zip_dirent_init
_zip_dirent_needs_zip64
_zip_dirent_new
_zip_dirent_read
_zip_dirent_size
_zip_dirent_write
zip_discard
_zip_ef_clone
_zip_ef_delete_by_id
_zip_ef_free
_zip_ef_get_by_id
_zip_ef_merge
_zip_ef_new
_zip_ef_parse
_zip_ef_remove_internal
_zip_ef_size
_zip_ef_write
_zip_entry_finalize
_zip_entry_init
_zip_error_clear
zip_error_clear
zip_error_code_system
zip_error_code_zip
_zip_error_copy
zip_error_fini
_zip_error_get
zip_error_get
zip_error_get_sys_type
zip_error_init
zip_error_init_with_code
zip_error_set
_zip_error_set_from_source
zip_error_strerror
zip_error_system_type
zip_error_to_data
zip_error_to_str
_zip_err_str
_zip_err_type
zip_fclose
zip_fdopen
zip_file_add
zip_file_error_clear
zip_file_error_get
zip_file_extra_field_delete
zip_file_extra_field_delete_by_id
zip_file_extra_field_get
zip_file_extra_field_get_by_id
_zip_file_extra_field_prepare_for_change
zip_file_extra_fields_count
zip_file_extra_fields_count_by_id
zip_file_extra_field_set
zip_file_get_comment
zip_file_get_error
zip_file_get_external_attributes
_zip_file_get_offset
_zip_filerange_crc
zip_file_rename
_zip_file_replace
zip_file_replace
zip_file_set_comment
zip_file_set_external_attributes
zip_file_set_mtime
zip_file_strerror
zip_fopen
zip_fopen_encrypted
zip_fopen_index
zip_fopen_index_encrypted
zip_fread
zip_get_archive_comment
zip_get_archive_flag
_zip_get_compression_implementation
_zip_get_dirent
_zip_get_encryption_implementation
zip_get_error
zip_get_file_comment
_zip_get_name
zip_get_name
zip_get_num_entries
zip_get_num_files
_zip_guess_encoding
_zip_memdup
_zip_mkstemp
_zip_name_locate
zip_name_locate
_zip_nerr_str
_zip_new
_zip_open
zip_open
zip_open_from_source
_zip_read
_zip_read_data
_zip_read_local_ef
_zip_read_string
_zip_register_source
zip_rename
zip_replace
zip_set_archive_comment
zip_set_archive_flag
zip_set_default_password
zip_set_file_comment
zip_set_file_compression
_zip_set_name
_zip_set_open_error
zip_source_begin_write
zip_source_buffer
zip_source_buffer_create
_zip_source_call
zip_source_close
zip_source_commit_write
zip_source_crc
zip_source_deflate
zip_source_error
zip_source_file
zip_source_file_create
_zip_source_file_or_p
zip_source_filep
zip_source_filep_create
zip_source_free
zip_source_function
zip_source_function_create
_zip_source_invalidate
zip_source_is_deleted
zip_source_keep
zip_source_layered
zip_source_layered_create
zip_source_make_command_bitmap
_zip_source_new
zip_source_open
zip_source_pkware
zip_source_read
zip_source_remove
zip_source_rollback_write
zip_source_seek
zip_source_seek_compute_offset
zip_source_seek_write
_zip_source_set_source_archive
zip_source_stat
zip_source_supports
zip_source_tell
zip_source_tell_write
zip_source_window
_zip_source_window_new
zip_source_write
zip_source_zip
_zip_source_zip_new
zip_stat
zip_stat_index
zip_stat_init
_zip_stat_merge
zip_strerror
_zip_string_crc32
_zip_string_equal
_zip_string_free
_zip_string_get
_zip_string_length
_zip_string_new
_zip_string_write
_zip_u2d_time
_zip_unchange
zip_unchange
zip_unchange_all
zip_unchange_archive
_zip_unchange_data
_zip_write
zlibCompileFlags
zlibVersion

## libframecache
_123 exports_

addFrame
androidtempera
androidtempera_pck_name
checkPckNameValidity
checkSigValidity
common
common_iruvc
common_mnn_pck_name
common_pck_name
dingjiang_pck_name
dingjiang_sig
EK160_pck_name
EK160_sdk_pck_name
EK160_sop_name
EK_hammer
EK_pad
EK_sop
FrameIndex::FrameIndex(unsigned char*, int, bool, bool)
getFirstFrame
getNextFrame
getPackageName
getSha1Sig
init
iruvc_spiir_pck_name
iruvc_usbdual_pck_name
iruvc_usbir_pck_name
iruvc_WN640v2_pck_name
iruvc_WN640v_pck_name
isSigValid
_JavaVM::GetEnv(void**, int)
_JNIEnv::CallObjectMethod(_jobject*, _jmethodID*, ...)
_JNIEnv::CallStaticObjectMethod(_jclass*, _jmethodID*, ...)
_JNIEnv::DeleteLocalRef(_jobject*)
_JNIEnv::FindClass(char const*)
_JNIEnv::GetArrayLength(_jarray*)
_JNIEnv::GetBooleanArrayElements(_jbooleanArray*, unsigned char*)
_JNIEnv::GetByteArrayElements(_jbyteArray*, unsigned char*)
_JNIEnv::GetFieldID(_jclass*, char const*, char const*)
_JNIEnv::GetIntArrayElements(_jintArray*, unsigned char*)
_JNIEnv::GetLongArrayElements(_jlongArray*, unsigned char*)
_JNIEnv::GetMethodID(_jclass*, char const*, char const*)
_JNIEnv::GetObjectArrayElement(_jobjectArray*, int)
_JNIEnv::GetObjectClass(_jobject*)
_JNIEnv::GetObjectField(_jobject*, _jfieldID*)
_JNIEnv::GetStaticMethodID(_jclass*, char const*, char const*)
_JNIEnv::GetStringUTFChars(_jstring*, unsigned char*)
_JNIEnv::NewObject(_jclass*, _jmethodID*, ...)
_JNIEnv::NewStringUTF(char const*)
_JNIEnv::RegisterNatives(_jclass*, JNINativeMethod const*, int)
_JNIEnv::ReleaseBooleanArrayElements(_jbooleanArray*, unsigned char*, int)
_JNIEnv::ReleaseByteArrayElements(_jbyteArray*, signed char*, int)
_JNIEnv::ReleaseIntArrayElements(_jintArray*, int*, int)
_JNIEnv::ReleaseLongArrayElements(_jlongArray*, long*, int)
_JNIEnv::ReleaseStringUTFChars(_jstring*, char const*)
_JNIEnv::UnregisterNatives(_jclass*)
JNI_OnLoad
JNI_OnUnload
methods
nativeAddFrameData(_JNIEnv*, _jclass*, long, unsigned char, _jbyteArray*, int)
nativeGetFirstFrameData(_JNIEnv*, _jclass*, long, _jlongArray*, _jbyteArray*, _jintArray*)
nativeGetNextFrameData(_JNIEnv*, _jclass*, long, _jlongArray*, _jbyteArray*, _jintArray*, _jbooleanArray*)
nativeInitCache(_JNIEnv*, _jclass*, _jobject*, int, unsigned char)
nativeReleaseCache(_JNIEnv*, _jclass*)
p2plusdome_sha1_sig
p2plus_pck_name
p2plus_sha1_sig
p2plus_teledome_pck_name
p2plus_teledome_sha1_sig
p2plus_telephoto_30_pck_name
p2plus_telephoto_google_sha1_sig
p2plus_telephoto_mobi
p2plus_telephoto_mobinotouch_pck_name
p2plus_telephoto_mobi_pck_name
p2plus_telephoto_pck_name
p2plus_telephoto_sha1_sig
registerNativeMethod(_JNIEnv*)
sig_valid_version
TC_133T_pck_name
TC_135_pck_name
TC_2500
TC_2500_pck_name
TC_common
TC_f006
TC_F02_pck_name
TC_m22S_pck_name
TC_platform
TC_S105B_pck_name
TC_S120_pck_name
UnInit
unique_readguard<WFirstRWLock>::~unique_readguard()
unique_readguard<WFirstRWLock>::unique_readguard(WFirstRWLock&)
unique_writeguard<WFirstRWLock>::~unique_writeguard()
unique_writeguard<WFirstRWLock>::unique_writeguard(WFirstRWLock&)
UT_pck_name_1
UT_pck_name_2
UT_pck_name_3
UT_sig_1
UT_sig_2
UT_sig_3
void std::__ndk1::allocator<long long>::construct<long long, long long const&>(long long*, long long const&)
void std::__ndk1::allocator<std::__ndk1::__tree_node<std::__ndk1::__value_type<long long, std::__ndk1::shared_ptr<FrameIndex> >, void*> >::construct<std::__ndk1::pair<long long const, std::__ndk1::shared_ptr<FrameIndex> >, std::__ndk1::pair<long long, std::__ndk1::shared_ptr<FrameIndex> > >(std::__ndk1::pair<long long const, std::__ndk1::shared_ptr<FrameIndex> >*, std::__ndk1::pair<long long, std::__ndk1::shared_ptr<FrameIndex> >&&)
void std::__ndk1::allocator_traits<std::__ndk1::allocator<long long> >::construct<long long, long long const&>(std::__ndk1::allocator<long long>&, long long*, long long const&)
void std::__ndk1::allocator_traits<std::__ndk1::allocator<long long> >::__construct<long long, long long const&>(std::__ndk1::integral_constant<bool, true>, std::__ndk1::allocator<long long>&, long long*, long long const&)
void std::__ndk1::allocator_traits<std::__ndk1::allocator<long long> >::destroy<long long>(std::__ndk1::allocator<long long>&, long long*)
void std::__ndk1::allocator_traits<std::__ndk1::allocator<long long> >::__destroy<long long>(std::__ndk1::integral_constant<bool, true>, std::__ndk1::allocator<long long>&, long long*)
void std::__ndk1::allocator_traits<std::__ndk1::allocator<std::__ndk1::__tree_node<std::__ndk1::__value_type<long long, std::__ndk1::shared_ptr<FrameIndex> >, void*> > >::construct<std::__ndk1::pair<long long const, std::__ndk1::shared_ptr<FrameIndex> >, std::__ndk1::pair<long long, std::__ndk1::shared_ptr<FrameIndex> > >(std::__ndk1::allocator<std::__ndk1::__tree_node<std::__ndk1::__value_type<long long, std::__ndk1::shared_ptr<FrameIndex> >, void*> >&, std::__ndk1::pair<long long const, std::__ndk1::shared_ptr<FrameIndex> >*, std::__ndk1::pair<long long, std::__ndk1::shared_ptr<FrameIndex> >&&)
void std::__ndk1::allocator_traits<std::__ndk1::allocator<std::__ndk1::__tree_node<std::__ndk1::__value_type<long long, std::__ndk1::shared_ptr<FrameIndex> >, void*> > >::__construct<std::__ndk1::pair<long long const, std::__ndk1::shared_ptr<FrameIndex> >, std::__ndk1::pair<long long, std::__ndk1::shared_ptr<FrameIndex> > >(std::__ndk1::integral_constant<bool, true>, std::__ndk1::allocator<std::__ndk1::__tree_node<std::__ndk1::__value_type<long long, std::__ndk1::shared_ptr<FrameIndex> >, void*> >&, std::__ndk1::pair<long long const, std::__ndk1::shared_ptr<FrameIndex> >*, std::__ndk1::pair<long long, std::__ndk1::shared_ptr<FrameIndex> >&&)
void std::__ndk1::allocator_traits<std::__ndk1::allocator<std::__ndk1::__tree_node<std::__ndk1::__value_type<long long, std::__ndk1::shared_ptr<FrameIndex> >, void*> > >::destroy<std::__ndk1::pair<long long const, std::__ndk1::shared_ptr<FrameIndex> > >(std::__ndk1::allocator<std::__ndk1::__tree_node<std::__ndk1::__value_type<long long, std::__ndk1::shared_ptr<FrameIndex> >, void*> >&, std::__ndk1::pair<long long const, std::__ndk1::shared_ptr<FrameIndex> >*)
void std::__ndk1::allocator_traits<std::__ndk1::allocator<std::__ndk1::__tree_node<std::__ndk1::__value_type<long long, std::__ndk1::shared_ptr<FrameIndex> >, void*> > >::__destroy<std::__ndk1::pair<long long const, std::__ndk1::shared_ptr<FrameIndex> > >(std::__ndk1::integral_constant<bool, false>, std::__ndk1::allocator<std::__ndk1::__tree_node<std::__ndk1::__value_type<long long, std::__ndk1::shared_ptr<FrameIndex> >, void*> >&, std::__ndk1::pair<long long const, std::__ndk1::shared_ptr<FrameIndex> >*)
void std::__ndk1::__tree_balance_after_insert<std::__ndk1::__tree_node_base<void*>*>(std::__ndk1::__tree_node_base<void*>*, std::__ndk1::__tree_node_base<void*>*)
void std::__ndk1::__tree_left_rotate<std::__ndk1::__tree_node_base<void*>*>(std::__ndk1::__tree_node_base<void*>*)
void std::__ndk1::__tree_remove<std::__ndk1::__tree_node_base<void*>*>(std::__ndk1::__tree_node_base<void*>*, std::__ndk1::__tree_node_base<void*>*)
void std::__ndk1::__tree_right_rotate<std::__ndk1::__tree_node_base<void*>*>(std::__ndk1::__tree_node_base<void*>*)
void std::__ndk1::vector<long long, std::__ndk1::allocator<long long> >::__construct_one_at_end<long long const&>(long long const&)
void std::__ndk1::vector<long long, std::__ndk1::allocator<long long> >::__push_back_slow_path<long long const&>(long long const&)
vtable for std::__ndk1::__shared_ptr_pointer<FrameIndex*, std::__ndk1::default_delete<FrameIndex>, std::__ndk1::allocator<FrameIndex> >
WFirstRWLock::lock_read()
WFirstRWLock::lock_read()::{lambda()#1}::operator()() const
WFirstRWLock::lock_write()
WFirstRWLock::lock_write()::{lambda()#1}::operator()() const
WFirstRWLock::release_read()
WFirstRWLock::release_write()
WFirstRWLock::~WFirstRWLock()

## libircam
_20 exports_

_bss_end__
.data
_edata
_end
ircam_callback_print
ircam_debug_info
ircam_debug_print
ircam_debug_void
ircam_error_info
ircam_error_print
ircam_error_void
ircam_log_priv_data
ircam_log_register
ircam_version
ircam_version_number
ir_control_handle_create
ir_control_handle_delete
ir_video_handle_create
ir_video_handle_delete
.text

## libirutilssdk
_0 exports_


## libcolormapping
_119 exports_

androidtempera
checkSigValidity
choosen_map_table
colormapping_dll_version()
colormapping_rgba(int, unsigned char*, unsigned char*)
colormapping_rgba_standalone(std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> >, int, unsigned char*, unsigned char*)
colormapping_rgba_with_temp_clamp(int, unsigned char*, unsigned short*, unsigned char*)
colormapping_rgba_with_temp_gray(int, unsigned char*, unsigned short*, unsigned char*)
colormapping_rgba_with_temp_strtch_clamp(int, unsigned char*, unsigned short*, unsigned char*)
colormapping_rgba_with_temp_strtch_gray(int, unsigned char*, unsigned short*, unsigned char*)
colormapping_rgb(int, unsigned char*, unsigned char*)
colormapping_rgb_with_temp_clamp(int, unsigned char*, unsigned short*, unsigned char*)
colormapping_rgb_with_temp_gray(int, unsigned char*, unsigned short*, unsigned char*)
colormapping_rgb_with_temp_strtch_clamp(int, unsigned char*, unsigned short*, unsigned char*)
colormapping_rgb_with_temp_strtch_gray(int, unsigned char*, unsigned short*, unsigned char*)
colormapping(std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> >, int, unsigned char*, unsigned char*)
common
common_iruvc
eco_sop
get_rgb_table()
getSha1Sig
init()
init_rgb_table(std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> >)
isSigValid
_JavaVM::GetEnv(void**, int)
_JNIEnv::CallObjectMethod(_jobject*, _jmethodID*, ...)
_JNIEnv::CallStaticObjectMethod(_jclass*, _jmethodID*, ...)
_JNIEnv::DeleteLocalRef(_jobject*)
_JNIEnv::FindClass(char const*)
_JNIEnv::GetArrayLength(_jarray*)
_JNIEnv::GetByteArrayElements(_jbyteArray*, unsigned char*)
_JNIEnv::GetFieldID(_jclass*, char const*, char const*)
_JNIEnv::GetMethodID(_jclass*, char const*, char const*)
_JNIEnv::GetObjectArrayElement(_jobjectArray*, int)
_JNIEnv::GetObjectClass(_jobject*)
_JNIEnv::GetObjectField(_jobject*, _jfieldID*)
_JNIEnv::GetShortArrayElements(_jshortArray*, unsigned char*)
_JNIEnv::GetStaticMethodID(_jclass*, char const*, char const*)
_JNIEnv::NewObject(_jclass*, _jmethodID*, ...)
_JNIEnv::NewStringUTF(char const*)
_JNIEnv::RegisterNatives(_jclass*, JNINativeMethod const*, int)
_JNIEnv::ReleaseByteArrayElements(_jbyteArray*, signed char*, int)
_JNIEnv::ReleaseShortArrayElements(_jshortArray*, short*, int)
_JNIEnv::SetByteArrayRegion(_jbyteArray*, int, int, signed char const*)
JNI_OnLoad
jstring2string(_JNIEnv*, _jstring*)
map
nativeColorMappingDllVersion(_JNIEnv*, _jclass*)
nativeColorMappingGetRGBTable(_JNIEnv*, _jclass*, _jbyteArray*)
nativeColorMapping(_JNIEnv*, _jclass*, _jstring*, int, _jbyteArray*, _jbyteArray*)
nativeColorMappingRGBA(_JNIEnv*, _jclass*, int, _jbyteArray*, _jbyteArray*)
nativeColorMappingRGBAWithTempClamp(_JNIEnv*, _jclass*, int, _jbyteArray*, _jshortArray*, _jbyteArray*)
nativeColorMappingRGBAWithTempGray(_JNIEnv*, _jclass*, int, _jbyteArray*, _jshortArray*, _jbyteArray*)
nativeColorMappingRGBAWithTempStrtchClamp(_JNIEnv*, _jclass*, int, _jbyteArray*, _jshortArray*, _jbyteArray*)
nativeColorMappingRGBAWithTempStrtchGray(_JNIEnv*, _jclass*, int, _jbyteArray*, _jshortArray*, _jbyteArray*)
nativeColorMappingRGB(_JNIEnv*, _jclass*, int, _jbyteArray*, _jbyteArray*)
nativeColorMappingRGBWithTempClamp(_JNIEnv*, _jclass*, int, _jbyteArray*, _jshortArray*, _jbyteArray*)
nativeColorMappingRGBWithTempGray(_JNIEnv*, _jclass*, int, _jbyteArray*, _jshortArray*, _jbyteArray*)
nativeColorMappingRGBWithTempStrtchClamp(_JNIEnv*, _jclass*, int, _jbyteArray*, _jshortArray*, _jbyteArray*)
nativeColorMappingRGBWithTempStrtchGray(_JNIEnv*, _jclass*, int, _jbyteArray*, _jshortArray*, _jbyteArray*)
nativeColorMappingStandAlong(_JNIEnv*, _jclass*, _jstring*, int, _jbyteArray*, _jbyteArray*)
nativeInit(_JNIEnv*, _jclass*, _jobject*)
nativeInitRgbTable(_JNIEnv*, _jclass*, _jstring*)
nativeSetTempRange(_JNIEnv*, _jclass*, float, float)
p2plusdome_sha1_sig
p2plus_sha1_sig
p2plus_teledome_sha1_sig
p2plus_telephoto_mobi
p2plus_telephoto_sha1_sig
registerNativeMethod(_JNIEnv*)
set_temp_range(unsigned short, unsigned short)
table_has_been_choosen
temp_has_been_set
temp_high_limit
temp_low_limit
tiny1c_2500
tiny1c_common
tiny1c_platform
void std::__ndk1::allocator<std::__ndk1::__hash_node<std::__ndk1::__hash_value_type<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> >, unsigned char*>, void*> >::construct<std::__ndk1::pair<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> > const, unsigned char*>, std::__ndk1::piecewise_construct_t const&, std::__ndk1::tuple<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> > const&>, std::__ndk1::tuple<> >(std::__ndk1::pair<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> > const, unsigned char*>*, std::__ndk1::piecewise_construct_t const&, std::__ndk1::tuple<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> > const&>&&, std::__ndk1::tuple<>&&)
void std::__ndk1::allocator<std::__ndk1::__hash_node<std::__ndk1::__hash_value_type<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> >, unsigned char*>, void*> >::construct<std::__ndk1::pair<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> > const, unsigned char*>, std::__ndk1::piecewise_construct_t const&, std::__ndk1::tuple<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> >&&>, std::__ndk1::tuple<> >(std::__ndk1::pair<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> > const, unsigned char*>*, std::__ndk1::piecewise_construct_t const&, std::__ndk1::tuple<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> >&&>&&, std::__ndk1::tuple<>&&)
void std::__ndk1::allocator_traits<std::__ndk1::allocator<std::__ndk1::__hash_node<std::__ndk1::__hash_value_type<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> >, unsigned char*>, void*> > >::construct<std::__ndk1::pair<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> > const, unsigned char*>, std::__ndk1::piecewise_construct_t const&, std::__ndk1::tuple<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> > const&>, std::__ndk1::tuple<> >(std::__ndk1::allocator<std::__ndk1::__hash_node<std::__ndk1::__hash_value_type<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> >, unsigned char*>, void*> >&, std::__ndk1::pair<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> > const, unsigned char*>*, std::__ndk1::piecewise_construct_t const&, std::__ndk1::tuple<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> > const&>&&, std::__ndk1::tuple<>&&)
void std::__ndk1::allocator_traits<std::__ndk1::allocator<std::__ndk1::__hash_node<std::__ndk1::__hash_value_type<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> >, unsigned char*>, void*> > >::__construct<std::__ndk1::pair<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> > const, unsigned char*>, std::__ndk1::piecewise_construct_t const&, std::__ndk1::tuple<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> > const&>, std::__ndk1::tuple<> >(std::__ndk1::integral_constant<bool, true>, std::__ndk1::allocator<std::__ndk1::__hash_node<std::__ndk1::__hash_value_type<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> >, unsigned char*>, void*> >&, std::__ndk1::pair<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> > const, unsigned char*>*, std::__ndk1::piecewise_construct_t const&, std::__ndk1::tuple<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> > const&>&&, std::__ndk1::tuple<>&&)
void std::__ndk1::allocator_traits<std::__ndk1::allocator<std::__ndk1::__hash_node<std::__ndk1::__hash_value_type<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> >, unsigned char*>, void*> > >::construct<std::__ndk1::pair<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> > const, unsigned char*>, std::__ndk1::piecewise_construct_t const&, std::__ndk1::tuple<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> >&&>, std::__ndk1::tuple<> >(std::__ndk1::allocator<std::__ndk1::__hash_node<std::__ndk1::__hash_value_type<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> >, unsigned char*>, void*> >&, std::__ndk1::pair<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> > const, unsigned char*>*, std::__ndk1::piecewise_construct_t const&, std::__ndk1::tuple<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> >&&>&&, std::__ndk1::tuple<>&&)
void std::__ndk1::allocator_traits<std::__ndk1::allocator<std::__ndk1::__hash_node<std::__ndk1::__hash_value_type<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> >, unsigned char*>, void*> > >::__construct<std::__ndk1::pair<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> > const, unsigned char*>, std::__ndk1::piecewise_construct_t const&, std::__ndk1::tuple<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> >&&>, std::__ndk1::tuple<> >(std::__ndk1::integral_constant<bool, true>, std::__ndk1::allocator<std::__ndk1::__hash_node<std::__ndk1::__hash_value_type<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> >, unsigned char*>, void*> >&, std::__ndk1::pair<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> > const, unsigned char*>*, std::__ndk1::piecewise_construct_t const&, std::__ndk1::tuple<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> >&&>&&, std::__ndk1::tuple<>&&)
void std::__ndk1::allocator_traits<std::__ndk1::allocator<std::__ndk1::__hash_node<std::__ndk1::__hash_value_type<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> >, unsigned char*>, void*> > >::destroy<std::__ndk1::pair<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> > const, unsigned char*> >(std::__ndk1::allocator<std::__ndk1::__hash_node<std::__ndk1::__hash_value_type<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> >, unsigned char*>, void*> >&, std::__ndk1::pair<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> > const, unsigned char*>*)
void std::__ndk1::allocator_traits<std::__ndk1::allocator<std::__ndk1::__hash_node<std::__ndk1::__hash_value_type<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> >, unsigned char*>, void*> > >::__destroy<std::__ndk1::pair<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> > const, unsigned char*> >(std::__ndk1::integral_constant<bool, false>, std::__ndk1::allocator<std::__ndk1::__hash_node<std::__ndk1::__hash_value_type<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> >, unsigned char*>, void*> >&, std::__ndk1::pair<std::__ndk1::basic_string<char, std::__ndk1::char_traits<char>, std::__ndk1::allocator<char> > const, unsigned char*>*)
YP0100
YP0103
YP0200
YP0203
YP0204
YP0300
YP0301
YP0303
YP0304
YP0400
YP0401
YP0402
YP0500
YP0501
YP0502
YP0503
YP0506
YP0600
YP0601
YP0700
YP0800
YP0900
YP0901
YP1000
YP1100
YP1200
YP1201
YP1204
YP1205
YP1300
YP1303
YP1304
YP1400
