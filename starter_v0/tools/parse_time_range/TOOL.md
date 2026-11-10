---
name: parse_time_range
track: bonus
kind: local_formatter
provider: Local
requires_env: []
inputs: [text, today]
outputs: [tool, status, matched, today, start_date, end_date, days, timeframe, note]
side_effect: false
---

# parse_time_range

Đổi một cụm thời gian tiếng Việt hoặc tiếng Anh thành khoảng ngày cụ thể và mức `timeframe` tương ứng của `lookup`.

- Nhận: `hôm nay`, `hôm qua`, `tuần này`, `tuần qua`, `tháng này`, `năm nay`, `N ngày/tuần/tháng/năm qua`, `last 3 days`, `past month`... Không phân biệt dấu và hoa thường.
- Tính cuốn chiếu lùi từ hôm nay (`tuần này` = 7 ngày gần nhất), không theo tuần hay tháng lịch.
- `timeframe` là mức nhỏ nhất trong `day`, `week`, `month`, `year` đủ bao phủ khoảng ngày. Ví dụ `3 ngày qua` có `days = 3` và `timeframe = week`.
- `today` (tùy chọn, dạng `YYYY-MM-DD`) để cố định ngày gốc; bỏ trống thì dùng ngày hiện tại.
- Cụm không nhận ra trả `status: unrecognized`, không phải lỗi. Dữ liệu sai (chuỗi rỗng, ngày gốc sai, số ngày ngoài 1 đến 3660) trả dict lỗi, không raise.

Chạy local, không gọi mạng. Chỉ dùng khi người dùng cần **ngày cụ thể**; với yêu cầu tin tức thông thường, truyền `timeframe` thẳng cho `lookup`.
