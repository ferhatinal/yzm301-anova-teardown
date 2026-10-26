# Görev (temiz oda, Oturum 2)
Yalnızca bu dizindeki SPEC.md'ye dayan. Bu dizinin DIŞINDAKİ hiçbir dosyayı okuma (LEDGER, decompile, mevcut motor, repo).
Python + scipy/numpy serbest. Şunu yaz: `anova_clean.py`
  - `a_priori(f, alpha, power, groups) -> dict` anahtarlar: n_total, actual_power, critical, df1, df2, ncp
  - `post_hoc(f, alpha, groups, n_total) -> dict` aynı anahtarlar
  - Geçersiz girdide `ValueError` (SPEC Bölüm 5 aralıkları).
  - scipy NaN verirse yedek yol (SPEC Bölüm 2 notu).
Ayrıca `test_anova_clean.py`: SPEC'teki her Gherkin senaryosu için bir test + sınır değerleri. Beklenen sayıları SPEC'te yazanlardan başkasını uydurma.
Testleri `python -I -m pytest` veya unittest ile çalıştır; sonunda ne yaptığını ve SPEC'te belirsiz/çelişkili bulduğun yerleri raporla.
