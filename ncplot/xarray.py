


import xarray as xr

from ncplot import ncplot

@xr.register_dataset_accessor('ncplot')
class NCAccessor:
    def __init__(self, xarray_obj):
        self._obj = xarray_obj

    def ncplot(self, **kwargs):
        """Plot data """
        return ncplot(self._obj, **kwargs)

@xr.register_dataarray_accessor('ncplot')
class NCAccessor:
    def __init__(self, xarray_obj):
        self._obj = xarray_obj

    def ncplot(self, **kwargs):
        """Plot data """
        return ncplot(self._obj, **kwargs)

