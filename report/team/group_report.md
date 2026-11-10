# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: Delta
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: Gemini (`gemini-3.8-flash`), provider `gemini`

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Research agent: tìm tin trên web, tìm bài đăng X/Twitter theo chủ đề hoặc theo tài khoản, đọc nội dung một URL, tìm và đọc paper arXiv, tra chính sách nội bộ, tổng hợp thành digest, và chỉ gửi lên Telegram sau khi người dùng xác nhận. Khi thiếu thông tin (không có tài khoản hoặc link) agent hỏi lại thay vì đoán; câu ngoài phạm vi research thì không gọi tool.

**Cách chạy UI:**

Có hai giao diện, cùng dùng agent và bộ `artifacts/` v3:
- Streamlit: `cd starter_v0 && pip install -r requirements.txt && streamlit run app.py` (http://localhost:8501). `streamlit` đã thêm vào `starter_v0/requirements.txt`.
- Web kiểu Vercel (`public/index.html` + `api/chat.py`): chạy thử trên máy bằng `cd starter_v0 && python dev_server.py` (http://localhost:8000). Ở bản này mỗi người nhập chat ID Telegram của mình ở giao diện để nhận tin ở chat đó.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL:

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

### A3. Câu hỏi mẫu để thử

1. `Tweet mới nhất của Sam Altman là gì?`: agent gọi `timeline` với tài khoản `sama`.
2. `Mọi người đang bàn gì về GPT-5 trên Twitter?`: agent gọi `social_search` (tìm theo chủ đề).
3. `Tin tức AI hôm nay có gì nổi bật?`: agent gọi `lookup` với tin tức trong ngày.
4. `Tóm tắt giúp mình bài này: https://openai.com/blog/gpt-5`: agent gọi `fetch` đúng link đó.
5. `Tóm tắt 5 tweet mới nhất giúp mình`: agent **hỏi lại** tài khoản nào; trả lời `Của Elon Musk` thì agent mới lấy tweet.
6. `Đăng bản tin này lên Telegram giúp mình`: agent **hỏi lại trước**, không gửi ngay.

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
    * Bổ sung 3 custom tools:
| Tên | Chức năng | Khi nào agent nên gọi |
|---|---|---|
| build_evidence_card | Đối chiếu nhận định với bằng chứng, phân loại nguồn thành ủng hộ, mâu thuẫn hoặc chưa rõ | Khi người dùng muốn kiểm chứng thông tin hoặc giải thích sự khác biệt giữa các nguồn |
| build_metric_delta_card | Tính mức thay đổi tuyệt đối và tương đối giữa hai giá trị KPI | Khi người dùng muốn so sánh số liệu trước/sau hoặc phân tích mức tăng, giảm |
| trace_source_chain | Truy vết quan hệ trích dẫn, xác định nhiều bài viết có sử dụng chung một nguồn hay không | Khi người dùng muốn kiểm tra tính độc lập của nguồn tin hoặc truy tìm nguồn gốc thông tin |

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

Metric là `case_accuracy` trên `eval_base.json` (20 case). Cả 4 run đều hợp lệ: `provider_error_cases = 0`, `measured_cases = 20/20`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline (prompt + tools gốc của starter) | Prompt gốc bảo đoán thay vì hỏi, gửi luôn, làm một bước nên agent đoán tài khoản/link và chỉ dùng một tool | n/a | 0.70 (14/20) | `starter_v0/runs/v0_B_base_gemini_20261110T182050282289.json` |
| v1 | `system_prompt` + mô tả `send` | Lỗi đoán bừa và gửi không xác nhận (R10, R11, R12) do prompt ép đoán/gửi ngay và mô tả `send` mơ hồ | 0.70 | 0.75 (15/20) | `starter_v0/runs/v1_B_base_gemini_20261110T181033805432.json` |
| v2 | `system_prompt` + quy ước tham số trong `tools.yaml` | Lỗi `query` dài và sai tham số (R03, R06, R13, M02) do thiếu quy ước routing và tham số | 0.75 | 0.95 (19/20) | `starter_v0/runs/v2_B_base_gemini_20261110T181241484099.json` |
| v3 | `system_prompt` + viết lại mô tả mọi tool | Mô tả rõ ranh giới dùng / không dùng giúp model chọn tool ổn định hơn | 0.95 | 0.95 (19/20) | `starter_v0/runs/v3_B_base_gemini_20261110T181506318713.json` |

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

Nhận xét:
- v2 là bước hiệu quả nhất (+0.20). v3 không tăng điểm so với v2: viết lại mô tả không cải thiện thêm trên bộ base.
- v1 và v2 sửa cả prompt lẫn `tools.yaml` trong cùng một vòng, nhưng cùng nhắm vào một nhóm lỗi.
- v3 viết lại prompt và mô tả mọi tool theo cùng một giả thuyết: ghi rõ khi nào dùng / không dùng từng tool.
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

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_evidence_card_conflicting_reports | Chọn công cụ tạo thẻ bằng chứng khi hai nguồn đưa ra số liệu gọi vốn mâu thuẫn (50 triệu USD và 40 triệu USD) | build_evidence_card |  |

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

Unit test phát hiện URL thiếu hostname và kiểm tra tool trả error dict. Case eval `G01_evidence_card_conflicting_reports` chỉ chấm model có chọn đúng tool.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | `starter_v0/transcripts/v3_gemini_20261110T184506173013.transcript.json` | Luồng: agent hỏi `yes_no`, người dùng trả lời "Có, gửi đi", `send(confirmed=true)` trả `status: sent` | Bản web mặc định tắt `send`. Tin gửi vào chat Telegram cấu hình trong `.env`; rubric ghi "private channel của nhóm" nên cần xác nhận chat này đúng yêu cầu |
| Test challenge (0 skipped / regression test) | `pytest` output |  |  |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?

## 5. Khó khăn và cách xử lý

> Khó khăn chính và cách nhóm xử lý. Nếu gặp lỗi kỹ thuật (provider lỗi, hết quota API, tool không chạy), mô tả lỗi và dẫn bằng chứng: run JSON, log, ảnh chụp.

- Lỗi mạng khi chạy eval: một lần chạy v0 có 1 case (M06) bị `ConnectError`, nên `provider_error_cases = 1` và run không hợp lệ theo rubric. Nhóm loại run đó và chạy lại v0 (xem B1).
- Lỗi mạng khi gửi Telegram: lượt `send` đầu trong transcript 1 bị `ConnectionError`. Nhóm chạy lại phần Telegram, thành công ở transcript 2 (xem B4).

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
