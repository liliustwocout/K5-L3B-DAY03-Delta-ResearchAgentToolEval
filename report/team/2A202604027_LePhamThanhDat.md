# Báo cáo cá nhân — Lê Phạm Thành Đạt (2A202604027)

## 1. Thông tin thành viên

- Họ tên: Lê Phạm Thành Đạt
- MSSV: 2A202604027
- Email: <26ai.datlpt@vinuni.edu.vn>

## 2. Phần việc phụ trách

Phụ trách CP3, thiết kế và tích hợp ba tool mới cho Research Agent. Phần việc gồm xác định dữ liệu đầu vào, khai báo tool cho model, viết unit test offline và bổ sung ba case kiểm tra việc chọn tool trong bộ eval nhóm.

## 3. Đóng góp cụ thể

- **`build_evidence_card`** nhóm các trích đoạn theo mức ủng hộ, mâu thuẫn hoặc chưa đủ rõ. Thẻ giữ link từng nguồn và có thể xem trước trước khi xác nhận gửi Telegram. [Mã và hợp đồng tool](../../starter_v0/tools/build_evidence_card/TOOL.md)
- **`build_metric_delta_card`** so sánh hai kỳ cùng đơn vị. Ví dụ, 20% lên 26% là **+6 điểm phần trăm** và **+30% so với kỳ gốc**. Với mốc gốc bằng 0 hoặc âm, tool trả chênh lệch tuyệt đối kèm ghi chú. [Mã và hợp đồng tool](../../starter_v0/tools/build_metric_delta_card/TOOL.md)
- **`trace_source_chain`** lần theo trích dẫn trực tiếp và gián tiếp, gộp URL trùng, phát hiện vòng lặp và đánh dấu nguồn chưa có dữ liệu. Mẫu Streamlit minh họa ba bài báo cùng dẫn về một thông cáo. [Mã và hợp đồng tool](../../starter_v0/tools/trace_source_chain/TOOL.md) · [UI Streamlit](../../starter_v0/app.py)

Cả ba tool được đăng ký trong `TOOL_FUNCTIONS`, khai báo tham số trong `artifacts/tools.yaml` và có quy tắc chọn tool trong system prompt. [Registry](../../starter_v0/tools/__init__.py) · [Khai báo tool](../../starter_v0/artifacts/tools.yaml) · [System prompt](../../starter_v0/artifacts/system_prompt.md)

## 4. Bằng chứng

- Thẻ bằng chứng, commit `ccfd311` và 4 trường hợp test. [PR #2](https://github.com/liliustwocout/K5-L3B-DAY03-Delta-ResearchAgentToolEval/pull/2)
- Thẻ so sánh số liệu và UI Streamlit, commit `f1d7db5` và 5 trường hợp test. [PR #3](https://github.com/liliustwocout/K5-L3B-DAY03-Delta-ResearchAgentToolEval/pull/3)
- Tool truy dấu trích dẫn và sơ đồ Streamlit, commit `643f266` và 5 trường hợp test. [PR #4](https://github.com/liliustwocout/K5-L3B-DAY03-Delta-ResearchAgentToolEval/pull/4)
- **Kiểm tra offline.** Chạy lại `python -m pytest -q` trên commit `c5d0764`. Kết quả toàn bộ suite là **91 đạt, 0 lỗi, 14 TODO cũ được bỏ qua**, trong đó 14 trường hợp mới của CP3 đều đạt. Ví dụ, test URL thiếu hostname kiểm tra tool trả error dict, còn eval routing kiểm tra model có chọn đúng tool. [Unit test](../../starter_v0/tests/test_tools_todo.py)
- **Kiểm tra tích hợp.** Các lượt thử riêng trên OpenRouter trong giai đoạn CP3 chọn đúng tool cho G01, G02 và case truy dấu nguồn G03. Trong bộ CP4 hiện tại, mã G03 dùng cho `rate_sources`. Đã thử hiển thị thẻ số liệu và sơ đồ trích dẫn trong Streamlit. Luồng xem trước, xác nhận và chuyển nguyên văn thẻ bằng chứng sang Telegram được kiểm tra với bước gửi giả lập. [Bộ CP4 hiện tại](../../starter_v0/data/eval_group.json) · [Case truy dấu nguồn tại commit 643f266](https://github.com/liliustwocout/K5-L3B-DAY03-Delta-ResearchAgentToolEval/blob/643f266/starter_v0/data/eval_group.json#L32)
- **AI và cách kiểm tra kết quả.** Dùng Codex để hỗ trợ triển khai, viết test và rà luồng tích hợp. Kết quả được đối chiếu với đối số model thực sự gửi và dữ liệu tool trả về. Ví dụ, khi model lặp URL bài báo trong G03, bài test kiểm tra việc gộp mục trùng vẫn cho đúng ba bài dẫn tới một thông cáo.

## 5. Tự đánh giá

Phần CP3 có bằng chứng cho hai việc riêng biệt. Unit test kiểm tra phép tính, xử lý dữ liệu thiếu và lỗi đầu vào. Eval kiểm tra model chọn đúng tool trong các tình huống minh họa. Hạn chế còn lại là thẻ bằng chứng phụ thuộc vào nhãn do agent gán cho trích đoạn, còn sơ đồ chỉ phản ánh các quan hệ trích dẫn đã thu thập được.
