# SPEC.md: F testi, tek yönlü ANOVA (güç analizi)

> **DURUM: TASLAK (v0, [DOK] baz çizgisi).** Bu belge REA oturumundan ÖNCE, yalnızca kılavuz/teori
> bilgisiyle yazıldı. "HIPOTEZ" etiketli senaryolar kanıtlanmış davranış DEĞİLDİR. Oturum 1 (REA)
> bunları `[REA]` kanıtıyla doğrular, düzeltir veya siler; ardından Oturum 2 yalnızca nihai
> SPEC.md ile başlar. Her senaryonun bağlı olduğu satır LEDGER.md'dedir.

Terimler: `f` Cohen etki büyüklüğü, `k` grup sayısı (`groups`), `N` toplam örneklem.

## Özellik 1: Güç hesabı (post hoc)  [DOK]

```gherkin
Senaryo: df ve merkezsel olmama parametresi            # LEDGER L1, L2
  Diyelim ki f=0.25, alpha=0.05, groups=3, n_total=159
  Eğer post-hoc modu çalıştırılırsa
  O zaman df1=2 ve df2=156
  Ve ncp = f² × n_total = 9.9375

Senaryo: kritik F                                       # LEDGER L3
  Diyelim ki f=0.25, alpha=0.05, groups=3, n_total=159
  Eğer post-hoc modu çalıştırılırsa
  O zaman critical, F dağılımının (df1, df2) için (1 - alpha) kuantilidir (≈ 3.054)

Senaryo: güç, merkezsel olmayan F kuyruk olasılığıdır   # LEDGER L4
  Diyelim ki f=0.25, alpha=0.05, groups=3, n_total=159
  O zaman actual_power = P(F'(df1, df2, ncp) > critical) (≈ 0.8049)
```

## Özellik 2: Örneklem büyüklüğü (a priori)

```gherkin
Senaryo: hedef gücü sağlayan en küçük N                 # LEDGER L5  [HIPOTEZ H-02]
  Diyelim ki f=0.25, alpha=0.05, power=0.80, groups=3
  Eğer a-priori modu çalıştırılırsa
  O zaman actual_power >= 0.80 olan en küçük n_total döner

Senaryo: N grup sayısının katıdır                       # LEDGER L6  [HIPOTEZ H-07]
  Diyelim ki groups=3
  O zaman n_total, 3'ün katıdır ve n_per_group = n_total / 3
  # Ders kitaplarında anılan 159 ve 252, birer-artış aramasının bulduğu 158 ve 251'den 1 büyüktür;
  # bu H-07'yi destekleyen DOLAYLI bir işarettir, kanıt DEĞİL. G*Power ekranından doğrulanacak.

Senaryo: alt sınır                                      # LEDGER L7  [HIPOTEZ H-03]
  Diyelim ki f çok büyük (ör. 5)
  O zaman n_per_group en az 2'dir
```

## Özellik 3: Girdi doğrulama  [HIPOTEZ H-04/05/06/08, hepsi REA/kâhin bekliyor]

```gherkin
Senaryo Taslağı: geçersiz girdi                         # LEDGER L8-L12
  Örnekler:
    | f   | alpha | power | groups | beklenen                       |
    | 0   | 0.05  | 0.9   | 3      | hata                           |
    | -1  | 0.05  | 0.9   | 3      | hata                           |
    | 0.25| 0     | 0.9   | 3      | hata                           |
    | 0.25| 1     | 0.9   | 3      | hata                           |
    | 0.25| 0.05  | 0.05  | 3      | hata (HIPOTEZ: power <= alpha) |
    | 0.25| 0.05  | 1     | 3      | hata                           |
    | 0.25| 0.05  | 0.9   | 1      | hata (HIPOTEZ: groups >= 2)    |
  O zaman çıktı {"error": "..."} ve çıkış kodu sıfırdan farklıdır
```

## Özellik 4: Arayüz sözleşmesi

```gherkin
Senaryo: tek satır JSON                                 # LEDGER L13  [DOK: ödev metni]
  Eğer komut başarılı olursa
  O zaman stdout tek satırlık JSON'dur ve çıkış kodu 0'dır
  Ve alan adları CONTRACT.md'ye uyar (şimdilik VARSAYIM: n_per_group, n_total, actual_power,
     critical, df1, df2, ncp)

Senaryo: motor tektir                                   # LEDGER L14  [DOK: Sommerville, katmanlı mimari]
  O zaman CLI (ve varsa MCP/REST) hesap yapmaz; yalnızca engine.compute çağırır
```

## Çözülmesi gereken bilinmeyenler (Oturum 1 hedefi)
H-01 (yalnızca t2 referansı), H-02 durma koşulu, H-03 alt sınırlar, H-05 power<=alpha, H-06 üst sınır,
H-07 N'nin k katına yuvarlanması, H-08 groups alt/üst sınırı, çıktı basamak sayıları.
