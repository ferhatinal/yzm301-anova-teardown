# HALLUCINATIONS.md: ajanın yanlış çıkardığı şeyler

Ödev: en az 2 kayıt; her biri için *ne yanlıştı, nasıl fark edildi, hangi test yakaladı*.
Bu dosyaya yalnızca gerçekten yaşananlar yazılır.

## H-A  (YAŞANDI) Kütüphane fonksiyonuna sessiz güven: `scipy.stats.nct.cdf` NaN verebilir

- **Ajanın yanlışı:** Motor ilk yazıldığında `scipy.stats.nct.cdf(-kritik, df, ncp)`'nin her girdide
  sonlu bir değer döndüreceği varsayıldı. Gerçekte bazı (df, ncp, x<0) kombinasyonlarında (örnek:
  df=254, ncp=6.4, x=−2.595) NaN döndürüyor. NaN karşılaştırmada sessizce `False` olduğundan
  N araması "hedefe ulaşılmadı" sanıp büyümeye devam etti ve yanlış, çok büyük bir N döndü
  (t testi referansında: d=0.8, α=0.01, güç=0.99, oran=1 için **358** döndü; doğrusu **77**).
  Hata mesajı yoktu; çıktı makul görünüyordu.
- **Nasıl fark edildi:** İkinci kâhin katmanındaki (statsmodels, 945 vektör) diferansiyel test
  tek bir uyuşmazlık gösterdi (kâhin 77, motor 358). Elle bakılınca güç fonksiyonunun n=128, 130,
  160, 256 için NaN döndürdüğü görüldü.
- **Hangi test yakaladı:** `tests/differential.py library` (uyuşmazlık), düzeltmeden sonra
  kalıcı regresyon: `tests/test_t2_reference.py::test_nan_regression_df254` ve
  `tests/test_anova.py::test_power_finite_over_grid_and_two_independent_paths_agree`.
- **Düzeltme:** `src/powerlab/robust.py`: CDF için geri-dönüş zinciri (`nctdtr` → `nct.cdf` →
  sayısal integral / Poisson karışımı), hiçbiri sonlu değilse `InputError`. Sessiz yanlış sonuç yok.
- **Ders:** "Tip güvenliği doğruluk değildir." NaN, sessiz hata kaynağıdır. Bağımsız ikinci bir
  kâhin olmasaydı bu hata G*Power vektörü toplanana kadar fark edilmeyebilirdi.

## H-B  (SENİN DOLDURMAN GEREKİYOR) REA oturumunda ajanın yanlış çıkardığı ikinci şey

*Boş. Oturum 1'de ajanın kanıtsız veya yanlış bir iddiası olursa (örn. "döngü >= ile duruyor"
deyip kod izi gösterememesi, ya da N yuvarlamasını yanlış yorumlaması) buraya şu başlıklarla yaz:
ajanın iddiası · nasıl fark ettin · hangi test/vektör yakaladı · düzeltme.*

*Aday: H-07 (N, k katına yuvarlanıyor mu?). G\*Power ekranından f=.25, α=.05, güç=.80, k=3 için
158 çıkarsa bu motorun varsayımı yanlış demektir; `ROUND_TO_MULTIPLE_OF_GROUPS=False` yap ve
kaydı buraya yaz. 159 çıkarsa hipotez doğrulanmış olur ve burada kayıt gerekmez.*
