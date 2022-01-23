# Minimum settings that are needed to run django test suite
import os
import secrets
import tempfile

USE_TZ = True
SECRET_KEY = secrets.token_hex()

if "postgresql" in os.getenv("TOX_ENV_NAME", "") or os.getenv("TEST_DATABASE") == "postgres":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'dirtyfields_test',
            'USER': os.getenv('POSTGRES_USER', 'postgres'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'postgres'),
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

MEDIA_ROOT = tempfile.mkdtemp(prefix="django-dirtyfields-test-media-root-")
