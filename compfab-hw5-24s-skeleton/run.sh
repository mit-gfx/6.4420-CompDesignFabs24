#!/bin/bash

for i in {0..16}
do
    python pareto.py -f data/points_$i.npy
done
python pareto.py -f data/points_17.npy --notest