# Minimum settings that are needed to run django test suite
import os

SECRET_KEY = 'WE DONT CARE ABOUT IT'

if "postgresql" in os.getenv("TOX_ENV_NAME", ""):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            # Should be the same defined in .travis.yml
            'NAME': 'dirtyfields_test',
            # postgres user is by default created in travis-ci
            'USER': os.getenv('POSTGRES_USER', 'postgres'),
            # postgres user has no password on travis-ci
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
            'HOST': 'localhost',
            'PORT': '5432',  # default postgresql port
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'dirtyfields.db',
        }
    }

INSTALLED_APPS = ('tests', )
