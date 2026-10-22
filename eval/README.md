# eval/: ajan değerlendirmesi (bonus katman, +10)

Ödev: 10 soruluk set (her soru için beklenen test ailesi, parametreler, N), doğru seçim oranı,
araç çağrı kayıtları, MCP ile GUI arasında ölçülmüş token karşılaştırması.

## Durum (dürüst özet)

| Parça | Durum |
|---|---|
| 10 soruluk Türkçe set (`questions.jsonl`) | hazır: 5 desteklenen, 4 desteklenmeyen, 1 belirsiz; her birinde bir tuzak |
| Ajan döngüsü ve değerlendirici | yazıldı, sahte istemciyle 14 testle sınandı |
| **Gerçek model ile doğru seçim oranı** | **ÖLÇÜLMEDİ** (canlı çalıştırma için API anahtarı gerekir) |
| **Beklenen N / güç değerleri** | **BOŞ**: G\*Power ekranından doldurulacak (uydurma yok) |
| **MCP vs GUI token karşılaştırması** | **ÖLÇÜLMEDİ**: GUI tarafı senin makinende ölçülecek |

## Setin yapısı
`questions.jsonl` satırı: `id, question, expected_tool, expected_params, expected_n_total, expected_power, trap`.
- `expected_tool = null`: desteklenmeyen (t testi, eşleştirilmiş, oranlar) ya da belirsiz soru. Doğru davranış: **hiç araç çağırma**, araştırmacıya söyle/sor.
- `expected_n_total` (a priori) ve `expected_power` (post hoc): G\*Power'dan okunana kadar `null`; `null` iken ilgili metrik "ölçülmedi" sayılır, sıfır sayılmaz.

## Çalıştırma
```sh
export ANTHROPIC_API_KEY=...            # YALNIZCA kurgusal senaryolar; gerçek hasta verisi asla
python eval/run_eval.py --live          # logs/agent_calls.jsonl ve eval/results.json üretir
python eval/run_eval.py --replay logs/agent_calls.jsonl   # mevcut log'u yeniden puanla
```
Model: `POWERLAB_MODEL` ortam değişkeni (varsayılan `claude-haiku-5-5`). Birkaç modeli kıyaslamak için
her model için ayrı bir `--log` yolu kullan.

## Kalibrasyon ve dil karşılaştırması (isteğe bağlı, ödev metni)
Güven puanı veren bir Sistem 1 modeli kullanırsan: "%90 güven" dediği seçimlerin gerçekte yüzde kaçı
doğru, ve aynı soruları İngilizce çeviriyle ölç. Bu repoda henüz yapılmadı.

## MCP ve GUI token karşılaştırması: ölçüm protokolü (SENİN YAPACAĞIN)
Aynı 10 soru iki yoldan çözülür; üçü de ölçülüp aşağıya yazılır. **Tahmin yazma, ölç.**

1. **MCP yolu:** `eval/results.json` içindeki `toplam_girdi_token`, `toplam_cikti_token`, `toplam_sure_sn`.
2. **GUI yolu:** ekran görüntüsü alabilen bir ajanla (ör. Claude'un bilgisayar kullanımı) G\*Power'ı
   açıp aynı soruları çözdür; kullanım panelinden her sorunun token ve süresini kaydet.
3. **Doğruluk:** her iki yolun cevabını G\*Power vektörüyle karşılaştır.

| Yol | Toplam token (girdi+çıktı) | Toplam süre | Doğru sayısı / 10 | Not |
|---|---|---|---|---|
| MCP | *ölç* | *ölç* | *ölç* | |
| GUI (ekran görüntüsü) | *ölç* | *ölç* | *ölç* | |

Ders notlarında "bir ekran görüntüsü yaklaşık bin token" gibi kaba bir sayı geçiyor; o sayıyı rapora
kendi ölçümün yerine koyma.
