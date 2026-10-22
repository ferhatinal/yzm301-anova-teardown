# LEDGER.md: kanıt defteri

Etiketler: **[DOK]** kılavuzda/makalede yazıyor · **[REA]** binary'den kanıtlandı (adres veya dize
referansı zorunlu) · **[AJAN]** ajanın çıkarımı, kanıtı yok. Puan yalnızca [REA] satırlarına verilir.

> **Dürüst durum:** Bu defterde şu an **hiç [REA] satırı yok.** REA/Ghidra oturumu henüz
> yapılmadı. Aşağıdaki satırlar [DOK] ve [AJAN]'dır. [REA] satırlarını yalnızca gerçek
> bir inceleme oturumunun bulgularıyla sen dolduracaksın; uydurma kanıt eklenmez.

## A) [DOK] satırları (kaynak sayfa numarasını kendin ekle)

| # | İddia | Etiket | Kaynak | Güven | Bilinmeyen |
|---|---|---|---|---|---|
| L1 | df1 = k − 1, df2 = N − k | [DOK] | G*Power kılavuzu / Faul vd. (2007): *sayfayı doğrula* | Yüksek | Binary'de de böyle mi? (REA) |
| L2 | ncp (λ) = f² · N | [DOK] | Faul vd. (2007); Cohen (1988): *sayfayı doğrula* | Yüksek | REA ile doğrula |
| L3 | critical F = F⁻¹(1−α; df1, df2) | [DOK] | standart istatistik | Yüksek | Kuantil rutini hangisi? |
| L4 | güç = P(F′(df1, df2, λ) > critical) | [DOK] | standart istatistik | Yüksek | Hesap yolu/sayısal yöntem? |
| L13 | CLI tek satır JSON, hata = {"error"} + sıfırdan farklı kod | [DOK] | ödev metni, "CLI sözleşmesi" | Yüksek | ANOVA alan adları (CONTRACT.md) |
| L15 | k=10, f=0.25, α=0.05, güç=0.95 → N=390 (39/grup), güç 0.952363, λ=24.375, F\*=1.904538, df=9/380 | [DOK] | G\*Power 3.1 kılavuzu (Haziran 2023), Bölüm 10, Örnek 10.3 (s. 25; sayfa/bölüm numarası alıntı aracından alındı, *PDF'ten teyit et*). Motor 6 basamağa birebir üretir: `tests/test_anova.py::ManualExample` | Yüksek | Ekran görüntüsü yok; GUI'de tekrar edilmeli |
| L16 | "non-integer sample sizes are always rounded up by G\*Power" | [DOK] | G\*Power 3.1 kılavuzu, Bölüm 1.2.3 (s. 4; *teyit et*) | Yüksek | Toplam N'nin k'nın katına yuvarlanıp yuvarlanmadığını TEK BAŞINA söylemez |
| L17 | df1 = k−1, df2 = N−k, λ = f²·N (Uygulama notları) | [DOK] | G\*Power 3.1 kılavuzu, Bölüm 10.5 (s. 25; *teyit et*) | Yüksek | L1/L2'yi kılavuzla doğrular |

## B) [AJAN] satırları (HİPOTEZ: diferansiyel testle sınanacak)

| # | İddia | Etiket | Kanıt | Güven | Nasıl sınanır |
|---|---|---|---|---|---|
| L5 | a priori N = koşulu sağlayan ilk N (>= güç) | [AJAN] | yok | Orta | oracle: sınırda vektörler (actual_power ≈ power) |
| L6 / H-07 | N grup sayısının katına yukarı yuvarlanır | [AJAN] (kısmen [DOK] destekli) | binary kanıtı yok. [DOK] L15: k=10 için birer-artış 386 verirdi, kılavuz 390 veriyor; k-katı kuralı 390'ı birebir üretir | Orta-yüksek (tek k için) | **k=3'te hâlâ ayırt edilmeli: f=.25, α=.05, power=.80 → 158 mi 159 mu?** |
| L7 / H-03 | grup başına en az 2 gözlem | [AJAN] | yok | Düşük | f büyük, k=3 vektörleri |
| L8 / H-04 | f ≤ 0, sonlu değil → hata | [AJAN] | yok | Orta | geçersiz girdi vektörleri |
| L9 / H-05 | power ≤ alpha → hata | [AJAN] | yok | Düşük | power=alpha, power<alpha |
| L10 / H-08 | groups ≥ 2, tam sayı | [AJAN] | yok | Orta | groups=1, groups=0 |
| L11 / H-06 | N için üst sınır var | [AJAN] | yok | Düşük | çok küçük f |
| L12 | çıktı 4 basamağa yuvarlanır | [AJAN] | yok | Düşük | ekranda gösterilen basamak sayısına göre güncelle |

## C) [REA] satırları (BOŞ: Oturum 1 doldurur)

| # | İddia | Etiket | REA kanıtı (fonksiyon adresi / dize ref.) | Güven | Bilinmeyen |
|---|---|---|---|---|---|
| R1 | | [REA] | | | |
| R2 | | [REA] | | | |
| … | | | | | |

Bulunması gereken ilk üç şey: (1) N arama döngüsünün başlangıcı, artışı ve çıkış koşulu,
(2) N'nin k katına yuvarlanıp yuvarlanmadığı, (3) geçersiz girdi doğrulama dalları ve hata dizeleri.
