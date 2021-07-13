import numpy as np

from geospacelab.datahub.__init_variable import Variable

import geospacelab.toolbox.utilities.pyclass as myclass
import geospacelab.toolbox.utilities.pybasic as mybasic


class DatasetBase(object):
    default_contents = ['database', 'facility', 'instrument']

    def __init__(self, **kwargs):
        self.name = kwargs.pop('name', None)
        self.category = kwargs.pop('category', None)
        self.mode = kwargs.pop('mode', 'temporary')
        self._variables = {}
        #self.config(**kwargs)

    def __setitem__(self, key, value):
        if not issubclass(value, Variable):
            raise TypeError
        self._variables[key] = value

    def __getitem__(self, key):
        return self._variables[key]

    def __delitem__(self, key):
        del self._variables[key]
        pass

    def config(self, **kwargs):
        append = kwargs.pop('append', True)
        logging = kwargs.pop('logging', False)
        myclass.set_object_attributes(self, **kwargs, append=append, logging=logging)

    def add_variable(self, variable, name=None):
        self[name] = variable

    def remove_variable(self, name):
        del self[name]

    def get_variable_names(self):
        return list(self._variables.keys())


#
#
# # BaseClass with the "set_attr" method
# class BaseClass(object):
#     def __init__(self, **kwargs):
#         self.name = kwargs.pop('name', None)
#         self.category = kwargs.pop('kind', None)
#         self.label = None
#
#     def label(self, fields=None, fields_ignore=None, separator='_', lowercase=True):
#         if fields_ignore is None:
#             fields_ignore = ['kind', 'note']
#         sublabels = []
#         if fields is None:
#             attrs = myclass.get_object_attributes(self)
#             for attr, value in attrs.items():
#                 if attr in fields_ignore:
#                     continue
#                 if not isinstance(attr, str):
#                     continue
#                 sublabels.append(value)
#         else:
#             for field in fields:
#                 sublabels.append(getattr(self, field))
#         label = mybasic.str_join(sublabels, separator=separator, lowercase=lowercase)
#         return label
#
#     def set_attr(self, **kwargs):
#         append = kwargs.pop('append', True)
#         logging = kwargs.pop('logging', False)
#         myclass.set_object_attributes(self, append=append, logging=logging, **kwargs)

#
# # Class Database
# class Database(BaseClass):
#     def __init__(self, name='temporary', kind='local', **kwargs):
#
#         super().__init__(name=name, kind=kind)
#         self.set_attr(logging=False, **kwargs)
#
#     def __str__(self):
#         return self.label()
#
#
# # Class Facility
# class Facility(BaseClass):
#     def __init__(self, name=None, category=None, **kwargs):
#         super().__init__(name=name, category=category)
#         self.set_attr(logging=False, **kwargs)
#
#     def __str__(self):
#         return self.label()
#
#
# # Class Instrument
# class Instrument(BaseClass):
#     def __init__(self, name=None, category=None, **kwargs):
#         super().__init__(name=name, category=category)
#         self.set_attr(logging=False, **kwargs)
#
#     def __str__(self):
#         return self.label()
#
#
# # Class Experiment
# class Experiment(BaseClass):
#     def __init__(self, name=None, category=None, **kwargs):
#         super().__init__(name=name, category=category)
#         self.set_attr(logging=False, **kwargs)
#
#     def __str__(self):
#         return self.label()
#
#
# # create the Dataset class
# class Dataset(object):
#     def __init__(self, **kwargs):
#         self.dataDir_root = kwargs.pop('dataDir_root', None)
#         self.dt_fr = kwargs.pop('dt_fr', None)
#         self.dt_to = kwargs.pop('dt_to', None)
#         database_config = kwargs.pop('database_config', {})
#         self.database = kwargs.pop('sources', Database(**database_config))
#         facility_config = kwargs.pop('facility_config', {})
#         self.facility = kwargs.pop('facility', Facility(**facility_config))
#         instrument_config = kwargs.pop('instrument_config', {})
#         self.instrument = kwargs.pop('instrument_opt', Instrument(**instrument_config))
#         experiment_config = kwargs.pop('experiment_config', {})
#         self.experiment = kwargs.pop('experiment', Experiment(**experiment_config))
#         self._variables = {}
#
#     def __getitem__(self, key):
#         return self._variables[key]
#
#     def __setitem__(self, key, value, var_class=Variable):
#         if issubclass(value.__class__, var_class):
#             self._variables[key] = value
#         elif isinstance(value, np.ndarray):
#             self._variables[key] = var_class(name=key, database=self)
#         else:
#             raise TypeError("Variable must be an instance of Geospace Variable or numpy ndarray!")
#
#     def add_variable(self, arr, **kwargs):
#
#         var_name = kwargs.get('name')
#         variable = Variable(arr, **kwargs)
#
#         self.__setitem__(var_name, variable)
#
#     def assign_data(self, Loader, loader_config=None):
#         load_obj = Loader(**loader_config)
#         self.variables
#
#     def label(self):
#         pass
#
#     def __str__(self):
#         return self.label()