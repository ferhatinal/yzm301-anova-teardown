# powerlab: istatistiksel güç hesabı motoru ve CLI (YZM301 Teardown Sprint)

**Aile:** F testi, tek yönlü ANOVA (üç tedavi kolu) · **Modlar:** a priori, post hoc
**Yapılan katmanlar:** ✅ CLI (temel) · 🟨 MCP sunucusu (kod ve testler hazır) · 🟨 AI ajanı (kod ve set hazır, canlı ölçüm yok)

> ⚠️ Ödevin kapısı: gizli vektörlerde N tam eşleşmesi ≥ %90. **G\*Power ile eşleşme henüz ölçülmedi**, bu yüzden MCP ve ajan katmanlarının puanı bu kapı doğrulanana kadar belirsizdir.

> **Kalan işler (senin bilgisayarında yapılacaklar) için: [`YAPILACAKLAR.md`](YAPILACAKLAR.md).**

> Bu çalışma eğitim amaçlıdır. Yazılım, G\*Power'ın bir kopyası değildir ve onun adıyla sunulmaz.
> Hesap motoru `gpower-clone` komut adıyla (ödev sözleşmesi gereği) çalışır.

## Durum (dürüst özet)

| Parça | Durum |
|---|---|
| Motor + CLI (ANOVA, a priori + post hoc) | yazıldı |
| MCP sunucusu (`powerlab.mcp_server`, 2 araç) | yazıldı; CLI = MCP eşitliği 14 girdide test edildi |
| Ajan (`powerlab.agent`) + 10 soruluk Türkçe set (`eval/`) | yazıldı; döngü sahte istemciyle test edildi, **gerçek model ölçülmedi** |
| Testler | 64 birim/entegrasyon testi geçiyor (Python 3.13, mcp 2.3.0, anthropic 1.17.0) |
| Kütüphane kâhini (statsmodels, 600 vektör) | üretildi; 428 uyuşmazlık tek bir hipoteze (H-07) bağlanıyor, 0 açıklanmamış |
| Kılavuz kâhini (`oracle/manual_anova-oneway.csv`, [DOK]) | 2 basılı örnek; motor 6 basamağa uyuyor ve k-katı yuvarlama (H-07) kanıtlandı: k=10 için 386 değil 390 |
| **G\*Power kâhini (`oracle/gpower_anova-oneway.csv`)** | **BOŞ: ≥30 vektör elle toplanacak** (`tools/add_oracle_row.py` yardımcı) |
| **REA bulguları (`LEDGER.md` C bölümü)** | **BOŞ: [REA] satırı yok** |
| **MCP vs GUI token ölçümü** | **BOŞ**: protokol `eval/README.md`'de |
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

## MCP sunucusu
```sh
pip install -e ".[mcp]"
python -m powerlab.mcp_server           # stdio
```
Claude Desktop (`claude_desktop_config.json`):
```json
{ "mcpServers": { "powerlab": {
    "command": "python3", "args": ["-m", "powerlab.mcp_server"],
    "env": { "PYTHONPATH": "/MUTLAK/YOL/teardown/src" } } } }
```
Araç şeması (kaynak: `src/powerlab/tools.py`; çıktı = CLI ile aynı JSON, hata: `{"error": "..."}`):

| Araç | Girdi | Çıktı |
|---|---|---|
| `anova_oneway_a_priori` | `f` (sayı >0), `alpha` (0-1), `power` (0-1), `groups` (tam sayı ≥2) | `n_per_group, n_total, actual_power, critical, df1, df2, ncp` |
| `anova_oneway_post_hoc` | `f`, `alpha`, `groups`, `n_total` (tam sayı) | aynı alanlar |

MCP katmanında hesap yoktur: iki araç da `tools.call` → `engine.compute` yolunu çağırır;
`tests/test_mcp.py` bunu hem eşitlik testiyle hem de adaptör kaynağında sayısal kod aranmadığını
kontrol ederek sınar.

## AI ajanı
`python -m powerlab.agent "Üç kolu f=0,25, α=0,05, %80 güçle karşılaştıracağız; kaç hasta gerekir?"`
Ajan sayı üretmez; araç çağırır, desteklenmeyen/belirsiz sorularda araştırmacıya sorar. 10 soruluk
değerlendirme, kayıtlar ve token ölçüm protokolü: `eval/README.md`. **Yalnızca kurgusal senaryolar** gönderin.

## Testler
```sh
python -m unittest discover -s tests -p "test_*.py"     # birim, bölüm/sınır, sözleşme, MCP, ajan (64 test)
python tests/differential.py library anova-oneway       # kütüphane kâhini
python tests/differential.py gpower  anova-oneway       # G*Power kâhini (CSV doldurulunca)
python tools/add_oracle_row.py --help                    # G*Power sonucunu CSV'ye güvenle ekle
sh tools/demo.sh                                         # 60 sn'lik demo videosu için komut dizisi
```

## Mimari (Sommerville: arayüz sözleşmesi, katmanlı mimari, bileşen yeniden kullanımı)
`engine.compute()` tek giriş noktasıdır; `families/anova_oneway.py` hesabı yapar; `robust.py`
dağılım çağrılarını NaN'a karşı korur; `cli.py` yalnızca argüman ayrıştırır. MCP ve REST,
`engine.compute`'u çağıran ince adaptörlerdir (`tools.py` ortak araç kaydı; hesap mantığı kopyalanmaz).

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
