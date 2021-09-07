import datetime
import matplotlib.pyplot as plt

import geospacelab.visualization.map_proj.geomap_viewer as geomap


def test_ssusi():
    dt_fr = datetime.datetime(2015, 10, 13, 0)
    dt_to = datetime.datetime(2015, 10, 13, 23, 59)
    time1 = datetime.datetime(2015, 10, 13, 13, 32)
    pole = 'S'
    sat_id = 'f16'
    band = 'LBHS'

    viewer = geomap.GeoMapViewer(dt_fr=dt_fr, dt_to=dt_to, figure_config={'figsize': (5, 5)})

    # viewer.dock(datasource_contents=['jhuapl', 'dmsp', 'ssusi', 'edraur'], pole='N', sat_id='f17', orbit_id='46863')
    viewer.dock(datasource_contents=['jhuapl', 'dmsp', 'ssusi', 'edraur'], pole=pole, sat_id=sat_id, orbit_id=None)
    viewer.set_layout(1, 1)

    lbhs = viewer.assign_variable('GRID_AUR_' + band, dataset_index=1)
    dts = viewer.assign_variable('DATETIME', dataset_index=1).value.flatten()
    mlat = viewer.assign_variable('GRID_MLAT', dataset_index=1).value
    mlon = viewer.assign_variable('GRID_MLON', dataset_index=1).value
    mlt = viewer.assign_variable(('GRID_MLT'), dataset_index=1).value

    ind_t = viewer.datasets[1].get_time_ind(ut=time1)

    pid = viewer.add_polar_map(row_ind=0, col_ind=0, style='mlt-fixed', cs='AACGM', mlt_c=0., pole=pole, ut=time1, boundary_lat=65., mirror_south=True)
    # pid = viewer.add_polar_map(row_ind=0, col_ind=0, style='mlt-fixed', cs='AACGM', mlt_c=0., pole=pole, ut=time1, mirror_south=True)
    # pid = viewer.add_polar_map(row_ind=0, col_ind=0, style='lst-fixed', cs='GEO', lst_c=3., pole='N', ut=time1)
    # pid = viewer.add_polar_map(row_ind=0, col_ind=0, style='lst-fixed', cs='GEO', lst_c=0, pole='S', ut=time1, mirror_south=True)
    # pid = viewer.add_polar_map(row_ind=0, col_ind=0, style='lon-fixed', cs='GEO', lon_c=0., pole='S', ut=time1,
    #                           boundary_lat=0, mirror_south=False)
    # pid = viewer.add_polar_map(row_ind=0, col_ind=0, style='lon-fixed', cs='GEO', lon_c=0., pole='N', ut=time1,
    #                          boundary_lat=0, mirror_south=False)
    panel1 = viewer.panels[pid]
    panel1.add_coastlines()
    panel1.add_gridlines(lat_res=5, lon_label_separator=5)

    lbhs_ = lbhs.value[ind_t, :, :]
    pcolormesh_config = lbhs.visual.plot_config.pcolormesh
    pcolormesh_config.update(c_scale='log')
    pcolormesh_config.update(c_lim=[100, 2000])
    import geospacelab.visualization.mpl.colormaps as cm
    pcolormesh_config.update(cmap=cm.cmap_jhuapl_ssj_like())
    ipc = panel1.add_pcolor(lbhs_, coords={'lat': mlat[ind_t, ::], 'lon': mlon[ind_t, ::], 'mlt': mlt[ind_t, ::], 'height': 250.}, cs='AACGM', **pcolormesh_config)
    panel1.add_colorbar(
       ipc, ax=panel1.major_ax, c_label=band + " (R)", c_scale=pcolormesh_config['c_scale'],
       left=1.1, bottom=0.1, width=0.05, height=0.7
    )

    polestr = 'North' if pole == 'N' else 'South'
    panel1.add_title('DMSP/SSUSI, ' + band + ', ' + sat_id.upper() + ', ' + polestr + ', ' + time1.strftime('%Y-%m-%d %H%M UT'), pad=20)
    plt.savefig('DMSP_SSUSI_' + band + '_' + sat_id.upper() + '_' + pole + '_' + time1.strftime('%Y%m%d-%H%M'), dpi=300)
    plt.show()


if __name__ == "__main__":
    test_ssusi()
