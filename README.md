
# ncplot - Automatic interactive plotting of NetCDF files in Python 


[![pypi](https://img.shields.io/pypi/v/ncplot.svg)](https://pypi.python.org/pypi/ncplot/)
[![Documentation Status](https://readthedocs.org/projects/ncplot/badge/?version=latest)](https://ncplot.readthedocs.io/en/latest/?badge=latest)



An easy to use Python (3.6 and above) package for quickly plotting the contents of NetCDF files or xarray datasets. 

This package is designed to work with CF compliant data. 

## Installation


Install the development version using using pip:
```sh
pip install git+https://github.com/pmlmodelling/ncplot.git
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


The package is made up of a simple easy to use function: ncplot. To visualize everything in a file:

```sh
from ncplot import ncplot

ncplot("example.nc")

```

or to visualize a specific variable or list of variables:

```sh
from ncplot import ncplot

ncplot("example.nc", vars)

```

where vars is a string representing a variable or a list of variables.




# Reference and tutorials

A full API reference, and a how-to guide are available at [readthedocs](https://ncplot.readthedocs.io/en/latest/).








