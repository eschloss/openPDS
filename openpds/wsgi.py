"""
WSGI config for openPDS project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
import os
import site
import sys
#import djcelery
import django.conf

#activate_this = os.path.expanduser("/Users/ericschlossberg/Dropbox/Documents/workspace/liversmart/pdsEnv/bin/activate_this.py")
#execfile(activate_this, dict(__file__=activate_this))

#djcelery.setup_loader()
django.conf.ENVIRONMENT_VARIABLE = "DJANGO_PDS_SETTINGS_MODULE"
sys.path.append('/Users/ericschlossberg/Dropbox/Documents/workspace/liversmart/pdsEnv/openPDS')
os.environ.setdefault("DJANGO_PDS_SETTINGS_MODULE", "openpds.settings")

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise
application = get_wsgi_application()
application = DjangoWhiteNoise(application)

# Fix django closing connection to MemCached after every request (#11331)
from django.core.cache.backends.memcached import BaseMemcachedCache
BaseMemcachedCache.close = lambda self, **kwargs: None