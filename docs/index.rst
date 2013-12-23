.. clitools documentation master file, created by
   sphinx-quickstart on Mon Dec 23 17:43:35 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to clitools's documentation!
====================================

Intro
-----

CliTools is a small library that helps in the task of creating
CLI utilities with many sub-commands (think for example of commands
like ``git``).

It is based on ``argparse`` (for Python < 2.7 the contributed ``argparse``
module is automatically added to dependencies; in >=2.7 it is in the
standard library).


How does it work?
-----------------

- The ``CliApp()`` instance contains am ``argparse.ArgumentParser`` object,
  a subparser object and a register for commands.
- New commands are added through a decorator
- Script execution is wrapped by running the ``.run()`` method.


Contents
--------

.. toctree::
   :maxdepth: 2

   usage


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

