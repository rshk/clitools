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
import textwrap


class Command(object):
    def __init__(self, func, argnames, kwnames, kwdefaults,
                 varargs_name, kwargs_name):
        self.func = func
        self.argnames = argnames
        self.kwnames = kwnames
        self.kwdefaults = kwdefaults
        self.varargs_name = varargs_name
        self.kwargs_name = kwargs_name

    def __call__(self, parsed_args):
        """
        We need to map parsed arguments to function arguments
        before calling..
        """

        args = []
        kwargs = {}

        for argname in self.argnames:
            args.append(getattr(parsed_args, argname))

        for argname in self.kwnames:
            kwargs[argname] = getattr(parsed_args, argname)

        return self.func(*args, **kwargs)

    def __getattr__(self, name):
        ## Let's fake to be the wrapped function
        return getattr(self.func, name)

    @property
    def command_name(self):
        name = self.func.__name__
        if name.startswith('command_'):
            name = name[len('command_'):]
        return name


class CliApp(object):
    class arg(object):
        """Class used to wrap arguments as function defaults"""
        def __init__(self, *a, **kw):
            self.args = a
            self.kwargs = kw

    def __init__(self, prog_name='cli-app'):
        self.prog_name = prog_name
        self.parser = argparse.ArgumentParser(prog=prog_name)
        self.subparsers = self.parser.add_subparsers(help='sub-commands')

    def command(self, func=None, **kwargs):
        """
        Decorator to register a command function

        :param name: Name for the command
        :param help: Help text for the function
        """
        def decorator(func):
            self._register_command(func, **kwargs)
            return func
        if func is None:
            return decorator
        return decorator(func)

    def _register_command(self, func, **kwargs):
        """
        Register a command function. We need to hack things a bit here:

        - we need to change argument defaults in the function (copying it)
        - The original function is copied, and default values changed
        - The new function is copied in the subparser object

        WARNING! variable arguments / keyword arguments are not supported
        (yet)! They are just stripped & ignored, ATM..
        """

        ## Prepare the command name
        name = kwargs.get('name')
        if name is None:
            name = func.func_name
            if name.startswith('command_'):
                name = name[len('command_'):]

        ## Prepare the help text
        help_text = kwargs.get('help')
        if help_text is None:
            help_text = func.__doc__
        if help_text is not None:
            help_text = textwrap.dedent(help_text).lstrip()

        ## Create the new subparser
        subparser = self.subparsers.add_parser(name, help=help_text)

        ## Interpret some flags
        accepts_varargs = func.func_code.co_flags & 0x04
        accepts_kwargs = func.func_code.co_flags & 0x08
        #is_generator = func.func_code.co_flags & 0x20

        ## Get function arguments / default values
        arg_names = list(func.func_code.co_varnames or [])
        arg_defaults = list(func.func_defaults or [])
        kwargs_name = arg_names.pop() if accepts_kwargs else None
        varargs_name = arg_names.pop() if accepts_varargs else None

        ## Split positional arguments form arguments with defaults
        nargs = len(arg_names) - len(arg_defaults)
        positional_args, keyword_args = arg_names[:nargs], arg_names[nargs:]
        #new_defaults = []

        for argname in positional_args:
            ## This is a required positional argument!
            subparser.add_argument(argname)

        for argname, argvalue in zip(keyword_args, arg_defaults):
            if isinstance(argvalue, self.arg):
                subparser.add_argument(
                    '--' + argname, *argvalue.args, **argvalue.kwargs)

            else:
                a, kw = self._arg_from_free_value(argname, argvalue)

        ## todo: replace defaults on the original function, to strip
        ##       any instance of ``self.arg``?

        new_function = Command(
            func=func, argnames=positional_args, kwnames=keyword_args,
            kwdefaults=arg_defaults, varargs_name=varargs_name,
            kwargs_name=kwargs_name)

        ## todo: wrap the function in something able to process
        ##       arguments and do stuff..

        ## Positional arguments are treated as required values
        subparser.set_defaults(func=new_function)

    def _arg_from_free_value(self, name, value):
        """
        Guess the correct argument type to be built for free-form
        arguments (default values)
        """
        arg_name = '--' + name

        def o(*a, **kw):
            return a, kw

        if value is None:
            ## None: this is just a generic argument, accepting any value
            return o(arg_name, default=value)

        elif (value is True) or (value is False):
            ## Boolean value: on/off flag
            action = 'store_false' if value else 'store_true'
            return o(arg_name, action=action, default=value)

        elif isinstance(value, (list, tuple)):
            ## List/tuple: if has at least two items, it will
            ## be used for a 'choice' option, else for an 'append'
            ## list.

            if len(value) > 1:
                ## Choices
                return o(arg_name, type='choice',
                         choices=value, default=value[0])

            else:
                ## Append (of type)
                type_ = None

                if len(value) > 0:
                    ## This is [<type>]
                    type_ = (value[0]
                             if isinstance(value[0], type)
                             else type(value[0]))
                return o(arg_name, type=type_, action='append')

        else:
            ## Anything of this type will fit..
            if isinstance(value, type):
                type_ = value
                default = None
            else:
                type_ = type(value)
                default = value
            return o(arg_name, type=type_, default=default)

    def run(self, args=None):
        """Handle running from the command line"""
        args = self.parser.parse_args(args)
        return args.func(args)
