"""
CLI Tools - Command Line Interface building tools

Example usage::

    cli = CliApp()

    @cli.command
    def hello(args):
        print "Hello, world!"

    @cli.command(args=['--name'])
    def hello2(args):
        print "Hello, {}!".format(args.name)
"""

import argparse


class CliApp(object):
    def __init__(self, prog_name='cli-app'):
        self.prog_name = prog_name
        self.parser = argparse.ArgumentParser(prog=prog_name)
        self.subparsers = self.parser.add_subparsers(help='sub-commands')

    def command(self, func=None, args=None):
        """Decorator used to mark a function as a new sub-command"""
        def wrapped(func):
            cmd_name = func.__name__

            ## Strip the ``command_`` prefix from name
            if cmd_name.startswith('command_'):
                cmd_name = cmd_name[len('command_'):]

            ## Prepare the sub-parser and add arguments
            subparser = self.subparsers.add_parser(cmd_name)
            subparser.set_defaults(func=func)
            if args is not None:
                for a, kw in args:
                    subparser.add_argument(*a, **kw)
            if hasattr(func, '_parser_args'):
                ## We reverse it to keep the ordering in the
                ## decorators..
                for a, kw in reversed(func._parser_args):
                    subparser.add_argument(*a, **kw)
        if func is None:
            return wrapped
        return wrapped(func)

    def parser_arg(self, *a, **kw):
        """Decorator to add a parser argument to a given command"""
        def wrapped(fun):
            if not hasattr(fun, '_parser_args'):
                fun._parser_args = []
            fun._parser_args.append((a, kw))
            return fun
        return wrapped

    def run_from_command_line(self, args=None):
        """Handle running from the command line"""
        args = self.parser.parse_args(args)
        args.func(args)
