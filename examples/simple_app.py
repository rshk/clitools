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
