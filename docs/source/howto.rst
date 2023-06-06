How to use ncplot 
---------------------------

Using ncplot is very easy. It lets you plot the contents of a NetCDF automatically. We will illustrate this by plotting sea surface temperature from the National Oceanic and Atmospheric Administration's COBE2 dataset. To plot a file in Python, preferably a Jupyter notebook, do the following::

    from ncplot import view
    view("https://psl.noaa.gov/thredds/dodsC/Datasets/COBE2/sst.mon.ltm.1981-2010.nc", coast = True)

In this case, we use the coast argument to ensure the world's coastlines are displayed.

.. raw:: html
   :file: plot.html

There is also built in support for xarray datasets::

    import ncplot.xarray
    import xarray as xr 
    ds = xr.open_dataset("https://psl.noaa.gov/thredds/dodsC/Datasets/COBE2/sst.mon.ltm.1981-2010.nc")
    ds["sst"].ncplot.view(coast = True)

.. raw:: html
   :file: xarray.html

ncplot operates as a command line tool, letting you view the contents of a NetCDF file on a website. All you need to do is provide the file you want to look at::

    $ ncplot foo.nc
