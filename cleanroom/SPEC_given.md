# SPEC.md (v1): F testi, tek yönlü sabit etkili ANOVA (omnibus), G*Power 3.1.9.7 davranışı

> Bu belge Oturum 2'nin (temiz oda yazımı) TEK girdisidir. Burada decompile kodu yoktur; yalnızca davranış,
> formüller ve kabul senaryoları vardır. Her senaryonun yanındaki `[Rn]` kodu `LEDGER.md` satırına bağlar.
> Etiketler: [REA] = binary'den (Ghidra, adres LEDGER'da), [DOK] = kılavuz, [AJAN] = çıkarım, [BİLİNMİYOR].

## 1. Kapsam
Test: "ANOVA: Fixed effects, omnibus, one-way" ([R17], [R29]). Analiz türleri:
- **a priori**: girdi f, alpha, power, k (grup sayısı) → çıktı toplam N ve türevleri.
- **post hoc**: girdi f, alpha, k, N (toplam) → çıktı power ve türevleri.

(G*Power'da sensitivity/criterion/compromise de vardır; bu ödevin kapsamı değildir.)

## 2. Formüller
Tüm sayılar IEEE çift duyarlıktır.

- df1 = k − 1; df2 = N − k [R26]. N a priori'nin arama aşamasında gerçek sayı olabilir.
- Merkezsel olmama: λ = f² · N [R25].
- Kritik F: **merkezsel** F dağılımının (λ = 0, df1, df2) (1 − alpha) kuantili [R19].
- Güç: 1 − P(F′ ≤ F_kritik), F′ ~ merkezsel olmayan F(df1, df2, λ) [R19]. λ < 1e-10 ise merkezsel F kullanılır, yani f = 0 iken güç = alpha [R14, R32].
- Merkezsel olmayan F CDF, λ/2 ortalamalı Poisson ağırlıklı eksik-beta toplamıyla hesaplanır (CDFLIB `cumfnc` benzeri) [R24, R32]. Durdurma eşikleri 1e-20 ve 1e-13 [R32]. Standart bir tam-doğru uygulama (örn. scipy `ncf`, dikkat: bazı sürümlerde `nct.cdf` NaN verebilir; yedek yol gerekir) kabul edilir, farklar N'yi değiştirmemelidir.

## 3. A priori N algoritması [R21, R27, R28, R34, R35]
1. Hedef güç P* = girilen power; alt sınır `lo = k + 1`.
2. Güç(N) fonksiyonu, N gerçek sayı kabul edilerek (df2 = N − k, λ = f²N) artan ve süreklidir. N\* = güç(N) = P* denkleminin kökü (N ≥ lo). Güç(lo) ≥ P* ise N\* := lo.
3. **N = ceil(N\* / k) · k** (k'nın katına yukarı yuvarlama).
4. Çıktı güçleri N için yeniden hesaplanır (actual power), kritik F, df1, df2, λ de bu N içindir.
5. Eşdeğer ifade: N, k'nın katı olan, **2k'dan küçük olmayan** ve güç(N) ≥ P* sağlayan **en küçük** sayıdır (kök bulucu duyarlığı sınırları dışında). En küçük olası N = 2k [R35] (grup başına en az 2).
6. N üst sınırı: bilinmiyor. Kök bulucu üst sınırı gerektiği kadar büyütür; G*Power'ın sonlu bir sınırı veya "hesaplanamadı" iletisi olabilir ([BİLİNMİYOR], GUI ile sınanacak).

## 4. Post hoc [R19, R22, R26]
- N, k'nın katı olmak ZORUNDA DEĞİL; güç doğrudan toplam N ile hesaplanır. (G*Power yalnızca bir uyarı verir: "total sample size is not a multiple of the number of groups; analysis based on the average group size.")
- n_per_group yalnızca N k'ya bölünüyorsa tamsayıdır; aksi halde N/k (ortalama grup büyüklüğü) anlamındadır.

## 5. Girdi doğrulaması (kapalı aralıklar) [R4–R8, R30, R36]
| Girdi | Geçerli aralık | Hata iletisi (G*Power) |
|---|---|---|
| k | tamsayı, k ≥ 2 | "There must be at least 2 groups." |
| f (a priori) | [1e-6, 50] | "... is outside the admissible range (1e-06, 50)" |
| f (post hoc) | [0, 50] | aynı |
| alpha | [1e-7, 0.9999999] | "Alpha is outside the admissible range (...)" |
| power | [1e-7, 0.9999999] | "Power is outside the admissible range (...)" |
| alpha ≤ power (a priori) | alpha ≤ power (eşitlik GEÇERLİ) | "Power must be greater than or equal to alpha." |
| N (post hoc) | tamsayı, k < N (kesin) | "Sample size must be greater than the number of groups (k)" |

CLI hata biçimi ödev sözleşmesindendir (tek satır JSON `{"error":...}`, sıfırdan farklı çıkış kodu); ileti metni sözleşmeye uyar, G*Power iletisini kelimesi kelimesine taşımak gerekmez.

## 6. Kabul senaryoları (Gherkin)

```gherkin
Özellik: Tek yönlü ANOVA güç analizi

  Senaryo: A priori toplam N, k'nın katıdır [R27, R35]
    Diyelim ki f=0.25, alpha=0.05, power=0.80, k=3
    Eğer a priori hesaplanırsa
    O zaman n_total, 3'e tam bölünür
    Ve actual_power ≥ 0.80
    Ve n_total − 3 için (k'nın bir önceki katı) güç 0.80'in altındadır

  Senaryo: Kılavuz örneği [DOK, L15]
    Diyelim ki f=0.25, alpha=0.05, power=0.95, k=10
    O zaman n_total = 390, actual_power ≈ 0.952363, critical ≈ 1.904538, df1=9, df2=380, ncp=24.375

  Senaryo: En küçük N 2k'dır [R35]
    Diyelim ki f=50, alpha=0.05, power=0.80, k=4
    O zaman n_total = 8

  Senaryo: Post hoc güç k'nın katı olmayan N ile hesaplanır [R22]
    Diyelim ki f=0.25, alpha=0.05, k=3, n_total=100
    O zaman hata yoktur ve güç, df1=2, df2=97, ncp=6.25 ile hesaplanır

  Senaryo: f=0 iken post hoc güç alpha'ya eşittir [R14, R32]
    Diyelim ki f=0, alpha=0.05, k=3, n_total=30
    O zaman actual_power = 0.05

  Senaryo: power = alpha geçerlidir [R6]
    Diyelim ki f=0.25, alpha=0.05, power=0.05, k=3
    O zaman hata yoktur ve n_total = 6 (en küçük N)

  Senaryo: Geçersiz girdiler [R4, R5, R6, R30]
    k=1 → hata
    post hoc, k=3, n_total=3 → hata
    a priori, power=0.04, alpha=0.05 → hata
    f=0 (a priori) → hata; f=51 → hata
    alpha=0 veya alpha=1 → hata
```

## 7. Bilinmeyenler (diferansiyel/GUI testi gerekir)
1. Çıktıların ekranda/yuvarlanmış gösterim basamakları (güç, kritik F, ncp). CLI sözleşmesi 4 basamak varsayar [AJAN].
2. N üst sınırı ve "hesaplanamadı" davranışı (çok küçük f).
3. Kök işlevinin tam tanımı (`FUN_00496830`) güç(N) − P* olduğu varsayımıdır [AJAN]; sonuç eşdeğerliği GUI vektörleriyle (özellikle N\* tam bir katın hemen yanındayken) doğrulanmalı.
4. k için üst sınır (G*Power GUI'si bir üst sınır koyuyor olabilir).
5. n_per_group alanının N k'ya bölünmediğinde çıktıda nasıl gösterileceği (CLI sözleşmesi).
