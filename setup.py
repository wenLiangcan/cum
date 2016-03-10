from setuptools import find_packages, setup
import sys


class PythonVersionException(Exception):
    __module__ = Exception.__module__

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)

if sys.version_info[0] < 3:
    raise PythonVersionException('Python 3.x required.')

setup(
    name='cum',
    version='0.4',
    packages=find_packages(),
    py_modules=['cum'],
    install_requires=[
        'alembic',
        'beautifulsoup4',
        'Click',
        'natsort',
        'requests',
        'SQLAlchemy',
        'snownlp'
    ],
    entry_points='''
        [console_scripts]
        cum=cum.cum:cli
    ''',
)
