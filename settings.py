from django.conf import settings

DEBUG = False
try:
    from local_settings import *
    INSTALLED_APPS += ('listutil',)
except ImportError:
    pass

