"""
Tests for the CLI tools
"""

import subprocess
import sys
import textwrap


def test_simple_script(tmpdir):
    ## Save the script in a temporary file
    script = textwrap.dedent("""\
    from clitools import CliApp

    cli = CliApp()

    @cli.command
    def hello(args):
        print "Hello, world!"

    @cli.command
    def command_example(args):
        print "Example"

    @cli.command
    @cli.parser_arg('--name')
    def hello2(args):
        print "Hello, {}!".format(args.name)

    @cli.command(args=[
        (('--arg1', ), {}),
        (('--arg2', ), {'action': 'append'}),
    ])
    def example2(args):
        if args.arg1:
            print args.arg1
        if args.arg2:
            print ' '.join(args.arg2)

    def akw(*a, **kw):
        return (a, kw)

    @cli.command(args=[
        akw('--arg1'),
        akw('--arg2', action='append'),
    ])
    def example3(args):
        if args.arg1:
            print args.arg1
        if args.arg2:
            print ' '.join(args.arg2)

    if __name__ == '__main__':
        cli.run_from_command_line()
    """)
    dest_file = str(tmpdir.join('myscript.py'))
    with open(dest_file, 'w') as f:
        f.write(script)

    def check_command(args, output="", returncode=0):
        proc = subprocess.Popen(
            [sys.executable, dest_file] + args,
            stdout=subprocess.PIPE)
        proc.wait()
        assert proc.returncode == returncode
        prog_output = proc.stdout.read()
        assert prog_output == output

    ## Check the program output
    check_command(['hello'], "Hello, world!\n")
    check_command(['hello2', '--name=spam'], "Hello, spam!\n")
    check_command(['hello2', '--name', 'egg'], "Hello, egg!\n")
    check_command(['example'], "Example\n")
    check_command(['example2'], "")
    check_command(['example2', '--arg1=Hello'], "Hello\n")
    check_command(['example2', '--arg1=Hello', '--arg1=World'],
                  "World\n")
    check_command(['example2', '--arg2=Hello', '--arg2=World'],
                  "Hello World\n")
    check_command(['example2', '--arg1=AAAA', '--arg2=Hello', '--arg2=World'],
                  "AAAA\nHello World\n")
    check_command(['example3', '--arg1=AAAA', '--arg2=Hello', '--arg2=World'],
                  "AAAA\nHello World\n")
