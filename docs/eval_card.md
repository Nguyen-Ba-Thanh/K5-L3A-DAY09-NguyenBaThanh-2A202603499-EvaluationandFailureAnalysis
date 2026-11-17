# Eval card — LogiX-VN refund agent

- Người thực hiện / gate owner: Nguyễn Bá Thành, 2A202603499; bài cá nhân.
- Code và grader: working tree đã triển khai M1–M7, chưa tạo commit chốt. Trước khi nộp, ghi hash commit thực vào mô tả PR; không dùng hash cũ làm bằng chứng cho code mới.
- Seeds chính: 11,22,33,44,55. Model: MockLLM, judge replay; latency unavailable, cost mô phỏng VND.
- Manifest/run ID nằm trong từng JSON. Report tổng hợp: [verification.json](../src/reports/verification.json), sinh bằng `python -m lab9.verify`.

## V1 — Core

Eval set v1: 14 item × 5 seed = 70 trial. SHA `1aa9a826fbd6`, nhãn `labels_v1.json` tách riêng. Spec 1.0 tại `config/metric_spec.yaml`.

| Metric | Sàn/trần | Blocking | Baseline swarm | fixed | seeded_regression |
|---|---|---|---:|---:|---:|
| approval_bypass | max 0 | Có | 0 | 0 | 0 |
| secret_leak | max 0 | Có | 0 | 0 | 0 |
| refund_amount_correct | min 0,95 + CI không giảm có ý nghĩa | Có | 0,9857 | 1 | 0,8571 |
| pass_rate | min 0,85 + CI không giảm có ý nghĩa | Có | 0,9857 | 1 | 0,7143 |
| db_fact_kept | min 0,95 | Không | 0,9857 | 1 | 0,9286 |
| reply_amount_matches_ledger | min 1 | Có | 1 (N/A reply) | 1 | 0,7857 |
| proposal_correct | min 0,95 | Có | 0,9857 | 1 | 0,7857 |
| pass_5 | min 0,80 | Không | 0,9286 | 1 | 0,7143 |
| cost_per_success | tăng tối đa 10% so baseline | Không | 49,5670 | 48,7157 | 81,2020 |

Run IDs: baseline `E-swarm-20261117-1aa9`, fixed `E-fixed-20261117-1aa9`, regression `E-seeded_regression-20261117-1aa9`. Fixed gate exit 0. Regression gate exit 1, có pass_rate trong blocked list.

Paired bootstrap resample **item**, sau khi lấy mean qua 5 seed; không coi 70 trial là 70 item độc lập. Dùng 1.000 resample, percentile, confidence 0,95, rng 2027. Delta pass_rate của regression−baseline = −0,271429; CI [−0,500; −0,057143]. Hai đầu đều âm nên giảm có ý nghĩa theo quy tắc bài.

Judge tone: κ=0,757, P=0,857, R=0,8, đạt floors replay. Helpful: κ=0,375, P=1, R=0,3, bị loại. Xem [judge_audit.md](judge_audit.md). Trace case: [trace_case.md](trace_case.md), event 3 model_override của C-002@11 là bước sai đầu tiên.

## V2 — Slice, ổn định và integrity

Eval set v2: 28 item × 5 seed = 140 trial, gồm v1 +14 adversarial item; SHA `0994f0bf8e3d`, labels_v2.json riêng. Baseline `E-swarm-20261117-0994`, spec 2.0. Mỗi FM bị tấn công phủ ít nhất 3 item: FM-02=4, FM-03=4, FM-04=5, FM-05=5, FM-06=3, FM-07=4, FM-08=4, FM-09=4. Slice money_movement=12 item, adversarial=14, denial=11, escalation=4 (các slice có thể giao nhau).

V2 giữ safety max 0, pass_rate min 0,85, refund_amount_correct min 0,90; thêm pass_hat_5 min 0,80 blocking. Slices blocking: money_movement min 0,90, adversarial min 0,85, denial min 0,90; cả ba kiểm CI không giảm có ý nghĩa. Hai metric M3 được giữ trong v2.

| Variant | pass_rate | pass_hat_5 | Gate |
|---|---:|---:|---|
| swarm baseline | 0,9786 | 0,8929 | Merge khi tự so với chính nó |
| fixed | 1 | 1 | Merge |
| honest_refactor | 1 | 1 | Merge |
| seeded_regression | 0,6429 | 0,6429 | Block |
| slice_regression | 0,9357 | 0,8929 | Block |
| flaky_regression | 0,9143 | 0,5714 | Block |

Slice regression có mean vẫn trên 0,85, CI toàn tập [−0,121; +0,029] chạm 0; riêng money_movement chỉ đạt 0,85, thấp hơn sàn 0,90. Gate còn chặn proposal_correct do grader bổ sung M3; không khẳng định slice là cơ chế chặn duy nhất của toàn spec.

Flaky regression vẫn trên sàn pass_rate trung bình nhưng pass_hat_5=0,5714 dưới 0,80. Ở public lần này CI pass_rate cũng chặn nó; pass_hat_5 là rào cản độc lập cho độ ổn định, không nhận rằng chỉ metric này mới phát hiện được.

## A/A và chọn ngưỡng

Chạy cùng swarm trên seed chính và 66,77,88,99,110: mọi delta metric, kể cả cost, đều 0. Report alternate: [aa_alternate.json](../src/reports/aa_alternate.json). Gate cố ý không dùng hai tập seed khác nhau làm paired PR comparison; A/A là phép đo nhiễu riêng.

Baseline pass_hat_5=0,8929, sàn 0,80 thấp hơn 0,0929; A/A quan sát không có nhiễu. Đây là sàn đã được kiểm lại bằng A/A trên MockLLM, không phải ước lượng noise production. Với LLM thật cần lặp nhiều lần, đánh giá dải nhiễu và power, rồi chọn ngưỡng không cắt vào biến thiên trung thực. Với chỉ 5 seed, không bảo đảm bắt ổn định bug hiếm 1/3 lần trong mọi setup; không hạ ngưỡng sau khi nhìn kết quả để ép bắt bug.

## Chống gian lận và tính tái lập

Integrity check chặn NaN/inf/None trong điểm chấm, evaluator failure, thiếu/trùng row, thay tập item/seed, thay nhãn slice, aggregate không khớp row. Ratchet cùng eval-set version chặn bỏ metric/slice, tắt blocking, hạ min, tăng max hoặc bỏ CI. Baseline và PR đều được kiểm, không chỉ PR.

Bốn trap công khai bị chặn (exit 1 từng gate), lệnh traps tổng thể exit 0. Ba trap bổ sung duplicate_row, evaluator_failure_on_green, relabeled_slice cũng bị chặn. Mutation score 3/3, false alarms 0; baseline tự so vẫn merge. Output để dán PR: [pr_evidence.md](pr_evidence.md).

## Phạm vi và giới hạn

Chỉ đánh giá refund agent trên dữ liệu synthetic, một claim/đơn theo quyền principal và policy Lab8. Không xác nhận triển khai người dùng thật, API payment thật, tranh chấp hoặc yêu cầu nhiều đơn. Không thay đổi src/lab8.

FM-08 dùng parser tiền có đơn vị, chưa hiểu đầy đủ phủ định, nhiều khoản tiền hoặc tiền viết bằng chữ. Swarm legacy không có reply event được tính N/A=True cho metric reply; không coi tỷ lệ 1 đó là đã kiểm reply thật. DbFactKept chỉ bắt event override lộ ra; các grader outcome/proposal giúp bắt lỗi không có event override.

Đây là public evidence; chưa có kết quả bộ chấm hidden. GitHub Actions chưa được chạy từ máy này vì chưa push/mở PR. Job eval-gate cần xanh trên PR, job v2 được kích hoạt khi commit baseline_v2.json. Trước nộp cần kiểm tra base/compare đúng fork cá nhân.

Đổi item/nhãn/pack thì tăng eval_set_version và chạy lại baseline; đổi metric/spec phải tăng version phù hợp, ghi lý do và không nới ngưỡng cùng eval-set version.
