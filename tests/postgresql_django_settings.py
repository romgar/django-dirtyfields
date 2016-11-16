# Minimum files that are needed to run django test suite

SECRET_KEY = 'WE DONT CARE ABOUT IT'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'dirtyfields_test',  # Should be the same defined in .travis.yml
        'USER': 'postgres',  # postgres user is by default created in travis-ci
        'PASSWORD': '',  # postgres user has no password on travis-ci
        'HOST': 'localhost',
        'PORT': '5432',  # default postgresql port
    }
}

INSTALLED_APPS = ('tests', )
