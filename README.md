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
@cli.arg('--name')
@cli.flag('--bye')
def hello2(args):
	if args.bye:
		print "Bye, {0}!".format(args.name)
	else:
		print "Hello, {0}!".format(args.name)

if __name__ == '__main__':
    cli.run()
```
