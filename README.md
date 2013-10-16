# Cli Tools

Tools for quickly creating Command Line Interface scripts with Python.

[![Build Status](https://travis-ci.org/rshk/clitools.png)](https://travis-ci.org/rshk/clitools)


## Example

```python
from clitools import CliApp

cli = CliApp()

@cli.command
def hello(args):
    print "Hello, world!"

@cli.command
@cli.parser_arg('--name')
def hello2(args):
    print "Hello, {0}!".format(args.name)

if __name__ == '__main__':
    cli.run_from_command_line()
```
