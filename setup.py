import sys
from pkg_resources import normalize_path
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

version = '0.4a1'  # sync with clitools.__version__ !

install_requires = []

if sys.version_info < (2, 7):
    ## In Python <2.7 argparse is not in standard library
    install_requires.append('argparse')

tests_require = [
    'pytest',
    'pytest-pep8',
    'pytest-cov',
]

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = [
            '--ignore=build',
            '--cov=clitools',
            '--cov-report=term-missing',
            '--pep8',
            'clitools']
        self.test_suite = True

    def run_tests(self):
        from pkg_resources import _namespace_packages
        import pytest

        # Purge modules under test from sys.modules. The test loader will
        # re-import them from the build location. Required when 2to3 is used
        # with namespace packages.
        if sys.version_info >= (3,) and \
                getattr(self.distribution, 'use_2to3', False):
            module = self.test_args[-1].split('.')[0]
            if module in _namespace_packages:
                del_modules = []
                if module in sys.modules:
                    del_modules.append(module)
                module += '.'
                for name in sys.modules:
                    if name.startswith(module):
                        del_modules.append(name)
                map(sys.modules.__delitem__, del_modules)

            ## Run on the build directory for 2to3-built code..
            ei_cmd = self.get_finalized_command("egg_info")
            self.test_args = [normalize_path(ei_cmd.egg_base)]

        errno = pytest.main(self.test_args)
        sys.exit(errno)

long_description = """\
Example usage
=============

You can create your CLI script like this:

.. code-block:: python

    from clitools import CliApp

    cli = CliApp()


    @cli.command
    def hello(name='world', bye=False):
        greet = 'Bye' if bye else 'Hello'
        print("{0}, {1}".format(greet, name))


    if __name__ == '__main__':
        cli.run()


and then run it right away!

::

    % python sample_app.py
    usage: cli-app [-h] {hello} ...
    cli-app: error: too few arguments
    >>> exited 2

    % python sample_app.py --help
    usage: cli-app [-h] {hello} ...

    positional arguments:
      {hello}     sub-commands
        hello

    optional arguments:
      -h, --help  show this help message and exit

    % python sample_app.py hello
    Hello, world

    % python sample_app.py hello --name=Python
    Hello, Python

    % python sample_app.py hello --help
    usage: cli-app hello [-h] [--bye] [--name NAME]

    optional arguments:
      -h, --help   show this help message and exit
      --bye
      --name NAME

    % python sample_app.py hello --bye --name=Spam
    Bye, Spam

..super-cool, isn't it?


What's the difference with other libraries, such as Cliff?
==========================================================

Cliff_ is meant for building complex, fully-featured CLI applications.
CliTools just acts as a "bridge" to quickly expose a Python
function as a script in the "most obvious" way, without need for extensibility
or support for more complex use cases.

The main goal is to provide something you can quickly use without having to
continuously refer to the documentation :)

.. _Cliff: https://cliff.readthedocs.org/

"""

setup(
    name='CliTools',
    version=version,
    packages=find_packages(),
    url='http://rshk.github.io/clitools',
    license='BSD License',
    author='Samuele Santi',
    author_email='samuele@samuelesanti.com',
    description='Utilities for building CLI scripts in Python',
    long_description=long_description,
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='clitools.tests',
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    package_data={'': ['README.md', 'LICENSE']},
    cmdclass={'test': PyTest},
    **extra)
