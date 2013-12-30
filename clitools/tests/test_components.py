"""
Unit tests for the internal components
"""

import pytest

from clitools import CliApp


def test_arg_from_free_value():
    cli = CliApp()

    assert cli._arg_from_free_value('dummy', None) \
        == (('--dummy',), {'default': None})

    assert cli._arg_from_free_value('dummy', True) \
        == (('--dummy',), {'default': True, 'action': 'store_false'})
    assert cli._arg_from_free_value('dummy', False) \
        == (('--dummy',), {'default': False, 'action': 'store_true'})

    assert cli._arg_from_free_value('dummy', []) \
        == (('--dummy',), {'action': 'append', 'type': None, 'default': []})
    assert cli._arg_from_free_value('dummy', [str]) \
        == (('--dummy',), {'action': 'append', 'type': str, 'default': []})
    assert cli._arg_from_free_value('dummy', ['string here']) \
        == (('--dummy',), {'action': 'append', 'type': str, 'default': []})

    assert cli._arg_from_free_value('dummy', ['one', 'two', 'three']) \
        == (('--dummy',), {'type': 'choice',
                           'choices': ['one', 'two', 'three'],
                           'default': 'one'})

    assert cli._arg_from_free_value('dummy', str) \
        == (('--dummy',), {'type': str, 'default': None})
    assert cli._arg_from_free_value('dummy', 'hello') \
        == (('--dummy',), {'type': str, 'default': 'hello'})


def generate_analyze_function_params():
    """
    Generate parameters for testing the function analysis
    """

    def func():
        pass

    yield func, {
        'name': 'func',
        'help_text': None,
        'accepts_varargs': False,
        'accepts_kwargs': False,
        'is_generator': False,
        'kwargs_name': None,
        'varargs_name': None,
        'positional_args': [],
        'keyword_args': [],
    }

    def func(aaa, bbb, ccc):
        pass

    yield func, {
        'name': 'func',
        'help_text': None,
        'accepts_varargs': False,
        'accepts_kwargs': False,
        'is_generator': False,
        'kwargs_name': None,
        'varargs_name': None,
        'positional_args': ['aaa', 'bbb', 'ccc'],
        'keyword_args': [],
    }

    def func(aaa, bbb, ccc, ddd='spam', eee='eggs'):
        pass

    yield func, {
        'name': 'func',
        'help_text': None,
        'accepts_varargs': False,
        'accepts_kwargs': False,
        'is_generator': False,
        'kwargs_name': None,
        'varargs_name': None,
        'positional_args': ['aaa', 'bbb', 'ccc'],
        'keyword_args': [('ddd', 'spam'), ('eee', 'eggs')],
    }

    def func(aa, bb='hello', *args):
        pass

    yield func, {
        'name': 'func',
        'help_text': None,
        'accepts_varargs': True,
        'accepts_kwargs': False,
        'is_generator': False,
        'kwargs_name': None,
        'varargs_name': 'args',
        'positional_args': ['aa'],
        'keyword_args': [('bb', 'hello')],
    }

    def func(name='hello'):
        pass

    yield func, {
        'name': 'func',
        'help_text': None,
        'accepts_varargs': False,
        'accepts_kwargs': False,
        'is_generator': False,
        'kwargs_name': None,
        'varargs_name': None,
        'positional_args': [],
        'keyword_args': [('name', 'hello')],
    }

    def func(arg1, arg2, kwa1='kwv1', kwa2='kwv2', *args, **kwargs):
        """This is a dummy function"""
        pass

    yield func, {
        'name': 'func',
        'help_text': 'This is a dummy function',
        'accepts_varargs': True,
        'accepts_kwargs': True,
        'is_generator': False,
        'kwargs_name': 'kwargs',
        'varargs_name': 'args',
        'positional_args': ['arg1', 'arg2'],
        'keyword_args': [('kwa1', 'kwv1'), ('kwa2', 'kwv2')],
    }

    def func(arg1, arg2, kwa1='kwv1', kwa2='kwv2', *args, **kwargs):
        """This is a dummy function"""
        hello = arg1 + arg2
        othervar = 123
        return hello, othervar

    yield func, {
        'name': 'func',
        'help_text': 'This is a dummy function',
        'accepts_varargs': True,
        'accepts_kwargs': True,
        'is_generator': False,
        'kwargs_name': 'kwargs',
        'varargs_name': 'args',
        'positional_args': ['arg1', 'arg2'],
        'keyword_args': [('kwa1', 'kwv1'), ('kwa2', 'kwv2')],
    }


@pytest.mark.parametrize('func,info', list(generate_analyze_function_params()))
def test_analyze_function(func, info):
    assert CliApp()._analyze_function(func) == info


def test_function_registration():
    """
    Pin-point a nasty bug that was occurring due to a wrong name..
    """

    cli = CliApp()

    def hello(name='world'):
        pass

    func_info = cli._analyze_function(hello)
    assert func_info['keyword_args'] == [('name', 'world')]

    a, kw = cli._arg_from_free_value('name', 'world')
    assert a == ('--name',)
    assert kw == {'default': 'world', 'type': str}

    subparser = cli._register_command(hello)
    assert subparser.get_default('func').func is hello
    assert subparser.get_default('name') == 'world'


def test_split_function_doc():
    from clitools import split_function_doc, extract_arguments_info

    doc = (
        'My example function\n'
        ':param name1: Arg1 doc\n'
        ':param str name2: Arg2 doc\n'
        ':param name3: Arg3 doc\n'
        ':type name3: int\n')

    splitted = list(split_function_doc(doc))
    assert splitted == [
        (None, 'My example function'),
        (('param', 'name1'), 'Arg1 doc'),
        (('param', 'str', 'name2'), 'Arg2 doc'),
        (('param', 'name3'), 'Arg3 doc'),
        (('type', 'name3'), 'int')
    ]

    args_info = extract_arguments_info(doc)
    assert args_info == {
        'function_help': 'My example function\n',
        'params_help': {
            'name1': {
                'help': 'Arg1 doc',
            },
            'name2': {
                'help': 'Arg2 doc',
                'type': 'str',
            },
            'name3': {
                'help': 'Arg3 doc',
                'type': 'int',
            },
        }
    }
