How to use ncplot in Python
---------------------------

Using ncplot is very easy. It let's you plot the contents of a NetCDF automatically. To plot a file in Python, preferably a Jupyter notebook, do the following:

.. code:: ipython3

    from ncplot import ncplot
    ncplot(example.nc)

If you only want to plot a specific variable, you can do the following:

.. code:: ipython3

    ncplot(example.nc, "variable")

If you want to plot a list of variables, do the following:

.. code:: ipython3

    ncplot(example.nc, ["variable1", "variable2"])
