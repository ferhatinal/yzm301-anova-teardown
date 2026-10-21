# Oturum 1: İNCELEME (REA + Ghidra). Çıktı yalnızca SPEC.md ve LEDGER.md.

> Bu dosya Oturum 1'e yapıştırılacak ilk prompt'tur. Gerçek oturumda kullandığın
> hâli neyse onu bu dosyaya olduğu gibi kaydet (ödev: "ilk prompt'u repoya koyun").

## Bağlam
Eğitim ödevi (YZM301). Hedef YALNIZCA resmi sayfadan indirilmiş G*Power 3.1.9.7 (Windows).
Aile: **F testi, tek yönlü sabit etkili ANOVA (omnibus)**; modlar: a priori (N hesapla) ve
post hoc (gücü hesapla). Dosya SHA-256'sını kaydet. Başka hiçbir yazılımı inceleme.

## Kısıtlar
- Decompile edilmiş kodu veya sözde kodu çıktıya YAPIŞTIRMA. Yalnızca davranış, fonksiyon
  adresi / dize referansı ve en fazla birkaç satırlık kısa alıntı.
- Her iddianın yanına etiket koy: `[DOK]` kılavuz/makale, `[REA]` binary'den kanıtlandı
  (adres veya dize referansı ZORUNLU), `[AJAN]` kendi çıkarımın (kanıt yok).
- Kanıtı gösteremiyorsan etiket `[AJAN]` olur. Emin değilsen "bilinmiyor" yaz; tahmin uydurma.
- Hesap yapma. Sayı üretme. Sayıları G*Power ekranından ayrıca toplayacağım.

## Kontrol
"REA araçları ve Ghidra sağlayıcısı bu oturumda kullanılabilir mi? Kaç araç aktif?" sorusunu
yanıtla ve çıktıyı bu klasöre kaydet (README ekran görüntüsü için).

## Bulman gerekenler (kılavuzda OLMAYAN davranışlar)
1. a priori toplam N tam olarak nasıl bulunuyor? Arama hangi N'den başlıyor, kaçar artıyor,
   hangi koşulda duruyor (>=, >)? Toplam N grup sayısının katına mı yuvarlanıyor?
2. df1 = k-1, df2 = N-k mi? Merkezsel olmayanlık parametresi f²·N mi? Kanıtla.
3. Kritik F ve güç hangi dağılım rutiniyle hesaplanıyor (ters CDF, merkezsel olmayan F CDF)?
   Sayısal yöntem veya yineleme sınırı var mı?
4. Geçersiz girdilerde ne oluyor: f<=0, alpha<=0 veya >=1, power<=alpha, power>=1, groups<2,
   groups'un üst sınırı, N çok büyük (üst sınır). Hata iletileri dizeleri neler?
5. Gösterilen basamak sayısı (güç, kritik F, ncp) ve yuvarlama kuralı.
6. Varsayılanlar ve izin verilen aralıklar (alpha, power, f için alt/üst sınır).

## Çıktı biçimi
- `SPEC.md`: kabul kriterleri Gherkin (Given/When/Then); her senaryo bir LEDGER satırına bağlı.
- `LEDGER.md`: tablo | iddia | etiket | kanıt (adres/dize) | güven | bilinmeyen |
- Sonda "bilinmeyenler" listesi ve diferansiyel testle sınanması gerekenler.
