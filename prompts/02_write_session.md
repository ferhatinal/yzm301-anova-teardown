# Oturum 2: YAZIM (temiz oda). Yalnızca SPEC.md ile başlar.

> Yeni bir oturum aç. Bu oturum Ghidra/REA çıktısını, LEDGER.md'yi veya decompile edilmiş
> hiçbir şeyi GÖRMEZ. Yalnızca SPEC.md ve CLI sözleşmesi verilir. Gerçek prompt'u aynen kaydet.

## Görev
Ekteki SPEC.md'deki davranışı gerçekleyen bir güç hesabı motoru ve CLI yaz (dil: Python).
Aile: F testi, tek yönlü ANOVA; modlar a-priori ve post-hoc.

## Mimari (Sommerville: arayüz sözleşmesi, katmanlı mimari)
- Tek motor: `src/powerlab/engine.py` + aile modülü. Hesap mantığı YALNIZCA burada.
- CLI, ileride MCP ve REST: yalnızca `engine.compute` çağıran ince adaptörler.
- Dağılım fonksiyonları için scipy serbest; NaN/sonsuz değerlere karşı korumalı ol.

## CLI sözleşmesi
- Başarı: tek satır JSON, çıkış kodu 0. Hata: `{"error":"<açıklama>"}` ve sıfırdan farklı kod.
- Örnek: `gpower-clone --test anova-oneway --mode a-priori --f 0.25 --groups 3 --alpha 0.05 --power 0.95`
- Alan adları CONTRACT.md'deki gibi olmalı (bu satırı gerçek alan adlarıyla güncelle).

## Test (önce davranış, sonra kod)
1. SPEC.md'deki her senaryo için bir test yaz; önce başarısız olduğunu gör.
2. Bölüm ve sınır değer testleri: f çok küçük/çok büyük, power≈alpha, groups=2, geçersiz girdiler.
3. Beklenen değerleri kendin üretme: oracle/*.csv (G*Power vektörleri) kâhindir.
4. `python tests/differential.py gpower anova-oneway` çıktısındaki her uyuşmazlığı açıkla veya düzelt.

## Yasak
- Decompile çıktısı/kodu yok. G*Power adı ve görünümü yok. Kâhin değerleri uydurma.
