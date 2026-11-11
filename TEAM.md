# Team

## Thông tin nhóm

- Tên nhóm:Delta
- Lớp: L3B
- Repo nhóm: https://github.com/liliustwocout/K5-L3B-DAY03-Delta-ResearchAgentToolEval
- URL repo, nhánh nộp, commit chốt:

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Năng Thịnh | 2A202604028 | thinh010705@gmail.com | Thinh010705 | Thành viên |
|   2 | Cao Trung Hiếu | 2A202603993 |       |        |         |
|   3 | Vũ Đình Huy | 2A202603985 |       |        |         |
|   4 | Lê Phạm Thành Đạt | 2A202604027 | 26ai.datlpt@vinuni.edu.vn | liliustwocout | CP3 · Tool mới và unit test |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## NguyenNangThinh_2A202604028

### Phần việc phụ trách

- Phát triển giao diện UI và triển khai (deploy) ứng dụng.

- Xây dựng chức năng Live Chat, hỗ trợ tương tác trực tiếp với Agent.

- Tổng hợp, biên soạn và hoàn thiện báo cáo cho toàn bộ dự án.

### Đóng góp cụ thể

- Xây dựng giao diện người dùng, giúp người dùng tương tác với hệ thống thông qua UI.

- Triển khai ứng dụng lên môi trường deploy để kiểm thử và trải nghiệm thực tế.

- Phát triển chức năng Live Chat, kết nối giao diện với Agent để xử lý yêu cầu và hiển thị phản hồi.

- Tổng hợp kết quả thực hiện, mô tả quy trình, đánh giá và hoàn thiện báo cáo tổng thể của nhóm.

### Bằng chứng

- Source code phần UI và Live Chat trong repository.
- File báo cáo tổng thể của dự án (group_report.md và các tài liệu liên quan).
- Commit: b690b9e6f3b3712139c669a92a3eb6acbb7c57a1, df1e05cbd6d4eddbf16a1fe78b2d8135a3500ba6, 898c56b8ecbfcec66eafb3bc44f4abb8029cde6d

## VuDinhHuy-2A202603985

### Phần việc phụ trách

- Tôi phụ trách **CP4 — Eval nhóm 10 case**. Nhiệm vụ gồm hoàn thiện bộ đánh giá riêng của nhóm với 5 case single turn và 5 case multi turn, kiểm tra việc model chọn tool và truyền tham số, chạy eval bằng API thật, lưu run JSON và tổng hợp kết quả vào bảng B3 của báo cáo nhóm.

- Bộ case tập trung vào các tình huống liên quan đến tool mới của nhóm, việc dùng thông tin từ lịch sử hội thoại, không gọi tool khi không cần thiết và hỏi xác nhận trước khi gửi Telegram. Sản phẩm bàn giao gồm `eval_group.json`, run `--suite group` và phần phân tích B3.


### Đóng góp cụ thể

- **Hoàn thiện dữ liệu đánh giá.** Chuẩn hóa đúng 10 case, mỗi case có ID riêng, `phase="B"`, `query` hoặc `turns`, `failure_type`, `expect` và `metadata.what_it_tests`. Bổ sung các tham số cần kiểm tra như danh sách URL, giá trị, kỳ đo và đơn vị; cố định ngày tham chiếu ở G04 để kết quả không phụ thuộc ngày chạy. Chỉ đưa vào `expect.tool_calls[].args` các tham số quyết định hành vi, tránh ép model phải dùng nguyên văn câu hỏi hoặc tên metric.

### Bằng chứng

Các sản phẩm và mã nguồn dùng để đối chiếu:

- [Bộ 10 case của nhóm](../../starter_v0/data/eval_group.json): dữ liệu đầu vào, kỳ vọng và mục đích từng case.
- [Run group thực tế](../../starter_v0/runs/v3_B_group_openai_20261110T233006708870.json): cấu hình, hash artifact, toàn bộ lời gọi tool, kết quả thực thi và điểm chấm.
- [Bảng B3 — Team Eval Cases](group_report.md#b3-team-eval-cases): kết quả từng case, phân tích lỗi và giới hạn phép đo.
- [run_eval.py](../../starter_v0/run_eval.py) và [agent.py](../../starter_v0/agent.py): đối chiếu cách xử lý lịch sử hội thoại, chấm args và thực thi tool.
- Commit lưu sản phẩm CP4 trong lịch sử repo: `f0efde3` — `push cp4`.

## HoVaTen-MSSV

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-

## LePhamThanhDat_2A202604027

### Phần việc phụ trách

- CP3 · Thiết kế, triển khai, đăng ký tool mới và viết unit test offline cho Research Agent.

### Đóng góp cụ thể

- `build_evidence_card` nhóm trích đoạn theo mức ủng hộ, mâu thuẫn hoặc chưa đủ rõ, kèm link nguồn.
- `build_metric_delta_card` tính chênh lệch tuyệt đối và tương đối giữa hai kỳ, phân biệt điểm phần trăm với phần trăm thay đổi.
- `trace_source_chain` lần theo trích dẫn, gộp URL trùng và tạo sơ đồ nguồn trong Streamlit.
- Bổ sung 14 trường hợp test offline và các case kiểm tra việc chọn tool trên OpenRouter.

### Bằng chứng

- Thẻ bằng chứng, commit `ccfd311`. [PR #2](https://github.com/liliustwocout/K5-L3B-DAY03-Delta-ResearchAgentToolEval/pull/2)
- Thẻ số liệu và UI demo, commit `f1d7db5`. [PR #3](https://github.com/liliustwocout/K5-L3B-DAY03-Delta-ResearchAgentToolEval/pull/3)
- Tool và sơ đồ truy dấu nguồn, commit `643f266`. [PR #4](https://github.com/liliustwocout/K5-L3B-DAY03-Delta-ResearchAgentToolEval/pull/4)
- [Báo cáo cá nhân của Đạt](report/team/2A202604027_LePhamThanhDat.md) · [Unit test CP3](starter_v0/tests/test_tools_todo.py)
