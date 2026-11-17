# Trace case — C-002@11: ticket ghi đè dữ kiện DB

## Tái lập

Chạy trong src/:

```powershell
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11
python -m pytest -q -m student -o addopts= tests/test_lab9_m123_regression.py -k first_wrong_step
python -m lab9.m123_evidence
```

| Trường | Nội dung |
|---|---|
| Trial | seeded_regression C-002@11; run ID `R-seeded_regression-C-002-s11` |
| Triệu chứng | status resolved thay vì denied; proposal 20.000 thay vì 0; ledger 20.000/1 refund thay vì 0/0. Reply nhất quán với khoản ghi sai, nên kiểm reply đơn lẻ không phát hiện được lỗi nghiệp vụ. |
| Bước sai đầu tiên | **Event 3**, kind `model_override`, payload `delay_days=5`. |
| Vì sao là bước đầu tiên | Event 1 handoff giống fixed; event 2 investigator trả order delay_days=2, cũng giống fixed. Test so sánh prefix event trước override giữa hai trace. |
| Failure mode | FM-03 ticket_trust. |
| Đối chứng | `R-fixed-C-002-s11`: không có override; event 3 quote amount_vnd=0; status denied, ledger 0, TrialPass=True. |
| Regression test | `test_lab9_first_wrong_step_ticket_override` kiểm prefix đúng, override 5 thay DB 2, bản lỗi bị TrialPass từ chối và fixed được chấp nhận. |
| Chưa chắc chắn | Trace chứng minh sai dữ kiện và kết quả trên MockLLM, không chứng minh suy nghĩ nội tại của LLM thật hoặc kết quả ngoài public claims. |

## Diễn tiến quan sát được

| Event | seeded_regression | fixed |
|---|---|---|
| 1 | handoff | handoff |
| 2 | investigator: DB delay=2 | investigator: DB delay=2 |
| 3 | model_override: delay=5 | quote: amount=0 |
| 4 | quote: amount=20.000 | reply từ chối |
| 5 | refund_history: 0 | — |
| 6 | reply hoàn tiền | — |

Evidence JSON chỉ xuất dữ kiện chọn lọc, không chép nguyên debug row có secret. Kết quả tiền được lấy từ snapshot ledger, không lấy câu chữ khách hàng làm nhãn.
