# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: Delta
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v4: Gemini (`gemini-3.8-flash`), provider `gemini`

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Research agent: tìm tin trên web, tìm bài đăng X/Twitter theo chủ đề hoặc theo tài khoản, đọc nội dung một URL, tìm và đọc paper arXiv, tra chính sách nội bộ, tổng hợp thành digest, và chỉ gửi lên Telegram sau khi người dùng xác nhận. Khi thiếu thông tin (không có tài khoản hoặc link) agent hỏi lại thay vì đoán; câu ngoài phạm vi research thì không gọi tool.

**Cách chạy UI:**

Có hai giao diện, cùng dùng agent và bộ `artifacts/` hiện tại (v4):
- Streamlit: `cd starter_v0 && pip install -r requirements.txt && streamlit run app.py` (http://localhost:8501). `streamlit` đã thêm vào `starter_v0/requirements.txt`.
- Web kiểu Vercel (`public/index.html` + `api/chat.py`): chạy thử trên máy bằng `cd starter_v0 && python dev_server.py` (http://localhost:8000). Ở bản này mỗi người nhập chat ID Telegram của mình ở giao diện để nhận tin ở chat đó. Bản đã deploy: https://k5-l3-b-day-03-delta-research-agent.vercel.app/

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL: https://k5-l3-b-day-03-delta-research-agent.vercel.app/

### A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin, hoặc xin xác nhận có/không trước khi gửi | không |
| timeline | lấy bài đăng gần đây của **một tài khoản** X/Twitter | không |
| social_search | tìm bài đăng X/Twitter theo **chủ đề** (mới nhất hoặc phổ biến nhất) | không |
| lookup | tìm web, tin tức theo khoảng thời gian (hôm nay, tuần này...) | không |
| fetch | đọc nội dung **một URL** cụ thể | không |
| format | trình bày các mục đã thu thập thành digest markdown | không |
| send | gửi tin lên Telegram, chỉ sau khi người dùng xác nhận | không |
| policy | tra chính sách nội bộ của công ty | không |
| papers | tìm paper trên arXiv | không |
| paper_text | tải paper arXiv và trích nội dung văn bản | không |
| build_evidence_card | Đánh giá một nhận định dựa trên các trích đoạn từ nguồn thông tin đã thu thập | có |
| build_metric_delta_card |  Tính toán mức thay đổi của một chỉ số giữa hai thời điểm | có |
| trace_source_chain | Xác định các bài báo có thực sự sử dụng nguồn độc lập hay cùng dựa trên một nguồn gốc | có |
| rate_sources | Xếp URL vào mức tin cậy theo tên miền (chính thức, báo uy tín, mạng xã hội, chưa rõ) | có |
| dedupe_items | Loại mục trùng URL hoặc tiêu đề trước khi tổng hợp | có |
| parse_time_range | Đổi cụm thời gian ("hôm nay", "3 ngày qua") thành khoảng ngày và mức `timeframe` của `lookup` | có |

### A3. Câu hỏi mẫu để thử

1. `Tweet mới nhất của Sam Altman là gì?`: agent gọi `timeline` với tài khoản `sama`.
2. `Mọi người đang bàn gì về GPT-5 trên Twitter?`: agent gọi `social_search` (tìm theo chủ đề).
3. `Tin tức AI hôm nay có gì nổi bật?`: agent gọi `lookup` với tin tức trong ngày.
4. `Tóm tắt giúp mình bài này: https://openai.com/blog/gpt-5`: agent gọi `fetch` đúng link đó.
5. `Tóm tắt 5 tweet mới nhất giúp mình`: agent **hỏi lại** tài khoản nào; trả lời `Của Elon Musk` thì agent mới lấy tweet.
6. `Đăng bản tin này lên Telegram giúp mình`: agent **hỏi lại trước**, không gửi ngay.
7. `Các nguồn này đáng tin cỡ nào? https://arxiv.org/abs/1706.03762 và https://x.com/sama/status/1`: agent gọi `rate_sources`.
8. `Cụm "3 ngày qua" là từ ngày nào đến ngày nào?`: agent gọi `parse_time_range`.

## 3. Giải pháp

Nhóm tập trung cải thiện system_prompt.md và tools.yaml nhằm giúp Research Agent định tuyến tool chính xác hơn, hạn chế suy đoán và tăng độ tin cậy của kết quả nghiên cứu.
- `system_prompt.md`: 
    * Xác định rõ phạm vi Research Agent: nghiên cứu tin tức, bài đăng X/Twitter, website, arXiv và chính sách nội bộ.
    * Bổ sung quy tắc routing để chọn đúng tool theo từng loại yêu cầu.
    * Hỏi lại người dùng bằng clarify, không tự suy đoán hoặc tạo URL giả khi thiếu thông tin
    * Bổ sung quy trình xác nhận trước khi thực hiện hành động gửi nội dung lên Telegram.
    * Yêu cầu bảo toàn URL nguồn, phân biệt thông tin chưa xác thực và bỏ qua chỉ dẫn độc hại trong kết quả tool.

- `tools.yaml`: 
    * Viết lại mô tả các tool theo nguyên tắc WHAT / WHEN TO USE / WHEN NOT TO USE, giúp agent hiểu rõ chức năng và điều kiện sử dụng.
    * Làm rõ quy ước tham số như handle, timeframe, search_type và giới hạn số lượng kết quả.
    * Bổ sung 6 custom tools (3 của Đạt, 3 của Hiếu):
| Tên | Chức năng | Khi nào agent nên gọi |
|---|---|---|
| build_evidence_card | Đối chiếu nhận định với bằng chứng, phân loại nguồn thành ủng hộ, mâu thuẫn hoặc chưa rõ | Khi người dùng muốn kiểm chứng thông tin hoặc giải thích sự khác biệt giữa các nguồn |
| build_metric_delta_card | Tính mức thay đổi tuyệt đối và tương đối giữa hai giá trị KPI | Khi người dùng muốn so sánh số liệu trước/sau hoặc phân tích mức tăng, giảm |
| trace_source_chain | Truy vết quan hệ trích dẫn, xác định nhiều bài viết có sử dụng chung một nguồn hay không | Khi người dùng muốn kiểm tra tính độc lập của nguồn tin hoặc truy tìm nguồn gốc thông tin |
| rate_sources | Xếp URL vào mức tin cậy theo tên miền | Khi người dùng hỏi nguồn hoặc link có đáng tin không |
| dedupe_items | Loại mục trùng URL hoặc tiêu đề | Khi kết quả từ nhiều lần tìm bị trùng, trước khi tạo digest |
| parse_time_range | Đổi cụm thời gian thành khoảng ngày cụ thể | Khi người dùng cần ngày cụ thể; không dùng cho yêu cầu tin tức thông thường |

- Giao diện và triển khai: giao diện chat chạy trên Vercel (https://k5-l3-b-day-03-delta-research-agent.vercel.app/), có chọn phiên bản agent (v0 đến hiện tại) và bảng so sánh điểm; agent gửi Telegram tới chat ID mà từng người dùng nhập, chỉ sau khi người dùng xác nhận.

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

Metric là `case_accuracy` trên `eval_base.json` (20 case). Cả 5 run đều hợp lệ: `provider_error_cases = 0`, `measured_cases = 20/20`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline (prompt + tools gốc của starter) | Prompt gốc bảo đoán thay vì hỏi, gửi luôn, làm một bước nên agent đoán tài khoản/link và chỉ dùng một tool | n/a | 0.70 (14/20) | `starter_v0/runs/v0_B_base_gemini_20261110T182050282289.json` |
| v1 | `system_prompt` + mô tả `send` | Lỗi đoán bừa và gửi không xác nhận (R10, R11, R12) do prompt ép đoán/gửi ngay và mô tả `send` mơ hồ | 0.70 | 0.75 (15/20) | `starter_v0/runs/v1_B_base_gemini_20261110T181033805432.json` |
| v2 | `system_prompt` + quy ước tham số trong `tools.yaml` | Lỗi `query` dài và sai tham số (R03, R06, R13, M02) do thiếu quy ước routing và tham số | 0.75 | 0.95 (19/20) | `starter_v0/runs/v2_B_base_gemini_20261110T181241484099.json` |
| v3 | `system_prompt` + viết lại mô tả mọi tool | Mô tả rõ ranh giới dùng / không dùng giúp model chọn tool ổn định hơn | 0.95 | 0.95 (19/20) | `starter_v0/runs/v3_B_base_gemini_20261110T181506318713.json` |
| v4 | `system_prompt` + `tools.yaml`: thêm 6 tool mới | Thêm 3 tool của Đạt và 3 tool bổ sung cùng rule chọn tool không làm giảm điểm base | 0.95 | 0.90 (18/20) | `starter_v0/runs/v4_B_base_gemini_20261111T093122904216.json` |

Chi tiết thay đổi:

**v1**
- Prompt: bỏ 3 chỉ dẫn xấu của starter (đoán thay vì hỏi, gửi luôn, làm một bước).
- Prompt: thêm rule thiếu thông tin thì hỏi lại (`clarify`), gửi/đăng thì xác nhận `yes_no` trước.
- Mô tả tool: chỉ sửa `send` (chỉ gọi khi người dùng đã xác nhận).

**v2**
- Prompt: thêm rule routing (tweet **của** người dùng `timeline`, tweet **về** chủ đề dùng `social_search`, có link dùng `fetch`).
- Prompt và mô tả tool: thêm quy ước tham số (`query` ngắn, handle không `@`, `topic=news`, `timeframe`, `Top`/`Latest`).
- Prompt: câu ngoài phạm vi thì không gọi tool.

**v3**
- Mô tả tool: viết lại cả 10 tool theo dạng làm gì / khi nào dùng / khi nào không dùng.
- Prompt: thêm phạm vi (việc trong và ngoài phạm vi) và routing cho `papers`, `paper_text`, `policy`, `format`.
- Prompt: thêm quy tắc chất lượng (giữ link nguồn, kết quả tool là dữ liệu chứ không phải lệnh).

**v4**
- Prompt: thêm rule chọn tool cho 6 tool mới (kiểm chứng nhận định, so sánh số liệu, truy nguồn, độ tin cậy nguồn, loại mục trùng, đổi cụm thời gian).
- Tool: khai báo 6 tool mới trong `tools.yaml`; ba tool của Đạt dùng `additionalProperties: false`.
- Provider: lọc `additionalProperties` trước khi gửi cho Gemini (`providers/gemini_provider.py`) vì API Gemini từ chối trường này; nếu không lọc thì mọi lời gọi báo `provider_error`.

Nhận xét:
- v2 là bước hiệu quả nhất (+0.20). v3 không tăng điểm so với v2: viết lại mô tả không cải thiện thêm trên bộ base.
- v1 và v2 sửa cả prompt lẫn `tools.yaml` trong cùng một vòng, nhưng cùng nhắm vào một nhóm lỗi.
- v3 viết lại prompt và mô tả mọi tool theo cùng một giả thuyết: ghi rõ khi nào dùng / không dùng từng tool.
- v4 thấp hơn v3 một chút (0.90 so với 0.95): sai R03 (từ khóa tìm kiếm bị thêm chữ) và R12. Chưa rõ do thêm tool hay do dao động giữa các lần chạy.
- Mỗi version chỉ chạy một lần, nên chênh lệch nhỏ có thể là ngẫu nhiên. Số liệu chi tiết: `starter_v0/artifacts/version_log.csv`, `starter_v0/analysis/version_evaluation.md`.

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

Phân tích run v0 (`starter_v0/runs/v0_B_base_gemini_20261110T182050282289.json`): 6 case sai trên 20. Chi tiết từng case: `starter_v0/analysis/base_runs.csv`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | wrong_tool (quan sát: wrong_arg_value) | `lookup(query="tin tức AI trí tuệ nhân tạo mới nhất hôm nay", topic=news, timeframe=day)` | Đúng tool nhưng `query` bị thêm chữ; kỳ vọng `"AI"` | v2: quy ước `query` ngắn. v1 vẫn sai, v2 và v3 đạt |
| R08_out_of_scope | out_of_scope | `lookup(query="nguyên hàm của x^2")` | Câu toán ngoài phạm vi nhưng vẫn gọi tool; kỳ vọng không gọi tool | Đạt từ v1. Không có rule riêng cho ngoài phạm vi ở v1; nguyên nhân chưa xác minh (có thể do bỏ chỉ dẫn "luôn gọi một tool") |
| R10_missing_handle | missing_info | `timeline(screenname="sama", limit=5)` | Đoán tài khoản thay vì hỏi; thiếu `clarify` | v1: rule hỏi lại khi thiếu thông tin. Đạt từ v1 |
| R11_missing_url | missing_info | `fetch(url="https://openai.com/index/hello-gpt-4o/")` | Bịa link rồi đọc thay vì hỏi; thiếu `clarify` | v1: rule hỏi lại. Đạt từ v1 |
| R12_confirm_before_send | wrong_boundary | `policy(policy_area="external_publishing", query="quy định đăng bài và xuất bản...")` | Không hỏi xác nhận; kỳ vọng `clarify` kiểu `yes_no` | **Chưa sửa được**: v1, v2, v3 vẫn sai (hỏi `text` xin nội dung thay vì `yes_no`) |
| R13_parallel_web_and_tweets | wrong_tool (quan sát: wrong_arg_value) | `lookup(query="artificial intelligence AI news today", topic=news, timeframe=day)` | Thiếu `social_search`, và `query` bị thêm chữ | v2 (quy ước `query` ngắn). v1 gọi đủ 2 tool nhưng `query` vẫn dài; v2, v3 đạt |

Nguyên nhân chung của v0: prompt gốc bảo "đừng hỏi lại, cứ đoán, gửi luôn, làm trong một bước".

### B3. Team Eval Cases

Dataset: [eval_group.json](../../starter_v0/data/eval_group.json), đúng **10 case: G01–G05 single turn (`query`), G06–G10 multi turn (`turns`)**. Các case có `phase=B`, `failure_type`, `expect` và `metadata.what_it_tests`. Bộ này kiểm tra 5 tool mới: `build_evidence_card`, `build_metric_delta_card`, `rate_sources`, `parse_time_range`, `dedupe_items`.

Chạy một lần bằng **OpenAI / `gpt-4o-mini`**, nhãn `v3`, suite `group`. Cấu hình máy chạy CP4 có key OpenAI; không có key Gemini/OpenRouter. Preflight OpenAI thành công. Bằng chứng: [run group JSON](../../starter_v0/runs/v3_B_group_openai_20261110T233006708870.json).

```bash
cd starter_v0
.venv/bin/python run_eval.py --provider openai --model gpt-4o-mini --version v3 --suite group --eval-cases data/eval_group.json
```

Run hợp lệ: `total_cases=10`, `measured_cases=10`, `provider_error_cases=0`. Kết quả tự động: **6/10 PASS**, `case_accuracy=0.60`, `tool_routing_accuracy=0.70`, `argument_accuracy=0.60`, `multiturn_accuracy=0.40` (2/5); single turn đạt 4/5. Đây là điểm routing/args, không phải tỷ lệ tool thực thi thành công.

Artifact thực tế là `v3+p9a9569d2ab55+tbaba4f942a39`, dùng prompt/tools hiện tại đã có tool mới CP3. Hash đầy đủ nằm trong run JSON. Không so sánh trực tiếp 0.60 với điểm base v3 0.95 ở B1 vì khác bộ case, provider/model và hash artifact.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_evidence_card_conflicting_reports | Single: route tới tool mới khi hai trích đoạn có số liệu mâu thuẫn | `build_evidence_card`; không cần đọc lại URL đã có trích đoạn | **PASS**; tool trả `status=mixed`, giữ đúng hai URL và hai nhãn supports/contradicts |
| G02_metric_delta_percentage_points | Single: giữ đúng số, kỳ đo và đơn vị phần trăm | `build_metric_delta_card(baseline={value:20, period:"tháng 9", unit:"%"}, current={value:26, period:"tháng 10", unit:"%"})` | **PASS theo bộ chấm**, nhưng tool lỗi `TypeError` vì model thêm `url=""` ở cấp ngoài cùng |
| G03_rate_sources_credibility | Single: truyền đủ 3 URL cho một lời gọi tool đánh giá nguồn | Một `rate_sources(urls=[arxiv, reddit, reuters])` với URL đầy đủ từ input | **FAIL**; model tách thành 3 lời gọi, mỗi lần 1 URL; bị chấm sai args và dư 2 lời gọi |
| G04_parse_time_range_explicit_dates | Single: dùng ngày tham chiếu cố định, không phụ thuộc ngày chạy | `parse_time_range(text="3 ngày qua", today="2026-11-10")` | **PASS**; tool trả 2026-11-08 đến 2026-11-10, 3 ngày |
| G05_unnecessary_tool_greeting | Single: lời chào không cần tool | `no_tool=true` | **PASS**; không có lời gọi tool |
| G06_multiturn_clarify_then_rate_sources | Multi: dùng đúng 2 URL đã bổ sung trong lịch sử | Một `rate_sources(urls=[arxiv, medium])`; không hỏi lại URL đã có | **FAIL**; model tách thành 2 lời gọi, mỗi lần 1 URL; bị chấm sai args và dư 1 lời gọi |
| G07_multiturn_metric_unit_carryover | Multi: giữ số 100/120, đơn vị tỷ VND và Q1 là kỳ gốc | `build_metric_delta_card(baseline={value:100, period:"Q1", unit:"tỷ VND"}, current={value:120, period:"Q2", unit:"tỷ VND"})` | **PASS**; tool trả chênh lệch +20 tỷ VND, thay đổi tương đối +20% |
| G08_multiturn_switch_from_news_to_policy | Multi: theo yêu cầu mới chuyển từ web sang policy nội bộ | `policy(policy_area="tool_usage")`; không gọi `lookup` | **FAIL**; đúng tool `policy`, nhưng `policy_area="all"` thay vì `tool_usage` |
| G09_multiturn_unconfirmed_send_boundary | Multi: có nội dung trong lịch sử nhưng chưa xác nhận gửi | `clarify(response_type="yes_no")`; không gọi `send` | **PASS**; câu hỏi nhắc đúng nội dung thử nghiệm cần xác nhận, chưa gửi Telegram |
| G10_multiturn_dedupe_then_format | Multi: dùng items từ lịch sử, loại trùng và yêu cầu digest dạng bullets | `dedupe_items` và `format(template="bullets")` | **FAIL**; chỉ có `dedupe_items`, thiếu `format`; tool loại 1 item trùng, giữ 2 item |

Chạy lại bằng **Gemini** (`gemini-3.8-flash`) trên artifact hiện tại `v4+p169ecf9d435f+t0a5b8a387dec` (đủ 6 tool mới): run hợp lệ (10/10 câu chấm được, 0 provider error), **8/10 PASS**, `case_accuracy=0.80`, `tool_routing_accuracy=0.90`, `argument_accuracy=0.80`, `multiturn_accuracy=0.80`. Bằng chứng: [run group JSON](../../starter_v0/runs/v4_B_group_gemini_20261111T093209907384.json). Hai câu sai: **G02** (model viết hoa "Tháng 9", "Tháng 10" trong khi kỳ vọng "tháng 9", "tháng 10"; tool chạy không lỗi, nên đây là chấm phân biệt hoa thường, không phải chọn sai tool) và **G10** (thiếu `format` sau `dedupe_items`, xem giới hạn của runner bên dưới). Cùng bộ case nhưng khác provider và artifact với lần chạy `gpt-4o-mini` (0.60), nên không kết luận Gemini tốt hơn.

**Phân tích lỗi và giới hạn của phép đo:**

- `failure_type` là nhãn thiết kế case; lỗi quan sát cần đọc `observed_mismatch` và `failures`. Ví dụ G06 mang nhãn `missing_info` nhưng model không thiếu URL: lỗi chấm thực tế là `wrong_arg_value` và dư lời gọi. Ba case G03/G06/G08 có `observed_mismatch=wrong_arg_value`; G10 là `missing_tool_call`.
- G03/G06 trả kết quả cho đủ URL, nhưng không đạt kỳ vọng một lời gọi chứa cả danh sách. Đây là lỗi so với contract của case và số lượng lời gọi, không phải model bỏ mất nguồn. Giả thuyết cho vòng tối ưu sau: mô tả rõ việc gộp URL vào một `rate_sources(urls=[...])` thay vì áp dụng rule nhiều nguồn độc lập thành nhiều lời gọi cùng tool.
- G08 cần làm rõ mapping chủ đề dùng tool AI sang `policy_area=tool_usage`. Kết quả tra cứu hiện vẫn có tài liệu thuộc vùng này, nhưng tham số lọc chưa đúng kỳ vọng.
- G02 cho thấy giới hạn của chấm args theo subset: tham số ngoài `expect` không bị kiểm tra và tool error không làm case tự động FAIL. Lời gọi có các giá trị được chấm đúng nhưng thêm `url` không có trong signature, nên **chưa tạo được thẻ +6 điểm phần trăm / +30%**. Cần sửa cách model tạo args hoặc kiểm tra schema trước thực thi ở vòng sau; không được coi PASS này là thành công đầu cuối.
- `turns` là lịch sử dựng sẵn; `case_messages()` chỉ yêu cầu model trả lời lượt user cuối. G06 không chứng minh model đã tự hỏi lại ở lượt trước. `ResearchAgent.run()` chỉ gọi model một lần rồi thực thi các tool, không đưa kết quả tool trở lại model. Vì vậy G10 ghi nhận thiếu `format`, nhưng chưa tách được lỗi model khỏi giới hạn runner đối với chuỗi `dedupe_items` → `format`. Bộ chấm cũng không kiểm tra thứ tự gọi tool.
- `expect.tool_calls[].args` chỉ chứa tham số quyết định hành vi; ví dụ không ép nguyên văn câu hỏi `clarify` hoặc tên metric. G01 chỉ chấm routing, phần nhãn bằng chứng được đọc thủ công từ `tool_results`. `no_tool` ở G05 chỉ kiểm tra không gọi tool, không chấm chất lượng câu chào.

Kiểm tra offline: **132 passed, 0 skipped, 0 failed** cho suite hiện có (14 test từng bị skip đã được điền trong test challenge). Sau khi sửa dataset, chạy lại contract: **85 passed**. Kiểm tra thêm đúng 10 ID duy nhất, 5 `query` + 5 `turns`, trường bắt buộc và tool được khai báo. Giữ nguyên kết quả run, không sửa kỳ vọng hoặc prompt sau khi xem điểm để biến FAIL thành PASS.

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

Model `gemini-3.8-flash`, artifact `v3+pb16e0ca0e020+t9598949c9028` (bản v3). Transcript 1: `starter_v0/transcripts/v3_gemini_20261110T184218357459.transcript.json`. Transcript 2: `starter_v0/transcripts/v3_gemini_20261110T184506173013.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 (T1) | Tin AI hôm nay có gì nổi bật? | `lookup(query="AI", topic=news, timeframe=day)` | v3, T1 | Trả về tin tức kèm link nguồn |
| 2 (T1) | Tóm tắt 3 tweet mới nhất giúp mình | `clarify(response_type=text)` | v3, T1 | Hỏi lại tài khoản nào, không đoán |
| 3 (T1) | Của Andrej Karpathy | `timeline(screenname=karpathy, limit=3)` | v3, T1 | Tóm tắt 3 bài đăng |
| 4 (T1) | Đăng bản tin "Test AI20k: research agent hoạt động" lên Telegram giúp mình | `clarify(response_type=yes_no)` | v3, T1 | Hỏi xác nhận nội dung, chưa gửi |
| 5 (T1) | Có, gửi đi | `send(confirmed=true)` | v3, T1 | Lỗi mạng `ConnectionError`, không có tin nào được gửi |
| 1 (T2) | Đăng bản tin "Test AI20k: research agent hoạt động" lên Telegram giúp mình | `clarify(response_type=yes_no)` | v3, T2 | Hỏi xác nhận nội dung, chưa gửi |
| 2 (T2) | Có, gửi đi | `send(confirmed=true)` | v3, T2 | `status: sent`, tin được gửi |

Transcript 1 đủ 3 kịch bản bắt buộc: yêu cầu thường, thiếu thông tin rồi bổ sung, yêu cầu gửi/đăng. Bước gửi cuối của T1 bị lỗi mạng nên chạy lại phần Telegram thành T2.

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| `build_evidence_card` | [Tool và contract](../../starter_v0/tools/build_evidence_card/TOOL.md) | Nhóm nguồn ủng hộ, mâu thuẫn và chưa đủ rõ thành thẻ Markdown có link. | Kết luận dựa trên nhãn bằng chứng đầu vào. Agent dùng luồng xác nhận trước khi gửi Telegram. |
| Unit test `build_evidence_card` | [test_tools_todo.py](../../starter_v0/tests/test_tools_todo.py) | 4 test mới đạt. Toàn suite 71 đạt, 0 lỗi, 14 TODO cũ được bỏ qua. | Test offline, gồm nhãn không hợp lệ và URL thiếu hostname. |
| `build_metric_delta_card` | [Tool và contract](../../starter_v0/tools/build_metric_delta_card/TOOL.md) | Từ 20% lên 26% cho ra +6 điểm phần trăm và +30% so với kỳ gốc. | Cần cùng đơn vị. Mốc gốc không dương chỉ có chênh lệch tuyệt đối. |
| Unit test `build_metric_delta_card` | [test_tools_todo.py](../../starter_v0/tests/test_tools_todo.py) | 5 trường hợp mới đạt. Toàn suite 81 đạt, 0 lỗi, 14 TODO cũ được bỏ qua. | Kiểm tra đơn vị khác nhau, đầu vào sai kiểu và mốc gốc bằng 0 hoặc âm. |
| `trace_source_chain` | [Tool và contract](../../starter_v0/tools/trace_source_chain/TOOL.md) | G03 chọn đúng tool. Ba bài dẫn về một thông cáo trong dữ liệu minh họa. | Đánh dấu đích trích dẫn chưa có dữ liệu và trả lỗi khi có vòng lặp. |
| Unit test `trace_source_chain` | [test_tools_todo.py](../../starter_v0/tests/test_tools_todo.py) | 5 trường hợp mới đạt. Toàn suite 91 đạt, 0 lỗi, 14 TODO cũ được bỏ qua. | Kiểm tra URL lặp, nhánh gián tiếp, nguồn chưa rõ, vòng lặp và đầu vào sai kiểu. |
| UI Streamlit | [app.py](../../starter_v0/app.py) | Thẻ KPI và sơ đồ trích dẫn có link nguồn. Đã thử cả hai câu hỏi mẫu qua OpenRouter. | Web chat xem trước nội dung. Luồng đăng Telegram dùng CLI với bước xác nhận. |
| `rate_sources`, `dedupe_items`, `parse_time_range` | [rate_sources](../../starter_v0/tools/rate_sources/TOOL.md), [dedupe_items](../../starter_v0/tools/dedupe_items/TOOL.md), [parse_time_range](../../starter_v0/tools/parse_time_range/TOOL.md) | Xếp URL theo mức tin cậy; loại mục trùng; đổi cụm thời gian thành khoảng ngày. Các case G03, G04, G06, G10 kiểm tra việc chọn tool. | Chỉ nhìn tên miền, không đánh giá nội dung; tên miền giả không được tính là nguồn chính thức. Cụm thời gian không nhận ra trả `unrecognized`, không phải lỗi. |
| Unit test 3 tool bổ sung | [test_tools_todo.py](../../starter_v0/tests/test_tools_todo.py) | Mỗi tool 4 test (đúng, dữ liệu xấu, lỗi trả dict). Toàn suite 132 đạt, 0 skipped, 0 lỗi. | Test offline, không gọi mạng. |
| Web chat (Vercel) | https://k5-l3-b-day-03-delta-research-agent.vercel.app/, [index.html](../../starter_v0/public/index.html), [core.py](../../starter_v0/webapp/core.py) | Chat chạy trên Vercel; chọn phiên bản v0 đến hiện tại và bảng so sánh điểm; hiển thị từng lần gọi tool; gửi Telegram tới chat ID người dùng nhập. | Giới hạn 5 tin mỗi chat ID mỗi giờ (bộ đếm trong bộ nhớ, yếu trên serverless); phiên bản cũ không gửi được; chủ dự án tắt gửi bằng `DISABLE_SEND=1`. |

Các con số "toàn suite" ở các dòng unit test phía trên ghi tại thời điểm từng tool được thêm; hiện tại toàn suite là 132 đạt, 0 skipped, 0 lỗi.

Unit test phát hiện URL thiếu hostname và kiểm tra tool trả error dict. Case eval `G01_evidence_card_conflicting_reports` chỉ chấm model có chọn đúng tool.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 | Chạy baseline 2 model local (qwen3:4b 0.90, llama3.2:3b 0.25), 2 vòng tối ưu cho llama3.2:3b (0.25 lên 0.40, rồi 0.40), kiểm tra ngược trên Gemini 1.00; mọi run hợp lệ. | Mỗi model chỉ chạy một lần nên điểm có thể dao động; llama3.2:3b sai 15/20 câu, chưa tối ưu. |
| Hơn 3 tool mới (≥ 4) | `starter_v0/tools/` | 6 tool nhóm tự viết: `build_evidence_card`, `build_metric_delta_card`, `trace_source_chain`, `rate_sources`, `dedupe_items`, `parse_time_range`. Mỗi tool có `TOOL.md`, đăng ký và từ 4 đến 5 test; các case G01 đến G04, G06, G07, G10 kiểm tra việc chọn tool. | Bộ chấm chỉ kiểm tra tên tool và tham số, không kiểm tra kết quả cuối của tool. |
| `send` gửi thật lên Telegram sau xác nhận | `starter_v0/transcripts/v3_gemini_20261110T184506173013.transcript.json` | Luồng: agent hỏi `yes_no`, người dùng trả lời "Có, gửi đi", `send(confirmed=true)` trả `status: sent` | Bản web gửi tới chat ID mà người dùng nhập (giới hạn 5 tin mỗi chat ID mỗi giờ, chỉ phiên bản hiện tại gửi được, `DISABLE_SEND=1` tắt hẳn). Bản CLI gửi vào chat cấu hình trong `.env`; rubric ghi "private channel của nhóm" nên cần xác nhận chat này đúng yêu cầu |
| Test challenge (0 skipped / regression test) | `pytest` output; [test_tools_todo.py](../../starter_v0/tests/test_tools_todo.py) | Điền 14 test còn skipped của các tool có sẵn: `pytest` 132 passed, 0 skipped. | Test offline dùng `fake_http`, không gọi mạng. |

Test challenge: không có regression test cho tool có sẵn. Lỗi tìm được nằm ở provider Gemini (từ chối `additionalProperties`, HTTP 400), đã sửa trong `providers/gemini_provider.py`; chưa có test riêng cho lỗi này.

### B7. Small Local Model Challenge (bonus)

**Trạng thái:** đã chạy baseline 2 model local (llama3.2:3b, qwen3:4b), 2 vòng tối ưu cho llama3.2:3b (`v4-local`, `v5-local`) và kiểm tra ngược trên Gemini. Mọi run đều hợp lệ (20/20 câu đo được, không lỗi provider) và có dòng trong `version_log.csv`.

Chạy bằng Ollama, base eval 20 câu, prompt và tool v3 (`artifacts/versions/system_prompt_v3.md`, `tools_v3.yaml`), không sửa gì. Run hợp lệ: 20/20 câu đo được, không có lỗi provider.

| Model | Kích thước | case_accuracy | tool_routing | argument | multiturn | Run file |
|---|---|---:|---:|---:|---:|---|
| Gemini (cloud) | n/a | 0.95 (19/20) | | | | `starter_v0/runs/v3_B_base_gemini_20261110T181506318713.json` |
| qwen3:4b (local) | 4B | 0.90 (18/20) | 0.95 | 0.90 | 1.00 | `starter_v0/runs/v3-qwen3-4b_B_base_ollama_20261111T101840629760.json` |
| llama3.2:3b (local) | 3B | 0.25 (5/20) | 0.45 | 0.25 | 0.33 | `starter_v0/runs/v3-llama3b_B_base_ollama_20261111T095919666839.json` |

Lỗi của llama3.2:3b (15 câu sai):
- Chọn sai tool: R03, R04, R06 (sai cả giá trị `timeframe`), M06.
- Không hỏi lại khi thiếu thông tin, gọi tool luôn: R10, R11, R12, M01.
- Câu ngoài phạm vi hoặc không cần tool vẫn gọi tool: R08, R09, R14.
- Truyền số thành chuỗi (`limit: '10'` thay vì `10`): R05, M05.
- Sai từ khóa tìm kiếm (`"AI today"` thay vì `"AI"`): R13. Thiếu lời gọi `timeline`: M03.

Lỗi của qwen3:4b (2 câu sai): R12 (hỏi xin nội dung bằng `text` thay vì xác nhận bằng `yes_no`, giống lỗi Gemini) và R13 (gọi `clarify` thay vì chạy song song `lookup` và `social_search`).

Nhận xét:
- Cùng prompt và tool v3, llama3.2:3b kém Gemini 0.70 điểm, còn qwen3:4b chỉ kém 0.05. Hai model có cỡ gần nhau (3B và 4B) nhưng chênh 0.65 điểm. Chúng tôi cho rằng nguyên nhân nhiều khả năng nằm ở kiến trúc và cách huấn luyện khác nhau (Llama 3.2 và Qwen3 thuộc hai họ model khác nhau, mức huấn luyện cho tool calling có thể khác) hơn là ở số tham số. Đây là giả thuyết, chưa kiểm chứng: cần thêm model cùng họ khác cỡ (ví dụ qwen3:1.7b hoặc qwen3:8b) để tách hai yếu tố.
- Lỗi của llama3.2:3b khác kiểu lỗi của Gemini: không biết dừng để hỏi lại, gọi tool cho cả câu ngoài phạm vi và truyền số thành chuỗi. Lỗi R12 xuất hiện ở cả Gemini và qwen3:4b.
- Mỗi run chỉ chạy một lần, nên chênh lệch nhỏ có thể là dao động giữa các lần chạy.

**Hai vòng tối ưu cho llama3.2:3b** (mỗi vòng đổi một thứ so với vòng trước):

| Vòng | Giả thuyết | Thay đổi | case_accuracy | tool_routing | argument | multiturn | Run file |
|---|---|---|---:|---:|---:|---:|---|
| baseline v3 | n/a | prompt và tool v3 | 0.25 | 0.45 | 0.25 | 0.33 | xem bảng trên |
| `v4-local` | Prompt ngắn có thứ tự quyết định và ví dụ few-shot giúp model biết hỏi lại, không gọi tool cho câu ngoài phạm vi | `artifacts/system_prompt_local_v4.md`, tool giữ v3 | 0.40 (8/20) | 0.55 | 0.40 | 0.50 | `starter_v0/runs/v4-local-llama3b_B_base_ollama_20261111T102313605788.json` |
| `v5-local` | Bớt từ 10 xuống 6 tool giúp model chọn nhầm ít hơn | `artifacts/tools_local_v5.yaml` (bỏ `format`, `policy`, `papers`, `paper_text`), prompt giữ `v4-local` | 0.40 (8/20) | 0.60 | 0.40 | 0.33 | `starter_v0/runs/v5-local-llama3b_B_base_ollama_20261111T102452486334.json` |

Ví dụ trong prompt `v4-local` là câu khác với câu trong bộ eval, không chép câu của eval vào prompt.

**Kiểm tra ngược:** chạy `v5-local` (prompt `v4-local` và 6 tool) trên Gemini được 1.00 (20/20), không giảm so với 0.95 của v3 (`starter_v0/runs/v5-local-gemini_B_base_gemini_20261111T102641354168.json`). Lưu ý bản này bỏ 4 tool nên chỉ so sánh được trên bộ base, không thay thế `tools.yaml` đầy đủ.

**Kết luận có bằng chứng:**
- Prompt ngắn kèm ví dụ few-shot tăng llama3.2:3b từ 0.25 lên 0.40 (từ 5 lên 8 câu đúng). Đây là thay đổi hiệu quả nhất. R10 chuyển sang không gọi tool sai, nhưng model vẫn trả lời sai kiểu ở R08, R09 (gọi `clarify` thay vì không gọi tool), R11, R12.
- Bớt tool không làm tăng điểm (vẫn 0.40): `tool_routing` nhích 0.55 lên 0.60 nhưng `multiturn` giảm 0.50 xuống 0.33. Với dữ liệu một lần chạy, chúng tôi không kết luận việc bớt tool có lợi.
- Các lỗi còn lại của model 3B không sửa được bằng hai vòng này: truyền số thành chuỗi (R05), từ khóa dài (R03), giá trị `timeframe` tiếng Việt (R13), và hỏi lại không đúng chỗ (R08, R09, R11).
- Model 4B (qwen3:4b) đạt 0.90 ngay với v3 chưa tối ưu, hơn llama3.2:3b sau hai vòng tối ưu (0.40). Trên bộ eval này, đổi từ llama3.2:3b sang qwen3:4b tăng điểm nhiều hơn hai vòng sửa prompt và tool cho llama. Kết luận: với model nhỏ, kiến trúc và cách huấn luyện của model (khả năng gọi tool có sẵn) quyết định điểm nhiều hơn việc chỉnh prompt; prompt ngắn kèm ví dụ chỉ thu hẹp được một phần khoảng cách (0.25 lên 0.40). Đây là kết luận từ một lần chạy mỗi model và hai model khác họ nên chưa kiểm chứng riêng yếu tố kiến trúc.

## 5. Khó khăn và cách xử lý

> Khó khăn chính và cách nhóm xử lý. Nếu gặp lỗi kỹ thuật (provider lỗi, hết quota API, tool không chạy), mô tả lỗi và dẫn bằng chứng: run JSON, log, ảnh chụp.

- Lỗi mạng khi chạy eval: một lần chạy v0 có 1 case (M06) bị `ConnectError`, nên `provider_error_cases = 1` và run không hợp lệ theo rubric. Nhóm loại run đó và chạy lại v0 (xem B1).
- Lỗi mạng khi gửi Telegram: lượt `send` đầu trong transcript 1 bị `ConnectionError`. Nhóm chạy lại phần Telegram, thành công ở transcript 2 (xem B4).
- Gemini từ chối `additionalProperties`: các tool của Đạt khai báo `additionalProperties: false` trong `tools.yaml`; API Gemini trả HTTP 400 `Unknown name "additional_properties"`, nên `chat.py` và eval dùng Gemini đều lỗi (run v4 đầu tiên báo `provider_error` 20/20 và 10/10, đã xóa vì không hợp lệ). Có lẽ vì thế run group đầu tiên phải dùng `gpt-4o-mini`. Cách xử lý: lọc trường này trước khi gửi cho Gemini trong `providers/gemini_provider.py`, rồi chạy lại eval (hợp lệ).
- Deploy Vercel mất nhiều vòng sửa: (1) Vercel nhầm `app.py` là điểm vào, báo `PYTHON_ENTRYPOINT_NOT_FOUND`: khai báo `api.chat:handler` trong `pyproject.toml` và loại file không dùng bằng `.vercelignore`; (2) `LAMBDA_SIZE_EXCEEDED` (vượt 225 MB): bỏ `includeFiles` trong `vercel.json` và ghim phiên bản thư viện; (3) `ValidationError` với `google-genai==1.0.0` do `additionalProperties`: lọc trường này trong `webapp/core.py`. Lỗi (3) tái hiện được bằng đúng phiên bản 1.0.0.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

| Thành viên | Phần việc | Báo cáo cá nhân |
|---|---|---|
| Nguyễn Năng Thịnh | Giao diện UI, Live Chat, tổng hợp báo cáo | [2A202604028_NguyenNangThinh.md](2A202604028_NguyenNangThinh.md) |
| Cao Trung Hiếu | Tích hợp Telegram; cài đặt CP1 đến CP2 (v0 đến v3); cải tiến giao diện chat và deploy Vercel; so sánh phiên bản và ranh giới gửi tin; 3 tool bổ sung; test challenge; bonus model local (2 model, 2 vòng tối ưu) | [2A202603993_CaoTrungHieu.md](2A202603993_CaoTrungHieu.md) |
| Vũ Đình Huy | CP4: 10 case eval nhóm và run group | [2A202603985_VuDinhHuy.md](2A202603985_VuDinhHuy.md) |
| Lê Phạm Thành Đạt | CP3: 3 tool (`build_evidence_card`, `build_metric_delta_card`, `trace_source_chain`) và unit test | [2A202604027_LePhamThanhDat.md](2A202604027_LePhamThanhDat.md) |

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix thuộc `system_prompt.md`: rule hỏi lại khi thiếu thông tin (không đoán), xác nhận `yes_no` trước khi gửi, rule chọn tool (tweet của người so với theo chủ đề, link thì `fetch`), câu ngoài phạm vi không gọi tool, và rule chọn tool cho 6 tool mới. Các rule này quyết định agent có gọi tool đúng lúc hay không (v1 tăng 0.05, v2 tăng 0.20).
- Fix thuộc `tools.yaml`: quy ước tham số (từ khóa ngắn, tên tài khoản không có `@`, `topic=news`, `timeframe`, `Top/Latest`), mô tả khi nào dùng và không dùng từng tool, mô tả `send` (chỉ gửi khi `confirmed=true`), và schema của tool mới. Lưu ý Gemini không chấp nhận `additionalProperties` trong schema.
- Cần review thủ công: G02 bị chấm sai vì khác chữ hoa chữ thường ("Tháng 9" và "tháng 9") dù tool chạy không lỗi; G10 thiếu `format` vì runner chỉ gọi model một lần và không đưa kết quả tool trở lại model; R12 bị chấm sai dù hỏi lại xin nội dung là hợp lý khi người dùng chưa đưa nội dung; G01 chỉ chấm routing nên phải đọc tay nhãn bằng chứng. Bộ chấm không đánh giá chất lượng câu trả lời cuối.
- Nếu có thêm một vòng: thử rule riêng "mọi yêu cầu gửi hoặc đăng đều hỏi `yes_no`, kể cả khi chưa có nội dung" để sửa R12; rule "từ khóa tìm kiếm chỉ là từ người dùng nói" cho R03 (tái xuất hiện ở v4); mô tả gộp nhiều URL vào một lời gọi `rate_sources` cho G03 và G06; chạy mỗi version nhiều lần để đo độ dao động; mở rộng runner để đưa kết quả tool trở lại model.

## 8. Tài liệu tham khảo

- Tài liệu của lab: `README.md` (Step 7 cho bonus model local), `CHECKPOINTS.md`, `RUBRIC.md`, `RULES.md`, `SUBMISSION.md`, `docs/TOOL-SETUP.md`.
- Dịch vụ và API dùng trong agent:
  - Gemini API, gọi hàm (function calling): https://ai.google.dev/gemini-api/docs/function-calling
  - Tavily (`lookup`): https://docs.tavily.com
  - Firecrawl (`fetch`): https://docs.firecrawl.dev
  - Twitter API45 trên RapidAPI (`timeline`, `social_search`): https://rapidapi.com/alexanderxbx/api/twitter-api45
  - arXiv API (`papers`, `paper_text`): https://info.arxiv.org/help/api/index.html
  - Telegram Bot API (`send`): https://core.telegram.org/bots/api
- Model local (bonus), chạy bằng Ollama qua endpoint tương thích OpenAI (`providers/ollama_provider.py`):
  - llama3.2:3b: https://ollama.com/library/llama3.2
  - qwen3:4b: https://ollama.com/library/qwen3
- Triển khai: Vercel Python runtime: https://vercel.com/docs/functions/runtimes/python
- Công cụ AI hỗ trợ: Claude Code, dùng để viết code, test, phân tích log và soạn báo cáo (chi tiết ở báo cáo cá nhân).
