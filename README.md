# powerlab: istatistiksel güç hesabı motoru ve CLI (YZM301 Teardown Sprint)

**Aile:** F testi, tek yönlü ANOVA (üç tedavi kolu) · **Modlar:** a priori, post hoc
**Yapılan katmanlar:** ✅ CLI (temel) · ⬜ MCP sunucusu · ⬜ AI ajanı

> Bu çalışma eğitim amaçlıdır. Yazılım, G\*Power'ın bir kopyası değildir ve onun adıyla sunulmaz.
> Hesap motoru `gpower-clone` komut adıyla (ödev sözleşmesi gereği) çalışır.

## Durum (dürüst özet)

| Parça | Durum |
|---|---|
| Motor + CLI (ANOVA, a priori + post hoc) | yazıldı, 37 birim testi geçiyor |
| Kütüphane kâhini (statsmodels, 600 vektör) | üretildi; 428 uyuşmazlık tek bir hipoteze (H-07) bağlanıyor, 0 açıklanmamış |
| **G\*Power kâhini (`oracle/gpower_anova-oneway.csv`)** | **BOŞ: ≥30 vektör elle toplanacak** |
| **REA bulguları (`LEDGER.md` C bölümü)** | **BOŞ: [REA] satırı yok** |
| `SPEC.md` | taslak ([DOK] baz çizgisi); REA ile doğrulanacak |
| `HALLUCINATIONS.md` | 1 gerçek kayıt (H-A), 1 kayıt senin doldurman için açık |
| Çıktı alan adları | VARSAYIM (CONTRACT.md elimde yoktu) |

## Kurulum ve çalıştırma
```sh
pip install -e ".[test]"          # ya da kurulumsuz: ./bin/gpower-clone ...
gpower-clone --test anova-oneway --mode a-priori --f 0.25 --groups 3 --alpha 0.05 --power 0.95
# {"n_per_group":84,"n_total":252,"actual_power":0.9515,"critical":3.0321,"df1":2,"df2":249,"ncp":15.75}
gpower-clone --test anova-oneway --mode post-hoc --f 0.25 --groups 3 --alpha 0.05 --n-total 159
```
Hata: `{"error":"..."}` ve çıkış kodu 2 (girdi) ya da 3 (bilinmeyen aile).

## Testler
```sh
python -m unittest discover -s tests -p "test_*.py"     # birim, bölüm/sınır, sözleşme
python tests/differential.py library anova-oneway       # kütüphane kâhini
python tests/differential.py gpower  anova-oneway       # G*Power kâhini (CSV doldurulunca)
```

## Mimari (Sommerville: arayüz sözleşmesi, katmanlı mimari, bileşen yeniden kullanımı)
`engine.compute()` tek giriş noktasıdır; `families/anova_oneway.py` hesabı yapar; `robust.py`
dağılım çağrılarını NaN'a karşı korur; `cli.py` yalnızca argüman ayrıştırır. MCP ve REST,
`engine.compute`'u çağıran ince adaptörler olmalıdır (hesap mantığı kopyalanmaz).

## Sürüm / konfigürasyon yönetimi
- İncelenen yazılım: G\*Power **3.1.9.7 (Windows)**, yalnızca resmi sayfadan: psychologie.hhu.de
- `GPower.exe` SHA-256: `TODO: sha256sum GPower.exe çıktısını buraya yaz`
- `GPower.exe` repoya konmaz (`.gitignore`).
- Demo videosu (60 sn, CLI): `TODO`
- REA ve ajan kurulum kontrol çıktısı (ekran görüntüsü): `TODO`

## Süreç beyanı
İlk motor, REA incelemesinden önce, yalnızca kılavuz/teori bilgisiyle ve decompile çıktısı
görmeden yazıldı ([DOK] baz çizgisi). Bu iskeletin nasıl kullanıldığını (test düzeneği /
başlangıç kodu) burada belirt: `TODO`. İki oturum ayrımı için `prompts/` klasörüne bak.

## Yazarlara atıf
- Faul, F., Erdfelder, E., Lang, A.-G., & Buchner, A. (2007). G\*Power 3: A flexible statistical
  power analysis program for the social, behavioral, and biomedical sciences. *Behavior Research
  Methods, 39*, 175–191.
- Faul, F., Erdfelder, E., Buchner, A., & Lang, A.-G. (2009). Statistical power analyses using
  G\*Power 3.1: Tests for correlation and regression analyses. *Behavior Research Methods, 41*,
  1149–1160.

*(Künyeleri teslimden önce kendin doğrula.)*
