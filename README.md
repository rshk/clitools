# Cli Tools

Tools for quickly creating Command Line Interface scripts with Python.

[![Build Status](https://travis-ci.org/rshk/clitools.png)](https://travis-ci.org/rshk/clitools)
[![Coverage Status](https://coveralls.io/repos/rshk/clitools/badge.png)](https://coveralls.io/r/rshk/clitools)
[![PyPi version](https://pypip.in/v/clitools/badge.png)](https://crate.io/packages/clitools/)


## Documentation

All the package documentation is hosted on GitHub pages:
[http://rshk.github.io/clitools/](http://rshk.github.io/clitools/).


## Example usage

```python
>>> from clitools import CliApp

>>> cli = CliApp()

>>> @cli.command
... def hello(name, bye=False):
... 	greeting = 'Bye' if bye else 'Hello'
...     print("{0}, {1".format(greeting, name))

>>> cli.run(['--name', 'world'])
Hello, world!

>>> cli.run(['--name', 'world', '--bye'])
Bye, world!
```

-----

[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/rshk/clitools/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

