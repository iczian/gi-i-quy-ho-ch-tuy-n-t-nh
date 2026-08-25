from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Tuple, Any
from fastapi.middleware.cors import CORSMiddleware
import os
import json

from methods.simplex import giai_don_hinh_dantzig
from methods.bland import giai_don_hinh_bland
from methods.two_phase import giai_don_hinh_2_pha
from methods.geometric import giai_hinh_hoc, ve_do_thi_hinh_hoc
from methods.convex_combo import giai_to_hop_loi, ve_do_thi_to_hop_loi
from methods.base import doi_phan_so

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimplexRequest(BaseModel):
    loai_hmt: str
    n_goc: int
    mang_c_goc: List[float]
    dau_cac_bien: List[str]
    ds_rb_vao: List[Tuple[List[float], str, float]]

@app.post("/api/solve/simplex")
def solve_simplex(req: SimplexRequest):
    try:
        status, z_str, nghiem_list, is_vo_so, log_lines, vo_so_info = giai_don_hinh_dantzig(
            req.loai_hmt, req.n_goc, req.mang_c_goc, req.dau_cac_bien, req.ds_rb_vao
        )
        return {
            "status": status,
            "z_str": z_str,
            "nghiem_list": nghiem_list,
            "is_vo_so": is_vo_so,
            "log_lines": log_lines,
            "vo_so_info": vo_so_info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/solve/bland")
def solve_bland(req: SimplexRequest):
    try:
        status, z_str, nghiem_list, is_vo_so, log_lines, vo_so_info = giai_don_hinh_bland(
            req.loai_hmt, req.n_goc, req.mang_c_goc, req.dau_cac_bien, req.ds_rb_vao
        )
        return {
            "status": status,
            "z_str": z_str,
            "nghiem_list": nghiem_list,
            "is_vo_so": is_vo_so,
            "log_lines": log_lines,
            "vo_so_info": vo_so_info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/solve/two_phase")
def solve_twophase(req: SimplexRequest):
    try:
        status, z_str, nghiem_list, is_vo_so, log_lines, vo_so_info = giai_don_hinh_2_pha(
            req.loai_hmt, req.n_goc, req.mang_c_goc, req.dau_cac_bien, req.ds_rb_vao
        )
        return {
            "status": status,
            "z_str": z_str,
            "nghiem_list": nghiem_list,
            "is_vo_so": is_vo_so,
            "log_lines": log_lines,
            "vo_so_info": vo_so_info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class GeometricRequest(BaseModel):
    loai_hmt: str
    c1: float
    c2: float
    ds_rb: List[Tuple[float, float, str, float]]
    dau_cac_bien: List[str]

@app.post("/api/solve/geometric")
def solve_geometric(req: GeometricRequest):
    try:
        ds_rb_hinh_hoc = list(req.ds_rb)
        if req.dau_cac_bien[0] == ">=": ds_rb_hinh_hoc.append((1.0, 0.0, ">=", 0.0))
        elif req.dau_cac_bien[0] == "<=": ds_rb_hinh_hoc.append((1.0, 0.0, "<=", 0.0))
        if req.dau_cac_bien[1] == ">=": ds_rb_hinh_hoc.append((0.0, 1.0, ">=", 0.0))
        elif req.dau_cac_bien[1] == "<=": ds_rb_hinh_hoc.append((0.0, 1.0, "<=", 0.0))

        status, cac_nghiem, z_toiuu, diem_hop_le = giai_hinh_hoc(req.loai_hmt, req.c1, req.c2, ds_rb_hinh_hoc)
        
        vo_so_info = ""
        if status in ("VO_SO_NGHIEM", "VO_SO_NGHIEM_TIA", "VO_SO_NGHIEM_DUONG_THANG") and len(cac_nghiem) >= 2:
            pt1 = cac_nghiem[0]
            pt2 = cac_nghiem[1]
            # Tim phuong trinh duong thang
            eq = ""
            for (a1, a2, dau, b) in ds_rb_hinh_hoc:
                if abs(a1*pt1[0] + a2*pt1[1] - b) < 1e-5 and abs(a1*pt2[0] + a2*pt2[1] - b) < 1e-5:
                    eq = f"{doi_phan_so(a1)}x₁ {'+ ' if a2>=0 else '- '}{doi_phan_so(abs(a2))}x₂ = {doi_phan_so(b)}"
                    break
            
            if not eq:
                a = pt1[1] - pt2[1]
                b = pt2[0] - pt1[0]
                d = a*pt1[0] + b*pt1[1]
                eq = f"{doi_phan_so(a)}x₁ {'+ ' if b>=0 else '- '}{doi_phan_so(abs(b))}x₂ = {doi_phan_so(d)}"

            if status == "VO_SO_NGHIEM":
                vo_so_info = f"Hàm mục tiêu đạt giá trị tối ưu (Z={doi_phan_so(z_toiuu)}) trên toàn bộ **đoạn thẳng** nối 2 đỉnh ({doi_phan_so(pt1[0])}, {doi_phan_so(pt1[1])}) và ({doi_phan_so(pt2[0])}, {doi_phan_so(pt2[1])}).<br>Đoạn thẳng này nằm trên đường thẳng: <b>{eq}</b>"
            elif status == "VO_SO_NGHIEM_TIA":
                vo_so_info = f"Hàm mục tiêu đạt giá trị tối ưu (Z={doi_phan_so(z_toiuu)}) trên **tia** xuất phát từ đỉnh ({doi_phan_so(pt1[0])}, {doi_phan_so(pt1[1])}) kéo dài ra vô tận.<br>Tia này nằm trên đường thẳng: <b>{eq}</b>"
            else:
                vo_so_info = f"Hàm mục tiêu đạt giá trị tối ưu (Z={doi_phan_so(z_toiuu)}) trên **đường thẳng** kéo dài ra vô tận có phương trình:<br><b>{eq}</b>"

        fig = ve_do_thi_hinh_hoc(req.c1, req.c2, req.loai_hmt, ds_rb_hinh_hoc, status, cac_nghiem, z_toiuu, diem_hop_le, z_hien_tai=z_toiuu)
        fig_json = json.loads(fig.to_json())

        return {
            "status": status,
            "cac_nghiem": cac_nghiem,
            "z_toiuu": z_toiuu,
            "fig_json": fig_json,
            "ds_rb_hinh_hoc": ds_rb_hinh_hoc,
            "vo_so_info": vo_so_info,
            "c1": req.c1,
            "c2": req.c2
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class ConvexRequest(BaseModel):
    loai_hmt: str
    n_goc: int
    mang_c_goc: List[float]
    dau_cac_bien: List[str]
    he_so_rb1: List[float]
    dau_rb1: str
    b1: float
    he_so_rb2: List[float]
    dau_rb2: str
    b2: float

@app.post("/api/solve/convex_combo")
def solve_convex_combo(req: ConvexRequest):
    try:
        status, log_lines, plot_data = giai_to_hop_loi(
            req.loai_hmt, req.n_goc, req.dau_cac_bien, req.mang_c_goc, 
            req.he_so_rb1, req.dau_rb1, req.b1, 
            req.he_so_rb2, req.dau_rb2, req.b2
        )
        
        fig_json = None
        if status == "TOI_UU" and plot_data:
            fig = ve_do_thi_to_hop_loi(plot_data)
            fig_json = json.loads(fig.to_json())
            
        return {
            "status": status,
            "log_lines": log_lines,
            "fig_json": fig_json
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Mount static files for frontend
if not os.path.exists("frontend"):
    os.makedirs("frontend")

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
