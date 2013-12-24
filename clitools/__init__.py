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
import logging


__version__ = '0.4a'  # sync with setup.py!


logger = logging.getLogger('clitools')


class Command(object):
    def __init__(self, func, func_info):
        self.func = func
        self.func_info = func_info
        logger.debug('-- New CliApp instance')

    def __call__(self, parsed_args):
        """
        We need to map parsed arguments to function arguments
        before calling..
        """

        args = []
        kwargs = {}

        for argname in self.func_info['positional_args']:
            args.append(getattr(parsed_args, argname))

        for argname, default in self.func_info['keyword_args'].iteritems():
            kwargs[argname] = getattr(parsed_args, argname, default)

        return self.func(*args, **kwargs)


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

        func_info = self._analyze_function(func)

        ## Read keyword arguments
        name = kwargs.get('name')
        if name is None:
            name = func_info['name']
            ## Strip the command_ prefix from function name
            if name.startswith('command_'):
                name = name[len('command_'):]

        help_text = kwargs.get('help')
        if help_text is None:
            help_text = func_info['help_text']

        ## Create the new subparser
        subparser = self.subparsers.add_parser(name, help=help_text)

        ## Process required positional arguments
        for argname in func_info['positional_args']:
            logger.debug('New argument: {0}'.format(argname))
            subparser.add_argument(argname)

        ## Process optional keyword arguments
        func_new_defaults = []
        for argname, argvalue in func_info['keyword_args'].iteritems():
            if isinstance(argvalue, self.arg):
                ## We already have args / kwargs for this argument
                a = (['--' + argname] + list(argvalue.args))
                kw = argvalue.kwargs
                func_new_defaults.append(kw.get('default'))

            else:
                ## We need to guess args / kwargs from default value
                a, kw = self._arg_from_free_value(argname, argvalue)
                func_new_defaults.append(argvalue)  # just use the old one

            logger.debug('New argument: {0!r} {1!r}'.format(a, kwargs))
            subparser.add_argument(*a, **kw)
        func.func_defaults = tuple(func_new_defaults)

        ## todo: replace defaults on the original function, to strip
        ##       any instance of ``self.arg``?

        new_function = Command(func=func, func_info=func_info)

        ## Positional arguments are treated as required values
        subparser.set_defaults(func=new_function)

        return subparser  # for further analysis during tests

    def _analyze_function(self, func):
        """
        Extract information from a function:

        - positional argument names
        - optional argument names / default values
        - does it accept *args?
        - does it accept **kwargs?
        """
        import pydoc

        info = {}

        info['name'] = func.__name__

        # todo extract arguments docs too!
        info['help_text'] = pydoc.getdoc(func)

        ## Interpret some flags
        info['accepts_varargs'] = bool(func.func_code.co_flags & 0x04)
        info['accepts_kwargs'] = bool(func.func_code.co_flags & 0x08)
        info['is_generator'] = bool(func.func_code.co_flags & 0x20)

        ## Name of all the variables used in the function
        var_names = list(func.func_code.co_varnames or [])

        ## Number of arguments (incl ones w/ default value,
        ## excluding *args / **kwargs)
        arg_count = func.func_code.co_argcount

        arg_names = var_names[:arg_count]
        var_names = var_names[arg_count:]  # other vars..

        ## Default values for arguments
        arg_defaults = list(func.func_defaults or [])

        info['varargs_name'] = var_names.pop(0) \
            if info['accepts_varargs'] else None
        info['kwargs_name'] = var_names.pop(0) \
            if info['accepts_kwargs'] else None

        ## Split positional arguments form arguments with defaults
        nargs = len(arg_names) - len(arg_defaults)
        pos_args, keyword_args = arg_names[:nargs], arg_names[nargs:]

        info['positional_args'] = pos_args
        info['keyword_args'] = dict(zip(keyword_args, arg_defaults))

        return info

    def _arg_from_free_value(self, name, value):
        """
        Guess the correct argument type to be built for free-form
        arguments (default values)
        """
        logger.debug('_arg_from_free_value({0!r}, {1!r})'.format(name, value))

        arg_name = '--' + name

        def o(*a, **kw):
            return a, kw

        if value is None:
            ## None: this is just a generic argument, accepting any value
            logger.debug('None -> generic optional argument')
            return o(arg_name, default=value)

        elif (value is True) or (value is False):
            ## Boolean value: on/off flag
            logger.debug('bool -> flag')
            action = 'store_false' if value else 'store_true'
            return o(arg_name, action=action, default=value)

        elif isinstance(value, (list, tuple)):
            ## List/tuple: if has at least two items, it will
            ## be used for a 'choice' option, else for an 'append'
            ## list.

            if len(value) > 1:
                ## Choices
                logger.debug('List with length >= 2 -> choices')
                return o(arg_name, type='choice', choices=value,
                         default=value[0])

            else:
                ## Append (of type)
                type_ = None

                logger.debug('List with length < 2 -> list of items')
                if len(value) > 0:
                    ## This is [<type>]
                    type_ = (value[0]
                             if isinstance(value[0], type)
                             else type(value[0]))
                return o(arg_name, type=type_, action='append', default=[])

        else:
            ## Anything of this type will fit..
            ## todo: make sure the type is a supported one?
            if isinstance(value, type):
                type_ = value
                default = None
            else:
                type_ = type(value)
                default = value
            logger.debug('Generic object of type {0!r} (default: {1!r})'
                         .format(type_, default))
            # import ipdb; ipdb.set_trace()
            return o(arg_name, type=type_, default=default)

    def run(self, args=None):
        """Handle running from the command line"""
        parsed_args = self.parser.parse_args(args)
        return parsed_args.func(parsed_args)
