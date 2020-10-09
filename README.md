
<!-- README.md is generated from README.Rmd. Please edit that file -->






# ncplot - Automatic interactive plotting of NetCDF files in Python 

An easy to use Python (3.6 and above) package for quickly plotting the contents of NetCDF files. 


## Installation


Install the development version using using pip:
```sh
pip install git+https://github.com/pmlmodelling/nctplot.git
```



## Issues with dependencies 

Right now there are a couple of issues with the interdependence of the Python packages ncplot relies. These should be resolved with imminent updates to those packages.

For now run the following to make sure the package works properly:

```sh
conda install -c conda-forge pandas=1.0.5 
```

or

```sh
pip install pandas==1.0.5
```

and


```sh
conda install -c conda-forge hvplot=0.5.2
```

or

```sh
pip install hvplot==0.5.2
```

## How to use

The package is made up of a simple easy to use function: ncplot.

```sh
from ncplot import ncplot

nplot("example.nc")

```







