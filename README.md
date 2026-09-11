# personal-finance-analysis
# Personal Finance Analysis

Dự án portfolio hoàn chỉnh dùng Python, Pandas và NumPy để biến 2.400+ giao dịch tài chính giả lập có lỗi thành báo cáo có thể tái lập. Không có dữ liệu ngân hàng thật.

## Business problem

Phân tích trả lời sáu câu hỏi: chi tiêu hàng tháng, danh mục tốn nhất, cân đối thu–chi, giao dịch bất thường, thay đổi so với tháng trước và cơ hội tiết kiệm.

## Dataset

Mỗi dòng trong `data/raw/transactions.csv` là một giao dịch từ 01/2025 đến 08/2026. Dữ liệu được sinh với seed cố định và có chủ ý chứa giá trị thiếu, số tiền không hợp lệ, ngày ở nhiều định dạng, nhãn không nhất quán, bản ghi trùng, khoảng trắng, ngoại lệ lớn, phương thức sai và ngày tương lai.

## Data-quality issues

| Vấn đề | Phát hiện | Xử lý và lý do |
|---|---|---|
| ID trùng | `duplicated()` | Giữ bản ghi đầu để tránh đếm hai lần |
| Thiếu danh mục | `isna()` | Suy ra food từ mô tả, còn lại gán other để không mất giao dịch |
| Số tiền âm/0 | điều kiện `<= 0` | Lấy trị tuyệt đối cho số âm; loại 0 vì không có giá trị phân tích |
| Nhãn không nhất quán | `value_counts()` | Strip, lowercase và ánh xạ về taxonomy chuẩn |
| Ngày sai/tương lai | `to_datetime(errors="coerce")` | Loại ngày không phân tích được hoặc sau mốc dữ liệu 31/08/2026 |
| Phương thức lạ | đối chiếu danh sách cho phép | Gán `other` để bảo toàn bản ghi |
| Ngoại lệ lớn | IQR riêng theo danh mục | Chỉ đánh dấu để rà soát; không tự động xóa giao dịch hợp lệ |

## Analysis process

`generate_data.py` tạo raw data; `clean_data.py` chuẩn hóa và tạo feature; `analyze.py` xuất bảng/báo cáo; `visualize.py` tạo 10 biểu đồ. Notebook trình bày toàn bộ quy trình khám phá. Tám test xác nhận ID duy nhất, số tiền, ngày, loại giao dịch, danh mục, phương thức và missing.

## Key findings

- Trong toàn kỳ, thu nhập là **1,20 tỷ VNĐ**, chi tiêu **1,031 tỷ VNĐ** và tiết kiệm **168,739 triệu VNĐ** (tỷ lệ **14,1%**).
- Tháng 08/2026 chi **49,787 triệu VNĐ**, tăng **21,8%** so với tháng 07.
- Shopping là danh mục lớn nhất: **232,961 triệu VNĐ**, chiếm **22,6%** tổng chi tiêu; riêng tháng 08 là **14,924 triệu VNĐ**.
- Pipeline đánh dấu **12 giao dịch** theo IQR riêng từng danh mục. Đây là tín hiệu rà soát, không phải bằng chứng gian lận.
- Subscription định kỳ trong tháng gần nhất là **247.000 VNĐ**. Nếu giảm 20% shopping toàn kỳ, có thể tiết kiệm thêm khoảng **46,592 triệu VNĐ**.

Kết quả đầy đủ nằm trong [`reports/summary.md`](reports/summary.md), các bảng `reports/*.csv` và 10 hình tại `reports/figures/`.

## Recommendations

- Ưu tiên rà soát danh mục có tỷ trọng cao nhất và các tháng tăng mạnh.
- Kiểm tra từng giao dịch bất thường theo bối cảnh danh mục, đặc biệt các khoản không định kỳ.
- Rà lại subscription/utility định kỳ và hủy dịch vụ ít sử dụng.
- Dùng tỷ lệ tiết kiệm theo tháng làm KPI; mô phỏng giảm 10–20% danh mục linh hoạt trước khi đặt ngân sách.

## How to run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run_pipeline.py
pytest -q
jupyter notebook notebooks/01_analysis.ipynb
```

## Project structure

```text
data/{raw,processed}/   dữ liệu nguồn và dữ liệu sạch
notebooks/             notebook khám phá
src/                   sinh dữ liệu, làm sạch, phân tích, biểu đồ
reports/               báo cáo, bảng và hình
tests/                 kiểm tra chất lượng
```

## Limitations and future improvements

Dữ liệu là giả lập cho một người dùng; quy tắc suy luận danh mục còn đơn giản và IQR không xét mùa vụ. Có thể mở rộng bằng nhiều hồ sơ, ngân sách mục tiêu, dự báo chuỗi thời gian, phân loại merchant và dashboard tương tác.

# this projects just use to help user understand the code, 
