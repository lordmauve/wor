#!/bin/sh

# Note: this file is more for documentation than for execution.

./gen-cratons >cratons-main.txt
./gen-scaffold-main >scaffold-main.txt
./loc-cratons -i cratons-main.txt >cragginess.txt
./loc-fractal -c cragginess.txt -k scaffold-main.txt >height.txt
./hydro-rivers -H height.txt >rivers.txt
./hydro-ponds -H height.txt -r rivers.txt >ponds.txt
