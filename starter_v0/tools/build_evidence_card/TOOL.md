---
name: build_evidence_card
track: core
kind: local_formatter
provider: Local
requires_env: []
inputs: [claim, evidence]
outputs: [tool, status, markdown]
side_effect: false
---

# build_evidence_card

Đối chiếu một nhận định với các nguồn đã thu thập. Mỗi mục gồm URL HTTP(S), tóm tắt dựa trên nguồn và nhãn `supports`, `contradicts` hoặc `unclear`.

- Trạng thái `mixed`, `support_only`, `contradiction_only` hoặc `insufficient` phản ánh các nhãn được cung cấp. Tool không đọc URL hay xác minh độc lập các nhãn.
- `evidence: []` hợp lệ và cho trạng thái `insufficient`.
- Agent xem trước thẻ và dùng luồng xác nhận hiện có nếu người dùng muốn gửi. Thẻ dùng cú pháp [Telegram Markdown](https://core.telegram.org/bots/api#markdown-style).
