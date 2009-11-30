#!/bin/bash

. ./set_env
./tools/newaccount -r "Hugo Mills" -e hugo@carfax.org.uk Ruthven
./tools/newaccount -r "David Merritt" -e DavidBMerritt@yahoo.com Mongo
./tools/newaccount -r "Don Brinker" -e dbrinker@pobox.com Thog
./tools/newaccount -r "Daniel Pope" -e mauve@mauveweb.co.uk Mauve
./tools/newaccount PotatoEngineer
./tools/newaccount AndyLandy

./tools/newplayer Ruthven Ruthven -aw
./tools/newplayer Mongo Mongo -ae
./tools/newplayer Thog Thog -af
./tools/newplayer PotatoEngineer PotatoEngineer -am
./tools/newplayer AndyLandy AndyLandy -at
./tools/newplayer Mauve Mauve -at
