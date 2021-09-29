# Licensed under the BSD 3-Clause License
# Copyright (C) 2021 GeospaceLab (geospacelab)
# Author: Lei Cai, Space Physics and Astronomy, University of Oulu

__author__ = "Lei Cai"
__copyright__ = "Copyright 2021, GeospaceLab"
__license__ = "BSD-3-Clause License"
__email__ = "lei.cai@oulu.fi"
__docformat__ = "reStructureText"

import numpy as np
import datetime
import cartopy.crs as ccrs
import re
import copy
from cartopy.mpl.ticker import (
    LongitudeLocator, LatitudeLocator,
    LongitudeFormatter, LatitudeFormatter)
import matplotlib.ticker as mticker
import matplotlib.path as mpath
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

import geospacelab.visualization.mpl as mpl
import geospacelab.toolbox.utilities.pylogging as mylog
import geospacelab.toolbox.utilities.pydatetime as dttool
import geospacelab.toolbox.utilities.numpymath as mathtool
import geospacelab.toolbox.utilities.pybasic as pybasic


def test():
    import matplotlib.pyplot as plt
    dt = datetime.datetime(2012, 1, 19, 10, 0)
    p = PolarMap(pole='N', lon_c=None, ut=dt, mlt_c=0)
    p.add_subplot(major=True)

    p.set_extent(boundary_style='circle')

    p.add_coastlines()
    p.add_grids()
    plt.show()
    pass


class PolarMap(mpl.Panel):
    def __init__(self, *args, cs='AACGM', style=None, lon_c=None, pole='N', ut=None, lst_c=None, mlt_c=None,
                 mlon_c=None,
                 boundary_lat=30., boundary_style='circle',
                 mirror_south=False,
                 proj_type='Stereographic', **kwargs):
        if style is None:
            style = input("Specify the mapping style: lon-fixed, lst-fixed, mlon-fixed, or mlt-fixed? ")
        self.style = style
        if style in ['lon-fixed']:
            if lon_c is None:
                raise ValueError
            lst_c = None
            mlon_c = None
            mlt_c = None

        if style in ['lst-fixed']:
            if lst_c is None:
                raise ValueError
            lon_c = None
            mlon_c = None
            mlt_c = None

        if style in ['mlon-fixed']:
            if mlon_c is None:
                raise ValueError
            lst_c = None
            lon_c = mlon_c
            mlt_c = None

        if style in ['mlt-fixed']:
            if mlt_c is None:
                raise ValueError
            lst_c = None
            lon_c = None
            mlon_c = None

        # if lon_c is not None and pole == 'S':
        #    lon_c = lon_c + 180.

        self.lat_c = None
        self.lon_c = lon_c
        self.ut = ut
        self.boundary_lat = boundary_lat
        self.boundary_style = boundary_style
        self.pole = pole
        self.lst_c = lst_c
        self.cs = cs
        self.depend_mlt = False
        self.mlt_c = mlt_c
        self.mirror_south = mirror_south
        self._extent = None
        proj = getattr(ccrs, proj_type)
        self.proj = proj(central_latitude=self.lat_c, central_longitude=self.lon_c)
        kwargs.setdefault('projection', self.proj)
        super().__init__(*args, **kwargs)
        self.set_extent()

    @staticmethod
    def _transform_mlt_to_lon(mlt):
        lon = mlt / 24. * 360.
        lon = np.mod(lon, 360.)
        return lon

    def add_axes(self, *args, major=False, label=None, **kwargs):
        if major:
            kwargs.setdefault('projection', self.proj)
        ax = super().add_axes(*args, major=major, label=label, **kwargs)
        return ax

    # def add_lands(self):
    #     import cartopy.io.shapereader as shpreader
    #
    #     resolution = '110m'
    #     shpfilename = shpreader.natural_earth(resolution=resolution,
    #                                           category='physical',
    #                                           name='coastline')
    #     reader = shpreader.Reader(shpfilename)
    #     lands = list(reader.geometries())
    #
    #     for ind1, land in enumerate(lands):
    #         land_polygons = list(land)
    #         for ind2, polygon in enumerate(land_polygons):
    #             x, y = polygon.exterior.coords.xy
    #
    def cs_transform(self, cs_fr=None, cs_to=None, coords=None, ut=None):
        import geospacelab.cs as geo_cs

        if cs_to is None:
            cs_to = self.cs
        if ut is None:
            ut = self.ut
        cs_class = getattr(geo_cs, cs_fr.upper())
        cs1 = cs_class(coords=coords, ut=ut)
        if cs_fr != cs_to:
            cs2 = cs1(cs_to=cs_to, append_mlt=self.depend_mlt)
        else:
            cs2 = cs1
        if self.depend_mlt:
            cs2.coords.lon = self._transform_mlt_to_lon(cs2.coords.mlt)
        return cs2

    def add_coastlines(self):
        import cartopy.io.shapereader as shpreader

        resolution = '110m'
        shpfilename = shpreader.natural_earth(resolution=resolution,
                                              category='physical',
                                              name='coastline')
        coastlines = list(shpreader.Reader(shpfilename).geometries())

        x = np.array([])
        y = np.array([])
        for ind, c in enumerate(coastlines[:-1]):
            # print(ind)
            # print(len(c.xy[0]))
            # if ind not in [4013, 4014]:
            #    continue
            x0 = np.array(c.xy[0])
            y0 = np.array(c.xy[1])
            # if len(x0) < 20:  # omit small islands, etc.
            #    continue
            x0 = np.mod(x0[::1], 360)
            y0 = y0[::1]
            x = np.append(np.append(x, x0), np.nan)
            y = np.append(np.append(y, y0), np.nan)

            # csObj = scs.SpaceCS(x, y, CS='GEO', dt=self.dt, coords_labels=['lon', 'lat'])

        coords = {'lat': y, 'lon': x, 'height': 250.}
        coords = self.cs_transform(cs_fr='GEO', cs_to=self.cs, coords=coords)
        x_new = coords['lon']
        y_new = coords['lat']
        # x_new, y_new = x, y
        self.major_ax.plot(x_new, y_new, transform=ccrs.Geodetic(),
                           linestyle='-', linewidth=0.8, color='#797A7D', zorder=100, alpha=0.7)
        # self.ax.scatter(x_new, y_new, transform=self.default_transform,
        #             marker='.', edgecolors='none', color='#C0C0C0', s=1)

        return

    def add_gridlines(self,
                      lat_res=None, lon_res=None,
                      lat_label_separator=None, lon_label_separator=None,
                      lat_label_format=None, lon_label_format=None,
                      lat_label=True, lat_label_clock=6.5, lat_label_config={},
                      lon_label=True, lon_label_config={},
                      gridlines_config={}):

        default_gridlines_label_config = {
            'lon-fixed': {
                'lat_res': 10.,
                'lon_res': 30.,
                'lat_label_separator': 0,
                'lon_label_separator': 0,
                'lat_label_format': '%d%D%N',
                'lon_label_format': '%d%D%E',
            },
            'mlon-fixed': {
                'lat_res': 10.,
                'lon_res': 30.,
                'lat_label_separator': 0,
                'lon_label_separator': 0,
                'lat_label_format': '%d%D%N',
                'lon_label_format': '%d%D%E',
            },
            'lst-fixed': {
                'lat_res': 10.,
                'lon_res': 15.,
                'lat_label_separator': 0,
                'lon_label_separator': 2,
                'lat_label_format': '%d%D%N',
                'lon_label_format': '%02d LT',
            },
            'mlt-fixed': {
                'lat_res': 10.,
                'lon_res': 15.,
                'lat_label_separator': 0,
                'lon_label_separator': 2,
                'lat_label_format': '%d%D%N',
                'lon_label_format': '%02d MLT',
            },
        }

        def label_formatter(value, fmt=''):
            ms = re.findall(r"(%[0-9]*[a-zA-Z])", fmt)
            fmt_new = copy.deepcopy(fmt)
            patterns = []
            if "%N" in ms:
                if value > 0:
                    lb_ns = 'N'
                elif value < 0:
                    lb_ns = 'S'
                else:
                    lb_ns = ''
                value = np.abs(value)

            if "%E" in ms:
                mod_value = np.mod(value - 180, 360) - 180.
                if mod_value == 0 or mod_value == 180:
                    lb_ew = ''
                elif mod_value < 0:
                    lb_ew = 'W'
                else:
                    lb_ew = 'E'
                value = np.abs(mod_value)

            for ind_m, m in enumerate(ms):
                if m == "%N":
                    fmt_new = fmt_new.replace(m, '{}')
                    patterns.append(lb_ns)
                elif m == "%E":
                    fmt_new = fmt_new.replace(m, '{}')
                    patterns.append(lb_ew)
                elif m == "%D":
                    continue
                else:
                    if 'd' in m:
                        value = int(value)
                    fmt_new = fmt_new.replace(m, '{:' + m[1:] + '}')
                    patterns.append(value)
            string_new = fmt_new.format(*patterns)
            if "%D" in string_new:
                splits = string_new.split("%D")
                string_new = splits[0] + r'$^{\circ}$' + splits[1]

            return string_new

        default_label_config = default_gridlines_label_config[self.style]
        if lat_res is None:
            lat_res = default_label_config['lat_res']
        if lon_res is None:
            lon_res = default_label_config['lon_res']
        if lat_label_separator is None:
            lat_label_separator = default_label_config['lat_label_separator']
        if lon_label_separator is None:
            lon_label_separator = default_label_config['lon_label_separator']
        if lat_label_format is None:
            lat_label_format = default_label_config['lat_label_format']
        if lon_label_format is None:
            lon_label_format = default_label_config['lon_label_format']

        # xlocator
        if self.style == 'lst-fixed':
            lon_shift = (self.ut - datetime.datetime(
                self.ut.year, self.ut.month, self.ut.day, self.ut.hour
            )).total_seconds() / 86400. * 360
        else:
            lon_shift = 0
        num_lons = 360. // lon_res + 1.
        lons = np.linspace(-180., 180., int(num_lons)) - lon_shift
        xlocator = mticker.FixedLocator(lons)

        # ylocator
        lat_fr = np.abs(self.boundary_lat) + np.mod(90 - np.abs(self.boundary_lat), lat_res)
        lat_to = 90.
        # num_lats = (lat_to - lat_fr) / lat_res + 1.
        lats = np.arange(lat_fr, lat_to, lat_res) * np.sign(self.lat_c)
        ylocator = mticker.FixedLocator(lats)

        pybasic.dict_set_default(gridlines_config, color='#331900', linewidth=0.5, linestyle=':',
                                     draw_labels=False)
        gl = self.major_ax.gridlines(crs=ccrs.PlateCarree(), **gridlines_config)

        gl.xlocator = xlocator
        gl.ylocator = ylocator

        if lat_label:
            pybasic.dict_set_default(lat_label_config, fontsize=plt.rcParams['font.size'] - 2, fontweight='roman',
                    ha='center', va='center',
                    family='fantasy', color='k', alpha=0.9
                )
            if self.pole == 'S':
                clock = lat_label_clock / 12 * 360
                rotation = 180 - clock
                if self.mirror_south:
                    clock = - clock
                    rotation = 180 + clock
            else:
                clock = np.mod(180. - lat_label_clock / 12 * 360, 360)
                rotation = clock
            label_lon = self.lon_c + clock
            for ind, lat in enumerate(lats):
                if np.mod(ind, lat_label_separator+1) != 0:
                    continue
                # if lat > 0:
                #     label = r'' + '{:d}'.format(int(lat)) + r'$^{\circ}$N'
                # elif lat < 0:
                #     label = r'' + '{:d}'.format(int(-lat)) + r'$^{\circ}$S'
                # else:
                #     label = r'' + '{:d}'.format(int(0)) + r'$^{\circ}$S'
                label = label_formatter(lat, fmt=lat_label_format)
                self.major_ax.text(
                    label_lon, lat, label, transform=ccrs.PlateCarree(),
                    rotation=rotation,
                    **lat_label_config
                )

        if lon_label:
            pybasic.dict_set_default(
                lon_label_config,
                va='center', ha='center',
                family='fantasy', fontweight='ultralight', color='k')
            lb_lons = np.arange(0, 360., lon_res)
            if self.pole == 'S':
                lon_shift_south = 180.
            else:
                lon_shift_south = 0
            if self.style == 'lon-fixed' or self.style == 'mlon-fixed':
                lb_lons_loc = lb_lons
            elif self.style == 'lst-fixed':
                lb_lons_loc = np.mod(self.lon_c + (lb_lons - self.lst_c / 24 * 360) + lon_shift_south, 360)
            elif self.style == 'mlt-fixed':
                lb_lons_loc = lb_lons

            if self.boundary_style == 'circle':
                lb_lats = np.empty_like(lb_lons)
                lb_lats[:] = self.boundary_lat
                data = self.proj.transform_points(ccrs.PlateCarree(), lb_lons_loc, lb_lats)
                xdata = data[:, 0]
                ydata = data[:, 1]
                scale = (self._extent[1] - self._extent[0]) * 0.03
                xdata = xdata + scale * np.sin((lb_lons_loc - self.lon_c) * np.pi / 180.)
                ydata = ydata - np.sign(self.lat_c) * scale * np.cos((lb_lons_loc - self.lon_c) * np.pi / 180.)
                for ind, lb_lon in enumerate(lb_lons):
                    if np.mod(ind, lon_label_separator+1) != 0:
                        continue
                    x = xdata[ind]
                    y = ydata[ind]
                    # if self.style in ['lon-fixed', 'mlon-fixed']:
                    #     lb_lon = np.mod(lb_lon + 180, 360) - 180
                    #     if lb_lon == 0 or np.abs(lb_lon) == 180.:
                    #         label = r'' + '{:d}'.format(int(np.abs(lb_lon))) + r'$^{\circ}$'
                    #     if lb_lon < 0:
                    #         label = r'' + '{:d}'.format(int(-lb_lon)) + r'$^{\circ}$W'
                    #     else:
                    #         label = r'' + '{:d}'.format(int(lb_lon)) + r'$^{\circ}$E'
                    # elif self.style == 'mlt-fixed':
                    #     label = '{:d}'.format(int(lb_lon / 15)) + ' MLT'
                    # elif self.style == 'lst-fixed':
                    #     label = '{:d}'.format(int(lb_lon / 15)) + ' LT'
                    if self.style in ['lon-fixed', 'mlon-fixed']:
                        lb_value = lb_lon
                    elif self.style in ['lst-fixed', 'mlt-fixed']:
                        lb_value = lb_lon / 15
                    label = label_formatter(lb_value, fmt=lon_label_format)
                    if self.pole == 'S':
                        rotation = self.lon_c - lb_lons_loc[ind]
                        if self.mirror_south:
                            rotation = -self.lon_c + lb_lons_loc[ind]
                    else:
                        rotation = (lb_lons_loc[ind] - self.lon_c) + 180
                    self.major_ax.text(
                        x, y, label,
                        rotation=rotation,
                        **lon_label_config,
                    )

        # gl.xformatter = LONGITUDE_FORMATTER()
        # gl.yformatter = LATITUDE_FORMATTER()
        # for ea in gl.label_artists:
        #     if ea[1]==False:
        #         tx = ea[2]
        #         xy = tx.get_position()
        #         #print(xy)
        #
        #         tx.set_position([30, xy[1]])

    def set_extent(self, boundary_lat=None, boundary_style=None):
        if boundary_lat is not None:
            self.boundary_lat = boundary_lat
        if boundary_style is not None:
            self.boundary_style = boundary_style
        x = np.array([270., 90., 180., 0.])
        y = np.ones(4) * self.boundary_lat
        x = np.arange(0., 360., 5.)
        y = np.empty_like(x)
        y[:] = 1. * self.boundary_lat
        data = self.proj.transform_points(ccrs.PlateCarree(), x, y)
        # self.axes.plot(x, y, '.', transform=ccrs.PlateCarree())
        ext = [np.nanmin(data[:, 0]), np.nanmax(data[:, 0]), np.nanmin(data[:, 1]), np.nanmax(data[:, 1])]
        self._extent = ext
        self.major_ax.set_extent(ext, self.proj)

        self._set_boundary_style()

        self._check_mirror_south()

    def _check_mirror_south(self):
        if self.pole == 'S' and self.mirror_south:
            xlim = self.major_ax.get_xlim()
            self.major_ax.set_xlim([max(xlim), min(xlim)])

    def _set_boundary_style(self):

        style = self.boundary_style
        if style == 'square':
            return
        elif style == 'circle':
            theta = np.linspace(0, 2 * np.pi, 400)
            center = self.proj.transform_point(self.lon_c, self.lat_c, ccrs.PlateCarree())
            radius = (self._extent[1] - self._extent[0]) / 2
            verts = np.vstack([np.sin(theta), np.cos(theta)]).T
            circle = mpath.Path(verts * radius + center)
            self.major_ax.set_boundary(circle, transform=self.proj)
        else:
            raise NotImplementedError

    def add_pcolor(self, data, coords=None, cs=None,
                   c_lim=None, c_scale='linear', c_label=None, **kwargs):

        if c_lim is None:
            c_lim = [np.nanmin(data.flatten()), np.nanmax(data.flatten())]

        if c_scale == 'log':
            norm = mcolors.LogNorm(vmin=c_lim[0], vmax=c_lim[1])
            kwargs.update(norm=norm)
        else:
            kwargs.update(vmin=c_lim[0])
            kwargs.update(vmax=c_lim[1])

        if cs != self.cs:
            from scipy.interpolate import griddata
            ind_data = np.where(np.isfinite(data))
            data_pts = data[ind_data]
            lat_pts = coords['lat'][ind_data]
            lon_pts = coords['lon'][ind_data]
            height = coords['height']
            cs_new = self.cs_transform(cs_fr=cs, coords={'lat': lat_pts, 'lon': lon_pts, 'height': height})

            grid_lat_res = kwargs.pop('grid_lat_res', 0.25)
            grid_lon_res = kwargs.pop('grid_lon_res', .5)
            grid_lon, grid_lat = np.meshgrid(
                np.arange(0., 360., grid_lon_res),
                np.append(np.arange(self.boundary_lat, self.lat_c, np.sign(self.lat_c) * grid_lat_res), self.lat_c)
            )

            grid_data = griddata((cs_new['lon'], cs_new['lat']), data_pts, (grid_lon, grid_lat), method='nearest')
            grid_data_lat = griddata(
                (cs_new['lon'], cs_new['lat']), cs_new['lat'], (grid_lon, grid_lat), method='nearest'
            )
            grid_data_lon = griddata(
                (cs_new['lon'], cs_new['lat']), cs_new['lon'], (grid_lon, grid_lat), method='nearest'
            )
            factor = np.pi / 180.
            big_circle_d = 6371. * np.arccos(
                np.sin(grid_data_lat * factor) * np.sin(grid_lat * factor) +
                np.cos(grid_data_lat * factor) * np.cos(grid_lat * factor) * np.cos((grid_lon - grid_data_lon) * factor)
            )
            grid_data = np.where(big_circle_d < 75., grid_data, np.nan)
            ipc = self.major_ax.pcolormesh(grid_lon, grid_lat, grid_data, transform=ccrs.PlateCarree(), **kwargs)
        else:
            cs_new = self.cs_transform(cs_fr=cs, coords=coords)
            ipc = self.major_ax.pcolormesh(cs_new['lon'], cs_new['lat'], data, transform=ccrs.PlateCarree(), **kwargs)

        # self.add_colorbar(im, ax=self.major_ax, figure=None, c_scale=c_scale, c_label=c_label,
        #              left=1.1, bottom=0.1, width=0.05, height=0.7
        #             )
        # self._check_mirror_south()
        return ipc

    def add_sc_trajectory(self, sc_lat, sc_lon, sc_alt, sc_dt=None, show_trajectory=True,
                          time_tick=False, time_tick_res=600., time_tick_scale=0.02,
                          time_tick_label=True, time_tick_label_format="%M:%H", time_tick_label_fontsize=8,
                          time_minor_tick=False, time_minor_tick_res=60, **kwargs):
        kwargs.setdefault('trajectory_config', {
            'linewidth': 1,
            'linestyle': '-',
            'color': 'k',
        })
        kwargs.setdefault('linewidth', 1)
        kwargs.setdefault('color', 'k')

        if self.pole == 'N':
            ind_lat = np.where(sc_lat > self.boundary_lat)[0]
        else:
            ind_lat = np.where(sc_lat < self.boundary_lat)[0]

        sc_lat = sc_lat.flatten()[ind_lat]
        sc_lon = sc_lon.flatten()[ind_lat]
        sc_alt = sc_alt.flatten()[ind_lat]
        sc_dt = sc_dt.flatten()[ind_lat]

        coords = {
            'lat': sc_lat,
            'lon': sc_lon,
            'height': sc_alt,
        }
        cs_new = self.cs_transform(cs_fr='GEO', coords=coords, ut=sc_dt)
        if show_trajectory:
            self.major_ax.plot(cs_new['lon'], cs_new['lat'], proj=ccrs.Geodetic(), **kwargs['trajectory_config'])

        if time_tick:
            data = self.proj.transform_points(ccrs.PlateCarree(), cs_new['lon'], cs_new['lat'])
            xdata = data[:, 0]
            ydata = data[:, 1]

            sectime, dt0 = dttool.convert_datetime_to_sectime(
                sc_dt, datetime.datetime(self.ut.year, self.ut.month, self.ut.day)
            )

            time_ticks = np.arange(np.floor(sectime[0] / time_tick_res) * time_tick_res,
                                   np.ceil(sectime[-1] / time_tick_res) * time_tick_res, time_tick_res)

            from scipy.interpolate import interp1d

            f = interp1d(sectime, xdata, fill_value='extrapolate')
            x_i = f(time_ticks)
            f = interp1d(sectime, ydata, fill_value='extrapolate')
            y_i = f(time_ticks)

            slope = mathtool.calc_curve_tangent_slope(xdata, ydata)
            l = np.empty_like(x_i)
            l[:] = (self._extent[1] - self._extent[0]) * time_tick_scale

            xq = x_i
            yq = y_i
            uq1 = - l * np.sin(slope)
            vq1 = l * np.cos(slope)

            self.major_ax.quiver(xq, yq, uq1, vq1, units='xy')

            uq2 = l * np.sin(slope)
            vq2 = - l * np.cos(slope)

            self.major_ax.quiver(xq, yq, uq2, vq2, units='xy')

            if time_tick_label:
                for ind, time_tick in enumerate(time_ticks):
                    time = dt0 + datetime.timedelta(seconds=time_tick)
                    x_time_tick = x_i[ind]
                    y_time_tick = y_i[ind]

                    self.major_ax.text(
                        x_time_tick + uq1[ind], y_time_tick + vq1[ind], time.strftime(time_tick_label_format),
                        fontsize=time_tick_label_fontsize,
                        rotation=slope[ind] * 180. / np.pi + 90.,
                        ha='left', va='middle'
                    )

            # self.major_ax.plot(x_time_ticks, y_time_ticks, **kwargs['time_tick_config'])

        if time_minor_tick:
            pass

    def add_sc_coloured_line(self, sc_lat, sc_lon, sc_alt, sc_data, sc_dt=None, label='', unit='', scale='linear',
                             vmin=None, vmax=None, colormap=None):
        from matplotlib.collections import LineCollection
        import matplotlib.colors as mpl_color

        if self.pole == 'N':
            ind_lat = np.where(sc_lat > self.boundary_lat)[0]
        else:
            ind_lat = np.where(sc_lat < self.boundary_lat)[0]

        sc_lat = sc_lat.flatten()[ind_lat]
        sc_lon = sc_lon.flatten()[ind_lat]
        sc_alt = sc_alt.flatten()[ind_lat]
        sc_data = sc_data.flatten()[ind_lat]
        sc_dt = sc_dt.flatten()[ind_lat]

        coords = {'lat': sc_lat, 'lon': sc_lon, 'height': sc_alt}
        cs_new = self.cs_transform(cs_fr='GEO', coords=coords)
        data = self.proj.transform_points(ccrs.PlateCarree(), cs_new['lon'], cs_new['lat'])
        x = data[:, 0]
        y = data[:, 1]
        z = sc_data.flatten()
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        if scale == 'linear':
            norm = mpl_color.LogNorm(vmin=vmin, vmax=vmax)
        elif scale == 'log':
            norm = mpl_color.Normalize(vmin, vmax)
        else:
            raise ValueError
        lc = LineCollection(segments, cmap=colormap, norm=norm)
        lc.set_array(z)
        lc.set_linewidth(6)
        im = self.major_ax.add_collection(lc)
        return im
        # clabel = label + ' (' + unit + ')'
        # self.add_colorbar(self.major_ax, line, cscale=scale, clabel=clabel)
        # cbar = plt.gcf().colorbar(line, ax=panel.major_ax, pad=0.1, fraction=0.03)
        # cbar.set_label(r'$n_e$' + '\n' + r'(cm$^{-3}$)', rotation=270, labelpad=25)

    def add_colorbar(self, im, ax=None, figure=None,
                     c_scale='linear', c_label=None,
                     c_ticks=None, c_tick_labels=None, c_tick_label_step=1,
                     left=1.1, bottom=0.1, width=0.05, height=0.7, **kwargs
                     ):
        if figure is None:
            figure = plt.gcf()
        pos = ax.get_position()
        ax_width = pos.x1 - pos.x0
        ax_height = pos.y1 - pos.y0
        ca_left = pos.x0 + ax_width * left
        ca_bottom = pos.y0 + ax_height * bottom
        ca_width = ax_width * width
        ca_height = ax_height * height
        cax = self.add_axes([ca_left, ca_bottom, ca_width, ca_height], major=False, label=c_label)
        cb = figure.colorbar(im, cax=cax, **kwargs)
        ylim = cax.get_ylim()

        cb.set_label(c_label, rotation=270, va='bottom', size='medium')
        if c_ticks is not None:
            cb.ax.yaxis.set_ticks(c_ticks)
            if c_tick_labels is not None:
                cb.ax.yaxis.set_ticklabels(c_tick_labels)
        else:
            if c_scale == 'log':
                num_major_ticks = int(np.ceil(np.diff(np.log10(ylim)))) * 2
                cax.yaxis.set_major_locator(mticker.LogLocator(base=10.0, numticks=num_major_ticks))
                n = c_tick_label_step
                [l.set_visible(False) for (i, l) in enumerate(cax.yaxis.get_ticklabels()) if i % n != 0]
                # [l.set_ha('right') for (i, l) in enumerate(cax.yaxis.get_ticklabels()) if i % n != 0]
                minorlocator = mticker.LogLocator(base=10.0, subs=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9),
                                                     numticks=12)
                cax.yaxis.set_minor_locator(minorlocator)
                cax.yaxis.set_minor_formatter(mticker.NullFormatter())
        cax.yaxis.set_tick_params(labelsize='x-small')
        return [cax, cb]

    @property
    def pole(self):
        return self._pole

    @pole.setter
    def pole(self, value):
        if value.upper() in ['N', 'NORTH', 'NORTHERN']:
            self._pole = 'N'
            self.lat_c = 90.
            self.boundary_lat = np.abs(self.boundary_lat)
        elif value.upper() in ['S', 'SOUTH', 'SOUTHERN']:
            self._pole = 'S'
            self.lat_c = -90.
            self.boundary_lat = - np.abs(self.boundary_lat)
        else:
            raise ValueError

    @property
    def lst_c(self):
        return self._lst_c

    @lst_c.setter
    def lst_c(self, lst):
        self._lst_c = lst
        if lst is None:
            return
        if self.pole == 'N':
            self.lon_c = np.mod((self.lst_c - (self.ut.hour + self.ut.minute / 60)) * 15., 360.)
        elif self.pole == 'S':
            self.lon_c = np.mod((self.lst_c - (self.ut.hour + self.ut.minute / 60)) * 15. + 180., 360.)

    @property
    def mlt_c(self):
        return self._mlt_c

    @mlt_c.setter
    def mlt_c(self, mlt):
        if mlt is not None:
            self.depend_mlt = True
            self.lon_c = self._transform_mlt_to_lon(mlt)
            if self.pole == 'S':
                self.lon_c = np.mod(self.lon_c + 180., 360)
            if self.cs == "GEO":
                raise AttributeError('A magnetic coordinate system must be specified (Set the attribute "cs")!')
        self._mlt_c = mlt


if __name__ == "__main__":
    test()
