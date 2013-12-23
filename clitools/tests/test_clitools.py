"""
Tests for the CLI tools
"""

from __future__ import print_function

from io import BytesIO
# import subprocess
# import sys
# import textwrap

import pytest
from mock import patch


@pytest.fixture
def sample_script():
    from clitools import CliApp

    cli = CliApp()

    @cli.command
    def hello():
        print("Hello, world!")

    @cli.command
    def command_example():
        print("Example text")

    @cli.command
    def hello_required_name(name):
        print("Hello, {0}!".format(name))

    @cli.command
    def hello_optional_name(name='world'):
        print("Hello, {0}!".format(name))

    @cli.command
    def hello_list(names=[str]):
        print('\n'.join('Hello, {0}'.format(name) for name in names))

    return cli


def gen_test_case(args, out=None, err=None, success=True):
    return (args, (out, err, success))


@pytest.mark.parametrize('args,result', [
    gen_test_case(['hello'], out='Hello, world!\n'),

    gen_test_case(['example'], out='Example text\n'),

    gen_test_case(['hello_required_name'], success=False),
    gen_test_case(['hello_required_name', 'world'], out='Hello, world!\n'),
    gen_test_case(['hello_required_name', 'world', 'garbage'], success=False),

    gen_test_case(['non_existent_command'], success=False),
])
def test_simple_script_internal(sample_script, args, result):
    out, err, success = result

    dummy_stdout = BytesIO()
    dummy_stderr = BytesIO()

    with patch('sys.stdout', dummy_stdout), \
            patch('sys.stderr', dummy_stderr):

        return_code = 0
        try:
            sample_script.run(args)

        except SystemExit, e:
            return_code = e.code

        if out is not None:
            assert dummy_stdout.getvalue() == out
        if err is not None:
            assert dummy_stderr.getvalue() == err
        if success:
            assert return_code == 0
        else:
            assert return_code != 0
