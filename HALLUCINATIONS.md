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

## H-B  (YAŞANDI) Ajan kaynak sayılarını ve kanıt satırlarını doğrulamadan yazdı

- **Ajanın yanlışı:** LEDGER R2'de PE kaynak sayıları RT_STRING ve RT_MENU için yer değiştirmiş yazıldı; ayrıca bazı
  R satırları (R7, R14, R26, R30, R32) sabit değerlerini, ilgili `doubles.txt` okunmadan "değer" olarak taşıdı.
  Daha önce de dokümana belleğe dayalı "159/252/280" sayıları girmişti.
- **Nasıl fark edildi:** kaynak ağacı yapısından yeniden sayım (10 RT_STRING, 6 RT_MENU, 89 RT_DIALOG, toplam 144);
  bellek sayıları kılavuzdaki Örnek 10.3 ile karşılaştırılınca kanıtsız olduğu için silindi.
- **Hangi kontrol yakaladı:** yeniden sayım ve "yalnızca [REA] etiketli kanıt" kuralı; sabitler `doubles.txt` ile eşlendi.
- **Düzeltme:** R2 sayıları düzeltildi, bellek kaynaklı sayılar kaldırıldı.
- **Ek kayıt:** REA Ghidra sağlayıcısı sorununu önce kullanıcı hatası sandım (yanlış `scriptPath` tanısı da); ortam
  değişkeni, yeniden başlatma ve config sonrası da aynı hata sürünce sağlayıcı sorunu olarak kabul edildi.

## H-C (ajan varsayımı, binary ile çelişiyor: ek doğrulama bekliyor)
- **İddia (benim, [AJAN], kanıtsız):** grup başına en az 2 gözlem (`MIN_PER_GROUP=2`, H-03) ve `power = alpha` hata (H-05).
- **Binary (R5, R6):** doğrulayıcılar yalnızca k < N ve alpha ≤ power istiyor; grup başına 2 koşulu ve power=alpha reddi bulunmadı.
- **Durum:** kodu henüz değiştirmedim; GUI vektörleriyle (post hoc k=3, N=4; power=alpha) sınanacak, sonra motor düzeltilecek.

## H-C notu (güncelleme)
R27 (yuvarlama `ceil(N/k)·k`) H-07'yi destekliyor. `MIN_PER_GROUP=2` ise a priori'de alt sınır (R28: k + sabit) bir katına yuvarlandığında KENDİLİĞİNDEN ortaya çıkabilir; sabit değeri okunana kadar hüküm verilmiyor. Post hoc'ta ise yalnızca N > k aranıyor (R5).
