Usage documentation
###################

First, you need to instantiate a ``CliApp`` object:

.. code-block:: python

    from clitools import CliApp
    cli = CliApp()


Registering a command
=====================

Each command is associated to a function accepting the parser arguments
as its only argument.

To register new commands, you can simply use the ``command`` decorator.

In order to prevent conflicts with builtin functions / reserved keywords,
you can add the ``command_`` prefix to function names. It will be stripped
when generating command name.

.. code-block:: python

    @cli.command
    def hello(args):
        print("Hello, world!")

Is equivalent to:

.. code-block:: python

    @cli.command
    def command_hello(args):
        print("Hello, world!")


Adding arguments to commands
----------------------------

Simply use the ``.arg()`` decorator, which accepts the same arguments
as argparse subparser ``.add_argument()`` method:

.. code-block:: python

    @cli.command
    @cli.arg('--name')
    def hello(args):
        print("Hello, {0}!".format(args.name))

You can also use the ``.flag()`` decorator, that simply has some different
default values (action='store_true', default=False).


Running
=======

Finally, to run your application:

.. code-block:: python

    if __name__ == '__main__':
        cli.run()
