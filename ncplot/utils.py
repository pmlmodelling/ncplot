import subprocess

import xarray as xr
import pandas as pd
import logging
import metpy

metpy_log = logging.getLogger("metpy")
metpy_log.setLevel(logging.CRITICAL)


def check_lon(x, ds):
    dims = list(ds.dims)
    news = ds.coords[x]
    possibles = [i for i in list(news.coords) if i in dims]

    if len(possibles) == 2:
        if possibles[0] < possibles[1]:
            return possibles[0]
        else:
            return possibles[1]

    return x


def check_lat(x, ds):
    dims = list(ds.dims)
    news = ds.coords[x]
    possibles = [i for i in list(news.coords) if i in dims]

    if len(possibles) == 2:
        if possibles[0] > possibles[1]:
            return possibles[0]
        else:
            return possibles[1]

    return x


def get_dims(ff):

    try:
        if type(ff) is xr.core.dataset.Dataset:
            ds = ff
        else:
            ds = xr.open_dataset(ff)

        ff_dims = list(ds.coords)
        var = [x for x in ds.variables.keys() if x not in ff_dims][0]
        ds = ds.metpy.parse_cf()

        try:
            for x in ds[var].metpy.coordinates("longitude"):
                lon_name = x.name
        except:
            lon_name = None

        try:
            for x in ds[var].metpy.coordinates("latitude"):
                lat_name = x.name
        except:
            lat_name = None

        try:
            for x in ds[var].metpy.coordinates("time"):
                time_name = x.name
        except:
            time_name = None

        # it's possible metpy will not parse lat/lon properly. In this case check if "lon"/"lat" appear in dims once
        if lon_name is None or lat_name is None:
            lons = [x for x in ff_dims if r"lon" in x]
            lats = [x for x in ff_dims if r"lat" in x]

            if len(lons) == 1 and len(lats) == 1:
                lon_name = lons[0]
                lat_name = lats[0]

        if lon_name is None and lat_name is None:
            if "x" in ff_dims and "y" in ff_dims:
                lon_name = "x"
                lat_name = "y"

            if "x_coord" in ff_dims and "y_coord" in ff_dims:
                lon_name = "x_coord"
                lat_name = "y_coord"

        return pd.DataFrame(
            {"longitude": [lon_name], "latitude": [lat_name], "time": [time_name]}
        )

    except:
        if type(ff) is xr.core.dataset.Dataset:
            ds = ff
        else:
            ds = xr.open_dataset(ff, decode_times=False)

        ff_dims = list(ds.coords)
        lats = [x for x in ff_dims if r"lat" in x]
        if len(lats) > 1:
            lats = [x for x in lats if x in list(ds.dims)]
            if len(lats) > 1:
                raise ValueError("Cannot parse dimension names!")

        if len(lats) == 0:
            lat_name = None
        else:
            lat_name = lats[0]

        lons = [x for x in ff_dims if r"lon" in x]
        if len(lons) > 1:
            lons = [x for x in lons if x in list(ds.dims)]
            if len(lons) > 1:
                raise ValueError("Cannot parse dimension names!")

        if len(lons) == 0:
            lon_name = None
        else:
            lon_name = lons[0]

        times = [x for x in ff_dims if r"time" in x]
        if len(times) > 1:
            raise ValueError("Cannot parse dimension names!")

        if len(times) == 0:
            time_name = None
        else:
            time_name = times[0]

        if lon_name is None and lat_name is None:
            if "x" in ff_dims and "y" in ff_dims:
                lon_name = "x"
                lat_name = "y"
            if "x_coord" in ff_dims and "y_coord" in ff_dims:
                lon_name = "x_coord"
                lat_name = "y_coord"

        return pd.DataFrame(
            {"longitude": [lon_name], "latitude": [lat_name], "time": [time_name]}
        )


def is_curvilinear(ff):
    """Function to work out if a file contains a curvilinear grid"""
    cdo_result = subprocess.run(
        f"cdo sinfo {ff}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    return (
        len(
            [
                x
                for x in cdo_result.stdout.decode("utf-8").split("\n")
                if "curvilinear" in x
            ]
        )
        > 0
    )
