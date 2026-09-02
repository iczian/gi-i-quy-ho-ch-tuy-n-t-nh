import numpy as np
import plotly.graph_objects as go
from methods.base import sap_xep_dinh_theo_goc, doi_phan_so

def giai_hinh_hoc(loai_hmt, c1, c2, ds_rb):
    """
    ds_rb: list of (a1, a2, dau, b) with dau in ['<=', '>=', '=']
    Returns: (status, cac_nghiem, z_toiuu, diem_hop_le)
    """
    M_lon = 1_000_000
    duong_thang = [(a1, a2, b) for (a1, a2, dau, b) in ds_rb]
    duong_thang.extend([(1, 0, M_lon), (-1, 0, M_lon), (0, 1, M_lon), (0, -1, M_lon)])

    giao_diem = []
    for i in range(len(duong_thang)):
        for j in range(i + 1, len(duong_thang)):
            dt1, dt2 = duong_thang[i], duong_thang[j]
            D = dt1[0] * dt2[1] - dt2[0] * dt1[1]
            if abs(D) > 1e-7:
                Dx = dt1[2] * dt2[1] - dt2[2] * dt1[1]
                Dy = dt1[0] * dt2[2] - dt2[0] * dt1[2]
                giao_diem.append((Dx / D, Dy / D))

    diem_ve = []
    for pt in giao_diem:
        x1, x2 = pt
        ok = True
        for (a1, a2, dau, b) in ds_rb:
            val = a1 * x1 + a2 * x2
            if dau in ['<=', '<'] and val > b + 1e-7:
                ok = False; break
            if dau in ['>=', '>'] and val < b - 1e-7:
                ok = False; break
            if dau == '=' and abs(val - b) > 1e-7:
                ok = False; break
        if ok:
            da_co = any(abs(pt[0] - d[0]) < 1e-7 and abs(pt[1] - d[1]) < 1e-7 for d in diem_ve)
            if not da_co:
                diem_ve.append(pt)

    if len(diem_ve) == 0:
        return "VO_NGHIEM", [], None, []

    gia_tri_z = [(c1 * pt[0] + c2 * pt[1], pt) for pt in diem_ve]
    if loai_hmt == 'max':
        z_toi_uu = max(v[0] for v in gia_tri_z)
    else:
        z_toi_uu = min(v[0] for v in gia_tri_z)

    nghiem_toi_uu_closure = [v[1] for v in gia_tri_z if abs(v[0] - z_toi_uu) < 1e-7]

    strict_valid_opt = []
    strict_invalid_opt = []
    for pt in nghiem_toi_uu_closure:
        x1, x2 = pt
        ok = True
        for (a1, a2, dau, b) in ds_rb:
            val = a1 * x1 + a2 * x2
            if dau == '<' and val >= b - 1e-7:
                ok = False; break
            if dau == '>' and val <= b + 1e-7:
                ok = False; break
        if ok:
            strict_valid_opt.append(pt)
        else:
            strict_invalid_opt.append(pt)

    if abs(z_toi_uu) > M_lon / 10:
        return "KHONG_GIOI_NOI", [], None, diem_ve

    if not strict_valid_opt and strict_invalid_opt:
        return "KHONG_DAT_TOI_UU_DO_BIEN_MO", strict_invalid_opt, z_toi_uu, diem_ve

    nghiem_thuc = []
    nghiem_ao = []
    for pt in strict_valid_opt:
        if abs(pt[0]) > M_lon - 100 or abs(pt[1]) > M_lon - 100:
            nghiem_ao.append(pt)
        else:
            nghiem_thuc.append(pt)

    if len(nghiem_thuc) == 0 and len(nghiem_ao) > 0:
        return "VO_SO_NGHIEM_DUONG_THANG", nghiem_ao[:2], z_toi_uu, diem_ve

    if len(nghiem_thuc) == 1 and len(nghiem_ao) > 0:
        return "VO_SO_NGHIEM_TIA", [nghiem_thuc[0], nghiem_ao[0]], z_toi_uu, diem_ve

    if len(nghiem_thuc) > 1:
        return "VO_SO_NGHIEM", nghiem_thuc, z_toi_uu, diem_ve

    return "NGHIEM_DUY_NHAT", nghiem_thuc, z_toi_uu, diem_ve

def ve_do_thi_hinh_hoc(c1, c2, loai_hmt, ds_rb, ket_qua, cac_nghiem, z_toiuu, diem_hop_le, z_hien_tai=None):
    """Vẽ đồ thị bằng Plotly"""
    fig = go.Figure()

    real_pts = [p for p in diem_hop_le if abs(p[0]) < 10000 and abs(p[1]) < 10000]
    if not real_pts:
        real_pts = [(0, 0), (5, 5)]
    min_x = min(p[0] for p in real_pts)
    max_x = max(p[0] for p in real_pts)
    min_y = min(p[1] for p in real_pts)
    max_y = max(p[1] for p in real_pts)
    
    if max_x - min_x < 4:
        cx = (min_x + max_x) / 2; min_x, max_x = cx - 4, cx + 4
    if max_y - min_y < 4:
        cy = (min_y + max_y) / 2; min_y, max_y = cy - 4, cy + 4
        
    pad_x = (max_x - min_x) * 0.35
    pad_y = (max_y - min_y) * 0.35
    xlim = (min_x - pad_x, max_x + pad_x)
    ylim = (min_y - pad_y, max_y + pad_y)
    
    x_arr = np.linspace(xlim[0], xlim[1], 400)

    PALETTE = ['#2563EB', '#DC2626', '#059669', '#7C3AED', '#D97706', '#0891B2']
    
    user_rb = [(a1, a2, dau, b) for (a1, a2, dau, b) in ds_rb
               if not (a1 == 1 and a2 == 0 and b == 0 and dau == '>=')
               and not (a1 == 0 and a2 == 1 and b == 0 and dau == '>=')]
    for idx, (a1, a2, dau, b) in enumerate(ds_rb):
        color = PALETTE[idx % len(PALETTE)]
        if a1 == 1 and a2 == 0 and b == 0 and dau == '>=':
            fig.add_vline(x=0, line_width=2, line_color='#888', opacity=0.6, name='x₁ ≥ 0')
        elif a1 == 0 and a2 == 1 and b == 0 and dau == '>=':
            fig.add_hline(y=0, line_width=2, line_color='#888', opacity=0.6, name='x₂ ≥ 0')
        else:
            rb_idx = user_rb.index((a1, a2, dau, b)) if (a1, a2, dau, b) in user_rb else idx
            lbl = f"RB {rb_idx+1}: {doi_phan_so(a1)}x₁ {'+ ' if a2 >= 0 else ''}{doi_phan_so(a2)}x₂ {dau} {doi_phan_so(b)}"
            line_dash = 'dash' if dau in ['<', '>'] else 'solid'
            if abs(a2) > 1e-9:
                y_arr = (b - a1 * x_arr) / a2
                fig.add_trace(go.Scatter(x=x_arr, y=y_arr, mode='lines', name=lbl, line=dict(color=color, width=3.5, dash=line_dash)))
            else:
                if abs(a1) > 1e-9:
                    fig.add_vline(x=b / a1, line_width=3.5, line_color=color, line_dash=line_dash, name=lbl)
    if len(diem_hop_le) >= 3:
        diem_sxep = sap_xep_dinh_theo_goc(list(diem_hop_le))
        x_poly = [pt[0] for pt in diem_sxep] + [diem_sxep[0][0]]
        y_poly = [pt[1] for pt in diem_sxep] + [diem_sxep[0][1]]
        fig.add_trace(go.Scatter(x=x_poly, y=y_poly, fill='toself', fillcolor='rgba(212,163,115,0.18)',
                                 line=dict(color='#C08B5C', width=1.5, dash='dash'), name='Miền khả thi'))
    elif len(diem_hop_le) == 2:
        pt1, pt2 = diem_hop_le
        fig.add_trace(go.Scatter(x=[pt1[0], pt2[0]], y=[pt1[1], pt2[1]], mode='lines',
                                 line=dict(color='#D4A373', width=3), opacity=0.5, name='Miền khả thi'))

    valid_x = [pt[0] for pt in diem_hop_le if abs(pt[0]) < 1e5 and abs(pt[1]) < 1e5]
    valid_y = [pt[1] for pt in diem_hop_le if abs(pt[0]) < 1e5 and abs(pt[1]) < 1e5]
    fig.add_trace(go.Scatter(x=valid_x, y=valid_y, mode='markers', name='Đỉnh khả thi',
                             marker=dict(color='#C08B5C', size=8, line=dict(color='white', width=1.5))))

    if cac_nghiem and ket_qua in ("NGHIEM_DUY_NHAT", "VO_SO_NGHIEM", "VO_SO_NGHIEM_TIA", "VO_SO_NGHIEM_DUONG_THANG", "KHONG_DAT_TOI_UU_DO_BIEN_MO"):
        opt_x = [pt[0] for pt in cac_nghiem if abs(pt[0]) <= 10000 and abs(pt[1]) <= 10000]
        opt_y = [pt[1] for pt in cac_nghiem if abs(pt[0]) <= 10000 and abs(pt[1]) <= 10000]
        
        texts = [f"({doi_phan_so(x)}, {doi_phan_so(y)})<br>Z{'&rarr;' if ket_qua == 'KHONG_DAT_TOI_UU_DO_BIEN_MO' else '='}{doi_phan_so(z_toiuu)}" for x, y in zip(opt_x, opt_y)]
        
        if ket_qua == "VO_SO_NGHIEM":
            fig.add_trace(go.Scatter(x=[pt[0] for pt in cac_nghiem], y=[pt[1] for pt in cac_nghiem], mode='lines',
                                     line=dict(color='#8B2500', width=4), opacity=0.7, name='Đoạn tối ưu'))
        elif ket_qua in ("VO_SO_NGHIEM_TIA", "VO_SO_NGHIEM_DUONG_THANG"):
            pt1 = cac_nghiem[0]
            pt2 = cac_nghiem[1]
            fig.add_trace(go.Scatter(x=[pt1[0], pt2[0]], y=[pt1[1], pt2[1]], mode='lines',
                                     line=dict(color='#8B2500', width=4), opacity=0.7, name='Tia/Đường tối ưu'))

        marker_symbol = 'x' if ket_qua == "KHONG_DAT_TOI_UU_DO_BIEN_MO" else 'star'
        marker_name = 'Đỉnh không đạt (Mở)' if ket_qua == "KHONG_DAT_TOI_UU_DO_BIEN_MO" else 'Nghiệm tối ưu'
        
        fig.add_trace(go.Scatter(x=opt_x, y=opt_y, mode='markers+text', name=marker_name,
                                 text=texts, textposition="top right",
                                 marker=dict(color='#8B2500', size=14, symbol=marker_symbol, line=dict(color='white', width=1.5))))

    z_ve = z_hien_tai if z_hien_tai is not None else z_toiuu
    if z_ve is None:
        z_ve = c1 * (xlim[0]+xlim[1])/2 + c2 * (ylim[0]+ylim[1])/2

    if abs(c1) > 1e-9 or abs(c2) > 1e-9:
        is_opt = False
        if z_hien_tai is None and z_toiuu is not None and abs(z_ve - z_toiuu) < 1e-5:
            is_opt = True
        lbl = f'Z = {doi_phan_so(z_ve)}' + (' (tối ưu)' if is_opt else ' (đường mức)')
        
        if abs(c2) > 1e-9:
            y_z = (z_ve - c1 * x_arr) / c2
            fig.add_trace(go.Scatter(x=x_arr, y=y_z, mode='lines', name=lbl,
                                     line=dict(color='#8B2500', width=1.8, dash='dot')))
        elif abs(c1) > 1e-9:
            x_z = z_ve / c1
            y_arr = np.linspace(ylim[0], ylim[1], 400)
            x_arr_z = np.full_like(y_arr, x_z)
            fig.add_trace(go.Scatter(x=x_arr_z, y=y_arr, mode='lines', name=lbl,
                                     line=dict(color='#8B2500', width=1.8, dash='dot')))

    fig.update_layout(
        title=f"Miền khả thi & Nghiệm tối ưu ({loai_hmt.upper()} Z)",
        xaxis_title="x₁",
        yaxis_title="x₂",
        plot_bgcolor='#fffbf7',
        paper_bgcolor='#fff8f3',
        xaxis=dict(range=xlim, showgrid=True, gridcolor='#eee', zeroline=True, zerolinecolor='#ccc'),
        yaxis=dict(range=ylim, showgrid=True, gridcolor='#eee', zeroline=True, zerolinecolor='#ccc'),
        legend=dict(bgcolor='rgba(255,255,255,0.9)', bordercolor='#D4A373', borderwidth=1),
        font=dict(color='#5E4B3C'),
        height=600,
        margin=dict(l=40, r=40, t=60, b=40)
    )

    return fig
