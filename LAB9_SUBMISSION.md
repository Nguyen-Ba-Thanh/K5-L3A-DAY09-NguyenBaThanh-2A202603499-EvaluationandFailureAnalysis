# Lab9 — Bài cá nhân của Nguyễn Bá Thành

- MSSV: 2A202603499; lớp L3A.
- Email theo TEAM.md: 26ai.thanhnb3@vinuni.edu.vn.
- Fork làm bài: https://github.com/Nguyen-Ba-Thanh/K5-L3A-DAY08-NguyenBaThanh-FromWorkflowsToAgents
- Nhánh bài làm: `starter/d09`; PR đích: `main` trong chính fork cá nhân này.
- Code agent Lab8 được kế thừa nguyên trạng. Bài Lab9 gồm code đánh giá, dữ liệu, cấu hình, tài liệu và workflow bổ sung trong repo này.

README/CHECKPOINTS/RUBRIC/SUBMISSION ở gốc vẫn là tài liệu Lab8 kế thừa theo hướng dẫn overlay. Checklist Lab9 được đối chiếu từ starter bên cạnh; trang này là mục lục bàn giao Lab9 để tránh nhầm bài cần nộp.

## 1. Trạng thái

- [x] M1 taxonomy, 14 item v1 có FM, labels riêng, trace case kèm regression test.
- [x] M2 confusion/P/R/kappa/Rogan–Gladen, judge calibration và 10 case audit.
- [x] M3 hai grader yêu cầu, metric FM-08 blocking và proposal correctness bổ sung.
- [x] M4 paired bootstrap, baseline v1, fixed pass và seeded_regression bị chặn.
- [x] M5 eval set v2 gồm 28 item, FM mapping, slices blocking.
- [x] M6 pass@k/pass^k, kiểm input, A/A và pass_hat_5 blocking.
- [x] M7 integrity, ratchet, 3/3 mutants bị chặn, 0 false alarms, 4 trap công khai +3 trap bổ sung bị chặn.
- [x] Eval card, PRD v1.1, section eval trong harness_map version 1.2.
- [x] Public test Lab9: 64 passed; bộ mặc định: 160 passed trong lần kiểm cuối.
- [x] Local submission audit: 33/33 checks pass, LOCAL READY.
- [ ] Tác giả đọc lại thông tin cá nhân và các nhận định audit có AI hỗ trợ.
- [ ] Commit cuối, push, mở PR và ghi hash commit thật.
- [ ] GitHub Actions hosted eval-gate và eval-gate-v2 xanh.
- [ ] Dán output bằng chứng vào PR và nộp link qua kênh lớp yêu cầu.

Không nhận kết quả public/local là điểm hidden hoặc xác nhận CI hosted. Bonus port Inspect AI/DeepEval là tùy chọn, không được triển khai; không thiếu phần bắt buộc M1–M7 vì không có bonus.

## 2. Những file chính được nộp qua Git

| Phần | Đường dẫn |
|---|---|
| Code M1–M7 | `src/lab9/`, trọng tâm stats.py, graders.py, evalset.py, gate.py |
| Test bổ sung | `src/tests/test_lab9_m123_regression.py`, `test_lab9_gate_integrity.py` |
| Spec và mapping | `src/config/metric_spec.yaml`, `metric_spec_v2.yaml`, `fm_map.yaml` |
| Eval sets | `src/data/eval/eval_set_v1.jsonl`, `labels_v1.json`, `eval_set_v2.jsonl`, `labels_v2.json` |
| Dữ liệu starter | `src/data/eval/adversarial_v2.json`, hai judge CSV |
| Tài liệu bắt buộc | `docs/failure_taxonomy.md`, `trace_case.md`, `judge_audit.md`, `eval_card.md`, `PRD_v1.1.md` |
| Baseline/eval Core | `src/reports/baseline_v1.json`, `eval_fixed.json`, `eval_seeded_regression.json` |
| Baseline v2 | `src/reports/baseline_v2.json` |
| Bằng chứng bổ sung | `src/reports/verification.json`, `eval_v2_*.json`, `aa_alternate.json`, `m123_evidence.json`, `submission_audit.json`, `traps/` |
| Harness và dependencies | `src/harness_map.yaml`, `harness_map.eval.yaml`, `requirements-lab9.txt` |
| CI | `.github/workflows/eval-gate.yml` |

Không nộp venv, traces, SQLite hoặc secret. Các báo cáo Lab8 kế thừa không thay thế báo cáo Lab9; TEAM.md và báo cáo cá nhân Lab8 không phải mẫu bắt buộc mới của Lab9. Không cần sửa tên repo DAY08 hoặc tạo repo Lab9 khác theo checklist hiện có.

## 3. Tài liệu nên đọc

- [Báo cáo M1–M3](docs/m123_report.md).
- [Báo cáo và giải thích M4–M7](docs/m47_report.md).
- [Eval card và kết quả tổng hợp](docs/eval_card.md).
- [Bằng chứng để dán vào PR](docs/pr_evidence.md).
- [PRD v1.1](docs/PRD_v1.1.md).

## 4. Kiểm tra nhanh trước commit

Chạy trong src/ với venv:

```powershell
python -m lab9.submission_check
```

Lệnh chỉ audit file/report có sẵn và tạo submission_audit.json, không chạy lại toàn bộ evaluation. Nếu thay code/spec/eval set, chạy test/eval tương ứng và `python -m lab9.verify` để sinh bằng chứng mới trước audit; không chỉnh report JSON bằng tay.

Nếu cần test lại:

```powershell
python -m pytest -q -m student -o addopts= -k lab9
python -m pytest -q
```

## 5. Commit, push và tạo PR

Chạy từ repo hoặc src/:

```powershell
git branch --show-current
git status
git add -- :/src :/docs :/.github/workflows/eval-gate.yml :/LAB9_SUBMISSION.md :/.github/PULL_REQUEST_TEMPLATE.md
git diff --cached --stat
git diff --cached --check
git diff --cached -- src/lab8
git commit -m "Complete Lab9 evaluation, regression gates and submission reports"
git rev-parse HEAD
git push -u origin starter/d09
```

Nhánh cần là starter/d09; diff src/lab8 phải trống. Kiểm staged files trước khi commit. Lệnh add trên gom cả overlay đã stage trước và các bản hoàn thiện mới; .gitignore giữ runtime artifacts ngoài Git.

Mở PR trên GitHub với **base repository và head repository đều là fork Nguyen-Ba-Thanh**, base main, compare starter/d09. Nếu GitHub mặc định trỏ về upstream thì đổi lại. Không push thẳng main cho bài này vì workflow yêu cầu PR hoặc workflow_dispatch.

Mô tả PR dùng nội dung [docs/pr_evidence.md](docs/pr_evidence.md), kèm hash từ git rev-parse HEAD. Template PR đã được chuẩn bị trong .github/PULL_REQUEST_TEMPLATE.md; nếu template chưa hiện khi tạo PR đầu tiên thì copy nội dung thủ công. Kiểm Actions, xử lý lỗi nếu có, rồi giữ PR/link để nộp. Chưa tự merge trước khi kiểm xong yêu cầu lớp.

## 6. Bạn cần tự điền/xác nhận gì?

Không còn bảng số liệu hoặc phần code bắt buộc để tự điền. Các việc cần chính bạn thực hiện/xác nhận là:

1. Đọc và xác nhận họ tên/MSSV/email đúng, hiểu các kết luận audit và ghi nhận dùng AI. Không nhận mình đã làm human annotation độc lập nếu chỉ dùng replay/AI.
2. Sau commit, đưa hash thật vào mô tả PR hoặc liên kết commit. Không đoán hash trước khi commit.
3. Mở PR, xác nhận đúng fork, lấy URL PR và kiểm hai job hosted xanh.
4. Nộp URL PR/repo qua LMS/kênh được giảng viên chỉ định. Starter yêu cầu PR và commit trước 23:59 cùng ngày lab; thông báo riêng của lớp có thể bổ sung cách nộp.

Không tự điền PASS cho hidden grading, không ký thay giảng viên/Product và không bịa URL/CI status. Key anchor và bộ chấm hidden do giảng viên quản lý, không phải phần tác giả phải tự tạo.
