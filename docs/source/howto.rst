How to use ncplot in Python
---------------------------

Using cmipsearch is relatively easy. It let’s you search and download
CMIP6 data files.

.. code:: ipython3

    from ncplot import ncplot
    ncplot(example.nc)

If you only want to plot a specific variable, you can do the following:

.. code:: ipython3

    ncplot(example.nc, "variable")

If you want to plot a list of variables, do the following:

.. code:: ipython3

    ncplot(example.nc, ["variable1", "variable2"])

How to use ncplot as a command line tool
----------------------------------------

ncplot operates as a command line tool, letting you view the contents of
a NetCDF file on a website. This feature only works in development
version right now. All you need to do is provide the file you want to
look at:

.. code:: ipython3

    ncplot example.nc
