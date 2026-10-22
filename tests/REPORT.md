# tests/REPORT.md: diferansiyel test ve uyum raporu

Üretim: `python tests/differential.py library anova-oneway` ve `... gpower anova-oneway`.

## 1) G*Power katmanı (asıl kâhin)
`oracle/gpower_anova-oneway.csv` **boş**. Uyum oranı **ölçülmedi**. Ödevin kapısı (gizli vektörlerde
N tam eşleşmesi ≥ %90) bu katman dolana kadar değerlendirilemez.

## 1b) Kılavuz katmanı ([DOK] kâhin: G\*Power 3.1 kılavuzundaki basılı örnek çıktılar)
`oracle/manual_anova-oneway.csv`; `python tests/differential.py manual anova-oneway`: **2/2 uyum**.

| Örnek | Girdi | Kılavuz | Motor |
|---|---|---|---|
| 10.3 a priori | k=10, f=.25, α=.05, güç=.95 | N=390, güç 0.952363, λ=24.375, F\*=1.904538, df 9/380 | **birebir** (6 basamak) |
| 10.3 compromise, post hoc yönünde | k=10, f=.25, α=.159194, N=200 | güç 0.840806, F\*=1.476210 | 0.840805 / 1.476211 (α 6 basamağa yuvarlı olduğu için ±1e-6) |

**H-07 için ayırt edici kanıt:** aynı girdide birer-artış arama **386** verir, kılavuz **390** der; k-katı kuralı 390'ı verir.
Bu yüzden varsayılan `ROUND_TO_MULTIPLE_OF_GROUPS = True` kalır. Sınır: bu yalnızca k=10 içindir ve kılavuz
değerleridir, GUI ekran görüntüsü ya da [REA] kanıtı değildir. Kılavuzdaki 6 basamak, motor çıktısının 4 basamaklı
sözleşme biçiminden daha sıkı karşılaştırılır (birim testte).

## 2) Kütüphane katmanı (yardımcı kâhin, statsmodels.FTestAnovaPower, 600 vektör)

| Motor ayarı | Tam uyum (n_total) | Açıklama |
|---|---|---|
| `ROUND_TO_MULTIPLE_OF_GROUPS = False` (N birer artar) | **600 / 600** | motor, kütüphanenin tavan değeriyle aynı |
| `ROUND_TO_MULTIPLE_OF_GROUPS = True`  (varsayılan, H-07) | 172 / 600 (%28.7) | 428 uyuşmazlığın **tamamı** "k'nın katına yukarı yuvarlama" kuralıyla açıklanıyor; açıklanmamış: 0 |

Her iki mod da bağımsız kaba kuvvet aramasıyla doğrulandı (`test_h07_both_modes_correct_against_independent_search`):
birer-artış modu = hedefi sağlayan ilk N; k-katı modu = o N'yi içeren en küçük k katı.

**Bulgu:** Kütüphane N'yi kesirli verir. G*Power'ın N'yi nasıl tamsayıya çevirdiği (birer artış mı, grup
sayısının katı mı) puanın %90 kapısını doğrudan belirler: yanlış seçilen mod N eşleşmesini ~%29'a
düşürür. Bu yüzden `oracle/README.md`'deki ilk vektör (f=.25, α=.05, güç=.80, k=3 → 158 mi 159 mu?)
ilk iş olmalıdır. Doğru modu seçmek tek sabiti değiştirmek demektir.

## 3) Referans aile (t2-indep)
945 vektör; 863 tam uyum; 82 uyuşmazlık H-01 (n2'nin yukarı yuvarlanması) ile açıklanıyor; açıklanmamış: 0.
Bu katman bir hatayı yakaladı: `scipy.stats.nct.cdf` NaN (bkz. HALLUCINATIONS.md H-A).

## 4) Sınırlar
Bu rapor G*Power ile eşleşmeyi KANITLAMAZ. Yalnızca motorun kütüphane teorisiyle tutarlı olduğunu ve
hipotezlerin açıkça ayrıldığını gösterir. Testler hataların varlığını gösterebilir, yokluğunu değil.
