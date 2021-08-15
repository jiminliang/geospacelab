from geospacelab import preferences
import geospacelab.datahub.sources.madrigal.utilities as utilities

from geospacelab.datahub import DatabaseModel


class MadrigalDatabase(DatabaseModel):
    def __new__(cls, str_in, **kwargs):
        obj = super().__new__(cls, str_in, **kwargs)
        return obj


madrigal_database = MadrigalDatabase('Madrigal')
madrigal_database.url = 'http://cedar.openmadrigal.org/'
madrigal_database.category = 'online database'


try:
    default_user_fullname = preferences.user_config['datahub']['madrigal']['user_fullname']
    default_user_email = preferences.user_config['datahub']['madrigal']['user_email']
    default_user_affiliation = preferences.user_config['datahub']['madrigal']['user_email']
except KeyError:
    print("Inputs for accessing the Madrigal database.")
    default_user_fullname = input("User's full name: ")
    default_user_email = input("User's email: ")
    default_user_affiliation = input("User's affiliation: ")
    save = input("Save as default? [y]/n: ")
    if save.lower() in ['', 'y', 'yes']:
        uc = preferences.user_config
        uc.setdefault('datahub', {})
        uc['datahub'].setdefault('madrigal', {})
        uc['datahub']['madrigal']['user_fullname'] = default_user_fullname
        uc['datahub']['madrigal']['user_email'] = default_user_email
        uc['datahub']['madrigal']['user_affiliation'] = default_user_affiliation
        preferences.set_user_config(user_config=uc, set_as_default=True)


