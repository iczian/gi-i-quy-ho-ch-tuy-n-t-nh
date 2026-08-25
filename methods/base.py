import math
import numpy as np
from fractions import Fraction

def doi_phan_so(he_so):
    if he_so is None: return "Không xác định"
    try:
        if abs(he_so) < 1e-9:
            return "0"
        f = Fraction(he_so).limit_denominator(1000)
        if f.denominator == 1:
            return str(f.numerator)
        return f"{f.numerator}/{f.denominator}"
    except:
        return f"{he_so:.4f}"

def format_coef_var(he_so, ten_bien):
    if abs(he_so) < 1e-9:
        return ""
    chuoi_ps = doi_phan_so(abs(he_so))
    if chuoi_ps == "1":
        chuoi_ps = ""
    dau = "+" if he_so > 0 else "-"
    return f"{dau} {chuoi_ps}{ten_bien}"

def format_terms_latex(coefs, vars):
    terms = []
    for c, v in zip(coefs, vars):
        if abs(c) > 1e-9:
            s = doi_phan_so(abs(c))
            if s == "1": s = ""
            terms.append(f"+ {s}{v}" if c > 0 else f"- {s}{v}")
    if not terms: return "0"
    res = " ".join(terms)
    if res.startswith("+ "): res = res[2:]
    return res

def xoay_ma_tran(ma_tran_a, mang_b, mang_c, v, tap_n, tap_b, r, c):
    p = float(ma_tran_a[r, c])
    m, n = ma_tran_a.shape
    a_moi = np.zeros((m, n))
    b_moi = np.zeros(m)
    c_moi = np.zeros(n)
    b_moi[r] = mang_b[r] / p
    for j in range(n):
        if j != c:
            a_moi[r, j] = ma_tran_a[r, j] / p
    a_moi[r, c] = 1.0 / p
    for i in range(m):
        if i != r:
            b_moi[i] = mang_b[i] - ma_tran_a[i, c] * b_moi[r]
            for j in range(n):
                if j != c:
                    a_moi[i, j] = ma_tran_a[i, j] - ma_tran_a[i, c] * a_moi[r, j]
            a_moi[i, c] = -ma_tran_a[i, c] / p
    v_moi = v + mang_c[c] * b_moi[r]
    for j in range(n):
        if j != c:
            c_moi[j] = mang_c[j] - mang_c[c] * a_moi[r, j]
    c_moi[c] = -mang_c[c] / p
    n_moi = list(tap_n)
    b_moi_tap = list(tap_b)
    n_moi[c], b_moi_tap[r] = tap_b[r], tap_n[c]
    return a_moi, b_moi, c_moi, v_moi, n_moi, b_moi_tap

def tao_chuoi_chuan_tac_text_thuong(c_chuan, a_tam_sau_tach, ds_vp, ten_bien_n, m_rb_moi):
    lines = []
    z_terms = format_terms_latex(c_chuan, ten_bien_n)
    lines.append(f"- Hàm Z: $Min\\; z = {z_terms}$")
    for i in range(m_rb_moi):
        rb_terms = format_terms_latex(a_tam_sau_tach[i], ten_bien_n)
        lines.append(f"- PT{i+1}: ${rb_terms} \\le {doi_phan_so(ds_vp[i])}$")
    vars_str = ", ".join(f"${v}$" for v in ten_bien_n)
    lines.append(f"*(Điều kiện: Tất cả {vars_str} $\\ge 0$)*")
    return "\n\n".join(lines)

def tao_chuoi_tu_vung(tap_n, tap_b, ma_tran_a, mang_b, mang_c, v, ten_bien, tieu_de, ten_ham="z"):
    lines = [f"**{tieu_de}**"]
    
    z_row = f"- ${ten_ham} = {doi_phan_so(v)}"
    for j in range(len(tap_n)):
        hs = mang_c[j]
        if abs(hs) > 1e-9:
            dau = "+" if hs > 0 else "-"
            chuoi_ps = doi_phan_so(abs(hs))
            if chuoi_ps == "1": chuoi_ps = ""
            term = f"{chuoi_ps}{ten_bien[tap_n[j]]}"
            z_row += f" {dau} {term}"
    z_row += "$"
    if z_row.endswith("= $"): z_row = z_row[:-2] + "0$"
    lines.append(z_row)
    
    for i in range(len(tap_b)):
        w_row = f"- ${ten_bien[tap_b[i]]} = {doi_phan_so(mang_b[i])}"
        for j in range(len(tap_n)):
            hs = -ma_tran_a[i, j]
            if abs(hs) > 1e-9:
                dau = "+" if hs > 0 else "-"
                chuoi_ps = doi_phan_so(abs(hs))
                if chuoi_ps == "1": chuoi_ps = ""
                term = f"{chuoi_ps}{ten_bien[tap_n[j]]}"
                w_row += f" {dau} {term}"
        w_row += "$"
        lines.append(w_row)
        
    return "\n\n".join(lines)

def tinh_vo_so_nghiem(tap_n, tap_b, ma_tran_a, mang_b, danh_sach_vo_so,
                       so_bien_n_chuan, luu_vet_vi_tri, luu_vet_dau, n_goc, ten_bien):
    """Tính biểu diễn nghiệm vô số theo tham số t."""
    result = {}
    for j_zero in danh_sach_vo_so:
        ten_bien_tham_so = ten_bien[tap_n[j_zero]]
        lines = []
        upper_bound = float('inf')
        for i in range(len(tap_b)):
            a_val = ma_tran_a[i, j_zero]
            if a_val > 1e-9:
                upper_bound = min(upper_bound, mang_b[i] / a_val)
        if upper_bound == float('inf'):
            lines.append("Điều kiện của t: $t \\ge 0$")
        else:
            lines.append(f"Điều kiện của t: $0 \\le t \\le {doi_phan_so(upper_bound)}$")
        for i_goc in range(n_goc):
            he_so_t = 0.0
            gia_tri_hang_so = 0.0
            for idx_chuan in range(so_bien_n_chuan):
                if luu_vet_vi_tri[idx_chuan] == i_goc:
                    dk = luu_vet_dau[idx_chuan]
                    if idx_chuan == tap_n[j_zero]:
                        he_so_t += dk * 1.0
                    elif idx_chuan in tap_b:
                        vi_tri_hang = tap_b.index(idx_chuan)
                        gia_tri_hang_so += dk * mang_b[vi_tri_hang]
                        he_so_t += dk * (-ma_tran_a[vi_tri_hang, j_zero])
            he_so_t_str = ""
            if abs(he_so_t) > 1e-9:
                dau_hs = "+" if he_so_t > 0 else "-"
                hs_val = doi_phan_so(abs(he_so_t))
                if hs_val == "1":
                    hs_val = ""
                he_so_t_str = f" {dau_hs} {hs_val}t"
            gia_tri_hang_str = doi_phan_so(gia_tri_hang_so)
            if gia_tri_hang_so == 0 and he_so_t_str:
                he_so_t_str = he_so_t_str.strip()
                if he_so_t_str.startswith("+ "):
                    he_so_t_str = he_so_t_str[2:]
                lines.append(f"$x_{{{i_goc+1}}} = {he_so_t_str}$")
            elif gia_tri_hang_so == 0:
                lines.append(f"$x_{{{i_goc+1}}} = 0$")
            else:
                lines.append(f"$x_{{{i_goc+1}}} = {gia_tri_hang_str}{he_so_t_str}$")
        result[j_zero] = {"ten_bien": ten_bien_tham_so, "lines": lines}
    return result

def sap_xep_dinh_theo_goc(cac_diem):
    if len(cac_diem) == 0:
        return []
    tam_x = sum(d[0] for d in cac_diem) / len(cac_diem)
    tam_y = sum(d[1] for d in cac_diem) / len(cac_diem)
    cac_diem.sort(key=lambda d: math.atan2(d[1] - tam_y, d[0] - tam_x))
    return cac_diem

def khoi_tao_bai_toan_don_hinh(loai_hmt, n_goc, mang_c_goc, dau_cac_bien, ds_rb_vao):
    log = []
    m_rb = len(ds_rb_vao)
    mang_c_goc = list(mang_c_goc)

    log.append("**Chuẩn hóa bài toán**")
    if loai_hmt == 'max':
        log.append("$\\rightarrow$ Chuyển Max về Min: $Max\\; Z = -Min(-Z)$")
        mang_c_goc = [-x for x in mang_c_goc]

    c_chuan, ten_bien_n, luu_vet_vi_tri, luu_vet_dau = [], [], [], []
    a_tam_sau_bien = [[] for _ in range(m_rb)]

    for i in range(n_goc):
        s = dau_cac_bien[i]
        if s == '<=':
            c_chuan.append(-mang_c_goc[i])
            for k in range(m_rb):
                a_tam_sau_bien[k].append(-ds_rb_vao[k][0][i])
            ten_bien_n.append(f"x'_{{{i+1}}}")
            luu_vet_vi_tri.append(i); luu_vet_dau.append(-1)
        elif s == 'tuy_y':
            c_chuan.append(mang_c_goc[i])
            for k in range(m_rb):
                a_tam_sau_bien[k].append(ds_rb_vao[k][0][i])
            ten_bien_n.append(f"x_{{{i+1}}}^+")
            luu_vet_vi_tri.append(i); luu_vet_dau.append(1)
            c_chuan.append(-mang_c_goc[i])
            for k in range(m_rb):
                a_tam_sau_bien[k].append(-ds_rb_vao[k][0][i])
            ten_bien_n.append(f"x_{{{i+1}}}^-")
            luu_vet_vi_tri.append(i); luu_vet_dau.append(-1)
        else:
            c_chuan.append(mang_c_goc[i])
            for k in range(m_rb):
                a_tam_sau_bien[k].append(ds_rb_vao[k][0][i])
            ten_bien_n.append(f"x_{{{i+1}}}")
            luu_vet_vi_tri.append(i); luu_vet_dau.append(1)

    a_tam_sau_tach, ds_vp = [], []
    for i in range(m_rb):
        dau_rb = ds_rb_vao[i][1]
        b_val = ds_rb_vao[i][2]
        if dau_rb == '=':
            a_tam_sau_tach.append(a_tam_sau_bien[i])
            ds_vp.append(b_val)
            a_tam_sau_tach.append([-x for x in a_tam_sau_bien[i]])
            ds_vp.append(-b_val)
        elif dau_rb == '>=':
            a_tam_sau_tach.append([-x for x in a_tam_sau_bien[i]])
            ds_vp.append(-b_val)
        else:
            a_tam_sau_tach.append(a_tam_sau_bien[i])
            ds_vp.append(b_val)

    m_rb_moi = len(a_tam_sau_tach)
    for i in range(m_rb_moi):
        log.append(f"- Thêm biến bù $w_{{{i+1}}}$ cho ràng buộc {i+1}")

    log.append(tao_chuoi_chuan_tac_text_thuong(c_chuan, a_tam_sau_tach, ds_vp, ten_bien_n, m_rb_moi))

    ten_bien_b_names = [f"w_{{{i+1}}}" for i in range(m_rb_moi)]
    so_bien_goc_chuan = len(c_chuan)
    
    ma_tran_a = np.zeros((m_rb_moi, so_bien_goc_chuan))
    mang_b = np.zeros(m_rb_moi)
    for i in range(m_rb_moi):
        ma_tran_a[i, :] = a_tam_sau_tach[i]
        mang_b[i] = ds_vp[i]

    ten_bien = ten_bien_n + ten_bien_b_names
    tap_n = list(range(so_bien_goc_chuan))
    tap_b = list(range(so_bien_goc_chuan, so_bien_goc_chuan + m_rb_moi))

    mang_c = np.zeros(so_bien_goc_chuan)
    for i in range(so_bien_goc_chuan):
        mang_c[i] = c_chuan[i]

    return {
        'ma_tran_a': ma_tran_a, 'mang_b': mang_b, 'mang_c': mang_c,
        'tap_n': tap_n, 'tap_b': tap_b, 'ten_bien': ten_bien,
        'luu_vet_vi_tri': luu_vet_vi_tri, 'luu_vet_dau': luu_vet_dau,
        'c_chuan': c_chuan, 'a_tam_sau_tach': a_tam_sau_tach,
        'ds_vp': ds_vp, 'ten_bien_n': ten_bien_n, 'm_rb_moi': m_rb_moi,
        'log': log
    }
