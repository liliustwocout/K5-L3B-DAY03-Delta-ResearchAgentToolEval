---
name: build_metric_delta_card
track: core
kind: local_formatter
provider: Local
requires_env: []
inputs: [metric, baseline, current]
outputs: [tool, metric, baseline, current, absolute_delta, absolute_display, relative_change_percent, relative_display, relative_note, markdown]
side_effect: false
---

# build_metric_delta_card

So sánh hai số liệu của cùng một chỉ số. Mỗi mốc có `value`, `period`, `unit` và URL nguồn nếu có. Hai mốc dùng cùng đơn vị. Số liệu dạng phần trăm dùng đơn vị `%`, ví dụ `20` cho 20%.

- Chênh lệch tuyệt đối bằng giá trị kỳ mới trừ giá trị kỳ gốc. Với đơn vị `%`, kết quả hiển thị bằng điểm phần trăm.
- Chênh lệch tương đối bằng chênh lệch tuyệt đối chia mốc gốc, nhân 100. Nếu mốc gốc bằng hoặc nhỏ hơn 0, tool chỉ trả chênh lệch tuyệt đối và ghi chú.
- Tool trả trường có cấu trúc cho UI và Markdown cho luồng xác nhận gửi Telegram. Nó dùng số liệu và nguồn đã có trong yêu cầu hoặc kết quả tra cứu.
