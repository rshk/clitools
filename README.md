# Cli Tools

Tools for quickly creating Command Line Interface scripts with Python.

[![Build Status](https://travis-ci.org/rshk/clitools.png)](https://travis-ci.org/rshk/clitools)
[![Coverage Status](https://coveralls.io/repos/rshk/clitools/badge.png)](https://coveralls.io/r/rshk/clitools)
[![PyPi version](https://pypip.in/v/clitools/badge.png)](https://crate.io/packages/clitools/)


## Documentation

All the package documentation is hosted on GitHub pages:
[http://rshk.github.io/clitools/](http://rshk.github.io/clitools/).


## Example usage

You can create your CLI script like this:

```python
from clitools import CliApp

cli = CliApp()


@cli.command
def hello(name='world', bye=False):
    greet = 'Bye' if bye else 'Hello'
    print("{0}, {1}".format(greet, name))


if __name__ == '__main__':
    cli.run()
```

and then run it right away!

```console
% python sample_app.py
usage: cli-app [-h] {hello} ...
cli-app: error: too few arguments
>>> exited 2

% python sample_app.py --help
usage: cli-app [-h] {hello} ...

positional arguments:
  {hello}     sub-commands
    hello

optional arguments:
  -h, --help  show this help message and exit

% python sample_app.py hello
Hello, world

% python sample_app.py hello --name=Python
Hello, Python

% python sample_app.py hello --help
usage: cli-app hello [-h] [--bye] [--name NAME]

optional arguments:
  -h, --help   show this help message and exit
  --bye
  --name NAME

% python sample_app.py hello --bye --name=Spam
Bye, Spam
```

..super-cool, isn't it?


-----

[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/rshk/clitools/trend.png)](https://bitdeli.com/free "Bitdeli Badge")
