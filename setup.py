from setuptools import setup, find_packages

def listify(filename):
    return [line for line in open(filename, 'r').read().split('\n') if line]

setup(
    name = "django-dirtyfields",
    version = "0.7",
    url = 'http://github.com/smn/django-dirtyfields',
    license = 'BSD',
    description = "Tracking dirty fields on a Django model instance (actively maintained)",
    long_description = open('README.rst','r').read(),
    author = 'Simon de Haan',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = listify('requirements.txt'),
    classifiers = listify('CLASSIFIERS.txt')
)

