---
name: trace_source_chain
track: core
kind: local_formatter
provider: Local
requires_env: []
inputs: [articles]
outputs: [tool, entry_count, roots, unresolved_urls, nodes, edges, markdown]
side_effect: false
---

# trace_source_chain

Mỗi tài liệu có `url`, `title` tùy chọn và danh sách URL trích dẫn trực tiếp `cites`. Chỉ đưa vào các liên kết có căn cứ từ dữ liệu người dùng hoặc nội dung đã đọc. Dùng `cites: []` cho tài liệu đã cung cấp mà chuỗi dừng tại đó. Nếu chỉ biết một URL được trích mà thiếu dữ liệu về tài liệu đó, giữ URL trong `cites` của bài dẫn.

- `roots` là tài liệu cuối chuỗi có trong dữ liệu đã cho. `article_count` đếm số bài đầu chuỗi dẫn tới nguồn đó, kể cả gián tiếp. Một bài có thể dẫn tới nhiều nguồn cuối chuỗi.
- Các mục cùng URL được gộp và mỗi liên kết trích dẫn được đếm một lần.
- `unresolved_urls` liệt kê các đích trích dẫn chưa có dữ liệu. Các nguồn cuối chuỗi trong sơ đồ chỉ phản ánh các liên kết đã được cung cấp.
- Tool trả error dict khi input sai, có trích dẫn vòng hoặc có quá 12 URL riêng biệt. `nodes` và `edges` dùng để vẽ sơ đồ web, `markdown` dùng cho phần xem trước Telegram.
