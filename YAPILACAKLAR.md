# YAPILACAKLAR: kalan işler (yalnızca senin bilgisayarında yapılabilenler)

Kod, testler, belge şablonları, MCP, ajan ve kılavuz kâhini hazır (`README.md` durum tablosu).
Aşağıdakiler G\*Power'ın kendisine veya senin hesaplarına bağlı olduğu için uzaktan yapılamadı.
Sırayla yaparsan toplam ~1,5–2 saat. En çok puan getiren: **2 ve 3**.

## 1. Ghidra kurulumu (REA incelemesinin ön şartı) ~15 dk
REA'nın durum raporu: *"Ghidra: not_configured, Set GHIDRA_INSTALL_DIR to an extracted Ghidra 12.1.x release directory"*;
IDA yok, Hopper Windows'ta desteklenmiyor. Yani Ghidra olmadan G\*Power'ın yerel ikilisi incelenemez.
1. JDK 21 kur (ör. Eclipse Temurin 21), `java -version` ile doğrula.
2. Ghidra 12.1.x'i ghidra-sre.org'dan indir, `C:\tools\ghidra_12.1` gibi bir klasöre aç.
3. Ortam değişkeni (PowerShell): `[Environment]::SetEnvironmentVariable("GHIDRA_INSTALL_DIR","C:\tools\ghidra_12.1","User")`
4. Claude Desktop'u tamamen kapat ve yeniden aç (REA sunucusu yeniden başlar).
5. Doğrula: ajana "REA araçları ve Ghidra sağlayıcısı bu oturumda kullanılabilir mi? Kaç araç aktif?" de, cevabın
   ekran görüntüsünü README'ye koy.

## 2. G\*Power 3.1.9.7 ve kâhin vektörleri ~45 dk (puanın %90 kapısı bunlara bağlı)
1. YALNIZCA resmi sayfadan indir (psychologie.hhu.de, G\*Power sayfası). `GPower.exe` repoya konmaz.
2. Hash: `Get-FileHash .\GPower.exe -Algorithm SHA256` → çıktıyı `README.md`'deki `TODO`'ya yaz.
3. **İlk vektör:** F tests → ANOVA: Fixed effects, omnibus, one-way → A priori; f=0.25, α=0.05, güç=0.80, 3 grup.
   Toplam N **158 mi 159 mu?** (kılavuz Örnek 10.3 zaten k-katı kuralını destekliyor; bu k=3'ü kesinleştirir.)
4. `oracle/README.md`'deki vektör planına göre **en az 30** vektör topla (Cohen eşikleri, güç 0.80–0.99,
   alpha 0.01/0.05/0.10, k=2–5, sınır değerler, geçersiz girdiler). Her biri için ekran görüntüsünü
   `oracle/screens/001.png, 002.png...` olarak kaydet ve ekle:
   `python tools/add_oracle_row.py a-priori --f 0.25 --alpha 0.05 --power 0.80 --groups 3 --n-total <..> --df1 <..> --df2 <..> --actual-power <..> --critical <..> --ncp <..> --screenshot oracle/screens/001.png`
   (betik satırı hemen motorla karşılaştırır ve uyuşmazlığı gösterir)
5. `python tests/differential.py gpower anova-oneway` çıktısını bana yapıştır, uyuşmazlıkları birlikte açıklarız.
   158 çıkarsa: `src/powerlab/families/anova_oneway.py` içinde `ROUND_TO_MULTIPLE_OF_GROUPS = False` yap ve
   `HALLUCINATIONS.md`'ye H-B olarak yaz.

## 3. REA incelemesi (Oturum 1) ve temiz oda yazımı (Oturum 2) ~30–60 dk
1. Ghidra hazır olunca **yeni bir sohbet** aç, `prompts/01_inspect_session.md` içeriğini yapıştır ve
   `GPower.exe`'nin tam yolunu ver. (Ya da bana yolu yaz; incelemeyi ayrı bir oturumda yürütürüm.)
2. Çıkan bulguları `LEDGER.md` C bölümüne ([REA], adres/dize referansıyla) ve `SPEC.md`'ye işle.
   Ajanın kanıtsız söylediği bir şeyi `HALLUCINATIONS.md`'ye yaz (ödev: en az 2 kayıt; H-A hazır).
3. **Ayrı** bir oturumda yalnızca `SPEC.md` ile `prompts/02_write_session.md`'yi çalıştır. Bu iskeletin
   nasıl kullanıldığını `README.md` süreç beyanına yaz. Decompile çıktısı repoya konmaz.

## 4. Ölçümler ve teslim ~30 dk
- `AGENT_COST.md`: kullanım panelinden gerçek token/maliyet.
- Ajan değerlendirmesi: `ANTHROPIC_API_KEY` ayarla, `python eval/run_eval.py --live`
  (yalnızca kurgusal senaryolar). GUI tarafı için `eval/README.md`'deki protokol.
- 60 sn demo: `sh tools/demo.sh` (Windows'ta Git Bash veya WSL) ekran kaydı; linki `README.md`'ye yaz.
- Künyeleri (Faul vd. 2007, 2009) ve kılavuz sayfa numaralarını (`LEDGER.md` L15–L17) PDF'ten teyit et.
- GitHub: boş depo aç, `git remote add origin <url>`, `git push -u origin main`, linki ödev formuna gönder.

## Dürüst not
Bu iskelet REA incelemesinden ÖNCE, yalnızca kılavuz/teoriyle yazıldı. Hocanın temiz oda kuralı için
nihai `src/` kodunun yalnızca nihai `SPEC.md`'den üretildiğini göstermen gerekiyor. İskeleti test düzeneği ve
referans olarak kullanıp, kodu Oturum 2'de yeniden ürettirmek en güvenli yoldur.
