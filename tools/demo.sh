#!/usr/bin/env sh
# 60 saniyelik CLI demosu için sıralı komutlar. Ekran kaydı sırasında çalıştır: sh tools/demo.sh
# Her komut önce ekrana yazılır, sonra çalışır; araya kısa bekleme konur.
set -u
cd "$(dirname "$0")/.."
run() { printf '\n$ %s\n' "$*"; sleep 1; "$@"; sleep 2; }

echo "== powerlab: tek yönlü ANOVA güç hesabı (eğitim amaçlı, G*Power kopyası değildir) =="
run ./bin/gpower-clone --test anova-oneway --mode a-priori --f 0.25 --groups 3 --alpha 0.05 --power 0.80
run ./bin/gpower-clone --test anova-oneway --mode a-priori --f 0.25 --groups 3 --alpha 0.05 --power 0.95
run ./bin/gpower-clone --test anova-oneway --mode post-hoc --f 0.25 --groups 3 --alpha 0.05 --n-total 90
echo; echo "== geçersiz girdi: JSON hata + sıfırdan farklı çıkış kodu =="
./bin/gpower-clone --test anova-oneway --mode a-priori --f 0 --groups 3 --alpha 0.05 --power 0.80; echo "çıkış kodu: $?"
sleep 2
echo; echo "== testler =="
python3 -m unittest discover -s tests -p "test_*.py" 2>&1 | tail -4
sleep 2
echo; echo "== diferansiyel test (kütüphane kâhini) =="
python3 tests/differential.py library anova-oneway | head -4
