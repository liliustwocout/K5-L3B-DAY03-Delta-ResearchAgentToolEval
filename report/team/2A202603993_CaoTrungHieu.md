# Báo cáo cá nhân — Cao Trung Hiếu — 2A202603993

## 1. Thông tin thành viên

- Họ tên: Cao Trung Hiếu
- MSSV: 2A202603993
- Email: 26ai.hieuct@vinuni.edu.vn
- Nhóm: Delta
- Lớp: L3B

## 2. Phần việc phụ trách

Phần việc chính của tôi gồm bốn mảng:

1. **Tích hợp Telegram**: agent gửi tin thật lên Telegram, chỉ sau khi người dùng xác nhận.
2. **Cài đặt CP1 đến CP2**: chạy baseline v0, tối ưu prompt và mô tả tool qua v1, v2, v3, ghi bằng `version_log.csv` và phân tích lỗi.
3. **Cải tiến giao diện chat và triển khai (deploy)**: giao diện web chạy trên Vercel, dùng được từ trình duyệt. Tôi là người deploy hệ thống lên Vercel.
4. **So sánh các phiên bản và ranh giới (boundary)**: chọn phiên bản agent ngay trong chat, bảng so sánh điểm các phiên bản, và các ranh giới an toàn khi gửi tin.

Ngoài ra tôi làm thêm 3 tool bổ sung (`rate_sources`, `dedupe_items`, `parse_time_range`) kèm unit test, và hoàn tất test challenge.

Link giao diện đang chạy: https://k5-l3-b-day-03-delta-research-agent.vercel.app/

## 3. Đóng góp cụ thể

### 3.1. Tích hợp Telegram

- Luồng đã chạy thật: agent hỏi xác nhận `yes_no`, tôi trả lời "Có, gửi đi", `send(confirmed=true)` trả `status: sent`. Lần đầu gặp `ConnectionError` do mạng nên chạy lại; cả hai transcript đều được lưu.
- Trên bản web, mỗi người dùng nhập **chat ID Telegram của chính họ** và tin được gửi tới đó, không dùng chat của chủ dự án. Chat ID do trình duyệt gửi lên, model không chọn được người nhận.
- Tool `send` nhận thêm tham số `chat_id` tùy chọn; tham số này không khai báo trong `tools.yaml` nên model không thấy và không thể bị dẫn dắt để gửi tới người khác.
- Giao diện có hướng dẫn kết nối bot, lấy chat ID và gửi tin.

### 3.2. Cài đặt CP1 đến CP2 (v0 đến v3)

Mỗi version chạy `eval_base.json` (20 câu) bằng Gemini; chỉ dùng run hợp lệ (`provider_error_cases = 0`, `measured_cases = total_cases`). Lần chạy v0 đầu bị lỗi mạng ở một câu nên tôi loại run đó và chạy lại.

| Version | Thay đổi chính | Điểm (`case_accuracy`) |
|---|---|---:|
| v0 | Prompt và tool gốc của starter | 0.70 (14/20) |
| v1 | Bỏ 3 chỉ dẫn xấu (đoán thay vì hỏi, gửi luôn, làm một bước); thêm rule hỏi lại và xác nhận trước khi gửi; sửa mô tả `send` | 0.75 (15/20) |
| v2 | Thêm rule chọn tool và quy ước tham số (từ khóa ngắn, tên tài khoản không có `@`, `topic=news`, `timeframe`, `Top/Latest`) | 0.95 (19/20) |
| v3 | Viết lại mô tả cả 10 tool theo dạng làm gì / khi nào dùng / khi nào không dùng; thêm phạm vi và quy tắc chất lượng | 0.95 (19/20) |
| v4 (hiện tại) | v3 cùng 6 tool mới (3 của Đạt, 3 của tôi) và rule chọn tool tương ứng | 0.90 (18/20) |

Nhận định từ log: v2 là bước hiệu quả nhất (+0.20) nhờ quy ước tham số; v3 không tăng thêm điểm. Bản hiện tại (v4) giảm nhẹ xuống 0.90 vì sai câu R03 (từ khóa tìm kiếm bị thêm chữ) và R12 (hỏi xin nội dung bằng `text` thay vì xác nhận bằng `yes_no`). R12 sai ở cả v1, v2, v3 và v4, tôi ghi nhận là chưa sửa được. Phân tích từng câu sai của v0 nằm ở bảng B2, so sánh các phiên bản nằm ở B1 trong báo cáo nhóm.

### 3.3. Cải tiến giao diện chat và triển khai (deploy)

- Giao diện web ở `public/index.html`, phần xử lý ở `webapp/core.py`, chạy trên Vercel và cả trên máy (`dev_server.py`).
- Tôi tự tạo dự án trên Vercel, đặt các biến môi trường (key của provider và các tool) và deploy; giao diện đang chạy tại https://k5-l3-b-day-03-delta-research-agent.vercel.app/.
- Thiết kế phẳng, đen trắng xám với một màu xanh dương nhẹ, có chế độ sáng và tối.
- Màn hình đầu có đoạn giới thiệu agent và các câu hỏi mẫu; bấm vào câu mẫu thì điền vào ô nhập để người dùng sửa trước khi gửi.
- Mỗi câu trả lời có phần "đã gọi n công cụ" cho biết agent đã gọi tool nào, với tham số gì.
- Khi agent hỏi xác nhận gửi Telegram, giao diện hiện hai nút "Có, gửi đi" và "Không".
- Trong quá trình deploy Vercel tôi gặp và xử lý ba lỗi: Vercel nhầm `app.py` (Streamlit) là điểm vào (khai báo `api.chat:handler` trong `pyproject.toml`, loại các file không dùng khỏi bản deploy); vượt giới hạn dung lượng hàm (bỏ `includeFiles` trong `vercel.json`); `ValidationError` với `google-genai==1.0.0` do trường `additionalProperties` trong mô tả tool (lọc trường này trước khi gửi cho Gemini, tái hiện lỗi bằng đúng phiên bản 1.0.0 rồi kiểm tra bản đã sửa).
- Sau đó tôi thấy API Gemini cũng từ chối trường này ở `chat.py` và eval, nên sửa thêm ở `providers/gemini_provider.py`.

### 3.4. So sánh các phiên bản và ranh giới (boundary)

- Trong chat có ô **chọn phiên bản agent** (v0, v1, v2, v3, hiện tại). Chọn bản nào thì agent dùng đúng prompt và tool của bản đó; đổi phiên bản thì cuộc trò chuyện được làm mới.
- Dưới giao diện có **bảng so sánh các phiên bản**: điểm, thay đổi chính và các câu còn sai. Điểm lấy trực tiếp từ các file run, không gõ tay.
- Cách này cho thấy khác biệt thật: cùng câu "Tóm tắt 5 tweet mới nhất giúp mình", bản v0 tự đoán tài khoản `sama`, còn bản hiện tại hỏi lại người dùng.
- **Ranh giới an toàn khi gửi:** chỉ phiên bản hiện tại gửi được Telegram (các bản cũ, đặc biệt v0 bảo gửi luôn không hỏi, bị chặn); chat ID phải hợp lệ; mỗi chat ID nhận tối đa 5 tin mỗi giờ; tin dài bị cắt ở 1000 ký tự; chủ dự án có thể tắt hẳn việc gửi bằng biến `DISABLE_SEND=1`.

### 3.5. Tool bổ sung và test challenge

- `rate_sources`: xếp URL vào mức tin cậy theo tên miền; tên miền giả như `arxiv.org.evil.com` không được tính là chính thức.
- `dedupe_items`: loại mục trùng URL (bỏ `www`, tham số theo dõi, dấu `/` cuối) hoặc trùng tiêu đề.
- `parse_time_range`: đổi cụm thời gian tiếng Việt hoặc Anh ("hôm nay", "3 ngày qua") thành khoảng ngày và mức `timeframe` của `lookup`.
- 12 unit test (mỗi tool 4 test) trong `starter_v0/tests/test_tools_todo.py`; các case G03, G04, G06, G10 của Huy kiểm tra việc model chọn các tool này.
- **Test challenge:** điền 14 test còn skipped của các tool có sẵn (clarify, format, send, lookup, fetch, timeline, social_search, policy). `pytest` hiện là 132 passed, 0 skipped.

## 4. Bằng chứng

- File/commit/PR:
  - CP1, CP2: commit `1f041c1` (`artifacts/versions/`, `artifacts/version_log.csv`, `analysis/`, run v0 đến v3 trong `runs/`); run v4 `starter_v0/runs/v4_B_base_gemini_20261111T093122904216.json`.
  - Telegram và giao diện web: commit `90422c3`; transcript `starter_v0/transcripts/v3_gemini_20261110T184218357459.transcript.json` và `..._20261110T184506173013.transcript.json`.
  - Deploy Vercel: commit `f49d712`, `6d997fa`, `ebe2a3d`; giao diện đang chạy tại https://k5-l3-b-day-03-delta-research-agent.vercel.app/.
  - Chọn phiên bản và bảng so sánh: commit `0abe7ef` (`public/index.html`, `public/versions.json`, `webapp/core.py`).
  - Ba tool bổ sung và test: commit `9f8e764`, `0ad7384`.
  - Test challenge và sửa provider Gemini: `starter_v0/tests/test_tools_todo.py`, `starter_v0/providers/gemini_provider.py`.
- AI/công cụ đã dùng và cách tự kiểm tra kết quả: tôi dùng Claude Code (Claude Sonnet 5.5) để hỗ trợ viết code, test, phân tích log và soạn báo cáo. Kết quả được kiểm tra bằng `pytest`, chỉ dùng run eval hợp lệ và đối chiếu số liệu với `version_log.csv` cùng các file run JSON; không dùng AI để tạo run, metric hay transcript giả.

## 5. Tự đánh giá

Làm được: có baseline hợp lệ và vòng tối ưu có số đo từ 0.70 lên 0.95; tích hợp Telegram gửi thật có xác nhận; giao diện chat chạy được trên Vercel với chọn phiên bản và bảng so sánh; thêm 3 tool; hoàn tất test challenge.

Hạn chế:

- Mỗi version chỉ chạy một lần, nên chênh lệch nhỏ giữa các lần có thể là ngẫu nhiên.
- v3 không tăng điểm so với v2, và v3 thay đổi cùng lúc cả prompt lẫn mô tả mọi tool nên khó tách phần nào đóng góp. Bản hiện tại (v4) thấp hơn v3 một chút (0.90 so với 0.95), chưa rõ do thêm tool hay do dao động giữa các lần chạy.
- Câu R12 vẫn chưa được sửa ở mọi version.
- Bộ chấm chỉ so khớp tên tool và tham số, không đánh giá chất lượng câu trả lời hay kết quả cuối của tool.
- Việc deploy mất nhiều vòng sửa lỗi vì khác biệt giữa môi trường máy và Vercel (phiên bản thư viện, giới hạn dung lượng).
- Giới hạn 5 tin mỗi giờ cho mỗi chat ID đếm trong bộ nhớ của từng instance, nên là hàng rào yếu trên Vercel.

Nếu có thêm thời gian: chạy mỗi version nhiều lần để đo độ dao động, thử sửa R12 bằng một rule riêng cho mọi yêu cầu gửi hoặc đăng, và tìm nguyên nhân R03 tái xuất hiện ở bản hiện tại.
