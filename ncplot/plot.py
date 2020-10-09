import sys
from threading import Thread

import time
import holoviews as hv
import panel as pn
import pandas as pd
import hvplot.pandas
import hvplot.xarray
from bokeh.plotting import show
import xarray as xr
import warnings

from ncplot.utils import get_dims

hv.extension("bokeh")
hv.Store.renderers


def is_curvilinear(ff):
    return False


def ctrc():
    time.sleep(1)
    print("Press Ctrl+C to stop plotting server")


def in_notebook():
    """
    Returns ``True`` if the module is running in IPython kernel,
    ``False`` if in IPython shell or other Python shell.
    """
    return "ipykernel" in sys.modules


def ncplot(x, vars=None):
    """
    Plot the contents of a NetCDF file
    Parameters
    -------------
    x : object or str
        xarray object or file path
    vars: list or str
        Variables you want to plot. Everything will be plotted if this is not supplied
    """

    log = False
    panel = False
    if type(x) is xr.core.dataset.Dataset:
        xr_file = True
    else:
        xr_file = False

    df_dims = get_dims(x)

    if xr_file is False:
        try:
            ds = xr.open_dataset(x)
        except:
            ds = xr.open_dataset(x, decode_times=False)
            warnings.warn("Warning: xarray could not decode times!")
    else:
        ds = x

    # figure out number of points
    lon_name = df_dims.longitude[0]
    lat_name = df_dims.latitude[0]

    n_points = 1
    if lon_name is not None:
        if len(ds[lon_name].values) > 1:
            n_points += len(ds[lon_name].values)

    if lat_name is not None:
        if len(ds[lat_name].values) > 1:
            n_points += len(ds[lat_name].values)

    # figure out number of times

    time_name = df_dims.time[0]

    n_times = len(ds[time_name].values)

    if lat_name is not None:
        if len(ds[lat_name].values) > 1:
            n_points += len(ds[lat_name].values)

    ff_dims = list(ds.dims)

    possible_others = [x for x in ff_dims if x not in df_dims.columns]

    if len(possible_others) == 0:
        n_levels = 1
    else:
        n_levels = len(ds[possible_others[0]].values)

    if vars is None:
        vars = [x for x in list(ds.variables) if x not in ff_dims]

        # also must have all of the coordinates...

    if type(vars) is list:
        new_vars = []
        for vv in vars:
            # if vv == "lon_bnds":
            if set(list(ds[vv].coords)) == set(list(ds.coords)):
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
    # Case when all you can plot is a time series

    # heat map 1

    coord_list = list(ds.coords)
    coord_df = pd.DataFrame(
        {"coord": coord_list, "length": [len(ds.coords[x].values) for x in coord_list]}
    )

    # line plot
    if len([x for x in coord_df.length if x > 1]) == 1:

        df = ds.to_dataframe().reset_index()
        if type(vars) is str:
            vars = [vars]

        for x in list(ds.coords):
            if len(ds.coords[x].values) > 1:
                x_var = x
                break

        selection = [x for x in df.columns if x in vars or x == x_var]

        df = df.loc[:, selection].melt(x_var).drop_duplicates().set_index(x_var)

        if panel:
            intplot = df.hvplot(
                by="variable",
                logy=log,
                subplots=True,
                shared_axes=False,
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
        else:
            intplot = df.hvplot(
                groupby="variable",
                logy=log,
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
    if len([x for x in coord_df.length if x > 1]) == 2:

        df = ds.to_dataframe().reset_index()
        x_var = coord_df.query("length > 1").reset_index().coord[0]
        y_var = coord_df.query("length > 1").reset_index().coord[1]

        selection = [x for x in df.columns if x in vars or x == x_var or x == y_var]

        df = df.loc[:, selection].melt([x_var, y_var]).drop_duplicates()
        if (len(ds.coords[lon_name].values) == 1) or (
            len(ds.coords[lat_name].values) == 1
        ):

            if type(vars) is list:
                intplot = df.drop_duplicates().hvplot.heatmap(
                    x=x_var,
                    y=y_var,
                    C="value",
                    groupby="variable",
                    colorbar=True,
                    cmap="viridis",
                )
            else:

                self_max = ds.rename({vars: "x"}).x.max()
                self_min = ds.rename({vars: "x"}).x.min()
                v_max = float(max(self_max.values, -self_min.values))

                if self_max > 0 and self_min < 0:

                    intplot = (
                        df.drop_duplicates()
                        .hvplot.heatmap(
                            x=x_var,
                            y=y_var,
                            C="value",
                            groupby="variable",
                            colorbar=True,
                            cmap="RdBu_r",
                            responsive=(in_notebook() is False),
                        )
                        .opts(clim=(-v_max, v_max))
                    )
                else:
                    intplot = df.drop_duplicates().hvplot.heatmap(
                        x=x_var,
                        y=y_var,
                        C="value",
                        groupby="variable",
                        colorbar=True,
                        cmap="viridis",
                    )

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

        time_in = False

        possible = 0
        for x in coord_list:
            if "time" in x:
                time_in = True
                possible += 1

        if possible > 1:
            time_in = False

        if time_name in coord_list and time_in:

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
                if (len(ds.coords[lon_name].values) == 1) or (
                    len(ds.coords[lat_name].values) == 1
                ):

                    intplot = df.drop_duplicates().hvplot.heatmap(
                        x=x_var,
                        y=y_var,
                        C="value",
                        groupby=["variable", time_name],
                        cmap="viridis",
                        colorbar=True,
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

        dim_dict = dict(df.dims)
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

        if panel:
            intplot = (
                df.set_index(time_name)
                .loc[:, vars]
                .reset_index()
                .melt(time_name)
                .set_index(time_name)
                .hvplot(
                    by="variable",
                    logy=log,
                    subplots=True,
                    shared_axes=False,
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

        else:
            intplot = (
                df.reset_index()
                .set_index(time_name)
                .loc[:, vars]
                .reset_index()
                .melt(time_name)
                .set_index(time_name)
                .hvplot(
                    groupby="variable",
                    logy=log,
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

        if is_curvilinear(ds):
            intplot = ds.hvplot.quadmesh(
                lon_name,
                lat_name,
                vars,
                dynamic=True,
                cmap="viridis",
                logz=log,
                responsive=in_notebook() is False,
            )
        else:
            intplot = ds.hvplot.image(
                lon_name,
                lat_name,
                vars,
                dynamic=True,
                cmap="viridis",
                logz=log,
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

        self_max = ds.rename({vars: "x"}).x.max()
        self_min = ds.rename({vars: "x"}).x.min()
        v_max = max(self_max.values, -self_min.values)

        if (self_max.values > 0) and (self_min.values < 0):
            if is_curvilinear(ds):
                intplot = ds.hvplot.quadmesh(
                    lon_name,
                    lat_name,
                    vars,
                    dynamic=True,
                    logz=log,
                    cmap="RdBu_r",
                    responsive=(in_notebook() is False),
                ).redim.range(**{vars: (-v_max, v_max)})
            else:
                intplot = ds.hvplot.image(
                    lon_name,
                    lat_name,
                    vars,
                    dynamic=True,
                    logz=log,
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
            if is_curvilinear(ds):
                intplot = ds.hvplot.quadmesh(
                    lon_name,
                    lat_name,
                    vars,
                    dynamic=True,
                    logz=log,
                    cmap="viridis",
                    responsive=(in_notebook() is False),
                ).redim.range(**{vars: (self_min.values, v_max)})
            else:
                intplot = ds.hvplot.image(
                    lon_name,
                    lat_name,
                    vars,
                    dynamic=True,
                    logz=log,
                    cmap="viridis",
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

    # Throw an error if case has not plotting method available yet
    # right now this only seems to be when you have lon/lat/time/levels and multiple variables
    # maybe needs an appropriate

    raise ValueError("Autoplotting method for this type of data is not yet available!")
