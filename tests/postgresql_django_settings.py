import os

# Minimum files that are needed to run django test suite


SECRET_KEY = 'WE DONT CARE ABOUT IT'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_NAME', 'dirtyfields_test'),  # Should be the same defined in .travis.yml
        'USER': os.getenv('POSTGRES_USER', 'postgres'),  # postgres user is by default created in travis-ci
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),  # postgres user has no password on travis-ci
        'HOST': 'localhost',
        'PORT': '5432',  # default postgresql port
    }
}

INSTALLED_APPS = ('tests', )
