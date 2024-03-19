#!/bin/bash

# Slicing
python slicer.py cube --slice_height 0.4
python slicer.py bunny --slice_height 1.2
python slicer.py armadillo --slice_height 1.2
python slicer.py tyra --slice_height 1.2

# Extra Credit: Offsetting
# python offset.py cube --layer 20 --offset_distance 1.0 --num_offsets 10
# python offset.py bunny --layer 40 --offset_distance -1.0 --num_offsets 5
# python offset.py armadillo --layer 42 --offset_distance 2.0 --num_offsets 5
# python offset.py tyra --layer 60 --offset_distance 1.0 --num_offsets 2