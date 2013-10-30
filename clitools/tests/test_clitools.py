"""
Tests for the CLI tools
"""

from __future__ import print_function

from io import BytesIO
import subprocess
import sys
import textwrap

import pytest
from mock import patch


@pytest.fixture
def sample_script():
    from clitools import CliApp

    cli = CliApp()

    ## Used to check simple functionality
    @cli.command
    def hello(args):
        print("Hello, world!")

    ## Used to check removal of the 'command_' prefix
    @cli.command
    def command_example(args):
        print("Example")

    ## Used to test arguments
    @cli.command
    @cli.parser_arg('--name')
    def hello_arg_old(args):
        print("Hello, {0}!".format(args.name))

    ## Used to test arguments (new style)
    @cli.command
    @cli.arg('--name')
    def hello_arg(args):
        print("Hello, {0}!".format(args.name))

    ## Used to test arguments, alternate way
    @cli.command(args=[
        (('--arg1', ), {}),
        (('--arg2', ), {'action': 'append'}),
    ])
    def hello_arg_ugly(args):
        if args.arg1:
            print(args.arg1)
        if args.arg2:
            print(' '.join(args.arg2))

    def akw(*a, **kw):
        return (a, kw)

    ## Used to test arguments, alternate way with helper function
    @cli.command(args=[
        akw('--arg1'),
        akw('--arg2', action='append'),
    ])
    def hello_arg_ugly2(args):
        if args.arg1:
            print(args.arg1)
        if args.arg2:
            print(' '.join(args.arg2))

    @cli.command
    @cli.arg('--name')
    @cli.flag('--bye')
    def hello_name_new(args):
        if not args.bye:
            print("Hello, {0}".format(args.name))
        else:
            print("Bye, {0}".format(args.name))

    @cli.command
    @cli.arg('--name')
    @cli.flag('--no-bye', default=True)
    def hello_name_new_invert(args):
        if args.no_bye:  # The logic is inverted!!
            print("Hello, {0}".format(args.name))
        else:
            print("Bye, {0}".format(args.name))

    return cli


def test_simple_script_internal(sample_script):
    pairs = [
        (['hello'], b"Hello, world!\n"),

        (['example'], b"Example\n"),

        (['hello_arg_old', '--name=spam'], b"Hello, spam!\n"),
        (['hello_arg_old', '--name', 'egg'], b"Hello, egg!\n"),

        (['hello_arg', '--name=spam'], b"Hello, spam!\n"),
        (['hello_arg', '--name', 'egg'], b"Hello, egg!\n"),

        (['hello_arg_ugly', '--arg1=A1'], b"A1\n"),
        (['hello_arg_ugly', '--arg1=A1', '--arg2=B1'], b"A1\nB1\n"),
        (['hello_arg_ugly', '--arg1=A1', '--arg1=A2',
          '--arg2=B1', '--arg2=B2'],
         b"A2\nB1 B2\n"),

        (['hello_arg_ugly2', '--arg1=A1'], b"A1\n"),
        (['hello_arg_ugly2', '--arg1=A1', '--arg2=B1'], b"A1\nB1\n"),
        (['hello_arg_ugly2', '--arg1=A1', '--arg1=A2',
          '--arg2=B1', '--arg2=B2'],
         b"A2\nB1 B2\n"),

        (['hello_name_new', '--name=world'], b'Hello, world\n'),
        (['hello_name_new', '--name=world', '--bye'], b'Bye, world\n'),

        (['hello_name_new_invert', '--name=world'], b'Hello, world\n'),
        (['hello_name_new_invert', '--name=world', '--no-bye'],
         b'Bye, world\n'),
    ]

    for args, expected in pairs:
        dummy_output = BytesIO()
        with patch('sys.stdout', dummy_output):
            sample_script.run(args)
            assert dummy_output.getvalue() == expected
