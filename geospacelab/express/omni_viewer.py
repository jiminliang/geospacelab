import datetime

from geospacelab.visualization.ts_viewer import TimeSeriesViewer


class OMNIViewer(TimeSeriesViewer):
    def __init__(self, dt_fr, dt_to, **kwargs):
        new_figure = kwargs.pop('new_figure', True)
        figure_config = kwargs.pop('figure_config', {'figsize': (10, 8)})
        super().__init__(dt_fr=dt_fr, dt_to=dt_to, new_figure=new_figure, figure_config=figure_config)
        omni_config = {
            'omni_type': kwargs.pop('omni_type', 'OMNI2'),
            'omni_res': kwargs.pop('omni_res', '1min'),
            'load_mode': kwargs.get('load_mode', 'AUTO'),
            'load_data': kwargs.get('load_data', True)
        }
        ds_1 = self.dock(datasource_contents=['cdaweb', 'omni'], **omni_config)
        ds_2 = self.dock(datasource_contents=['wdc', 'ae'], load_data=True, load_mode='AUTO')
        ds_2 = self.dock(datasource_contents=['wdc', 'asysym'])
        # ds_1.list_all_variables()
        self.title = kwargs.pop('title', ', '.join([ds_1.facility, ds_1.omni_res]))

    def list_all_variables(self):
        self.datasets[1].list_all_variables()
        self.datasets[2].list_all_variables()

    def save_figure(self, **kwargs):
        file_name = kwargs.pop('filename', self.title.replace(', ', '_'))
        super().save_figure(file_name=file_name, **kwargs)

    def add_title(self, **kwargs):
        title = kwargs.pop('title', self.title)
        super().add_title(x=0.5, y=1.06, title=title)

    def quicklook(self):
        Bx = self.assign_variable('B_x_GSM', dataset=self.datasets[1])
        By = self.assign_variable('B_y_GSM', dataset=self.datasets[1])
        Bz = self.assign_variable('B_z_GSM', dataset=self.datasets[1])

        n_p = self.assign_variable('n_p', dataset=self.datasets[1])
        v_sw = self.assign_variable('v_sw', dataset=self.datasets[1])
        p_dyn = self.assign_variable('p_dyn', dataset=self.datasets[1])

        au = self.assign_variable('AU', dataset=self.datasets[2])
        au.visual.axis[1].lim = [None, None]
        al = self.assign_variable('AL', dataset=self.datasets[2])

        sym_h = self.assign_variable('SYM_H', dataset=self.datasets[3])
        sym_h.visual.axis[1].lim = [None, None]
        sym_h.visual.axis[1].label = '@v.label'
        self.list_assigned_variables()
        self.list_datasets()

        layout = [[Bx, By, Bz], [v_sw], [n_p], [p_dyn], [au, al], [sym_h]]
        self.set_layout(panel_layouts=layout)
        # plt.style.use('dark_background')
        # dt_fr_1 = datetime.datetime.strptime('20201209' + '1300', '%Y%m%d%H%M')
        # dt_to_1 = datetime.datetime.strptime('20201210' + '1200', '%Y%m%d%H%M')

        self.draw()
        self.add_title()
        self.add_panel_labels()


def example():

    dt_fr = datetime.datetime.strptime('20210314' + '0600', '%Y%m%d%H%M')
    dt_to = datetime.datetime.strptime('20210320' + '0600', '%Y%m%d%H%M')

    omni_type = 'OMNI2'
    omni_res = '1min'
    load_mode = 'AUTO'
    viewer = OMNIViewer(
        dt_fr, dt_to, omni_type=omni_type, omni_res=omni_res, load_mode=load_mode
    )
    viewer.quicklook()

    # save figure
    # viewer.save_figure()
    # show on screen
    viewer.show()


if __name__ == '__main__':
    example()