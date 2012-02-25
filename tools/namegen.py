#!/usr/bin/python

import sys
import os.path
import pickle
import random
import pprint

probs = {}

def load_data(data_file):
    global probs
    if not os.path.isfile(data_file):
        return
    probs = pickle.load(open(data_file, "r"))
    print pprint.pformat(probs)

def save_data(data_file):
    of = open(data_file, "w")
    pickle.dump(probs, of)
    print pprint.pformat(probs)

def update_probs(a, b):
    try:
        this_prob = probs[a]
    except KeyError:
        probs[a] = {}
        this_prob = probs[a]

    try:
        this_prob[b] += 1
    except KeyError:
        this_prob[b] = 1

def learn():
    line = sys.stdin.readline()
    while line != "":
        words = line.split()
        for w in words:
            last = "\0"
            for this in w:
                update_probs(last, this)
                last = this
            update_probs(last, "\0")

        line = sys.stdin.readline()

def generate():
    this = "\0"
    c = None
    while c != "\0":
        output = probs[this]
        total = reduce(lambda x, y: x+y, output.values())
        r = random.randrange(0, total)
        t = 0
        for c, p in output.iteritems():
            t += p
            if t > r:
                this = c
                if c != "\0":
                    sys.stdout.write(c)
                break
        if c == "\0":
            print

load_data(sys.argv[2])
if sys.argv[1] == "learn":
    learn()
    save_data(sys.argv[2])
elif sys.argv[1] == "generate":
    generate()
