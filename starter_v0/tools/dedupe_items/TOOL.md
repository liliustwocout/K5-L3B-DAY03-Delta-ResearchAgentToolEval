---
name: dedupe_items
track: bonus
kind: local_formatter
provider: Local
requires_env: []
inputs: [items]
outputs: [tool, items, kept_count, removed, removed_count]
side_effect: false
---

# dedupe_items

Loại các mục trùng trong danh sách kết quả đã thu thập (ví dụ gộp kết quả `lookup` và `social_search`) trước khi `format`. Giữ mục đầu tiên của mỗi nhóm trùng.

- Trùng URL: so sánh sau khi bỏ `www.`, fragment, tham số theo dõi (`utm_*`, `fbclid`, `gclid`...) và dấu `/` cuối.
- Trùng tiêu đề: so sánh không phân biệt hoa thường, dấu tiếng Việt và dấu câu.
- Mục không phải object thì bị bỏ với lý do `not_an_object`. Mục không có URL và tiêu đề thì được giữ lại vì không đủ căn cứ để coi là trùng.
- `removed` cho biết mục nào bị bỏ, vì sao và trùng với mục nào (`duplicate_of_index` là vị trí trong danh sách gốc).

Chạy local, không đọc URL. Đầu vào sai kiểu trả về dict lỗi, không raise.
