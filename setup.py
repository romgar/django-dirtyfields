from setuptools import setup, find_packages


def listify(filename):
    with open(filename, 'r') as f:
        return list(filter(None, f.read().splitlines(keepends=False)))


setup(
    name="django-dirtyfields",
    version="1.3.1",
    url='http://github.com/romgar/django-dirtyfields',
    license='BSD',
    description=("Tracking dirty fields on a Django model instance "
                 "(actively maintained)"),
    long_description=open('README.rst', 'r').read(),
    author='Romain Garrigues',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=listify('requirements.txt'),
    classifiers=listify('CLASSIFIERS.txt')
)
