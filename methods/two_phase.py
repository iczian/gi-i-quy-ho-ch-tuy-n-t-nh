import numpy as np
from methods.base import (
    tao_chuoi_chuan_tac_text_thuong,
    tao_chuoi_tu_vung,
    xoay_ma_tran,
    doi_phan_so,
    tinh_vo_so_nghiem,
    format_terms_latex,
    khoi_tao_bai_toan_don_hinh
)

def giai_don_hinh_2_pha(loai_hmt, n_goc, mang_c_goc, dau_cac_bien, ds_rb_vao):
    """Hỗ trợ ràng buộc >= (vế phải âm sau chuẩn hóa)."""
    data = khoi_tao_bai_toan_don_hinh(loai_hmt, n_goc, mang_c_goc, dau_cac_bien, ds_rb_vao)
    ma_tran_a, mang_b, mang_c = data['ma_tran_a'], data['mang_b'], data['mang_c']
    tap_n, tap_b, ten_bien = data['tap_n'], data['tap_b'], data['ten_bien']
    luu_vet_vi_tri, luu_vet_dau = data['luu_vet_vi_tri'], data['luu_vet_dau']
    c_chuan = data['c_chuan']
    ten_bien_n = data['ten_bien_n']
    a_tam_sau_tach = data['a_tam_sau_tach']
    ds_vp = data['ds_vp']
    m_rb_moi = data['m_rb_moi']
    log = data['log']
    so_bien_goc_chuan = len(c_chuan)

    mang_c_goc_day_du = np.zeros(len(ten_bien))
    for i in range(len(c_chuan)):
        mang_c_goc_day_du[i] = c_chuan[i]

    can_pha_1 = any(b < -1e-9 for b in mang_b)
    log.append("")

    if not can_pha_1:
        log.append(">> Không có vế phải âm $\\rightarrow$ Bỏ qua Pha 1.")
        mang_c = np.array(c_chuan, dtype=float)
        gia_tri_v = 0.0
    else:
        log.append("---")
        idx_x0 = len(ten_bien)
        ten_bien.append("x_0")
        tap_n.append(idx_x0)
        ma_tran_a = np.hstack((ma_tran_a, np.ones((m_rb_moi, 1)) * -1.0))
        mang_c_pha1 = np.zeros(len(tap_n))
        mang_c_pha1[-1] = 1.0
        gia_tri_v1 = 0.0

        log.append("--- PHA 1 ---")
        
        lines_bt = []
        lines_bt.append(f"- Hàm W: $Min\\; W = x_0$")
        for i in range(m_rb_moi):
            rb_terms = format_terms_latex(a_tam_sau_tach[i], ten_bien_n)
            lines_bt.append(f"- PT{i+1}: ${rb_terms} - x_0 \\le {doi_phan_so(ds_vp[i])}$")
        vars_str = ", ".join(f"${v}$" for v in ten_bien_n)
        lines_bt.append(f"*(Điều kiện: Tất cả $x_0$, {vars_str} $\\ge 0$)*")
        
        log.append("**Bài toán bổ trợ (P'_BT):**")
        log.append("\n\n".join(lines_bt))
        
        log.append(tao_chuoi_tu_vung(tap_n, tap_b, ma_tran_a, mang_b, mang_c_pha1, gia_tri_v1, ten_bien, "Từ vựng xuất phát:", "W"))
        
        c = len(tap_n) - 1
        r = int(np.argmin(mang_b))
        log.append(f"**Biến vào:** $x_0$ — **Biến ra:** ${ten_bien[tap_b[r]]}$")
        ma_tran_a, mang_b, mang_c_pha1, gia_tri_v1, tap_n, tap_b = xoay_ma_tran(ma_tran_a, mang_b, mang_c_pha1, gia_tri_v1, tap_n, tap_b, r, c)

        vong_lap_p1 = 1
        while True:
            log.append(tao_chuoi_tu_vung(tap_n, tap_b, ma_tran_a, mang_b, mang_c_pha1, gia_tri_v1, ten_bien, f"Từ vựng Pha 1 (xoay {vong_lap_p1}):", "W"))
            c = -1; nho_nhat = -1e-9
            for j in range(len(tap_n)):
                if mang_c_pha1[j] < nho_nhat:
                    nho_nhat = mang_c_pha1[j]; c = j
            if c == -1:
                break
            r = -1; ti_so_min = float('inf')
            chuoi_ti_so = []
            for i in range(len(tap_b)):
                if ma_tran_a[i, c] > 1e-9:
                    ti_so = mang_b[i] / ma_tran_a[i, c]
                    if ti_so < ti_so_min - 1e-9:
                        ti_so_min = ti_so; r = i
            min_ti_so_str = doi_phan_so(ti_so_min)
            str_ti_so_all = ", ".join(chuoi_ti_so)
            log.append(f"**Biến vào:** ${ten_bien[tap_n[c]]}$ — **Biến ra:** ${ten_bien[tap_b[r]]}$ — **Tỉ số:** ${min_ti_so_str}$")
            ma_tran_a, mang_b, mang_c_pha1, gia_tri_v1, tap_n, tap_b = xoay_ma_tran(ma_tran_a, mang_b, mang_c_pha1, gia_tri_v1, tap_n, tap_b, r, c)
            vong_lap_p1 += 1

        if gia_tri_v1 > 1e-9:
            log.append(f"**Kết luận Pha 1:** $W^* = {doi_phan_so(gia_tri_v1)} > 0$ $\\rightarrow$ **Bài toán vô nghiệm.**")
            return "VO_NGHIEM_PHA_1", None, None, False, log, {}

        log.append(f"**Pha 1 kết thúc:** $W^* = 0$")
        log.append(f"Loại bỏ $x_0$.")

        if idx_x0 in tap_b:
            r_x0 = tap_b.index(idx_x0)
            duoi_ok = False
            for j in range(len(tap_n)):
                if abs(ma_tran_a[r_x0, j]) > 1e-9:
                    ma_tran_a, mang_b, mang_c_pha1, gia_tri_v1, tap_n, tap_b = xoay_ma_tran(ma_tran_a, mang_b, mang_c_pha1, gia_tri_v1, tap_n, tap_b, r_x0, j)
                    duoi_ok = True; break
            if not duoi_ok:
                ma_tran_a = np.delete(ma_tran_a, r_x0, axis=0)
                mang_b = np.delete(mang_b, r_x0)
                tap_b.pop(r_x0)

        if idx_x0 in tap_n:
            vi_tri_x0 = tap_n.index(idx_x0)
            tap_n.pop(vi_tri_x0)
            ma_tran_a = np.delete(ma_tran_a, vi_tri_x0, axis=1)

        gia_tri_v = 0.0
        mang_c = np.zeros(len(tap_n))
        for i in range(len(tap_b)):
            if tap_b[i] < len(mang_c_goc_day_du):
                gia_tri_v += mang_c_goc_day_du[tap_b[i]] * mang_b[i]
        for j in range(len(tap_n)):
            hs_moi = mang_c_goc_day_du[tap_n[j]] if tap_n[j] < len(mang_c_goc_day_du) else 0.0
            for i in range(len(tap_b)):
                if tap_b[i] < len(mang_c_goc_day_du):
                    hs_moi -= mang_c_goc_day_du[tap_b[i]] * ma_tran_a[i, j]
            mang_c[j] = hs_moi
        
        log.append("**Khôi phục hàm $z$ gốc:**")
        
        z_khoi_phuc = format_terms_latex(mang_c, [ten_bien[idx] for idx in tap_n])
        z_v_str = doi_phan_so(gia_tri_v)
        if z_v_str != "0":
            z_khoi_phuc = f"{z_v_str} {'+ ' + z_khoi_phuc if not z_khoi_phuc.startswith('-') else z_khoi_phuc}"
        log.append(f"$\\quad z = {z_khoi_phuc}$")
        log.append("")

    log.append("---")
    log.append("**--- PHA 2 ---**")
    is_vo_so = False; danh_sach_vo_so = []
    vong_lap_p2 = 1

    while True:
        log.append(tao_chuoi_tu_vung(tap_n, tap_b, ma_tran_a, mang_b, mang_c, gia_tri_v, ten_bien, f"Từ vựng Pha 2 (xoay {vong_lap_p2}):"))
        c = -1; nho_nhat = -1e-9
        for j in range(len(tap_n)):
            if mang_c[j] < nho_nhat:
                nho_nhat = mang_c[j]; c = j
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
        r = -1; ti_so_min = float('inf'); co_hs_duong = False
        chuoi_ti_so = []
        for i in range(len(tap_b)):
            if ma_tran_a[i, c] > 1e-9:
                co_hs_duong = True
                ti_so = mang_b[i] / ma_tran_a[i, c]
                if ti_so < ti_so_min - 1e-9:
                    ti_so_min = ti_so; r = i
        if not co_hs_duong:
            return "KHONG_GIOI_NOI", None, None, False, log, {}
        
        min_ti_so_str = doi_phan_so(ti_so_min)
        str_ti_so_all = ", ".join(chuoi_ti_so)
        log.append(f"**Biến vào:** ${ten_bien[tap_n[c]]}$ — **Biến ra:** ${ten_bien[tap_b[r]]}$ — **Tỉ số:** ${min_ti_so_str}$")
        ma_tran_a, mang_b, mang_c, gia_tri_v, tap_n, tap_b = xoay_ma_tran(ma_tran_a, mang_b, mang_c, gia_tri_v, tap_n, tap_b, r, c)
        vong_lap_p2 += 1

    z_ket_qua = -gia_tri_v if loai_hmt == 'max' else gia_tri_v
    z_str = doi_phan_so(z_ket_qua)
    mang_x_chuan = np.zeros(len(ten_bien))
    for i in range(len(tap_b)):
        if tap_b[i] < len(mang_x_chuan):
            mang_x_chuan[tap_b[i]] = mang_b[i]
    mang_x_goc = [0.0] * n_goc
    for i in range(so_bien_goc_chuan):
        mang_x_goc[luu_vet_vi_tri[i]] += luu_vet_dau[i] * mang_x_chuan[i]
    vo_so_info = {}
    if is_vo_so:
        vo_so_info = tinh_vo_so_nghiem(tap_n, tap_b, ma_tran_a, mang_b, danh_sach_vo_so,
                                        so_bien_goc_chuan, luu_vet_vi_tri, luu_vet_dau, n_goc, ten_bien)
    return "TOI_UU", z_str, mang_x_goc, is_vo_so, log, vo_so_info
