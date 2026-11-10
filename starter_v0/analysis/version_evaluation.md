# Đánh giá agent qua từng version

Eval: `data/eval_base.json` (20 case), Gemini. Mỗi version chạy 1 lần.

## Điểm

- v0: **0.70** (14/20)
- v1: 0.75 (15/20), sai 5 case
- v2: **0.95** (19/20), sai 1 case
- v3: **0.95** (19/20), sai 1 case

## v0 (prompt gốc)
- Điểm: 0.70 (14/20), số case sai: 6. Run hợp lệ (20/20, không lỗi mạng).
- Lỗi: R03, R08, R10, R11, R12, R13
- Đánh giá: model đoán thay vì hỏi (R10 đoán `sama`, R11 bịa link), không từ chối câu ngoài phạm vi (R08 gọi `lookup` tìm nguyên hàm), không xác nhận trước khi gửi (R12), chỉ dùng một tool (R13) và thêm chữ vào `query` (R03, R13).

## v1 (sửa prompt + mô tả `send`)
- Điểm: 0.75, số case sai: 5
- Lỗi: R03, R06, R12, R13, M02
- Đánh giá: hết đoán bừa (R10, R11 đã đúng) và không gửi tin ngay nữa. Còn lại là lỗi tham số: `query` quá dài ("AI news today"), R06 gọi `lookup` hai lần, R12 hỏi `text` thay vì `yes_no`.

## v2 (thêm quy ước tham số)
- Điểm: 0.95, số case sai: 1
- Lỗi: R12
- Đánh giá: bước tăng lớn nhất (+0.20). Quy ước `query` ngắn, `timeframe`, `topic` sửa được R03, R06, R13, M02.

## v3 (viết lại mô tả mọi tool)
- Điểm: 0.95, số case sai: 1
- Lỗi: R12
- Đánh giá: không tăng so với v2. Viết lại mô tả không cải thiện thêm trên bộ base này.

## So sánh khác biệt
- **v0 → v1:** hết lỗi đoán bừa (R10, R11) và hết lỗi câu ngoài phạm vi (R08). Điểm tăng 0.70 → 0.75 vì lỗi tham số vẫn còn và R06, M02 mới sai.
- **v1 → v2:** sửa tham số (query, timeframe) làm điểm nhảy 0.75 → 0.95. Đây là bước hiệu quả nhất.
- **v2 → v3:** điểm giữ 0.95, cùng một lỗi còn lại.
- **Lỗi R12 còn ở mọi version:** đề yêu cầu `clarify` kiểu `yes_no`, nhưng model hỏi nội dung bằng `text` vì người dùng chưa đưa nội dung bản tin. Cách tiếp theo: thêm rule "mọi yêu cầu gửi/đăng đều dùng `yes_no`, kể cả khi chưa có nội dung".
- Không có lần chạy nào gọi `send`, nên không có tin Telegram thật bị gửi.
