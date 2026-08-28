const API_BASE = "/api/solve";

let currentMethod = "simplex";
let varCount = 2;

// SPA Routing Elements
const navMainBtns = document.querySelectorAll('.nav-btn-main');
const spaViews = document.querySelectorAll('.spa-view');
const solverMethodsNav = document.getElementById('solver-methods-nav');

// Elements
const methodBtns = document.querySelectorAll('.nav-btn');
const methodDescription = document.getElementById('method-description');
const varCountInput = document.getElementById('n_goc');
const cInputsContainer = document.getElementById('c_inputs');
const rbInputsContainer = document.getElementById('rb_inputs');
const addRbBtn = document.getElementById('add-constraint-btn');
const boundInputsContainer = document.getElementById('bound_inputs');
const solveBtn = document.getElementById('solve-btn');
const resultsSection = document.getElementById('results-section');
const resultStatus = document.getElementById('result-status');
const resultDetails = document.getElementById('result-details');
const graphContainer = document.getElementById('graph-container');
const logsContainer = document.getElementById('logs-container');
const simplexLogs = document.getElementById('simplex-logs');
const spinner = document.getElementById('loading-spinner');

const methodInfo = {
    simplex: { name: "Phương pháp Đơn hình (Dantzig)", desc: "Thuật toán cơ bản giải bài toán QHTT dạng chuẩn." },
    bland: { name: "Phương pháp Bland", desc: "Tránh vòng lặp vô hạn trong các bài toán suy biến." },
    two_phase: { name: "Phương pháp 2 Pha", desc: "Áp dụng khi hệ thống ràng buộc không có phương án cơ sở khởi đầu." },
    geometric: { name: "Phương pháp Hình học", desc: "Giải trực quan bài toán QHTT có 2 biến bằng đồ thị." },
    convex_combo: { name: "Phương pháp Tổ hợp lồi", desc: "Biến đổi bài toán QHTT thành bài toán trên đoạn thẳng." }
};

// Examples Data (From cases.py)
const EXAMPLES = [
    {
        name: "Nghiệm duy nhất", desc: "Bài toán cơ bản, có một điểm cực biên tối ưu duy nhất.",
        loai_hmt: "max", n: 2, c_goc: [5.0, 4.0], dau_cac_bien: [">=", ">="],
        ds_rb: [ [[6.0, 4.0], "<=", 24.0], [[1.0, 2.0], "<=", 6.0], [[-1.0, 1.0], "<=", 1.0], [[0.0, 1.0], "<=", 2.0] ],
        phuong_phap: ["simplex", "bland", "geometric"]
    },
    {
        name: "Vô số nghiệm", desc: "Hàm mục tiêu song song với một cạnh của miền khả thi.",
        loai_hmt: "max", n: 2, c_goc: [3.0, 2.0], dau_cac_bien: [">=", ">="],
        ds_rb: [ [[6.0, 4.0], "<=", 24.0], [[1.0, 2.0], "<=", 6.0] ],
        phuong_phap: ["simplex", "bland", "geometric"]
    },
    {
        name: "Không giới nội", desc: "Miền khả thi mở, hàm mục tiêu có thể tăng đến vô cực.",
        loai_hmt: "max", n: 2, c_goc: [2.0, 1.0], dau_cac_bien: [">=", ">="],
        ds_rb: [ [[1.0, -1.0], "<=", 10.0], [[2.0, 0.0], "<=", 40.0] ],
        phuong_phap: ["simplex", "bland", "geometric"]
    },
    {
        name: "Vô nghiệm", desc: "Các ràng buộc mâu thuẫn, không có miền khả thi.",
        loai_hmt: "max", n: 2, c_goc: [3.0, 2.0], dau_cac_bien: [">=", ">="],
        ds_rb: [ [[1.0, 1.0], "<=", 2.0], [[1.0, 1.0], ">=", 4.0] ],
        phuong_phap: ["two_phase", "geometric"]
    },
    {
        name: "Cần 2 Pha (b < 0)", desc: "Vế phải âm hoặc ràng buộc >=, cần pha 1 để tìm phương án mồi.",
        loai_hmt: "min", n: 3, c_goc: [2.0, 3.0, 1.0], dau_cac_bien: [">=", ">=", ">="],
        ds_rb: [ [[1.0, 1.0, 1.0], ">=", 3.0], [[1.0, 2.0, 0.0], ">=", 2.0], [[0.0, 1.0, 2.0], ">=", 4.0] ],
        phuong_phap: ["two_phase"]
    },
    {
        name: "Xoay vòng suy biến", desc: "Bài toán kinh điển của Beale. Thuật toán Dantzig sẽ lặp vô hạn, phải dùng Quy tắc Bland.",
        loai_hmt: "max", n: 4, c_goc: [0.75, -20.0, 0.5, -6.0], dau_cac_bien: [">=", ">=", ">=", ">="],
        ds_rb: [ [[0.25, -8.0, -1.0, 9.0], "<=", 0.0], [[0.5, -12.0, -0.5, 3.0], "<=", 0.0], [[0.0, 0.0, 1.0, 0.0], "<=", 1.0] ],
        phuong_phap: ["bland", "simplex"]
    }
];

// Initialization
function init() {
    renderInputs();
    renderExamples();
    
    // SPA Navigation
    navMainBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active state
            navMainBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Show requested view
            const viewId = `view-${btn.dataset.view}`;
            spaViews.forEach(view => {
                view.classList.remove('active');
                if(view.id === viewId) view.classList.add('active');
            });
            
            // Toggle solver methods nav
            if (btn.dataset.view === 'solver') {
                solverMethodsNav.style.display = 'flex';
            } else {
                solverMethodsNav.style.display = 'none';
            }
        });
    });

    // Method selection
    methodBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            methodBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentMethod = btn.dataset.method;
            methodDescription.textContent = methodInfo[currentMethod].desc;
            
            // Save current data before re-rendering
            const currentData = getFormData();
            
            // Force varCount to 2 for geometric and convex
            if (currentMethod === 'geometric' || currentMethod === 'convex_combo') {
                if (varCount > 2) {
                    showToast(`Phương pháp ${methodInfo[currentMethod].name} chỉ hỗ trợ bài toán 2 biến. Hệ thống đã tự động cắt bỏ các biến dư thừa để tiếp tục.`);
                }
                varCount = 2;
                varCountInput.value = 2;
                document.getElementById('n_goc_col').style.display = 'none';
            } else {
                document.getElementById('n_goc_col').style.display = 'block';
            }
            
            renderInputs();
            restoreFormData(currentData);
            resultsSection.style.display = 'none';
        });
    });

    varCountInput.addEventListener('change', (e) => {
        varCount = parseInt(e.target.value) || 2;
        renderInputs();
    });

    addRbBtn.addEventListener('click', () => {
        addConstraintRow();
    });

    solveBtn.addEventListener('click', solveProblem);
}

function renderInputs() {
    // Render Objective Function (C)
    cInputsContainer.innerHTML = '';
    for (let i = 1; i <= varCount; i++) {
        cInputsContainer.innerHTML += `
            <div class="flex-row" style="gap: 0.25rem;">
                <input type="number" step="any" class="styled-input input-var c-val" value="0">
                <span class="var-label">x<sub>${i}</sub></span>
                ${i < varCount ? '<span style="color: var(--text-muted)">+</span>' : ''}
            </div>
        `;
    }

    // Initialize constraints (default 2)
    rbInputsContainer.innerHTML = '';
    addConstraintRow();
    addConstraintRow();

    // Render Variable Bounds
    boundInputsContainer.innerHTML = '';
    for (let i = 1; i <= varCount; i++) {
        boundInputsContainer.innerHTML += `
            <div class="flex-row" style="gap: 0.25rem;">
                <span class="var-label">x<sub>${i}</sub></span>
                <select class="styled-select bound-val">
                    <option value=">=">&ge; 0</option>
                    <option value="<=">&le; 0</option>
                    <option value="tuỳ ý">Tùy ý</option>
                </select>
            </div>
        `;
    }
}

function addConstraintRow() {
    const row = document.createElement('div');
    row.className = 'rb-row';
    
    let varsHtml = '';
    for (let i = 1; i <= varCount; i++) {
        varsHtml += `
            <input type="number" step="any" class="styled-input input-var a-val" value="0">
            <span class="var-label">x<sub>${i}</sub></span>
            ${i < varCount ? '<span style="color: var(--text-muted)">+</span>' : ''}
        `;
    }

    row.innerHTML = `
        <div class="flex-row" style="gap: 0.25rem; flex: 1;">
            ${varsHtml}
        </div>
        <select class="styled-select dau-val">
            <option value="<=">&le;</option>
            <option value="<">&lt;</option>
            <option value=">=">&ge;</option>
            <option value=">">&gt;</option>
            <option value="=">=</option>
        </select>
        <input type="number" step="any" class="styled-input input-var b-val" value="0">
        <button class="btn-remove" onclick="this.parentElement.remove()">✕</button>
    `;
    rbInputsContainer.appendChild(row);
    return row; // Return the row element for auto-filling
}

function renderExamples() {
    const grid = document.getElementById('examples-grid');
    grid.innerHTML = '';
    
    EXAMPLES.forEach((ex, idx) => {
        const methodsHtml = ex.phuong_phap.map(m => `<span class="methods-badge">${methodInfo[m] ? methodInfo[m].name : m}</span>`).join(' ');
        
        const card = document.createElement('div');
        card.className = 'example-card';
        card.innerHTML = `
            <h4>${ex.name}</h4>
            <p>${ex.desc}</p>
            <div style="margin-top: auto; display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem;">
                ${methodsHtml}
            </div>
            <button class="btn btn-secondary w-100" style="width: 100%; border: 1px solid var(--primary-color); color: var(--primary-color);" onclick="loadExample(${idx})">Chạy thử ví dụ</button>
        `;
        grid.appendChild(card);
    });
}

function loadExample(idx) {
    const ex = EXAMPLES[idx];
    
    // Switch to solver view
    document.querySelector('.nav-btn-main[data-view="solver"]').click();
    
    // Select the first recommended method
    const methodToSelect = ex.phuong_phap[0];
    document.querySelector(`.nav-btn[data-method="${methodToSelect}"]`).click();
    
    // Set basic params
    document.getElementById('loai_hmt').value = ex.loai_hmt;
    varCount = ex.n;
    varCountInput.value = ex.n;
    
    // Trigger render first to create inputs
    renderInputs();
    
    // Fill objective function
    const cInputs = document.querySelectorAll('.c-val');
    ex.c_goc.forEach((val, i) => {
        if (cInputs[i]) cInputs[i].value = val;
    });
    
    // Fill bounds
    const boundInputs = document.querySelectorAll('.bound-val');
    ex.dau_cac_bien.forEach((val, i) => {
        if (boundInputs[i]) boundInputs[i].value = val;
    });
    
    // Fill constraints
    rbInputsContainer.innerHTML = '';
    ex.ds_rb.forEach(rb => {
        const a_vals = rb[0];
        const dau = rb[1];
        const b = rb[2];
        
        const row = addConstraintRow();
        const aInputs = row.querySelectorAll('.a-val');
        a_vals.forEach((val, i) => {
            if (aInputs[i]) aInputs[i].value = val;
        });
        row.querySelector('.dau-val').value = dau;
        row.querySelector('.b-val').value = b;
    });
    
    // Hide results if open
    resultsSection.style.display = 'none';
}

function getFormData() {
    const loai_hmt = document.getElementById('loai_hmt').value;
    
    const mang_c_goc = Array.from(document.querySelectorAll('.c-val')).map(inp => parseFloat(inp.value) || 0);
    const dau_cac_bien = Array.from(document.querySelectorAll('.bound-val')).map(sel => sel.value);
    
    const rbRows = document.querySelectorAll('.rb-row');
    const ds_rb_vao = [];
    const ds_rb_hinh_hoc = []; // For geometric
    
    rbRows.forEach(row => {
        const a_vals = Array.from(row.querySelectorAll('.a-val')).map(inp => parseFloat(inp.value) || 0);
        const dau = row.querySelector('.dau-val').value;
        const b = parseFloat(row.querySelector('.b-val').value) || 0;
        
        ds_rb_vao.push([a_vals, dau, b]);
        // For geometric, format is (a1, a2, dau, b)
        if (a_vals.length >= 2) {
            ds_rb_hinh_hoc.push([a_vals[0], a_vals[1], dau, b]);
        }
    });

    return { loai_hmt, mang_c_goc, dau_cac_bien, ds_rb_vao, ds_rb_hinh_hoc };
}

function restoreFormData(data) {
    if (!data) return;
    
    document.getElementById('loai_hmt').value = data.loai_hmt || 'max';
    
    const cInputs = document.querySelectorAll('.c-val');
    data.mang_c_goc.forEach((val, i) => {
        if (cInputs[i]) cInputs[i].value = val;
    });
    
    const boundInputs = document.querySelectorAll('.bound-val');
    data.dau_cac_bien.forEach((val, i) => {
        if (boundInputs[i]) boundInputs[i].value = val;
    });
    
    rbInputsContainer.innerHTML = '';
    data.ds_rb_vao.forEach(rb => {
        const row = addConstraintRow();
        const aInputs = row.querySelectorAll('.a-val');
        rb[0].forEach((val, i) => {
            if (aInputs[i]) aInputs[i].value = val;
        });
        row.querySelector('.dau-val').value = rb[1];
        row.querySelector('.b-val').value = rb[2];
    });
    
    // Ensure at least one constraint row exists if empty
    if (rbInputsContainer.children.length === 0) {
        addConstraintRow();
    }
}

async function solveProblem() {
    const data = getFormData();
    
    let endpoint = `${API_BASE}/${currentMethod}`;
    let payload = {};

    if (currentMethod === 'geometric') {
        payload = {
            loai_hmt: data.loai_hmt,
            c1: data.mang_c_goc[0],
            c2: data.mang_c_goc[1],
            ds_rb: data.ds_rb_hinh_hoc,
            dau_cac_bien: data.dau_cac_bien
        };
    } else if (currentMethod === 'convex_combo') {
        // Requires exactly 2 constraints
        if (data.ds_rb_vao.length < 2) {
            alert("Phương pháp tổ hợp lồi yêu cầu ít nhất 2 ràng buộc.");
            return;
        }
        payload = {
            loai_hmt: data.loai_hmt,
            n_goc: varCount,
            mang_c_goc: data.mang_c_goc,
            dau_cac_bien: data.dau_cac_bien,
            he_so_rb1: data.ds_rb_vao[0][0],
            dau_rb1: data.ds_rb_vao[0][1],
            b1: data.ds_rb_vao[0][2],
            he_so_rb2: data.ds_rb_vao[1][0],
            dau_rb2: data.ds_rb_vao[1][1],
            b2: data.ds_rb_vao[1][2]
        };
    } else {
        payload = {
            loai_hmt: data.loai_hmt,
            n_goc: varCount,
            mang_c_goc: data.mang_c_goc,
            dau_cac_bien: data.dau_cac_bien,
            ds_rb_vao: data.ds_rb_vao
        };
    }

    spinner.style.display = 'block';
    solveBtn.disabled = true;

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const resData = await response.json();
        
        if (!response.ok) {
            throw new Error(resData.detail || "Có lỗi xảy ra khi giải toán.");
        }

        displayResults(resData);
    } catch (err) {
        resultStatus.style.display = 'block';
        resultStatus.className = 'status-banner status-danger';
        resultStatus.innerHTML = `Lỗi: ${err.message}`;
        
        // Clear old result data
        resultDetails.innerHTML = '';
        graphContainer.style.display = 'none';
        logsContainer.style.display = 'none';
        
        resultsSection.style.display = 'block';
    } finally {
        spinner.style.display = 'none';
        solveBtn.disabled = false;
        
        // Re-render MathJax
        if (window.MathJax) {
            MathJax.typesetPromise();
        }
    }
}

function displayResults(data) {
    resultsSection.style.display = 'block';
    resultStatus.style.display = 'block';
    resultDetails.innerHTML = '';
    graphContainer.style.display = 'none';
    logsContainer.style.display = 'none';

    // Status Banner
    const status = data.status;
    const is_vo_so = data.is_vo_so;
    
    if (status === 'VO_NGHIEM' || status === 'VO_NGHIEM_PHA_1') {
        resultStatus.className = 'status-banner status-danger';
        resultStatus.innerHTML = 'BÀI TOÁN VÔ NGHIỆM';
        const hmtType = document.getElementById('loai_hmt').value;
        const infinityStr = (hmtType === 'max') ? '-&infin;' : '+&infin;';
        resultDetails.innerHTML += `<div class="result-z" style="color: var(--danger); font-weight: bold; margin-bottom: 0.5rem;">Giá trị tối ưu: Z<sup>*</sup> = ${infinityStr}</div>`;
    } else if (status === 'VE_PHAI_AM') {
        resultStatus.className = 'status-banner status-danger';
        resultStatus.innerHTML = 'BÀI TOÁN CÓ VẾ PHẢI ÂM, HÃY DÙNG 2 PHA';
    } else if (status === 'VONG_LAP') {
        resultStatus.className = 'status-banner status-danger';
        resultStatus.innerHTML = 'PHÁT HIỆN XOAY VÒNG SUY BIẾN, HÃY DÙNG BLAND';
    } else if (status === 'KHONG_GIOI_NOI') {
        resultStatus.className = 'status-banner status-danger';
        resultStatus.innerHTML = 'BÀI TOÁN KHÔNG GIỚI NỘI';
    } else if (status === 'KHONG_DAT_TOI_UU_DO_BIEN_MO') {
        resultStatus.className = 'status-banner status-warning';
        resultStatus.innerHTML = 'BÀI TOÁN KHÔNG ĐẠT TỐI ƯU DO ĐỈNH NẰM TRÊN BIÊN MỞ';
    } else if (status === 'NGHIEM_DUY_NHAT' || (status === 'TOI_UU' && !is_vo_so)) {
        resultStatus.className = 'status-banner status-success';
        resultStatus.innerHTML = 'ĐÃ TÌM THẤY NGHIỆM TỐI ƯU DUY NHẤT';
    } else if (status.startsWith('VO_SO_NGHIEM') || (status === 'TOI_UU' && is_vo_so)) {
        resultStatus.className = 'status-banner status-warning';
        if (status === 'VO_SO_NGHIEM_TIA') {
            resultStatus.innerHTML = 'BÀI TOÁN CÓ VÔ SỐ NGHIỆM TRÊN MỘT TIA';
        } else if (status === 'VO_SO_NGHIEM_DUONG_THANG') {
            resultStatus.innerHTML = 'BÀI TOÁN CÓ VÔ SỐ NGHIỆM TRÊN MỘT ĐƯỜNG THẲNG';
        } else {
            resultStatus.innerHTML = 'BÀI TOÁN CÓ VÔ SỐ NGHIỆM';
        }
    } else {
        resultStatus.className = 'status-banner status-warning';
        resultStatus.innerHTML = status;
    }

    // Z and Solutions
    if ((data.z_str !== undefined && data.z_str !== null) || (data.z_toiuu !== undefined && data.z_toiuu !== null)) {
        let z_val = (data.z_str !== undefined && data.z_str !== null) ? data.z_str : data.z_toiuu;
        resultDetails.innerHTML += `<div class="result-z">Giá trị tối ưu: Z<sup>*</sup> = ${z_val}</div>`;
    }

    // For Simplex (array of floats/strings)
    if (data.nghiem_list && (!is_vo_so || !data.vo_so_info)) {
        let nghiem_str = data.nghiem_list.map((n, i) => `x<sub>${i+1}</sub> = ${n}`).join(', ');
        resultDetails.innerHTML += `<div style="font-size: 1.1rem; margin-top: 0.5rem;"><strong>Nghiệm tối ưu:</strong> (${nghiem_str})</div>`;
    } 
    // For Geometric (array of points)
    else if (data.cac_nghiem && status !== 'VO_SO_NGHIEM' && status !== 'VO_SO_NGHIEM_TIA' && status !== 'VO_SO_NGHIEM_DUONG_THANG') {
        resultDetails.innerHTML += '<ul>';
        data.cac_nghiem.forEach(pt => {
            resultDetails.innerHTML += `<li>(x₁, x₂) = (${parseFloat(pt[0]).toFixed(4)}, ${parseFloat(pt[1]).toFixed(4)})</li>`;
        });
        resultDetails.innerHTML += '</ul>';
    }

    if (data.vo_so_info) {
        if (typeof data.vo_so_info === 'string') {
            // String from geometric
            resultDetails.innerHTML += `<div class="mt-4 p-3" style="background: rgba(255,171,0,0.1); border-left: 4px solid var(--warning); border-radius: 4px; color: var(--text-main);">${data.vo_so_info}</div>`;
        } else if (typeof data.vo_so_info === 'object') {
            // Dict from simplex
            let html = '<div class="mt-4">';
            for (const key in data.vo_so_info) {
                const info = data.vo_so_info[key];
                html += `<div style="margin-bottom: 1rem; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 8px;">`;
                html += `<div style="font-weight: bold; color: var(--warning); margin-bottom: 0.5rem;">Biểu diễn theo tham số t (khi đưa ${info.ten_bien} vào cơ sở):</div>`;
                html += `<ul style="list-style: none; padding-left: 0;">`;
                info.lines.forEach(l => {
                    html += `<li>${l}</li>`;
                });
                html += `</ul></div>`;
            }
            html += '</div>';
            resultDetails.innerHTML += html;
        }
    }

    // Graph
    if (data.fig_json) {
        graphContainer.style.display = 'block';
        
        // Adapt Plotly layout for Light Theme and frame
        let fig = data.fig_json;
        fig.layout.paper_bgcolor = 'transparent';
        fig.layout.plot_bgcolor = 'transparent';
        fig.layout.font = { color: '#212529' };
        if (fig.layout.xaxis) {
            fig.layout.xaxis.gridcolor = 'rgba(0,0,0,0.05)';
            fig.layout.xaxis.zerolinecolor = 'rgba(0,0,0,0.6)';
            fig.layout.xaxis.zerolinewidth = 2;
            fig.layout.xaxis.showline = true;
            fig.layout.xaxis.linewidth = 1;
            fig.layout.xaxis.linecolor = 'rgba(0,0,0,0.3)';
            fig.layout.xaxis.mirror = true;
        }
        if (fig.layout.yaxis) {
            fig.layout.yaxis.gridcolor = 'rgba(0,0,0,0.05)';
            fig.layout.yaxis.zerolinecolor = 'rgba(0,0,0,0.6)';
            fig.layout.yaxis.zerolinewidth = 2;
            fig.layout.yaxis.showline = true;
            fig.layout.yaxis.linewidth = 1;
            fig.layout.yaxis.linecolor = 'rgba(0,0,0,0.3)';
            fig.layout.yaxis.mirror = true;
        }
        
        // Move legend below the graph and adjust margins to prevent cutoff
        fig.layout.legend = { 
            bgcolor: 'rgba(255,255,255,0.9)', 
            font: { color: '#212529' }, 
            bordercolor: 'rgba(0,0,0,0.2)', 
            borderwidth: 1,
            orientation: 'h',
            yanchor: 'top',
            y: -0.2,
            xanchor: 'center',
            x: 0.5
        };
        fig.layout.margin = { l: 60, r: 40, t: 60, b: 150 };

        let zTraceIndex = -1;
        if (currentMethod === 'geometric') {
            zTraceIndex = fig.data.findIndex(trace => trace.name && trace.name.startsWith('Z ='));
        }

        Plotly.newPlot('plotly-graph', fig.data, fig.layout, { responsive: true });

        // Add Slider Logic for Geometric
        const zSliderContainer = document.getElementById('z-slider-container');
        if (currentMethod === 'geometric' && zSliderContainer) {
            const c1 = data.c1 !== undefined ? data.c1 : (parseFloat(document.querySelectorAll('.c-val')[0].value) || 0);
            const c2 = data.c2 !== undefined ? data.c2 : (parseFloat(document.querySelectorAll('.c-val')[1].value) || 0);
            
            if (zTraceIndex >= 0) {
                zSliderContainer.style.display = 'flex';
                const slider = document.getElementById('z-slider');
                const zValDisplay = document.getElementById('z-slider-value');
                
                let xlim = fig.layout.xaxis.range;
                let ylim = fig.layout.yaxis.range;
                let z1 = c1*xlim[0] + c2*ylim[0];
                let z2 = c1*xlim[0] + c2*ylim[1];
                let z3 = c1*xlim[1] + c2*ylim[0];
                let z4 = c1*xlim[1] + c2*ylim[1];
                let minZ = Math.min(z1, z2, z3, z4);
                let maxZ = Math.max(z1, z2, z3, z4);
                
                slider.min = minZ;
                slider.max = maxZ;
                slider.step = (maxZ - minZ) / 1000;
                slider.value = data.z_toiuu !== null ? data.z_toiuu : (minZ + maxZ) / 2;
                
                zValDisplay.innerText = parseFloat(slider.value).toFixed(2);
                
                const graphDiv = document.getElementById('plotly-graph');
                
                // Xoá các event listener cũ nếu chạy nhiều lần
                const newSlider = slider.cloneNode(true);
                slider.parentNode.replaceChild(newSlider, slider);
                
                newSlider.addEventListener('input', function() {
                    try {
                        let newZ = parseFloat(this.value);
                        let update = {};
                        
                        let pts = 400;
                        let x_arr = [];
                        let y_arr = [];

                        if (Math.abs(c2) > 1e-9) {
                            for(let i=0; i<pts; i++) {
                                let x_val = xlim[0] + i*(xlim[1]-xlim[0])/(pts-1);
                                x_arr.push(x_val);
                                y_arr.push((newZ - c1 * x_val) / c2);
                            }
                            update = {x: [x_arr], y: [y_arr], name: [`Z = ${newZ.toFixed(2)} (đường mức)`]};
                        } else if (Math.abs(c1) > 1e-9) {
                            for(let i=0; i<pts; i++) {
                                let y_val = ylim[0] + i*(ylim[1]-ylim[0])/(pts-1);
                                y_arr.push(y_val);
                                x_arr.push(newZ / c1);
                            }
                            update = {x: [x_arr], y: [y_arr], name: [`Z = ${newZ.toFixed(2)} (đường mức)`]};
                        }
                        
                        Plotly.restyle('plotly-graph', update, [zTraceIndex]);
                        zValDisplay.innerText = newZ.toFixed(2);
                    } catch(e) {
                        zValDisplay.innerText = "Lỗi: " + e.message;
                        console.error(e);
                    }
                });
            } else {
                zSliderContainer.style.display = 'none';
            }
        } else if (zSliderContainer) {
            zSliderContainer.style.display = 'none';
        }
    } else {
        const zSliderContainer = document.getElementById('z-slider-container');
        if (zSliderContainer) zSliderContainer.style.display = 'none';
    }

    // Logs
    if (data.log_lines && data.log_lines.length > 0) {
        logsContainer.style.display = 'block';
        if (typeof marked !== 'undefined') {
            marked.use({ breaks: true });
            simplexLogs.innerHTML = marked.parse(data.log_lines.join('\n'));
        } else {
            simplexLogs.innerHTML = data.log_lines.join('\n');
        }
    }
}

// Start
init();

// Utilities
function showToast(message) {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `<span style="font-weight: bold; color: var(--warning);">Lưu ý:</span> <div>${message}</div>`;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('toast-closing');
        toast.addEventListener('animationend', () => {
            toast.remove();
        });
    }, 5000);
}
