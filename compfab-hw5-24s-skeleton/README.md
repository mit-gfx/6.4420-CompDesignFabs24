# Comp Fab HW5

Skeleton repo for HW5

## Installation

You don't need to install anything else.

### First time Set-up Only

If you don't have an environment setup previously, run

```
conda env create -f environment.yml
conda activate compfab
```

## Usage

### Part 1: Performance Exploration

```
python pareto.py [-n 10] [-f filename] [-v] [-t|--test|--notest]
```

#### Arguments
- `-n`: Number of random points to generate if filename is not given
- `-f, --filename`: Filename of the input points in npy format containing an array (n, 2)
- `-v, --verbose`: Whether to print out input and output points (Defualt to true if file not given)
- `-t, --test`: Whether to test against the brute-force solution (Default to true)
