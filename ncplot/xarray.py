


import xarray as xr

from ncplot import view

@xr.register_dataset_accessor('ncplot')
class NCAccessor:
    def __init__(self, xarray_obj):
        self._obj = xarray_obj

    def view(self, **kwargs):
        """Plot data """
        return view(self._obj, **kwargs)

@xr.register_dataarray_accessor('ncplot')
class NCAccessor:
    def __init__(self, xarray_obj):
        self._obj = xarray_obj

    def view(self, **kwargs):
        """Plot data """
        return view(self._obj, **kwargs)

