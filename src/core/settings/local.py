"""Development settings and globals."""
from unipath import Path  # Avoid pyflakes complains

import warnings

from base import *  # noqa
from base import INSTALLED_APPS, MIDDLEWARE_CLASSES  # Avoid pyflake complains

# ######### DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG
# ######### END DEBUG CONFIGURATION

# Third party templates are cached.
TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.app_directories.Loader',
    ]),
    'django.template.loaders.filesystem.Loader',
)


# ######### EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
SEND_EMAIL_REMINDERS = True
SEND_NEW_ACCOUNTS_EMAILS = True
# ######### END EMAIL CONFIGURATION


# ######### DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'phase',
        'USER': 'phase',
        'PASSWORD': 'phase',
        'HOST': 'localhost',
        'PORT': '',
    }
}
# ######### END DATABASE CONFIGURATION


# ######### CACHE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
# ######### END CACHE CONFIGURATION


# ######### TOOLBAR CONFIGURATION
# See: https://github.com/django-debug-toolbar/django-debug-toolbar#installation
INSTALLED_APPS += (
    'debug_toolbar',
)

# See: https://github.com/django-debug-toolbar/django-debug-toolbar#installation
INTERNAL_IPS = ('127.0.0.1',)

# See: https://github.com/django-debug-toolbar/django-debug-toolbar#installation
MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

DEBUG_TOOLBAR_CONFIG = {
}
# ######### END TOOLBAR CONFIGURATION

warnings.filterwarnings(
    'error', r"DateTimeField .* received a naive datetime",
    RuntimeWarning, r'django\.db\.models\.fields')

# ######### TRANSMITTALS IMPORT CONFIGURATION

TRS_IMPORTS_ROOT = Path('/tmp/dummy_ctr')

TRS_IMPORTS_CONFIG = {
    'dummy_ctr': {
        'INCOMING_DIR': TRS_IMPORTS_ROOT.child('incoming'),
        'REJECTED_DIR': TRS_IMPORTS_ROOT.child('rejected'),
        'TO_BE_CHECKED_DIR': TRS_IMPORTS_ROOT.child('tobechecked'),
        'ACCEPTED_DIR': TRS_IMPORTS_ROOT.child('accepted'),
        'EMAIL_LIST': ['test@localhost'],
    }
}

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
