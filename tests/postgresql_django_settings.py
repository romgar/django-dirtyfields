# Minimum files that are needed to run django test suite

SECRET_KEY = 'WE DONT CARE ABOUT IT'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'xxx',                      # Or path to database file if using sqlite3.
        'USER': 'xxx',                      # Not used with sqlite3.
        'PASSWORD': 'xxx',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5432',                      # Set to empty string for default. Not used with sqlite3.
    }
}

INSTALLED_APPS = ('tests', )
