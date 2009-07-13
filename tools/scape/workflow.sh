#!/bin/sh

# Note: this file is more for documentation than for execution.

./gen-cratons >cratons-main.txt
./gen-scaffold-main >scaffold-main.txt
./loc-cratons -i cratons-main.txt >cragginess.txt
./loc-fractal -c cragginess.txt -k scaffold-main.txt >height.txt
./hydro -r new-height.txt -w new-water.txt -H height.txt

. <(./minmax water.*.txt)
for f in water.*.txt; do
	./plot -o ${f/txt/png} --min-max $min,$max -f $f -0 -m 128,128,255
done

. <(./minmax height.*.txt)
for f in height.*.txt; do
	./plot -o ${f/txt/png} --min-max $min,$max -f $f -0 -m 255,255,255
done

./plot -o water.png -f new-water.txt -0 -m 128,128,255
