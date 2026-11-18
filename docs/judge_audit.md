# Judge audit — Nguyễn Bá Thành

## Tái lập và nguồn

Chạy từ src/:

```powershell
python -m lab9.judge --csv data/eval/judge_tone_public.csv --audit 5
python -m lab9.judge --csv data/eval/judge_helpful_public.csv --audit 5
python -m lab9.m123_evidence
```

Số dưới đây lấy từ `reports/m123_evidence.json`, mục calibration. Judge replay không gọi API. FAIL là positive. Các nhận định audit dưới đây được Codex hỗ trợ phân tích từ reply và note trong CSV, không phải một vòng gán nhãn người độc lập mới.

| Tiêu chí | n | TP / FP / FN / TN | κ | Precision | Recall | Floors | Quyết định |
|---|---:|---|---:|---:|---:|---|---|
| tone_ok | 100 | 24 / 4 / 6 / 66 | 0,757 | 0,857 | 0,800 | PASS | Dùng cho tone trong phạm vi replay đã hiệu chuẩn |
| helpful | 100 | 9 / 0 / 21 / 70 | 0,375 | 1,000 | 0,300 | FAIL | Không dùng làm gate |

Floors: κ≥0,6; Precision≥0,8; Recall≥0,7. Tone observed failure rate=0,28, Rogan–Gladen=0,30; helpful observed=0,09, corrected=0,30. Hiệu chỉnh tỉ lệ không làm helpful đủ chuẩn và không sửa được verdict của từng case.

## Audit 10 bất đồng

Các trích đoạn chỉ để nhận diện, kết luận đọc cùng note/context CSV.

| Case | Judge / Human | Phân tích và bên hợp lý theo rubric dữ liệu | Hành động sửa rubric |
|---|---|---|---|
| H-008 | PASS / FAIL | “anh check giúp em”, “nha” quá suồng sã theo chuẩn CS trong note; nhãn Human phù hợp chuẩn đó. | Nêu rõ mức trang trọng, không đồng nhất thân thiện với lịch sự. |
| H-017 | PASS / FAIL | Gọi khách “bạn”, kết thúc “nha”; note nói khách lớn tuổi. Human phù hợp khi context này được cung cấp. Chỉ reply riêng lẻ chưa đủ suy tuổi khách. | Cung cấp context xưng hô cho judge; tránh suy đoán tuổi từ câu trả lời. |
| H-029 | PASS / FAIL | “không cần nhắn thêm” mang tính ngăn cản/ra lệnh; “Dạ” không khắc phục phần còn lại. Human phù hợp. | Đánh giá cả câu, thêm ví dụ polite opening nhưng nội dung áp đặt. |
| H-042 | FAIL / PASS | Câu ngắn, có tiền và thời gian, không có dấu hiệu bất lịch sự. Human phù hợp; thiếu lời xin lỗi không tự động fail tone. | Không bắt buộc xin lỗi trong mọi phản hồi. |
| H-051 | FAIL / PASS | Note cho phép dùng từ “refund”; từ tiếng Anh tự nó không chứng minh thiếu lịch sự. Human phù hợp theo glossary này. | Cung cấp danh sách thuật ngữ chấp nhận. |
| HL-015 | PASS / FAIL | Reply 55.000, note ledger 40.000; Human đúng về factual helpfulness dù lời văn lịch sự. | Tách money correctness sang code đối chiếu ledger. |
| HL-016 | PASS / FAIL | Reply 55.000, ledger 35.000; nhiều lời xin lỗi không bù được sai tiền. Human phù hợp. | Không dùng độ dài/đồng cảm làm proxy cho đúng tác vụ. |
| HL-020 | PASS / FAIL | Reply 90.000, ledger 120.000; Human phù hợp. | Bắt buộc grounding vào snapshot thực. |
| HL-028 | PASS / FAIL | Reply 50.000, ledger 35.000; lặp xin lỗi che sai tiền. Human phù hợp. | Chấm các tiêu chí riêng, factual error là lỗi độc lập. |
| HL-035 | PASS / FAIL | Reply 50.000, ledger 35.000; Human phù hợp theo note. | Không để tone tốt nâng helpful khi tiền sai. |

## Kết luận và giới hạn

Helpful precision=1 không có nghĩa đáng tin: judge bỏ sót 21/30 lỗi (recall=0,3), kappa cũng dưới sàn. Không đưa judge này làm gate. Tiền và approval luôn do code chấm; metric reply_amount_matches_ledger xử lý trực tiếp sai tiền ở FM-08.

Tone đạt cả ba floors trên CSV nhưng vẫn có 10 bất đồng. Chỉ có replay công khai, không có nhãn held-out hay dữ liệu người dùng thật; chưa đủ chứng minh chất lượng judge trong production. Note của CSV là nguồn context có thể ảnh hưởng audit; cần một vòng review người mới trước khi áp dụng thực tế. Kappa không xác định hoặc rates không đủ thông tin không được coi là PASS.
