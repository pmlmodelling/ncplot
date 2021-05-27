import sys
from threading import Thread

from cartopy import crs
import time
import holoviews as hv
import panel as pn
import cartopy.crs as ccrs

import pandas as pd
import hvplot.pandas
import hvplot.xarray
from bokeh.plotting import show
import xarray as xr
import warnings
import copy
import numpy as np

from ncplot.utils import get_dims, check_lon, check_lat

hv.extension("bokeh")
hv.Store.renderers


def get_coastline(ds, lon_name, lat_name):
    """
    A function to work out an appropriate coastline resolution
    """
    lon_max = ds[lon_name].values.max()
    lon_min = ds[lon_name].values.min()

    lat_max = ds[lat_name].values.max()
    lat_min = ds[lat_name].values.min()

    if ((lon_max - lon_min) * (lat_max - lat_min)) / (360 ** 2) < 0.0016:
        return "10m"

    if ((lon_max - lon_min) * (lat_max - lat_min)) / (360 ** 2) < 0.25:
        return "50m"

    return "110m"


def change_coords(dx):
    """
    Some model output will have repeated zeros as lon/lat. This will mess up quadmesh. Replace lon/lat with indices
    """

    ds = dx.copy()
    df_dims = get_dims(ds)

    lon_name = df_dims.longitude[0]
    lat_name = df_dims.latitude[0]

    # if there are repeated zeros
    if len([x for x in ds[lat_name].values[0] if x == 0]) <= 1:
        return ds

    if sum(ds[lon_name].values[0] == ds[lon_name].values[1]) == len(ds[lon_name][0]):
        for i in range(0, len(ds[lon_name])):
            ds[lon_name].values[i] = range(0, len(ds[lon_name][0]))
    else:
        for i in range(0, len(ds[lat_name])):
            ds[lon_name].values[i] = np.repeat(i, len(ds[lon_name][i]))

    if sum(ds[lat_name].values[0] == ds[lat_name].values[1]) == len(ds[lon_name][0]):
        for i in range(0, len(ds[lat_name])):
            ds[lat_name].values[i] = range(0, len(ds[lat_name][i]))
    else:
        for i in range(0, len(ds[lat_name])):
            ds[lat_name].values[i] = np.repeat(i, len(ds[lat_name][i]))

    if "x" in list(ds.dims.keys()):
        ds.coords[lon_name].attrs["long_name"] = "x"
        ds.coords[lon_name].attrs["units"] = "x"
        ds = ds.rename({lon_name: "x_coord"})
    else:
        ds = ds.rename({lon_name: "x"})

    if "y" in list(ds.dims.keys()):
        ds.coords[lat_name].attrs["long_name"] = "y"
        ds.coords[lat_name].attrs["units"] = "y"
        ds = ds.rename({lat_name: "y_coord"})
    else:
        ds = ds.rename({lat_name: "y"})

    return ds


def is_curvilinear(ds):
    """
    A function originally in nctoolkit, which used CDO to figure out if a grid was curvilinear. This should
    be rename to something like is_quadmesh
    """

    ds_dims = get_dims(ds)
    if ds_dims.longitude.values[0] is None or ds_dims.latitude.values[0] is None:
        return False

    if len(ds.coords[ds_dims.longitude.values[0]].dims) > 1:
        return True

    return False


def ctrc():
    """
    A basic control to send a message to the terminal
    """
    time.sleep(1)
    print("Press Ctrl+C to stop plotting server")


def in_notebook():
    """
    Returns ``True`` if the module is running in IPython kernel,
    ``False`` if in IPython shell or other Python shell.
    """
    if "spyder" in sys.modules:
        return False

    return "ipykernel" in sys.modules


def view(x, vars=None):
    """
    Plot the contents of a NetCDF file
    Parameters
    -------------
    x : object or str
        xarray object or file path
    vars : list or str
        Variables you want to plot. Everything will be plotted if this is not supplied

    """

    coastline = True
    if type(x) is xr.core.dataarray.DataArray:
        x = x.to_dataset()

    if type(x) is xr.core.dataset.Dataset:
        xr_file = True
    else:
        xr_file = False

    if xr_file is False:
        try:
            ds = xr.open_dataset(x)
        except:
            ds = xr.open_dataset(x, decode_times=False)
            warnings.warn("Warning: xarray could not decode times!")
    else:
        ds = x

    coord_list = list(ds.coords)

    for cc in coord_list:
        if len(ds[cc].values.ravel()) <= 1:
            if cc in list(ds.dims):
                ds = ds.squeeze(cc, drop=True)

    coord_list = list(ds.dims)

    for cc in coord_list:
        if len(ds[cc].values.ravel()) <= 1:
            if cc in list(ds.dims):
                ds = ds.squeeze(cc, drop=True)

    quadmesh = False

    if len(list(ds.dims)) + len(list(ds.coords)) == 0:
        raise ValueError("There are no dimensions or coordinates in the dataset!")

    df_dims = get_dims(ds)
    # figure out number of points
    lon_name = df_dims.longitude[0]
    lat_name = df_dims.latitude[0]

    if lon_name is not None:
        if "long_name" in ds[lon_name].attrs:
            if "rotate" in ds[lon_name].long_name:
                coastline = False

            if "pole" in ds[lon_name].long_name:
                coastline = False

    if len([x for x in ds.coords if "lon" in x]) > len(
        [x for x in ds.dims if "lon" in x]
    ):
        coastline = False

    if quadmesh is False and lat_name is not None:
        lats = ds[lat_name].values
        if len(lats) > 1:

            max_step = np.max([np.abs(x) for x in (lats[0:-2] - lats[1:-1])])
            min_step = np.min([np.abs(x) for x in (lats[0:-2] - lats[1:-1])])
            if min_step == 0:
                quadmesh = True
            else:
                if max_step / min_step > 1.001:
                    quadmesh = True

    switch_coords = False

    rasterize = True

    if quadmesh:
        switch_coords = True
        if len(np.shape(ds[lon_name].values)) == 1:
            switch_coords = False

        if switch_coords:
            if lon_name != check_lon(lon_name, ds):
                lon_name = check_lon(lon_name, ds)
                rasterize = False
                switch_coords = False
                quadmesh = False
                coastline = False
            if lat_name != check_lat(lat_name, ds):
                lat_name = check_lat(lat_name, ds)
                rasterize = False
                quadmesh = False

    if switch_coords:
        orig_coords = list(ds.coords)
        ds = change_coords(ds)
        new_coords = list(ds.coords)
        quadmesh = True
        df_dims = get_dims(ds)
        # figure out number of points
        lon_name = df_dims.longitude[0]
        lat_name = df_dims.latitude[0]
        if orig_coords != new_coords:
            coastline = False
            rasterize = False

    if lon_name is not None:
        if len(ds[lon_name].dims) > 1:
            quadmesh = True

    n_points = 1
    if lon_name is not None:
        if len(ds[lon_name].values) > 1:
            n_points += len(ds[lon_name].values)

    if lat_name is not None:
        if len(ds[lat_name].values) > 1:
            n_points += len(ds[lat_name].values)

    # figure out number of times

    time_name = df_dims.time[0]

    # time name maybe cannot be parsed. If "time" is among the coords, use that

    if time_name is None:
        candidates = list()
        n_candidates = 0
        for x in list(ds.coords):
            if x.startswith("time"):
                candidates.append(x)
                n_candidates += 0
        if len(candidates) == 1:
            time_name = candidates[0]

    if time_name is None:
        n_times = 0
    else:
        n_times = len(ds[time_name].values)

    if lat_name is not None:
        if len(ds[lat_name].values) > 1:
            n_points += len(ds[lat_name].values)

    ff_dims = list(ds.coords)

    possible_others = [x for x in ff_dims if x not in df_dims.columns]

    if len(possible_others) == 0:
        n_levels = 1
    else:
        n_levels = len(ds[possible_others[0]].values)

    if vars is None:
        vars = [x for x in list(ds.variables) if x not in ff_dims]

        # also must have all of the coordinates...

    # code below figures out what is a variable, not a coordinate. Could be improved...

    coord_list = list(ds.coords)

    for cc in coord_list:
        if len(ds[cc].values.ravel()) <= 1:
            if cc in list(ds.dims):
                ds = ds.squeeze(cc, drop=True)

    if type(vars) is list:
        new_vars = []
        for vv in vars:
            set_coords = set(
                [x for x in list(ds.coords) if "vertice" not in x and "bnds" not in x]
            )
            if set(list(ds[vv].coords)) == set_coords:
                new_vars.append(vv)
        vars = new_vars

    if type(vars) is list:
        if len(vars) == 1:
            vars = vars[0]

    if type(vars) is list:
        for vv in vars:
            if vv not in list(ds.variables):
                raise ValueError(f"{vv} is not a valid variable")
    else:
        if vars not in list(ds.variables):
            raise ValueError(f"{vars} is not a valid variable")

    if (lon_name is not None) and (lat_name is not None) and type(vars) is list:
        new_vars = []
        for x in vars:

            dims_required = []
            for i in list(ds.coords):
                dims_required += ds.coords[i].dims
            dims_required = set(dims_required)

            if set(ds[x].dims) == dims_required:
                new_vars.append(x)
        vars = new_vars

    if len(vars) == 1:
        vars = vars[0]

    if (lon_name is None) or (lat_name is None):
        rasterize = False

    # Case when all you can plot is a time series

    # heat map 1

    # get rid of coordinates without multiple values

    coord_list = list(ds.coords)

    for cc in coord_list:
        if len(ds[cc].values.ravel()) <= 1:
            if cc in list(ds.dims):
                ds = ds.squeeze(cc, drop=True)

    coord_list = list(ds.coords)

    coord_df = pd.DataFrame(
        {"coord": coord_list, "length": [len(ds.coords[x].values) for x in coord_list]}
    )

    # work out if it should be a spatial map

    spatial_map = False

    # line plot

    if lon_name is not None and lat_name is not None:

        if lon_name in list(ds.coords) and lat_name in list(ds.coords):
            if (len(ds[lon_name].values) > 1) and (len(ds[lat_name].values) > 1):
                spatial_map = True

    if len([x for x in coord_df.length if x > 1]) == 1 and spatial_map is False:

        df = ds.to_dataframe().reset_index()
        if type(vars) is str:
            vars = [vars]

        for x in list(ds.coords):
            if len(ds.coords[x].values) > 1:
                x_var = x
                break

        selection = [x for x in df.columns if x in vars or x == x_var]

        df = df.loc[:, selection].melt(x_var).drop_duplicates().set_index(x_var)

        intplot = df.hvplot(
            groupby="variable",
            dynamic=True,
            responsive=(in_notebook() is False),
        )
        if in_notebook():
            return intplot

        t = Thread(target=ctrc)
        t.start()

        bokeh_server = pn.panel(intplot, sizing_mode="stretch_both").show(
            threaded=False
        )
        return None

    # heat map where 2 coords have more than 1 value, not a spatial map
    if len([x for x in coord_df.length if x > 1]) == 2 and spatial_map is False:

        df = ds.to_dataframe().reset_index()
        x_var = coord_df.query("length > 1").reset_index().coord[0]
        y_var = coord_df.query("length > 1").reset_index().coord[1]

        selection = [x for x in df.columns if x in vars or x == x_var or x == y_var]

        df = df.loc[:, selection].melt([x_var, y_var]).drop_duplicates()

        # we need to make sure this is not 2d geographic data
        case1 = 0
        if lon_name is not None and lon_name in list(ds.coords):
            if len(ds.coords[lon_name].values) > 1:
                case1 += 1

        if lat_name is not None and lat_name in list(ds.coords):
            if len(ds.coords[lat_name].values) > 1:
                case1 += 1

        if case1 <= 1:

            if type(vars) is list:
                # figure out if it needs to be quadmesh
                if x_var == time_name:
                    quadmesh = True
                x_vals = ds[x_var].values

                if len(x_vals) > 2:

                    if (
                        np.nanmax(x_vals[0:-2] - x_vals[1:-1]).astype("float")
                        - np.nanmin(x_vals[0:-2] - x_vals[1:-1]).astype("float")
                        > 0
                    ):
                        quadmesh = True
                y_vals = ds[y_var].values
                if len(y_vals) > 2:
                    if (
                        np.nanmax(y_vals[0:-2] - y_vals[1:-1]).astype("float")
                        - np.nanmin(y_vals[0:-2] - y_vals[1:-1]).astype("float")
                        > 0
                    ):
                        quadmesh = True

                if quadmesh:
                    intplot = ds.hvplot.quadmesh(x_var, y_var, vars, cmap="viridis")
                else:
                    intplot = ds.hvplot.image(x_var, y_var, vars, cmap="viridis")

            else:

                self_max = ds.rename({vars: "x"}).x.max()
                self_min = ds.rename({vars: "x"}).x.min()
                v_max = float(max(self_max.values, -self_min.values))

                # figure out if it needs to be quadmesh
                if x_var == time_name:
                    quadmesh = True
                x_vals = ds[x_var].values

                if len(x_vals) > 2:
                    if (
                        np.nanmax(x_vals[0:-2] - x_vals[1:-1]).astype("float")
                        - np.nanmin(x_vals[0:-2] - x_vals[1:-1]).astype("float")
                        > 0
                    ):
                        quadmesh = True
                y_vals = ds[y_var].values

                if len(y_vals) > 2:
                    if (
                        np.nanmax(y_vals[0:-2] - y_vals[1:-1]).astype("float")
                        - np.nanmin(y_vals[0:-2] - y_vals[1:-1]).astype("float")
                        > 0
                    ):
                        quadmesh = True

                if self_max > 0 and self_min < 0:
                    if quadmesh:
                        intplot = ds.hvplot.quadmesh(
                            x_var,
                            y_var,
                            vars,
                            cmap="RdBu_r",
                            responsive=(in_notebook() is False),
                        ).redim.range(**{vars: (-v_max, v_max)})
                    else:
                        intplot = ds.hvplot.image(
                            x_var,
                            y_var,
                            vars,
                            cmap="RdBu_r",
                            rasterize=False,
                            responsive=(in_notebook() is False),
                        ).redim.range(**{vars: (-v_max, v_max)})

                else:
                    if quadmesh:
                        intplot = ds.hvplot.quadmesh(x_var, y_var, vars, cmap="viridis")
                    else:
                        intplot = ds.hvplot.image(x_var, y_var, vars, cmap="viridis")

            if in_notebook():
                return intplot

            t = Thread(target=ctrc)
            t.start()
            bokeh_server = pn.panel(intplot, sizing_mode="stretch_both").show(
                threaded=False
            )
            return None

    # heat map where 3 coords have more than 1 value, and one of them is time. Not a spatial map though
    if len([x for x in coord_df.length if x > 1]) == 3:

        non_map = True

        if lon_name is not None and lat_name is not None:
            if (lon_name is not None) and (lon_name in list(ds.coords)):
                lons = int(coord_df.query("coord == @lon_name").length)
            else:
                lons = 0

            if (lat_name) is not None and (lat_name in list(ds.coords)):
                lats = int(coord_df.query("coord == @lat_name").length)
            else:
                lats = 0

            if lons > 1 and lats > 1:
                non_map = False

        time_in = False

        possible = 0

        for x in coord_list:
            if "time" in x:
                time_in = True
                possible += 1

        if time_name in coord_list and time_in and non_map:

            if coord_df.query("coord == @time_name").length.values > 1:

                df = ds.to_dataframe().reset_index()
                for x in list(ds.coords):
                    if (len(ds.coords[x].values) > 1) and (x != time_name):
                        x_var = x
                        break

                for x in list(ds.coords):
                    if (
                        (len(ds.coords[x].values) > 1)
                        and (x is not x_var)
                        and (x != time_name)
                    ):
                        y_var = x
                        break

                selection = [
                    x
                    for x in df.columns
                    if x in vars or x == x_var or x == y_var or x == time_name
                ]

                df = df.loc[:, selection]
                df = df.melt([x_var, y_var, time_name]).drop_duplicates()
                case1 = 0
                if lon_name is not None and lon_name in list(ds.coords):
                    if len(ds.coords[lon_name].values) > 1:
                        case1 += 1

                if lat_name is not None and lat_name in list(ds.coords):
                    if len(ds.coords[lat_name].values) > 1:
                        case1 += 1

                if case1 <= 1:

                    # this could also do with a blue to red option

                    # figure out if it should be quadmesh
                    quadmesh = False
                    x_vals = ds[x_var].values
                    if len(x_vals) > 2:
                        if (
                            np.nanmax(x_vals[0:-2] - x_vals[1:-1]).astype("float")
                            - np.nanmin(x_vals[0:-2] - x_vals[1:-1]).astype("float")
                            > 0
                        ):
                            quadmesh = True

                    y_vals = ds[y_var].values
                    if len(y_vals) > 2:
                        if (
                            np.nanmax(y_vals[0:-2] - y_vals[1:-1]).astype("float")
                            - np.nanmin(y_vals[0:-2] - y_vals[1:-1]).astype("float")
                            > 0
                        ):
                            quadmesh = True

                    if quadmesh:
                        intplot = ds.hvplot.quadmesh(
                            x_var, y_var, vars, cmap="viridis", rasterize=True
                        )
                    else:
                        intplot = ds.hvplot.image(
                            x_var, y_var, vars, cmap="viridis", rasterize=False
                        )

                    if in_notebook():
                        return intplot

                    t = Thread(target=ctrc)
                    t.start()
                    bokeh_server = pn.panel(intplot, sizing_mode="stretch_both").show(
                        threaded=False
                    )
                    return None

    if (n_times > 1) and (n_points < 2) and (n_levels <= 1):

        if type(vars) is str:
            vars = [vars]

        df = ds

        dim_dict = dict(df.coords)
        to_go = []
        for kk in dim_dict.keys():
            if dim_dict[kk] == 1:
                df = df.squeeze(kk)
                to_go.append(kk)

        df = df.to_dataframe()
        keep = vars
        df = df.reset_index()

        to_go = [x for x in df.columns if (x not in [time_name] and x not in keep)]

        df = df.drop(columns=to_go).drop_duplicates()

        intplot = (
            df.reset_index()
            .set_index(time_name)
            .loc[:, vars]
            .reset_index()
            .melt(time_name)
            .set_index(time_name)
            .hvplot(
                groupby="variable",
                dynamic=True,
                responsive=(in_notebook() is False),
            )
        )
        if in_notebook():
            return intplot

        t = Thread(target=ctrc)
        t.start()

        bokeh_server = pn.panel(intplot, sizing_mode="stretch_both").show(
            threaded=False
        )
        return None

    if (n_points > 1) and (n_levels >= 1) and (type(vars) is list):

        if quadmesh:

            if coastline:
                coastline = get_coastline(ds, lon_name, lat_name)
                projection = ccrs.PlateCarree()
            else:
                projection = None

            intplot = ds.hvplot.quadmesh(
                lon_name,
                lat_name,
                vars,
                dynamic=True,
                cmap="viridis",
                coastline=coastline,
                projection=projection,
                rasterize=rasterize,
                responsive=in_notebook() is False,
            )
        else:

            if coastline:
                coastline = get_coastline(ds, lon_name, lat_name)
                projection = ccrs.PlateCarree()
            else:
                projection = None

            intplot = ds.hvplot.image(
                lon_name,
                lat_name,
                vars,
                dynamic=True,
                cmap="viridis",
                coastline=coastline,
                rasterize=False,
                projection=projection,
                responsive=in_notebook() is False,
            )

        if in_notebook():
            return intplot

        t = Thread(target=ctrc)
        t.start()
        bokeh_server = pn.panel(intplot, sizing_mode="stretch_both").show(
            threaded=False
        )
        return None

    if n_points > 1:

        if type(vars) is list:
            warnings.warn(message="Warning: Only the first variable is mapped")
            vars = vars[0]

        self_max = ds.rename({vars: "x_dim12345"}).x_dim12345.max()
        self_min = ds.rename({vars: "x_dim12345"}).x_dim12345.min()
        v_max = max(self_max.values, -self_min.values)

        if (self_max.values > 0) and (self_min.values < 0):
            if quadmesh:
                if coastline:
                    coastline = get_coastline(ds, lon_name, lat_name)
                    projection = ccrs.PlateCarree()
                else:
                    projection = None

                intplot = ds.hvplot.quadmesh(
                    lon_name,
                    lat_name,
                    vars,
                    dynamic=True,
                    cmap="RdBu_r",
                    coastline=coastline,
                    projection=projection,
                    rasterize=rasterize,
                    responsive=(in_notebook() is False),
                ).redim.range(**{vars: (-v_max, v_max)})
                # intplot = pn.Row(pn.WidgetBox(w1), intplot)
            else:
                if coastline:
                    coastline = get_coastline(ds, lon_name, lat_name)
                    projection = ccrs.PlateCarree()
                else:
                    projection = None

                intplot = ds.hvplot.image(
                    lon_name,
                    lat_name,
                    vars,
                    dynamic=True,
                    coastline=coastline,
                    projection=projection,
                    rasterize=False,
                    cmap="RdBu_r",
                    responsive=(in_notebook() is False),
                ).redim.range(**{vars: (-v_max, v_max)})

            if in_notebook():
                return intplot

            t = Thread(target=ctrc)
            t.start()
            bokeh_server = pn.panel(intplot, sizing_mode="stretch_both").show(
                threaded=False
            )
            return None

        else:
            if quadmesh:
                if coastline:
                    coastline = get_coastline(ds, lon_name, lat_name)
                    projection = ccrs.PlateCarree()
                else:
                    projection = None
                intplot = ds.hvplot.quadmesh(
                    lon_name,
                    lat_name,
                    vars,
                    dynamic=True,
                    cmap="viridis",
                    coastline=coastline,
                    projection=projection,
                    rasterize=rasterize,
                    responsive=(in_notebook() is False),
                ).redim.range(**{vars: (self_min.values, v_max)})
            else:

                if coastline:
                    coastline = get_coastline(ds, lon_name, lat_name)
                    projection = ccrs.PlateCarree()
                else:
                    projection = None

                intplot = ds.hvplot.image(
                    lon_name,
                    lat_name,
                    vars,
                    dynamic=True,
                    cmap="viridis",
                    coastline=coastline,
                    rasterize=False,
                    projection=projection,
                    responsive=(in_notebook() is False),
                ).redim.range(**{vars: (self_min.values, v_max)})

            if in_notebook():
                return intplot

            t = Thread(target=ctrc)
            t.start()
            bokeh_server = pn.panel(intplot, sizing_mode="stretch_both").show(
                threaded=False
            )

            return None

    # it's possible that the data has not spatial or temporal coordinates. Do something about it....

    # Throw an error if case has not plotting method available yet
    # right now this only seems to be when you have lon/lat/time/levels and multiple variables
    # maybe needs an appropriate

    raise ValueError("Autoplotting method for this type of data is not yet available!")
