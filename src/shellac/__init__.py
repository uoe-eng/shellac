#!/usr/bin/python

import sys
import readline
import inspect
from functools import wraps


def generator(func):
    """Turn an iterable function into a readline-style completion function which
    accepts an integer "state" as its last argument.

    """
    @wraps(func)
    def new_func(self, text, state):
        """A wrapper for this function."""
        try:
            if state == 0:
                self.iterable = iter(func(self, text))
            try:
                return next(self.iterable)
            except StopIteration:
                self.iterable = None
                return None
        except CompletionError as exc:
            # CompletionError exceptions can be thrown by generators when next()
            # is called, or by simple functions (i.e. those returning a list) at
            # the point of call (i.e. before iter() is applied). Catch both
            # cases.
            sys.stdout.write("\n%s\n" % str(exc))
            self.redraw()
            return None
    return new_func


class CompletionError(Exception):
    """Errors in completion functions."""

    def __init__(self, args="Error during completion."):
        Exception.__init__(self, args)


def completer(func):
    """Attach a completion function to the decorated function."""

    def inner_completer(obj):
        """The inner decorator which takes the completion function as its only
        argument."""

        if not hasattr(obj, "completions"):
            obj.completions = []
        obj.completions.append(func)
        return obj
    return inner_completer


def members(obj, prefix='do_'):
    """Return a list of members of the given class which start with a given
    prefix."""

    return (f[0][len(prefix):] for f in inspect.getmembers(obj) if f[0].startswith(prefix))


def complete_list(names, token):
    """Filter given list which starts with the given string, and pad with a
    trailing space."""

    return (x + ' ' for x in names if x.startswith(token))


class Shellac(object):
    """An interactive command interpreter."""

    def __init__(self, completekey='tab', stdin=sys.stdin, stdout=sys.stdout):
        """Create a command interpreter.

        You should never call this class directly. To use it, inherit from this
        class and implement do_*() methods which map to * commands. Implement
        child methods of classes defined in your subclass to create subcommands
        in the interface.

        """

        self.stdin = stdin
        self.stdout = stdout
        self.completekey = completekey
        if self.stdin.isatty():
            self.prompt = "(%s) " % (self.__class__.__name__)
        else:
            self.prompt = ""
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
           when an empty line is entered."""

        return

    def default(self, line):
        """Default action for commands with no do_ method."""

        self.stdout.write('*** Unknown syntax: {0}\n'.format(line))

    def do_exit(self, args):
        """Exit the interactive interpreter."""

        return True

    do_EOF = do_exit

    def do_help(self, args):
        """Help system documentation!"""

        self.stdout.write((self._get_help(args, self) or
                           "*** No help for %s" % (args or repr(self))) + "\n")

    @classmethod
    def _get_help(cls, args, root):
        """Recursive class method to find a help string for the given command.

        Returns either a string from the result of a help_*() or do_*()
        function, the do_*() function's docstring or None.

        """

        cmd, _, args = args.partition(' ')
        if not cmd:
            return root.__doc__
        if inspect.isclass(root):
            root = root()
        try:
            func = getattr(root, 'help_' + cmd)
        except AttributeError:
            if hasattr(root, 'do_' + cmd):
                return cls._get_help(args, getattr(root, 'do_' + cmd)) or \
                       getattr(root, 'do_' + cmd).__doc__
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
        """Implement an interactive command interpreter which grabs a line of
        input and passes it to onecmd() until the postcmd() function returns
        True.

        This method will also:
        - Execute a preloop() method before starting the interpreter,
        - Install a complete() readline completer function, and
        - Write the string intro followed by a newline to stdout, then
            - Read from a list of commands called cmdqueue, or
            - Read from stdin, and
                - Call precmd() with the line as an argument,
                - Call onecmd() with the line as an argument,
                - Call postcmd() with the stop flag and the line as an argument.
        - Finally, restore the previous readline completer, if any.

        """

        self.preloop()
        old_completer = readline.get_completer()
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
            readline.set_completer(old_completer)

    def onecmd(self, line, args='', root=None):
        """Execute a single command line.

        If the given line is False (i.e. empty), call return the result of
        emptyline(). Thereafter, try to find a chain of do_*() methods and
        classes which ends with a callable, then return the result of calling
        it.

        """

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
        """Recurse through the class tree of do_*() methods and classes to find
        a help_*() method which can be used to provide help."""

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
        """Traverse through the class tree of do_*() methods to find a do_*()
        method whose completions function is called to give a list of possible
        arguments or subcommands."""

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
        if tokens[0] in members(tree):
            return cls._traverse_do(tokens[1:],
                                    getattr(tree, 'do_' + tokens[0]))
        if hasattr(tree, 'completions'):
            return (c for f in tree.completions for c in f(tokens[-1]))
        return []

    @generator
    def complete(self, text):
        """Return a list of possible completions from the line currently entered
        at the prompt. If the first word is "help", try to find a help_*()
        method through _traverse_do, otherwise look for a command through
        _traverse_do()."""

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
        """Refresh the current input line."""

        sys.stdout.write("%s%s" % (self.prompt,
                                   readline.get_line_buffer()))
        readline.redisplay()
