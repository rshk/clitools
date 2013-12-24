#!/usr/bin/env python

## New generation example script

from __future__ import print_function

from clitools import CliApp


cli = CliApp()


@cli.command
def simple_command():
    print("Hello, world")


@cli.command
def hello(name='world'):
    print("Hello, {0}".format(name))


if __name__ == '__main__':
    cli.run()
