# Cli Tools

Tools for quickly creating Command Line Interface scripts with Python.

[![Build Status](https://travis-ci.org/rshk/clitools.png)](https://travis-ci.org/rshk/clitools)
[![Coverage Status](https://coveralls.io/repos/rshk/clitools/badge.png)](https://coveralls.io/r/rshk/clitools)
[![PyPi version](https://pypip.in/v/clitools/badge.png)](https://crate.io/packages/clitools/)


[Package documentation](http://rshk.github.io/clitools/)


## New architecture

This is a complete rethinking of the whole thing, in order to make things
even more fun to use!


### Defining commands

```python
from clitools import CliApp

cli = CliApp()

@cli.command
def hello(name, bye=False):
	greeting = 'Bye' if bye else 'Hello'
    print("{0}, {1".format(greeting, name))


>>> cli.run(['--name', 'world'])
Hello, world!

>>> cli.run(['--name', 'world', '--bye'])
Bye, world!
```







## Example

```python
#!/usr/bin/env python

from clitools import CliApp

cli = CliApp()

@cli.command
def hello(args):
    print "Hello, world!"

@cli.command
@cli.arg('--name')
@cli.flag('--bye')
def hello2(args):
    greeting = "Bye" if args.bye else "Hello"
    message = "{0}, {1}!".format(greeting, args.name or 'Mr.X')
    print(message)

if __name__ == '__main__':
    cli.run()
```

### Running the example

```console
% ./simple_app.py
usage: cli-app [-h] {hello,hello2} ...
cli-app: error: too few arguments

% ./simple_app.py hello
Hello, world!

% ./simple_app.py hello --help
usage: cli-app hello [-h]

optional arguments:
  -h, --help  show this help message and exit

% ./simple_app.py hello2
Hello, Mr.X!

% ./simple_app.py hello2 --help
usage: cli-app hello2 [-h] [--name NAME] [--bye]

optional arguments:
  -h, --help   show this help message and exit
  --name NAME
  --bye

% ./simple_app.py hello2 --name=world
Hello, world!

% ./simple_app.py hello2 --name=world --bye
Bye, world!
```


[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/rshk/clitools/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

