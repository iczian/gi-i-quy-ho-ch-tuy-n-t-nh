import numpy as np
from scipy.spatial import ConvexHull
import plotly.graph_objects as go
from methods.base import doi_phan_so

def giai_to_hop_loi(loai_hmt, n_goc, dau_cac_bien, arr_C, arr_A1, dau_rb1, b1, arr_A2, dau_rb2, b2):
    log = []
    
    C_chuan, A1_chuan, A2_chuan = [], [], []
    ten_bien_chuan = []
    vet_idx = [] 
    vet_dau = [] 
    tong_so_bien = n_goc 

    for i in range(n_goc):
        s = dau_cac_bien[i]
        if s == '=':
            pass 
        elif s == '<=':
            C_chuan.append(-arr_C[i]); A1_chuan.append(-arr_A1[i]); A2_chuan.append(-arr_A2[i])
            ten_bien_chuan.append(f"x'_{i+1}")
            vet_idx.append(i); vet_dau.append(-1)
        elif s == 'tuy_y':
            C_chuan.append(arr_C[i]); A1_chuan.append(arr_A1[i]); A2_chuan.append(arr_A2[i])
            ten_bien_chuan.append(f"x_{i+1}^+")
            vet_idx.append(i); vet_dau.append(1)
            
            C_chuan.append(-arr_C[i]); A1_chuan.append(-arr_A1[i]); A2_chuan.append(-arr_A2[i])
            ten_bien_chuan.append(f"x_{i+1}^-")
            vet_idx.append(i); vet_dau.append(-1)
        else: 
            C_chuan.append(arr_C[i]); A1_chuan.append(arr_A1[i]); A2_chuan.append(arr_A2[i])
            ten_bien_chuan.append(f"x_{i+1}")
            vet_idx.append(i); vet_dau.append(1)

    if dau_rb1 == '<=':
        tong_so_bien += 1
        A1_chuan.append(1.0); A2_chuan.append(0.0); C_chuan.append(0.0)
        ten_bien_chuan.append(f"x_{tong_so_bien}")
        vet_idx.append(tong_so_bien - 1); vet_dau.append(1)
    elif dau_rb1 == '>=':
        tong_so_bien += 1
        A1_chuan.append(-1.0); A2_chuan.append(0.0); C_chuan.append(0.0)
        ten_bien_chuan.append(f"x_{tong_so_bien}")
        vet_idx.append(tong_so_bien - 1); vet_dau.append(1)

    if dau_rb2 == '<=':
        tong_so_bien += 1
        A1_chuan.append(0.0); A2_chuan.append(1.0); C_chuan.append(0.0)
        ten_bien_chuan.append(f"x_{tong_so_bien}")
        vet_idx.append(tong_so_bien - 1); vet_dau.append(1)
    elif dau_rb2 == '>=':
        tong_so_bien += 1
        A1_chuan.append(0.0); A2_chuan.append(-1.0); C_chuan.append(0.0)
        ten_bien_chuan.append(f"x_{tong_so_bien}")
        vet_idx.append(tong_so_bien - 1); vet_dau.append(1)

    def in_phuong_trinh(arr_he_so, ve_phai, ten_cac_bien):
        cac_so_hang = []
        for i, c in enumerate(arr_he_so):
            if abs(c) > 0.000001:
                chuoi_f = doi_phan_so(c)
                if chuoi_f == "1":
                    cac_so_hang.append(f"+ {ten_cac_bien[i]}")
                elif chuoi_f == "-1":
                    cac_so_hang.append(f"- {ten_cac_bien[i]}")
                elif chuoi_f.startswith("-"):
                    cac_so_hang.append(f"- {chuoi_f[1:]}{ten_cac_bien[i]}")
                else:
                    cac_so_hang.append(f"+ {chuoi_f}{ten_cac_bien[i]}")
                    
        if not cac_so_hang:
            return f"0 = {doi_phan_so(ve_phai)}"
        
        chuoi_pt = " ".join(cac_so_hang)
        if chuoi_pt.startswith("+ "): chuoi_pt = chuoi_pt[2:]
        if chuoi_pt.startswith("- "): chuoi_pt = "-" + chuoi_pt[2:]
        return chuoi_pt + f" = {doi_phan_so(ve_phai)}"

    log.append("**Bước 1: Đổi hệ thành phương trình dấu bằng**")
    log.append(f"- PT1: ${in_phuong_trinh(A1_chuan, b1, ten_bien_chuan)}$")
    log.append(f"- PT2: ${in_phuong_trinh(A2_chuan, b2, ten_bien_chuan)}$")
    log.append(f"- Hàm Z: ${in_phuong_trinh(C_chuan, 0, ten_bien_chuan).replace(' = 0', '').strip()}$")
    log.append(f"*(Điều kiện: Tất cả {', '.join('$' + v + '$' for v in ten_bien_chuan)} $\\ge 0$)*")

    log.append("**Bước 2: Tổng 2 phương trình**")
    arr_PT_tong = [A1_chuan[i] + A2_chuan[i] for i in range(len(A1_chuan))]
    b_tong = b1 + b2
    if abs(b_tong) < 0.000001:
        log.append("**Lỗi:** Tổng b1 + b2 = 0, không thể áp dụng phương pháp này.")
        return "LOI", log, {}

    log.append(f"- PT Tổng: ${in_phuong_trinh(arr_PT_tong, b_tong, ten_bien_chuan)}$")
    log.append(f"- PT Chọn (PT2): ${in_phuong_trinh(A2_chuan, b2, ten_bien_chuan)}$")

    log.append("**Bước 3: Chia 2 vế PT tổng để tạo điều kiện chuẩn**")
    arr_W = [a / b_tong for a in arr_PT_tong]
    log.append(f"- PT Tổng (b=1): ${in_phuong_trinh(arr_W, 1, ten_bien_chuan)}$")

    log.append("**Bước 4: Đặt $\\lambda$**")
    ten_bien_lamda = [f"\\lambda_{{{i+1}}}" for i in range(len(arr_W))]
    for i in range(len(arr_W)):
        if arr_W[i] > 0.000001:
            log.append(f"- Đặt $\\lambda_{{{i+1}}} = {doi_phan_so(arr_W[i])}{ten_bien_chuan[i]} \\implies {ten_bien_chuan[i]} = \\frac{{\\lambda_{{{i+1}}}}}{{{doi_phan_so(arr_W[i])}}}$")
        else:
            log.append(f"- *Bỏ qua $\\lambda_{{{i+1}}}$ vì hệ số W $\\le$ 0 (Không tạo thành điểm cực biên hợp lệ).*")

    log.append("**Bước 5: Biến đổi phương trình theo $\\lambda$**")
    PT2_theo_lamda, Z_theo_lamda = [], []
    for i in range(len(arr_W)):
        if arr_W[i] > 0.000001:
            PT2_theo_lamda.append(A2_chuan[i] / arr_W[i])
            Z_theo_lamda.append(C_chuan[i] / arr_W[i])
        else:
            PT2_theo_lamda.append(0)
            Z_theo_lamda.append(0)

    bien_lamda_hop_le = [lam for i, lam in enumerate(ten_bien_lamda) if arr_W[i] > 0.000001]
    if not bien_lamda_hop_le:
        log.append("**Lỗi:** Không tồn tại hệ số $\\lambda$ nào hợp lệ. Bài toán không thể giải tiếp.")
        return "LOI", log, {}
        
    log.append(f"- PT Tổng $\\lambda$: ${' + '.join(bien_lamda_hop_le)} = 1$")
    log.append(f"- PT2 (theo $\\lambda$): ${in_phuong_trinh(PT2_theo_lamda, b2, ten_bien_lamda)}$")
    log.append(f"- Hàm Z (theo $\\lambda$): $Z = {in_phuong_trinh(Z_theo_lamda, 0, ten_bien_lamda).replace(' = 0', '').strip()}$")

    log.append("**Bước 6: Xác định tọa độ các điểm $A_j$**")
    cac_toa_do_A = []
    for i in range(len(arr_W)):
        if arr_W[i] > 0.000001:
            log.append(f"- Điểm $A_{{{i+1}}}$: $({doi_phan_so(PT2_theo_lamda[i])}, {doi_phan_so(Z_theo_lamda[i])})$")
            cac_toa_do_A.append((i, PT2_theo_lamda[i], Z_theo_lamda[i]))

    log.append(f"**Bước 7: Tìm giao điểm với đường $X = {doi_phan_so(b2)}$**")
    Z_toi_uu = float('inf') if loai_hmt == 'min' else float('-inf')
    cap_canh_chon = None
    gia_tri_lamda = (0, 0)
    
    for pt in cac_toa_do_A:
        idx, xi, yi = pt
        if abs(xi - b2) < 0.000001:
            if (loai_hmt == 'min' and yi < Z_toi_uu) or (loai_hmt == 'max' and yi > Z_toi_uu):
                Z_toi_uu = yi; cap_canh_chon = (idx, idx); gia_tri_lamda = (1.0, 0.0)

    for i in range(len(cac_toa_do_A)):
        for j in range(i+1, len(cac_toa_do_A)):
            idx_i, xi, yi = cac_toa_do_A[i]
            idx_j, xj, yj = cac_toa_do_A[j]
            if min(xi, xj) - 0.000001 <= b2 <= max(xi, xj) + 0.000001 and abs(xi - xj) > 0.000001:
                lam_j = (b2 - xi) / (xj - xi)
                lam_i = 1.0 - lam_j
                z_test = lam_i * yi + lam_j * yj
                if (loai_hmt == 'min' and z_test < Z_toi_uu) or (loai_hmt == 'max' and z_test > Z_toi_uu):
                    Z_toi_uu = z_test; cap_canh_chon = (idx_i, idx_j); gia_tri_lamda = (lam_i, lam_j)

    if cap_canh_chon is None:
        log.append("**Lỗi:** Đường thẳng X không cắt đa giác. Bài toán vô nghiệm!")
        return "VO_NGHIEM", log, {}

    i1, i2 = cap_canh_chon
    l1, l2 = gia_tri_lamda
    if i1 != i2:
        log.append(f"$\\implies$ Giao điểm tối ưu nằm trên cạnh $A_{{{i1+1}}}$ và $A_{{{i2+1}}}$.")
        log.append(f"$\\implies$ Tính được: $\\lambda_{{{i1+1}}} = {doi_phan_so(l1)}$, $\\lambda_{{{i2+1}}} = {doi_phan_so(l2)}$")
    else:
        log.append(f"$\\implies$ Giao điểm tối ưu trùng với đỉnh $A_{{{i1+1}}}$.")
        log.append(f"$\\implies \\lambda_{{{i1+1}}} = 1$")

        log.append("**Bước 8: Kết luận cực trị địa phương**")
    arr_x_chuan_out = [0.0] * len(arr_W)
    arr_x_chuan_out[i1] = l1 / arr_W[i1]
    if i1 != i2:
        arr_x_chuan_out[i2] = l2 / arr_W[i2]

    arr_x_logic_out = [0.0] * tong_so_bien
    for i, std_val in enumerate(arr_x_chuan_out):
        index_thuc = vet_idx[i]
        sign_nhan = vet_dau[i]
        arr_x_logic_out[index_thuc] += sign_nhan * std_val

    for i in range(tong_so_bien):
        log.append(f"- $x_{{{i+1}}} = {doi_phan_so(arr_x_logic_out[i])}$")
        
    log.append(f"**$\\implies {loai_hmt.upper()} Z = {doi_phan_so(Z_toi_uu)}$**")

    from methods.simplex import giai_don_hinh_dantzig
    ds_rb_vao = [(arr_A1, dau_rb1, b1), (arr_A2, dau_rb2, b2)]
    status_check, _, _, _, _, _ = giai_don_hinh_dantzig(loai_hmt, n_goc, arr_C, dau_cac_bien, ds_rb_vao)
    
    if status_check == "KHONG_GIOI_NOI":
        log.append("---")
        log.append("Mặc dù phương pháp Tổ hợp lồi tìm được cực trị, nhưng miền khả thi thực chất là mở (tồn tại tia cực biên).")
        log.append("Nhìn lại Bước 4, có biến đã bị bỏ qua do hệ số $W \\le 0$. Nếu đi dọc theo các biến này, hàm mục tiêu sẽ tăng/giảm ra tới vô cực mà không vi phạm ràng buộc!")
        log.append(f"**Kết luận:** Bài toán KHÔNG GIỚI NỘI.")
        return "KHONG_GIOI_NOI", log, {}

    plot_data = {
        'cac_toa_do_A': cac_toa_do_A,
        'b2': b2,
        'Z_toi_uu': Z_toi_uu,
        'loai_hmt': loai_hmt,
        'cap_canh_chon': cap_canh_chon,
        'PT2_theo_lamda': PT2_theo_lamda,
        'Z_theo_lamda': Z_theo_lamda,
        'arr_x_logic_out': arr_x_logic_out,
        'tong_so_bien': tong_so_bien
    }

    return "TOI_UU", log, plot_data
def ve_do_thi_to_hop_loi(plot_data):
    """Vẽ đồ thị Tổ hợp lồi bằng Plotly"""
    fig = go.Figure()

    cac_toa_do_A = plot_data['cac_toa_do_A']
    b2 = plot_data['b2']
    Z_toi_uu = plot_data['Z_toi_uu']
    loai_hmt = plot_data['loai_hmt']
    cap_canh_chon = plot_data['cap_canh_chon']
    PT2_theo_lamda = plot_data['PT2_theo_lamda']
    Z_theo_lamda = plot_data['Z_theo_lamda']

    mang_toa_do = np.array([(pt[1], pt[2]) for pt in cac_toa_do_A])
    
    if len(mang_toa_do) >= 3:
        try:
            khung_bao = ConvexHull(mang_toa_do)
            x_hull = np.append(mang_toa_do[khung_bao.vertices, 0], mang_toa_do[khung_bao.vertices[0], 0])
            y_hull = np.append(mang_toa_do[khung_bao.vertices, 1], mang_toa_do[khung_bao.vertices[0], 1])
            fig.add_trace(go.Scatter(x=x_hull, y=y_hull, fill='toself', fillcolor='rgba(212,163,115,0.15)',
                                     mode='lines', line=dict(color='#D4A373', width=2), name='Bao lồi'))
        except:
            fig.add_trace(go.Scatter(x=mang_toa_do[:, 0], y=mang_toa_do[:, 1], mode='lines',
                                     line=dict(color='#D4A373', width=2), name='Đường nối'))
    elif len(mang_toa_do) == 2:
        fig.add_trace(go.Scatter(x=mang_toa_do[:, 0], y=mang_toa_do[:, 1], mode='lines',
                                 line=dict(color='#D4A373', width=2), name='Đoạn thẳng'))

    x_pts = [pt[1] for pt in cac_toa_do_A]
    y_pts = [pt[2] for pt in cac_toa_do_A]
    texts = [f"A{pt[0]+1}" for pt in cac_toa_do_A]
    
    fig.add_trace(go.Scatter(x=x_pts, y=y_pts, mode='markers+text', name='Các đỉnh A',
                             text=texts, textposition="top center",
                             marker=dict(color='#C08B5C', size=10)))

    if len(y_pts) > 0:
        y_min, y_max = min(y_pts), max(y_pts)
        pad = (y_max - y_min) * 0.2 if y_max > y_min else 2
        fig.add_vline(x=b2, line_width=2, line_dash='dash', line_color='#2ca02c', name=f'Đường X = {doi_phan_so(b2)}')
    
    fig.add_trace(go.Scatter(x=[b2], y=[Z_toi_uu], mode='markers', name=f'Tối ưu Z = {doi_phan_so(Z_toi_uu)}',
                             marker=dict(color='#8B2500', size=16, symbol='star')))
    
    if cap_canh_chon:
        i1, i2 = cap_canh_chon
        if i1 != i2:
            fig.add_trace(go.Scatter(x=[PT2_theo_lamda[i1], PT2_theo_lamda[i2]], 
                                     y=[Z_theo_lamda[i1], Z_theo_lamda[i2]], 
                                     mode='lines', name='Cạnh chứa nghiệm',
                                     line=dict(color='#8B2500', width=3)))

    fig.update_layout(
        title=f"Đồ thị Tổ Hợp Lồi ({loai_hmt.upper()})",
        xaxis_title="Giá trị PT2",
        yaxis_title="Hàm Z",
        plot_bgcolor='#fffbf7',
        paper_bgcolor='#fff8f3',
        xaxis=dict(showgrid=True, gridcolor='#eee'),
        yaxis=dict(showgrid=True, gridcolor='#eee'),
        legend=dict(bgcolor='rgba(255,255,255,0.9)', bordercolor='#D4A373', borderwidth=1),
        font=dict(color='#5E4B3C'),
        height=600,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig
