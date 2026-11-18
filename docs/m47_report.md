# Báo cáo và giải thích M4–M7 — Nguyễn Bá Thành

Triển khai cá nhân với Codex hỗ trợ trên `starter/d09`. Không sửa package `src/lab8/`, các variant, trap hoặc test được cung cấp. Report được sinh bằng script. Kết quả tổng hợp: [verification.json](../src/reports/verification.json); nội dung dán PR: [pr_evidence.md](pr_evidence.md).

## 1. Quy trình sau khi có grader M1–M3

```text
Eval set + nhãn + spec + seed cố định
                 ↓
Chạy baseline và bản mới trên cùng các tình huống
                 ↓
Kiểm report đầy đủ, hợp lệ, không bị chỉnh để che lỗi (M7)
                 ↓
So kết quả tổng thể bằng sàn và paired CI (M4)
                 ↓
So riêng nhóm quan trọng: hoàn tiền, đối kháng (M5)
                 ↓
Kiểm ổn định qua nhiều seed bằng pass^5 (M6)
                 ↓
Không có lý do chặn → exit 0; có vi phạm → exit 1
```

## 2. M4 — Bản mới có kém đi đủ rõ không?

Baseline là swarm có sẵn. V1 có 14 item, mỗi item chạy 5 seed. Đầu tiên lấy mean của mỗi item qua seed, rồi bootstrap các cặp item của hai bản. Cách này giữ cùng câu hỏi ở hai vế và tránh coi 5 lần chạy của một câu hỏi là 5 câu hỏi độc lập.

Đã dùng SciPy paired percentile bootstrap, 1.000 resample, confidence 95%, rng 2027. Nếu delta CI nằm hoàn toàn dưới 0 thì bản mới giảm có ý nghĩa theo quy tắc lab. Dù CI chưa chứng minh giảm, bản mới vẫn bị chặn nếu dưới sàn tuyệt đối hoặc vi phạm safety.

| V1 | Pass rate | Gate |
|---|---:|---|
| swarm baseline | 0,9857 | Tự so merge |
| fixed | 1,0000 | exit 0 |
| seeded_regression | 0,7143 | exit 1, có pass_rate |

Regression−baseline: delta −0,271429, CI [−0,500;−0,057143]. Cả hai đầu đều âm, khớp giá trị tham chiếu trong đề. Bằng chứng gồm baseline_v1.json, eval_fixed.json, eval_seeded_regression.json. SHA chuẩn LF: `1aa9a826fbd6`.

## 3. M5 — Trung bình tốt có thể che một nhóm đang hỏng

Đã map attack mechanisms trong fm_map.yaml sang mã taxonomy, build v2 gồm 28 item. Mỗi FM được adversarial pack tấn công có ít nhất 3 item phủ. SHA `0994f0bf8e3d`, labels riêng. Money_movement có 12 item, adversarial 14; một item có thể thuộc nhiều slice.

Ví dụ slice_regression: pass_rate toàn tập **0,9357**, trên sàn 0,85. CI delta toàn tập [−0,121; +0,029] chạm 0 nên chưa đủ bằng chứng giảm toàn tập. Nhưng riêng nhóm có tiền chuyển, tỷ lệ chỉ **0,85**, dưới sàn money_movement **0,90**, nên slice gate chặn.

Đây là lý do không được chỉ đọc điểm trung bình: nhóm hiếm nhưng quan trọng có thể chịu lỗi nặng. Với spec hiện tại, proposal_correct cũng chặn bản này; không nhận rằng slice là lý do duy nhất trong toàn bộ spec.

## 4. M6 — Có lúc đúng khác với đúng ổn định

Đã implement và kiểm input cho hai estimator:

- pass@k: xác suất ít nhất một lần đúng trong k lần lấy từ n trial có c lần đúng: `1 − C(n−c,k)/C(n,k)`.
- pass^k (pass_hat_k): xác suất cả k lần đều đúng: `C(c,k)/C(n,k)`.

Ví dụ n=5,c=4,k=5: pass@5=1 nhưng pass^5=0. Tìm được một câu trả lời đúng chưa đủ cho agent tự động chuyển tiền; cần ổn định qua nhiều lần.

| V2 | Pass rate | Pass^5 |
|---|---:|---:|
| swarm | 0,9786 | 0,8929 |
| fixed / honest_refactor | 1 | 1 |
| flaky_regression | 0,9143 | 0,5714 |

Flaky vẫn trên sàn trung bình 0,85 nhưng bị sàn pass_hat_5=0,80 chặn. Trong lần public này, CI pass_rate và metric khác cũng chặn nó; pass^5 bổ sung một kiểm tra về độ tin cậy độc lập.

A/A chạy cùng swarm trên seed 11,22,33,44,55 và 66,77,88,99,110: delta mọi metric bằng 0. Baseline pass^5=0,8929, cách sàn 0,80 là 0,0929; không thấy honest noise cắt sàn trong MockLLM. Không suy ra noise production bằng 0. Năm seed còn ít, không bảo đảm phát hiện ổn định mọi bug hiếm; cần nhiều mẫu hơn và held-out thật trước quyết định production.

## 5. M7 — Kiểm tra bài thi chưa bị làm đẹp

Nếu chỉ nhìn tỷ lệ pass, một report có thể giả tốt bằng cách bỏ case fail, bỏ seed xấu hoặc để lỗi grader thành None/NaN rồi rơi khỏi trung bình.

Integrity check đã kiểm:

- Đủ item×seed và mỗi cặp chỉ xuất hiện một lần; tập cặp trùng baseline.
- Không có evaluator failure hoặc score thiếu/không hữu hạn; số tổng hợp được tính lại từ rows.
- Tag slice không thay đổi theo seed hoặc so với baseline.
- Cả baseline và PR đều hợp lệ.
- Ratchet cùng eval-set version: không bỏ metric/slice, tắt blocking, hạ min, tăng max hoặc bỏ yêu cầu CI khi có --base-spec.

Kết quả: 4 trap công khai đều gate exit 1 với INTEGRITY; thêm duplicate_row, evaluator_failure_on_green và relabeled_slice cũng bị chặn. Baseline tự so vẫn merge. Lệnh traps tổng thể exit 0 nghĩa là mọi trap đã bị bắt, không phải các report trap được cho qua.

Không khớp cứng tên variant/trap. Việc chặn dựa vào dữ liệu, metric và cấu trúc report. Bộ chấm hidden của giảng viên chưa chạy, nên chưa khẳng định đã bắt mọi trap ẩn.

## 6. Tái lập, test và CI

Chạy từ src/:

```powershell
python -m pytest -q -m student -o addopts= -k lab9
python -m pytest -q
python -m lab9.evalset --check
python -m lab9.evalset --v2
python -m lab9.verify
python -m lab9.traps --pr reports/eval_v2_slice_regression.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml
python -m lab9.ci_check --pr reports/eval_pr.json --baseline reports/baseline_v1.json --spec config/metric_spec.yaml
```

Nếu thay eval set hoặc spec, tạo lại baseline và các eval report trước khi verify. Quy trình sinh baseline chi tiết trong HUONG_DAN_LAB9.md ở thư mục cha và README của starter.

Đã bổ sung test cho duplicate row, null score, grader failure trên report xanh, đổi slice, chọn seed, sửa aggregate, nới spec, miền hợp lệ pass-k và tính đồng nhất LF giữa Windows/Linux. Evalset writer dùng newline LF rõ ràng để SHA không đổi khi Git chuẩn hóa file trên Linux CI. Fix này không thay nội dung nghiệp vụ hoặc labels.

Kết quả cuối: **64 test Lab9 pass, 408 deselected**; bộ mặc định **160 pass, 312 deselected**. ci_check exit 0, replay swarm PR so baseline exit 0, traps tổng thể exit 0. Output gate xem pr_evidence.md/verification.json. Hosted GitHub Actions chưa được chạy vì chưa commit/push/mở PR. Workflow có sẵn được giữ để kiểm eval-gate và eval-gate-v2; harness_map.yaml đã có section eval, version 1.2. Không nhận local PASS là hosted CI xanh.

## 7. Trạng thái bàn giao

Đã hoàn thiện code local M1–M7, report, eval card và PRD v1.1. Chưa commit/push hoặc merge. Cần người nộp đọc lại tài liệu, ghi hash commit thực khi chốt, push starter/d09 lên fork cá nhân, mở PR vào main của chính fork và kiểm Actions xanh trước nộp. Các nội dung phê duyệt/waiver không được tự ký thay giảng viên.
