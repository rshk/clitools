"""
Functional tests for the CLI tools
"""

from __future__ import print_function

import pytest


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
    gen_test_case([], success=False),  # no args -> invalid usage
    gen_test_case(['--help'], success=True),  # --help is ok
    gen_test_case(['help'], success=False),  # does not exist by default

    gen_test_case(['hello'], out='Hello, world!\n'),
    gen_test_case(['hello', 'garbage'], success=False),

    gen_test_case(['example'], out='Example text\n'),

    gen_test_case(['hello_required_name', 'world'], out='Hello, world!\n'),
    gen_test_case(['hello_required_name'], success=False),
    gen_test_case(['hello_required_name', 'world', 'garbage'],
                  success=False),
    gen_test_case(['hello_required_name', 'world', '--garbage'],
                  success=False),
    gen_test_case(['hello_required_name', '--help'],
                  success=True),

    gen_test_case(
        ['hello_optional_name', '--help'],
        out=u'usage: cli-app hello_optional_name [-h] [--name NAME]\n\n'
        'optional arguments:\n'
        '  -h, --help   show this help message and exit\n'
        '  --name NAME\n'),
    gen_test_case(['hello_optional_name'], out='Hello, world!\n'),
    gen_test_case(['hello_optional_name', '--name', 'Python'],
                  out='Hello, Python!\n'),

    gen_test_case(['non_existent_command'], success=False),
])
def test_simple_script_internal(sample_script, args, result, capsys):
    exp_out, exp_err, exp_success = result

    return_code = 0
    try:
        sample_script.run(args)

    except SystemExit, e:
        ## Record exit code on failure
        return_code = e.code

    stdout, stderr = capsys.readouterr()

    if exp_success:
        assert return_code == 0
    else:
        assert return_code != 0

    if exp_out is not None:
        assert stdout == exp_out
    if exp_err is not None:
        assert stderr == exp_err
