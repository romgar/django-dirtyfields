from setuptools import setup, find_packages

setup(
    name = "django-dirtyfields",
    version = "0.1",
    url = 'http://github.com/smn/django-dirtyfields',
    license = 'BSD',
    description = "Tracking dirty fields on a Django model instance",
    author = 'Simon de Haan',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = ['django',],
)

