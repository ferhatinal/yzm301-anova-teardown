# LEDGER.md: kanıt defteri

Etiketler: **[DOK]** kılavuzda/makalede yazıyor · **[REA]** binary'den kanıtlandı (adres veya dize
referansı zorunlu) · **[AJAN]** ajanın çıkarımı, kanıtı yok. Puan yalnızca [REA] satırlarına verilir.

> **Dürüst durum:** Şu an yalnızca **artefakt düzeyinde** [REA] satırları var (hash, PE biçimi, kaynak ağacı). **Algoritma
> hakkında [REA] kanıtı yok**: Ghidra bu makinede yapılandırılmadığı için hesap motoru henüz incelenemedi. Aşağıdaki satırlar [DOK] ve [AJAN]'dır. [REA] satırlarını yalnızca gerçek
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

## C) [REA] satırları (şimdilik yalnızca artefakt düzeyi; algoritma satırlarını Ghidra'lı Oturum 1 doldurur)

| # | İddia | Etiket | REA kanıtı (fonksiyon adresi / dize ref.) | Güven | Bilinmeyen |
|---|---|---|---|---|---|
| R1 | `GPowerNT.exe`: PE biçimi, x86, SHA-256 `c63e6a133eb6372932f810c08cc33dc35a06d1ddb658f897bd6c34a754efc812` | [REA] (artefakt düzeyi) | `open_binary` (REA 6.5.0), C:\Users\ferha\Desktop\GPowerWin_3.1.9.7\GPower_3.1.9.7_143\GPowerNT.exe | Yüksek | Algoritma hakkında bilgi vermez; Ghidra yok |
| R2 | Kaynak ağacı (toplam 144 kaynak, tarama tamam, makine 0x14C = x86): 89 RT_DIALOG, 18 RT_ICON, 10 RT_STRING, 6 RT_MENU, 2 RT_BITMAP, 2 RT_GROUP_ICON, 1 RT_ACCELERATOR, 1 RT_VERSION, 1 RT_MANIFEST ve iki özel tip (240: 13, 241: 1) | [REA] (artefakt düzeyi) | `inspect_pe_resources`, kanıt kimliği `ev_8f2d8e77b0d0b8fff53b231e9586860677e8f1a0686462bf618de876b4e3b0d8` (authority: shipped-artifact, confidence: observed) | Yüksek | Yük içerikleri opak; sürüm dizeleri çözülmedi |
| R3 | Arayüz yerel Win32 iletişim kutusu kaynaklarıyla kurulmuş (Delphi/.NET değil, büyük olasılıkla C++/MFC tarzı); Ghidra x86 PE'yi destekler | [AJAN] | R2'den çıkarım (`IDR_ICON3` adlandırması MFC/Visual C++ geleneğidir) | Orta | Derleyici/çerçeve doğrulanmadı; Ghidra ile teyit |
| R4 | Grup sayısı doğrulaması: k > 1 ise geçerli, değilse "There must be at least 2 groups." Çağıranlar: 004ba6b0, 004c0300, 004bb540, 004bed00, 004b95e0 | [REA] | `FUN_00487cb0`; Ghidra 12.1.4 headless (`tools/ghidra/DumpAnova.java`); REA'nın Ghidra sağlayıcısı bu kurulumda yapılandırılamadı | Yüksek | Hangi çağıran tek yönlü ANOVA? |
| R5 | N ile k ilişkisi: geçerli ⇔ k < N (**kesin eşitsizlik**), mesaj "Sample size must be greater than the number of groups (k)". Yani N ≥ k+1 yeterli; grup başına ≥2 koşulu bu doğrulayıcıda YOK. Çağıranlar: 004c0300, 004bed00, 004c63c0, 004b9f00 | [REA] | `FUN_00488800` (arg sırası mesajdan çıkarıldı); Ghidra 12.1.4 headless (`tools/ghidra/DumpAnova.java`); REA'nın Ghidra sağlayıcısı bu kurulumda yapılandırılamadı | Orta-yüksek | a priori aramanın başlangıç N'si ayrı bir yerde olabilir (H-03 sınanmalı) |
| R6 | Güç ≥ alpha doğrulaması: geçerli ⇔ alpha ≤ power (**eşitlik geçerli**), mesaj "Power must be greater than or equal to alpha." Çağıranlar: 004a1b6e, 004ad740, 004ee1f0, 004c0300, 004a6940, 004f1890, 004e8160, 004bed00 | [REA] | `FUN_004880e0`; Ghidra 12.1.4 headless (`tools/ghidra/DumpAnova.java`); REA'nın Ghidra sağlayıcısı bu kurulumda yapılandırılamadı | Orta (arg sırası mesajdan çıkarıldı) | power = alpha vektörü GUI'de denenmeli (H-05 ile çelişir) |
| R7 | A priori'de etki büyüklüğü ≈ 0 reddi: |a − b| ≤ `DAT_005c4970` ise "In a priori calculations the effect size must not be zero." Tek çağıran 004aa0b0 | [REA] | `FUN_00487d20`; Ghidra 12.1.4 headless (`tools/ghidra/DumpAnova.java`); REA'nın Ghidra sağlayıcısı bu kurulumda yapılandırılamadı | Orta | Eşik değeri (`DAT_005c4970`) henüz okunmadı |
| R8 | Genel en küçük örneklem doğrulaması: geçerli ⇔ min ≤ N, mesaj "Sample size must be greater than or equal to min" | [REA] | `FUN_00488700`, 19 çağıran; Ghidra 12.1.4 headless (`tools/ghidra/DumpAnova.java`); REA'nın Ghidra sağlayıcısı bu kurulumda yapılandırılamadı | Yüksek | ANOVA için min kaç? |
| R9 | F dağılımı sarmalayıcıları: Cdf `FUN_00459e70` ortak rutini `FUN_0044e7a0`'ı which=1, Quantile `FUN_0045ac00` which=2 (q = 1−p) ile çağırır; durum kodları: <0 "input parameter out of range", 1 "below lower search bound", 2 "above upper search bound", 3 "p + q != 1.0", diğer "unknown error". Quantile sonucu ölçek alanına (`puVar1[3]`) bölünür | [REA] | `FUN_00459e70`, `FUN_0045ac00`, `FUN_0044e7a0`; Ghidra 12.1.4 headless (`tools/ghidra/DumpAnova.java`); REA'nın Ghidra sağlayıcısı bu kurulumda yapılandırılamadı | Yüksek (yapı), Düşük (hangi kütüphane) | `FUN_0044e7a0` içeriği okunmadı; CDFLIB `cdff` benzeri görünüyor = [AJAN] |
| R10 | Merkezsel olmayan F parametre adları: indeks 0 "noncentrality lambda", 1 "numerator df", 2 "denominator df" | [REA] | `FUN_0047d2a0`; Ghidra 12.1.4 headless (`tools/ghidra/DumpAnova.java`); REA'nın Ghidra sağlayıcısı bu kurulumda yapılandırılamadı | Yüksek | λ'nın f²·N olduğunu KANITLAMAZ; hesap rutini bulunmadı |
| R11 | Merkezsel olmayan χ² parametre adları: "noncentrality lambda", "df" | [REA] | `FUN_0043ef80`; Ghidra 12.1.4 headless (`tools/ghidra/DumpAnova.java`); REA'nın Ghidra sağlayıcısı bu kurulumda yapılandırılamadı | Yüksek | — |
| R12 | `FUN_00522300` ve `FUN_0050e460` arayüz işleyicileri: "Number of groups" ve "Total sample size" alanlarını okur, uyuşmazlıkta `AfxMessageBox` (0x23) sorar; hesap yok | [REA] | `FUN_00522300`, `FUN_0050e460`; Ghidra 12.1.4 headless (`tools/ghidra/DumpAnova.java`); REA'nın Ghidra sağlayıcısı bu kurulumda yapılandırılamadı | Yüksek | Hesap fonksiyonu bunlar değil: 004c0300 / 004bed00 incelenecek |
| R13+ | *(sonraki turlar: 004c0300, 004bed00, 0044e7a0 ...)* | | | | |

Bulunması gereken ilk üç şey: (1) N arama döngüsünün başlangıcı, artışı ve çıkış koşulu,
(2) N'nin k katına yuvarlanıp yuvarlanmadığı, (3) geçersiz girdi doğrulama dalları ve hata dizeleri.
