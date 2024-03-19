# Comp Fab HW3

Skeleton repo for HW3

## Installation

You don't need to install anything else.

### First time Set-up Only

If you don't have an environment setup previously, run

```
conda env create -f environment.yml
conda activate compfab
```

## Usage

### Part 2: Mesh Slicing

1. Go to `slicing` directory.
2. Run
```
python slicer.py MODEL_NAME [SLICE_HEIGHT=0.4]
```

#### Extra Credit: Offsetting
```
python offset.py MODEL_NAME LAYER OFFSET_DISTANCE NUM_OFFSEST
```

### Part 3: DSL for Sheet Metal

1. Go to `dsl` directory.
2. Implement `tab.py`.
3. Look at `example.py` on how write a program in your DSL.
