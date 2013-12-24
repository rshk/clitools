#!/usr/bin/env python

from __future__ import print_function

from clitools import CliApp


cli = CliApp()


@cli.command
def hello(name='world', bye=False):
    greet = 'Bye' if bye else 'Hello'
    print("{0}, {1}".format(greet, name))


if __name__ == '__main__':
    cli.run()
