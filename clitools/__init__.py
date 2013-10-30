"""
CLI Tools - Command Line Interface building tools

Example usage::

    from clitools import CliApp

    cli = CliApp()

    @cli.command
    def hello(args):
        print("Hello, world!")

    @cli.command
    @cli.parser_arg('--name')
    def hello2(args):
        print("Hello, {0}!".format(args.name))

    if __name__ == '__main__':
        cli.run_from_command_line()
"""

import argparse


class Command(object):
    def __init__(self, func):
        self.func = func
        self.parser_args = []

    def __call__(self, *a, **kw):
        return self.func(*a, **kw)

    def __getattr__(self, name):
        return getattr(self.func, name)

    @property
    def command_name(self):
        name = self.func.__name__
        if name.startswith('command_'):
            name = name[len('command_'):]
        return name


class CliApp(object):
    def __init__(self, prog_name='cli-app'):
        self.prog_name = prog_name
        self.parser = argparse.ArgumentParser(prog=prog_name)
        self.subparsers = self.parser.add_subparsers(help='sub-commands')

    def _wrap_func(self, func):
        """Make sure the function is wrapped in a Command object"""
        if not isinstance(func, Command):
            func = Command(func)
        return func

    def command(self, func=None, args=None):
        """
        Decorator used to register a function as a new sub-command
        """

        def wrapped(func):
            func = self._wrap_func(func)

            ## Prepare the sub-parser and add arguments
            subparser = self.subparsers.add_parser(func.command_name)
            subparser.set_defaults(func=func)

            if args is not None:
                func.parser_args.extend(args)

            ## Add arguments to subparser
            for a, kw in reversed(func.parser_args):
                subparser.add_argument(*a, **kw)

        ## If func is None, we want to return a decorator
        if func is None:
            return wrapped

        return wrapped(func)

    def arg(self, *a, **kw):
        """Decorator to add a parser argument to a given command"""

        def wrapped(func):
            func = self._wrap_func(func)
            func.parser_args.append((a, kw))
            return func

        return wrapped

    def flag(self, *a, **kw):
        """Decorator to add a parser argument to a given command"""

        kw.setdefault('default', False)
        kw['action'] = 'store_false' if kw['default'] else 'store_true'

        def wrapped(func):
            func = self._wrap_func(func)
            func.parser_args.append((a, kw))
            return func

        return wrapped

    def run(self, args=None):
        """Handle running from the command line"""
        args = self.parser.parse_args(args)
        args.func(args)

    ## for retro-compatibility..
    parser_arg = arg
    run_from_command_line = run
