#!/usr/bin/python

import sys
import readline
import inspect
from functools import wraps


def generator(func):
    @wraps(func)
    def new_func(self, text, state):
        try:
            if state == 0:
                self.iterable = iter(func(self, text))
            try:
                return next(self.iterable)
            except StopIteration:
                self.iterable = None
                return None
        except CompletionError as e:
            # CompletionError exceptions can be thrown by generators when next()
            # is called, or by simple functions (i.e. those returning a list) at
            # the point of call (i.e. before iter() is applied). Catch both
            # cases.
            sys.stdout.write("\n%s\n" % str(e))
            self.redraw()
            return None
    return new_func


class CompletionError(Exception):
    """Errors in completion functions."""

    def __init__(self, args="Error during completion."):
        Exception.__init__(self, args)


def completer(func):
    def inner_completer(obj):
        if not hasattr(obj, "completions"):
            obj.completions = []
        obj.completions.append(func)
        return obj
    return inner_completer


def members(obj, prefix='do_'):
    return (f[0][len(prefix):] for f in inspect.getmembers(obj) if f[0].startswith(prefix))


def complete_list(names, token):
    return (x + ' ' for x in names if x.startswith(token))


class Shellac(object):

    def __init__(self, completekey='tab', stdin=sys.stdin, stdout=sys.stdout):
        self.stdin = stdin
        self.stdout = stdout
        self.completekey = completekey
        self.prompt = "(%s) " % (self.__class__.__name__)
        self.lastcmd = ''
        self.intro = None
        self.cmdqueue = []
        # raw_input() replaced with input() in python 3
        try:
            self.inp = raw_input
        except NameError:
            self.inp = input

    def emptyline(self):
        """This method can be overridden to change what happens
           when an empty line is entered"""
        return

    def default(self, line):
        """Default action for commands with no do_ method"""

        self.stdout.write('*** Unknown syntax: %s\n' % (line))

    def do_exit(self, args):
        return True

    do_EOF = do_exit

    def do_help(self, args):
        """Help system documentation!"""
        self.stdout.write((self._get_help(args, self) or
              "*** No help for %s" % (args or repr(self))) + "\n")

    @classmethod
    def _get_help(cls, args, root):
        cmd, _, args = args.partition(' ')
        if not cmd:
            return root.__doc__
        if inspect.isclass(root):
            root = root()
        if hasattr(root, 'do_' + cmd):
            res = cls._get_help(args, getattr(root, 'do_' + cmd))
            if res:
                return res
        try:
            func = getattr(root, 'help_' + cmd)
        except AttributeError:
            if hasattr(root, 'do_' + cmd):
                return getattr(root, 'do_' + cmd).__doc__
            return None
        else:
            return func(args)

    def precmd(self, line):
        """Hook method executed just before the command line is dispatched."""
        return line

    def postcmd(self, stop, line):
        """Hook method executed just after a command dispatch is finished."""
        return stop

    def preloop(self):
        """Hook method executed once when the cmdloop() method is called."""
        pass

    def postloop(self):
        """Hook method executed once when the cmdloop() method is finished."""
        pass

    def cmdloop(self):
        self.preloop()
        self.old_completer = readline.get_completer()
        readline.set_completer(self.complete)
        readline.parse_and_bind(self.completekey + ": complete")

        try:
            if self.intro:
                self.stdout.write(str(self.intro) + "\n")
            stop = None
            while not stop:
                if self.cmdqueue:
                    line = self.cmdqueue.pop()
                else:
                    try:
                        line = self.inp(self.prompt)
                    except EOFError:
                        line = 'EOF'
                line = self.precmd(line)
                stop = self.onecmd(line)
                stop = self.postcmd(stop, line)
            self.postloop()
        finally:
            readline.set_completer(self.old_completer)

    def onecmd(self, line, args='', root=None):
        if not args:
            args = line
        if not root:
            root = self
        if args:
            child, _, args = args.partition(' ')
        elif not line:
            return self.emptyline()
        self.lastcmd = line
        if line == 'EOF':  # http://bugs.python.org/issue13500
            self.lastcmd = ''
        try:
            root = getattr(root, 'do_' + child)
        except AttributeError:
            return self.default(line)
        if inspect.isclass(root):
            # If a class, we must instantiate it
            root = root()
        try:
            # Is root (really) callable
            return root(args)
        # python2 and 3 return different exceptions here
        except (AttributeError, TypeError):
            # It wasn't callable, recurse
            if not args:
                return self.default(line)
            return self.onecmd(line, args, root)

    # traverse_help is recursive so needs to find itself through the class
    @classmethod
    def _traverse_help(cls, tokens, tree):
        if tree is None:
            return []
        elif len(tokens) == 0:
            return members(tree)
        if len(tokens) == 1:
            return complete_list(set(members(tree, 'help_')) | set(members(tree)), tokens[0])
        elif tokens[0] in members(tree):
            return cls._traverse_help(tokens[1:],
                                      getattr(tree, 'do_' + tokens[0]))
        return []

    # traverse_do is recursive so needs to find itself through the class
    @classmethod
    def _traverse_do(cls, tokens, tree):
        if inspect.isclass(tree):
            tree = tree()
        if tree is None:
            return []
        elif len(tokens) == 0:
            return members(tree)
        if len(tokens) == 1:
            if hasattr(tree, 'completions'):
                return (c for f in tree.completions for c in f(tokens[0]))
            return complete_list(members(tree), tokens[0])
        elif tokens[0] in members(tree):
            return cls._traverse_do(tokens[1:],
                                    getattr(tree, 'do_' + tokens[0]))
        return []

    @generator
    def complete(self, text):
        endidx = readline.get_endidx()
        buf = readline.get_line_buffer()
        tokens = buf[:endidx].split()
        if not tokens or buf[endidx - 1] == ' ':
            tokens.append('')
        if tokens[0] == "help":
            return self._traverse_help(tokens[1:], self)
        else:
            return self._traverse_do(tokens, self)

    def redraw(self):
        sys.stdout.write("%s%s" % (self.prompt,
                                   readline.get_line_buffer()))
        readline.redisplay()
