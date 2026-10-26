# Oturum 2: temiz oda yazımı (kanıt)

- Girdi: yalnızca `SPEC_given.md` (= SPEC.md v1, commit 5bc329b) ve `TASK.md`. Ajan LEDGER'ı, decompile çıktısını ve mevcut motoru görmedi (ayrı alt ajan, boş dizin; dizin dışına çıkmama talimatı verildi, teknik olarak zorlanmadı: [AJAN] düzeyinde güvence).
- Çıktı: `anova_clean.py`, `test_anova_clean.py` (13 test geçti, unittest).
- Diferansiyel: `scratch` karşılaştırması, 1080 a priori vektörü (9 f x 4 alpha x 5 power x 6 k), ana motorla **0 uyuşmazlık** (n_total). Post hoc güç iki motorda 4 basamağa kadar aynı.
- Uyarı: iki motor da aynı SPEC formülünden türedi, bu yüzden bu karşılaştırma G*Power doğrulaması DEĞİLDİR. Gerçek kâhin: oracle/gpower_anova-oneway.csv (GUI vektörleri, henüz boş).
- Ajanın SPEC'te bulduğu belirsizlikler: çıktı yuvarlama, N üst sınırı, kök bulucu vs en küçük-katı tanımı, tamsayı değerli float girdi, k üst sınırı.
