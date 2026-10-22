# AGENT_COST.md: ajan maliyet ve süreç günlüğü

> Şu an doldurulabilen kısım yalnızca yazılım iskeleti oturumudur. REA/Ghidra oturumlarını ve
> token/maliyet sayılarını kendi kullanım panelinden doldur. **Sayıları tahmin etme, ölç.**

| Oturum | Ajan / model | Görev | Yaklaşık token | Yaklaşık maliyet | İterasyon |
|---|---|---|---|---|---|
| 0: iskelet | Claude Sonnet 5.5 (claude.ai) | CLI + motor + test iskeleti ([DOK] baz çizgisi, REA'dan önce) | *ölç* | *ölç* | 3 (aşağıya bak) |
| 1: inceleme | *(Claude Code / Codex / ...)* | REA + Ghidra, SPEC.md + LEDGER.md | | | |
| 2: yazım | *(yeni oturum)* | yalnızca SPEC.md ile yeniden yazım | | | |

## Oturum 0 iterasyonları (gerçekte olanlar)
1. t2-indep referansıyla motor + CLI: sözleşme örneğini birebir verdi.
2. Kütüphane kâhininde bulunan NaN hatası düzeltildi (bkz. HALLUCINATIONS.md H-A).
3. Kod aile yapısına bölündü ve ANOVA ailesine geçirildi. Yuvarlama hipotezi (H-07) iki modlu ve
   her iki mod bağımsız aramayla doğrulanmış olarak yazıldı.

4. Bonus katmanlar: ortak araç kaydı (`tools.py`), MCP sunucusu, ajan döngüsü ve 10 soruluk set eklendi.
   `mcp` paketinin 2.x sürümünde `FastMCP` adı `MCPServer` olarak değişmişti; ilk içe aktarma hata verdi,
   yeni API okunup adaptör ona göre yazıldı (bir iterasyon). Gerçek model çağrısı YAPILMADI, bu yüzden bu
   katman için ölçülmüş token/maliyet değeri yok.

## Neyi farklı yapardım
- Sınır vektörleri (özellikle `actual_power ≈ power` olanlar) G*Power'dan ilk gün toplanmalı;
  yuvarlama hipotezlerini tek vektörle ayırmak N'yi tahmin etmeye çalışmaktan çok daha ucuz.
- Her dağılım çağrısını ikinci bir bağımsız yolla çapraz kontrol etmek baştan yapılmalıydı.

## Süreç beyanı (temiz oda)
Bu depodaki ilk motor, REA incelemesinden önce yalnızca kılavuz/teori bilgisiyle yazıldı; hiçbir
decompile çıktısı görülmedi. Hocanın iki-oturum kuralına göre Oturum 2'nin nihai `src/` kodu
yalnızca nihai SPEC.md'den üretilmelidir. Bu iskeleti nasıl kullandığını (test düzeneği olarak mı,
başlangıç kodu olarak mı) README'de açıkça yaz.
