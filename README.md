# Hệ Thống Trực Quan Hóa Và Giải Bài Toán Quy Hoạch Tuyến Tính

## Tổng Quan Dự Án

Dự án này cung cấp một hệ thống phần mềm dựa trên nền tảng web, được thiết kế nhằm hỗ trợ giải quyết và minh họa chi tiết các bước giải của bài toán Quy hoạch tuyến tính.

Với mục tiêu phục vụ công tác nghiên cứu, giảng dạy và học tập trong các học phần Tối ưu hóa và Vận trù học, hệ thống không chỉ đưa ra nghiệm tối ưu cuối cùng mà còn trình bày quá trình tính toán một cách tường minh, chặt chẽ về mặt toán học thông qua bảng biến đổi và đồ thị.

## Các Thuật Toán Được Tích Hợp

Hệ thống hỗ trợ thực thi và diễn giải các phương pháp tiếp cận kinh điển trong Tối ưu hóa tuyến tính:

&nbsp;&nbsp;&nbsp;&nbsp;Thuật toán Đơn hình: Trình bày chi tiết quá trình lặp để tìm phương án tối ưu thông qua việc di chuyển giữa các phương án cực biên liền kề trên đa diện lồi, kèm theo sự biến đổi của bảng đơn hình ở mỗi bước.

&nbsp;&nbsp;&nbsp;&nbsp;Quy tắc Bland: Cung cấp tiêu chuẩn chọn biến vào và biến ra nhằm khắc phục hiện tượng xoay vòng và sự thoái hóa trong thuật toán đơn hình, qua đó đảm bảo tính hội tụ của bài toán trong một số hữu hạn bước.

&nbsp;&nbsp;&nbsp;&nbsp;Phương pháp Hai pha: Giải quyết các bài toán Quy hoạch tuyến tính không có sẵn phương án cực biên xuất phát bằng cách đưa thêm hệ thống các biến nhân tạo và thiết lập hàm mục tiêu phụ ở Pha 1 để tìm phương án cơ bản khả thi, trước khi tiến hành tối ưu ở Pha 2.

&nbsp;&nbsp;&nbsp;&nbsp;Phương pháp Hình học: Phân tích hình học trên mặt phẳng tọa độ đối với bài toán hai biến. Trực quan hóa hệ bất phương trình ràng buộc thành một đa diện lồi chứa tập phương án chấp nhận được và mô phỏng sự dịch chuyển của các đường mức hàm mục tiêu để xác định điểm cực trị.

&nbsp;&nbsp;&nbsp;&nbsp;Phương pháp Tổ hợp lồi: Xác định và biểu diễn tập nghiệm tối ưu dựa trên tính chất tổ hợp lồi của các đỉnh, minh họa cho Định lý biểu diễn đa diện lồi.

## Kiến Trúc Và Công Nghệ Sử Dụng

&nbsp;&nbsp;&nbsp;&nbsp;Lõi tính toán: Python, kết hợp cùng các thư viện toán học NumPy, SciPy để xử lý ma trận và tính toán số học. Khung làm việc FastAPI và Uvicorn được sử dụng để xây dựng các giao diện lập trình ứng dụng hiệu năng cao.

&nbsp;&nbsp;&nbsp;&nbsp;Xử lý Đồ thị: Tích hợp Matplotlib, Plotly và Pandas để kết xuất biểu đồ miền nghiệm và bảng đơn hình đạt chuẩn hiển thị khoa học.

&nbsp;&nbsp;&nbsp;&nbsp;Giao diện người dùng: Xây dựng bằng HTML, CSS, và JavaScript thuần, tập trung vào trải nghiệm tương tác với dữ liệu toán học và khả năng nhập liệu ma trận động.

## Hướng Dẫn Triển Khai Hệ Thống

Yêu cầu môi trường

&nbsp;&nbsp;&nbsp;&nbsp;Môi trường thực thi: Python phiên bản 3.8 trở lên.

Quy trình cài đặt

&nbsp;&nbsp;&nbsp;&nbsp;Tải mã nguồn dự án
&nbsp;&nbsp;&nbsp;&nbsp;Mở cửa sổ dòng lệnh và thực thi lệnh sau để sao chép kho lưu trữ:

```bash
git clone https://github.com/iczian/gi-i-quy-ho-ch-tuy-n-t-nh.git
cd gi-i-quy-ho-ch-tuy-n-t-nh
```

&nbsp;&nbsp;&nbsp;&nbsp;Cài đặt các gói phụ thuộc
&nbsp;&nbsp;&nbsp;&nbsp;Tiến hành cài đặt các thư viện lõi đã được định nghĩa sẵn:

```bash
pip install -r requirements.txt
```

&nbsp;&nbsp;&nbsp;&nbsp;Khởi chạy máy chủ nội bộ
&nbsp;&nbsp;&nbsp;&nbsp;Thực thi lệnh sau để chạy máy chủ:

```bash
uvicorn main:app --reload
```

&nbsp;&nbsp;&nbsp;&nbsp;Truy cập ứng dụng
&nbsp;&nbsp;&nbsp;&nbsp;Sau khi máy chủ khởi tạo thành công, tiến hành truy cập vào giao diện hệ thống qua trình duyệt web tại định tuyến: http://localhost:8000

## Cấu Trúc Mã Nguồn

```text
├── frontend/             
│   ├── index.html        
│   ├── app.js            
│   └── styles.css        
├── methods/              
│   ├── base.py           
│   ├── bland.py          
│   ├── convex_combo.py   
│   ├── geometric.py      
│   ├── simplex.py        
│   └── two_phase.py      
├── utils/                
├── main.py               
└── requirements.txt      
```

## Bản Quyền Khai Thác

Dự án và mã nguồn đi kèm được phát triển phục vụ mục đích nghiên cứu khoa học và giáo dục đại học. Cộng đồng được phép tham khảo, trích dẫn và tùy biến mã nguồn nhằm đóng góp vào các công cụ hỗ trợ tính toán toán học.
