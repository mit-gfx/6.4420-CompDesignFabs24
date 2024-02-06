# Comp Fab HW1

Skeleton repo for HW1

## Installation

### From HW1

You will need to install additional dependencies. Make sure you are in the `compfab` enviromnent by running `conda activate compfab`. Then:

```
pip install svgwrite cairosvg
```

### First time Set-up Only

If you don't have an environment setup previously, run

```
conda env create -f environment.yml
conda activate compfab
```

## Usage

### Part 3: Deformation

1. Go to `deformation` directory.
2. Run
```
python main.py [port=3030]
```
3. Go to [localhost:3030](http://localhost:3030) on your browser.

### Part 4: Design with ChatGPT

1. Go to `gptdesign` directory.
2. Run
```
python json_to_img.py sample.json sample.png
```

