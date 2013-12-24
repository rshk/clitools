"""
Unit tests for the components
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
        == (('--dummy',), {'action': 'append', 'type': None})
    assert cli._arg_from_free_value('dummy', [str]) \
        == (('--dummy',), {'action': 'append', 'type': str})
    assert cli._arg_from_free_value('dummy', ['string here']) \
        == (('--dummy',), {'action': 'append', 'type': str})

    assert cli._arg_from_free_value('dummy', ['one', 'two', 'three']) \
        == (('--dummy',), {'type': 'choice',
                           'choices': ['one', 'two', 'three'],
                           'default': 'one'})

    assert cli._arg_from_free_value('dummy', str) \
        == (('--dummy',), {'type': str, 'default': None})
    assert cli._arg_from_free_value('dummy', 'hello') \
        == (('--dummy',), {'type': str, 'default': 'hello'})


def generate_analyze_function_params():
    def func():
        pass

    yield func, {
        'name': 'func',
        'help_text': '',
        'accepts_varargs': False,
        'accepts_kwargs': False,
        'is_generator': False,
        'kwargs_name': None,
        'varargs_name': None,
        'positional_args': [],
        'keyword_args': {},
    }

    def func(aaa, bbb, ccc):
        pass

    yield func, {
        'name': 'func',
        'help_text': '',
        'accepts_varargs': False,
        'accepts_kwargs': False,
        'is_generator': False,
        'kwargs_name': None,
        'varargs_name': None,
        'positional_args': ['aaa', 'bbb', 'ccc'],
        'keyword_args': {},
    }

    def func(aaa, bbb, ccc, ddd='spam', eee='eggs'):
        pass

    yield func, {
        'name': 'func',
        'help_text': '',
        'accepts_varargs': False,
        'accepts_kwargs': False,
        'is_generator': False,
        'kwargs_name': None,
        'varargs_name': None,
        'positional_args': ['aaa', 'bbb', 'ccc'],
        'keyword_args': {'ddd': 'spam', 'eee': 'eggs'},
    }

    def func(aa, bb='hello', *args):
        pass

    yield func, {
        'name': 'func',
        'help_text': '',
        'accepts_varargs': True,
        'accepts_kwargs': False,
        'is_generator': False,
        'kwargs_name': None,
        'varargs_name': 'args',
        'positional_args': ['aa'],
        'keyword_args': {'bb': 'hello'},
    }

    def func(name='hello'):
        pass

    yield func, {
        'name': 'func',
        'help_text': '',
        'accepts_varargs': False,
        'accepts_kwargs': False,
        'is_generator': False,
        'kwargs_name': None,
        'varargs_name': None,
        'positional_args': [],
        'keyword_args': {'name': 'hello'},
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
        'keyword_args': {'kwa1': 'kwv1', 'kwa2': 'kwv2'},
    }


@pytest.mark.parametrize('func,info', list(generate_analyze_function_params()))
def test_analyze_function(func, info):
    assert CliApp()._analyze_function(func) == info
