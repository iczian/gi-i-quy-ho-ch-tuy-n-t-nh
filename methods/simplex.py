import numpy as np
from methods.base import (
    tao_chuoi_chuan_tac_text_thuong,
    tao_chuoi_tu_vung,
    xoay_ma_tran,
    doi_phan_so,
    tinh_vo_so_nghiem,
    khoi_tao_bai_toan_don_hinh
)

def giai_don_hinh_dantzig(loai_hmt, n_goc, mang_c_goc, dau_cac_bien, ds_rb_vao):
    """
    ds_rb_vao[i] = (list_he_so, dau, b)  dau in ['<=', '>=']
    Returns: (status, z_str, nghiem_list, is_vo_so, log_lines, vo_so_info)
    """
    data = khoi_tao_bai_toan_don_hinh(loai_hmt, n_goc, mang_c_goc, dau_cac_bien, ds_rb_vao)
    ma_tran_a, mang_b, mang_c = data['ma_tran_a'], data['mang_b'], data['mang_c']
    tap_n, tap_b, ten_bien = data['tap_n'], data['tap_b'], data['ten_bien']
    luu_vet_vi_tri, luu_vet_dau = data['luu_vet_vi_tri'], data['luu_vet_dau']
    log = data['log']
    so_bien_n_chuan = len(data['c_chuan'])
    v = 0.0

    log.append("")
    log.append(tao_chuoi_tu_vung(tap_n, tap_b, ma_tran_a, mang_b, mang_c, v, ten_bien, "Từ vựng xuất phát:"))

    if any(b < -1e-9 for b in mang_b):
        return "VE_PHAI_AM", None, None, False, log, {}

    is_vo_so = False
    danh_sach_vo_so = []
    lich_su = []
    vong_lap = 1

    while True:
        co_so_ht = tuple(sorted(tap_b))
        if co_so_ht in lich_su:
            return "VONG_LAP", None, None, False, log, {}
        lich_su.append(co_so_ht)

        c = -1
        min_val = 0
        for j in range(len(tap_n)):
            if mang_c[j] < -1e-9 and mang_c[j] < min_val:
                min_val = mang_c[j]; c = j

        if c == -1:
            log.append(">> Tất cả hệ số $\\bar{c}_j \\ge 0$ → **Đã tối ưu.**")
            tap_vo_so = []
            for j in range(len(tap_n)):
                if abs(mang_c[j]) < 1e-9:
                    ub = float('inf')
                    for i in range(len(tap_b)):
                        if ma_tran_a[i, j] > 1e-9:
                            ub = min(ub, mang_b[i] / ma_tran_a[i, j])
                    if ub > 1e-9:
                        tap_vo_so.append(j)
            if tap_vo_so:
                is_vo_so = True; danh_sach_vo_so = tap_vo_so
            break

        ten_bien_vao = ten_bien[tap_n[c]]
        r = -1; min_ti_so = float('inf'); co_hs_duong = False
        for i in range(len(tap_b)):
            if ma_tran_a[i, c] > 1e-9:
                co_hs_duong = True
                ti_so = mang_b[i] / ma_tran_a[i, c]
                if ti_so < min_ti_so:
                    min_ti_so = ti_so; r = i

        if not co_hs_duong:
            return "KHONG_GIOI_NOI", None, None, False, log, {}

        ten_bien_ra = ten_bien[tap_b[r]]
        log.append(f"**Biến vào:** ${ten_bien_vao}$ — **Biến ra:** ${ten_bien_ra}$ — Tỷ số: ${doi_phan_so(min_ti_so)}$")
        ma_tran_a, mang_b, mang_c, v, tap_n, tap_b = xoay_ma_tran(ma_tran_a, mang_b, mang_c, v, tap_n, tap_b, r, c)
        vong_lap += 1
        log.append(tao_chuoi_tu_vung(tap_n, tap_b, ma_tran_a, mang_b, mang_c, v, ten_bien, f"Từ vựng sau lần xoay {vong_lap-1}:"))

    z_ket_qua = -v if loai_hmt == 'max' else v
    z_str = doi_phan_so(z_ket_qua)
    mang_x_chuan = np.zeros(len(ten_bien))
    for i in range(len(tap_b)):
        mang_x_chuan[tap_b[i]] = mang_b[i]
    mang_x_goc = [0.0] * n_goc
    for i in range(so_bien_n_chuan):
        mang_x_goc[luu_vet_vi_tri[i]] += luu_vet_dau[i] * mang_x_chuan[i]

    vo_so_info = {}
    if is_vo_so:
        vo_so_info = tinh_vo_so_nghiem(tap_n, tap_b, ma_tran_a, mang_b, danh_sach_vo_so,
                                        so_bien_n_chuan, luu_vet_vi_tri, luu_vet_dau, n_goc, ten_bien)
    return "TOI_UU", z_str, mang_x_goc, is_vo_so, log, vo_so_info
