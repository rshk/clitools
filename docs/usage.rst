Usage documentation
###################

All the commands registration and execution is handled by the ``CliApp`` class.
You need to create an instance of it on top of your main module, and then
call its ``.run()`` method when you're ready to go:

.. code-block:: python

    from clitools import CliApp

    cli = CliApp()

    # ...

    if __name__ == '__main__':
        cli.run()


Registering a command
=====================

Each command is simply a function to be called when the appropriate
sub-command is selected.

To register a new command, simply use the ``CliApp().command`` decorator.

Arguments, options, documentation, etc. are all taken from function
arguments and docstring.

For example:

.. code-block:: python

    @cli.command
    def hello(name):
        print("Hello, {0}!".format(name))

You'll get a sub-command named ``hello``, accepting a single (required)
positional argument, ``name``.

If you invoke the script like this::

    % ./my-script.py hello world

You'll get the string ``Hello, world!`` on the output.

Suppose we'd now want to make the argument optional:

.. code-block:: python

    @cli.command
    def hello(name='world'):
        print("Hello, {0}!".format(name))

Let's invoke it::

    % ./my-script.py
    Hello, world!

    % ./my-script.py --name Python
    Hello, Python!


Arguments auto-discovery
========================

The arguments generation pattern is quite smart, to try to guess the appropriate
argument type based on the argument default value.

* Positional arguments are treated just as positional arguments
* If the default value is ``None``, a simple optional argument will be generated.
* A boolean default value will result in a ``store_{false,true}`` with default
  value == the function default value
* A list/tuple with less than two elemets will result in an ``action=append``
  argument. If there is at least one element, its type will be enforced on
  the received arguments.
* A list/tuple with at least two elements will result in a ``type='choice'``
  argument.
* Anything else will result in a normal argument, with default value and
  enforced type.

.. warning:: There is no support for variable arguments / kwargs (yet).
	     If you use them in your command function, they will simply
	     be ignored.

Manually specify arguments
==========================

You can use the ``CliApp().arg`` class to manually specify arguments/kwargs
to ``.add_argument()`` call.

The ``default`` value you specify will then be set as the actual default value
on the function:

.. code-block:: python

    @cli.command
    def hello(name=cli.arg(default='world'))
        print("hello, " + name)

::

    % ./my-script.py hello
    hello, world

    % ./my-script.py hello --name=python
    hello, python

    >>> hello()
    hello, world

    >>> hello(name='python')
    hello, python
