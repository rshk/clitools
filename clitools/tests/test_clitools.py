"""
Functional tests for the CLI tools
"""

from __future__ import print_function

import re
from functools import partial

import pytest

from clitools import CliApp


@pytest.fixture
def sample_script():

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
    def hello_list(name=[str]):
        for nm in name:
            print("Hello, {0}".format(nm))

    @cli.command
    def cmd_with_many_args(arg1, kw1='val1', kw2=123, kw3=False):
        assert isinstance(kw3, bool)
        print('arg1: {0!s}'.format(arg1))
        print('kw1: {0!s}'.format(kw1))
        print('kw2: {0!s}'.format(kw2))
        print('kw3: {0!s}'.format(kw3))

    @cli.command
    def cmd_with_explicit_args(aaa=cli.arg(default='spam'),
                               bbb=cli.arg(type=int, default=100),
                               ccc='example'):
        print('aaa: {0!s}'.format(aaa))
        print('bbb: {0!s}'.format(bbb))
        print('ccc: {0!s}'.format(ccc))

    @cli.command(name='custom_name')
    def command_with_custom_name():
        print('itworks')

    return cli


def gen_test_case(args, out=None, err=None, success=True):
    return (args, (out, err, success))


def match_pattern(pattern):
    def _match_pattern(pattern, s):
        return bool(re.match(pattern, s, re.DOTALL))
    return partial(_match_pattern, pattern)


def fuzzy_match(chunks):
    """Make sure text contains all chunks in the given order"""
    return match_pattern('.*'.join(re.escape(l) for l in chunks))


@pytest.mark.parametrize('args,result', [
    ## todo: we need to test that invocation without arguments
    ## prints the command help, instead of an exception traceback..
    gen_test_case(
        [],
        err=fuzzy_match([
            '', 'usage: cli-app [-h]',
            # 'cli-app: error: too few arguments',
            '',
        ]),
        success=False),  # no args -> invalid usage

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
        out=fuzzy_match([
            u'',
            u'usage: cli-app hello_optional_name [-h] [--name NAME]',
            u'optional arguments:',
            u'-h, --help', u'show this help message and exit',
            u'--name', u'NAME',
            u''
        ])),
    gen_test_case(['hello_optional_name'], out='Hello, world!\n'),
    gen_test_case(['hello_optional_name', '--name', 'Python'],
                  out='Hello, Python!\n'),

    gen_test_case(['hello_list'], out=''),
    gen_test_case(['hello_list', '--name', 'spam', '--name', 'eggs'],
                  out='Hello, spam\nHello, eggs\n'),

    gen_test_case(['cmd_with_many_args'], success=False),
    gen_test_case(
        ['cmd_with_many_args', 'hello'],
        out='arg1: hello\nkw1: val1\nkw2: 123\nkw3: False\n'),
    gen_test_case(
        ['cmd_with_many_args', 'hello', '--kw1', 'hello'],
        out='arg1: hello\nkw1: hello\nkw2: 123\nkw3: False\n'),
    gen_test_case(
        ['cmd_with_many_args', 'hello', '--kw2', 'not-an-int'],
        success=False),
    gen_test_case(
        ['cmd_with_many_args', 'hello', '--kw2', '1024', '--kw1', 'yay'],
        out='arg1: hello\nkw1: yay\nkw2: 1024\nkw3: False\n'),
    gen_test_case(
        ['cmd_with_many_args', 'hello', '--kw2', '1024', '--kw3'],
        out='arg1: hello\nkw1: val1\nkw2: 1024\nkw3: True\n'),

    gen_test_case(
        ['cmd_with_explicit_args'],
        out='aaa: spam\nbbb: 100\nccc: example\n'),
    gen_test_case(
        ['cmd_with_explicit_args', '--aaa=AAA', '--bbb', '123',
         '--ccc', 'foo'],
        out='aaa: AAA\nbbb: 123\nccc: foo\n'),
    gen_test_case(
        ['cmd_with_explicit_args', '--bbb', 'not-an-int'],
        success=False),

    gen_test_case(['custom_name'], out='itworks\n'),

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
        if callable(exp_out):
            assert exp_out(stdout)
        else:
            assert stdout == exp_out
    if exp_err is not None:
        if callable(exp_err):
            assert exp_err(stderr)
        else:
            assert stderr == exp_err


def test_make_sure_we_clean_default_args(sample_script, capsys):
    ## todo: we have more cleanup + tests to do!

    cli = CliApp()

    @cli.command
    def cmd_with_explicit_args(aaa=cli.arg(default='spam'),
                               bbb=cli.arg(type=int, default=100),
                               ccc='example'):
        print('aaa: {0}'.format(aaa))
        print('bbb: {0}'.format(bbb))
        print('ccc: {0}'.format(ccc))

    cli.run(['cmd_with_explicit_args', '--aaa=AAA'])
    out, err = capsys.readouterr()
    assert out == 'aaa: AAA\nbbb: 100\nccc: example\n'

    cmd_with_explicit_args()
    out, err = capsys.readouterr()
    assert out == 'aaa: spam\nbbb: 100\nccc: example\n'
