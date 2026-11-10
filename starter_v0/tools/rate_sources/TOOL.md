---
name: rate_sources
track: bonus
kind: local_knowledge
provider: Local
requires_env: []
inputs: [urls]
outputs: [tool, items, summary, note]
side_effect: false
---

# rate_sources

Xếp mỗi URL vào một mức tin cậy theo **tên miền**, dựa trên `company_policy/source-citation-policy.md`:

- `tier1`: nguồn gốc hoặc chính thức (arXiv, blog của hãng, GitHub, `.gov`, `.edu`).
- `tier2`: báo chí uy tín.
- `tier3`: mạng xã hội, diễn đàn. Chỉ là tín hiệu ban đầu.
- `unknown`: tên miền chưa có trong danh sách. `invalid`: không phải URL http(s).

Chỉ nhìn tên miền, không đọc trang và không đánh giá nội dung. Tên miền giả như `arxiv.org.evil.com` hoặc `notarxiv.org` không được tính là tier1. Dữ liệu sai kiểu trả về dict lỗi, không raise. Tối đa 50 URL mỗi lần gọi.

Khác với `trace_source_chain` (truy chuỗi trích dẫn) và `build_evidence_card` (đối chiếu nội dung các nguồn).
