# oracle/: kâhin vektörleri

| Dosya | İçerik | Durum |
|---|---|---|
| `gpower_anova-oneway.csv` | G*Power 3.1.9.7 arayüzünden ELLE toplanan vektörler (asıl kâhin) | **BOŞ: sen dolduracaksın** (en az 30, her biri ekran görüntüsüyle) |
| `library_anova-oneway.csv` | `statsmodels.FTestAnovaPower` ile üretilen 600 vektör (yardımcı kâhin) | üretildi |
| `gpower_t2-indep.csv`, `library_t2-indep.csv` | referans aile (ödev sözleşmesi örneği) | teslimden önce silinebilir |

Kâhin dosyasına ben veya başka bir ajan değer UYDURAMAZ: bu sütunlar G*Power ekranından okunur.

## Toplama protokolü (G*Power, Windows)
1. Test family: **F tests**; Statistical test: **ANOVA: Fixed effects, omnibus, one-way**.
2. Type of power analysis: **A priori** (N hesapla) ve **Post hoc** (güç hesapla).
3. Her vektör için girdileri yaz, **Calculate**'e bas, çıktı kutusunu ekran görüntüsüne al
   (`oracle/screens/NNN.png`), CSV'ye satır ekle.
4. Sütunlar: `test,mode,f,alpha,power,groups,n_total,n_per_group,df1,df2,actual_power,critical,ncp,source,note,screenshot,expect_error`
   - `test` = `anova-oneway`; `mode` = `a-priori` | `post-hoc`
   - a-priori satırında girdi: f, alpha, power, groups; çıktı: n_total, df1, df2, actual_power, critical, ncp
   - post-hoc satırında girdi: f, alpha, groups, n_total; çıktı: power(actual_power), critical, ncp, df1, df2
   - `source` = `gpower-3.1.9.7-gui`
   - Hata veren girdi için `expect_error` = `1` yaz, G*Power mesajını `note`a koy.
5. **İlk iş (en bilgilendirici tek vektör):** f=0.25, α=0.05, power=0.80, groups=3 gir.
   Sonuç 158 mi 159 mu? Bu, N'nin grup sayısının katına yuvarlandığı hipotezini (H-07) hemen ayırır.

## Vektör planı (bölüm ve sınır değer testi)
- Cohen eşikleri: f = 0.10 / 0.25 / 0.40; groups = 2, 3, 4, 5
- Güç: 0.80, 0.90, 0.95, 0.99; alpha: 0.01, 0.05, 0.10
- Sınır: f çok küçük (0.01-0.05), çok büyük (2-5); power ≈ alpha, power < alpha; power = 0.99+
- Geçersiz: f=0, f<0, alpha=0, alpha=1, groups=1, groups=0, N çok küçük (post hoc)
