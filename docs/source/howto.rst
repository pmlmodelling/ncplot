How to use ncplot in Python
---------------------------

Using ncplot is very easy. It let's you plot the contents of a NetCDF automatically. To plot a file in Python, preferably a Jupyter notebook, do the following::

.. code:: ipython3

    from ncplot import view
    view(example.nc)

If you only want to plot a specific variable, you can do the following::

.. code:: ipython3

    view(example.nc, "variable")

If you want to plot a list of variables, do the following::

.. code:: ipython3

    view(example.nc, ["variable1", "variable2"])


There is also built in support for xarray datasets and dataarrays.

.. code:: ipython3

    import ncplot.xarray
    ds.ncplot.view()


How to use ncplot as a command line tool
----------------------------------------

ncplot operates as a command line tool, letting you view the contents of
a NetCDF file on a website. This feature only works in development
version right now. All you need to do is provide the file you want to
look at::

.. code:: ipython3

    ncplot example.nc
