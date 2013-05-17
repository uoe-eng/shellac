#!/usr/bin/python

from cmd import Cmd
import readline
import inspect


def completer(func):
    def innerCompleter(obj):
        if not hasattr(obj, "completions"):
            obj.completions = []
        obj.completions.append(func)
        return obj
    return innerCompleter


def members(obj):
        for f in inspect.getmembers(obj):
            if f[0].startswith('do_'):
                yield f[0][3:]


def complete_list(l, token):
        for x in l:
            if x.startswith(token):
                yield x + ' '


class Shellac(Cmd):

    # onecmd is recursive so needs to find itself through the class
    @classmethod
    def onecmd(cls, line, pos=0, root=None):
        if line:
            tokens = line.split()
            try:
                child, args = tokens[pos], tokens[pos + 1:]
            except IndexError:
                # We fell off the end with no callable functions
                print("Nothing to do!")
                return
        else:
            return
        if not root:
            root = cls
        try:
            root = getattr(root, 'do_' + child)
        except AttributeError as e:
            print(e)
        if inspect.isclass(root):
            # If a class, we must instantiate it
            root = root()
        try:
            # Is root (really) callable
            return root(args)
        except AttributeError:
            # It wasn't callable, recurse
            return cls.onecmd(line, pos + 1, root)

    # traverse is recursive so needs to find itself through the class
    @classmethod
    def traverse(cls, tokens, tree):
        if tree is None:
            return []
        elif len(tokens) == 0:
            return members(tree)
        if len(tokens) == 1:
            if hasattr(tree, 'completions'):
                complist = []
                for f in getattr(tree, 'completions'):
                    complist.extend(f(tokens[0]))
                return complist
            return complete_list(members(tree), tokens[0])
        elif tokens[0] in members(tree):
            return cls.traverse(tokens[1:], getattr(tree, 'do_' + tokens[0]))
        return []

    def complete(self, text, state):
        if state == 0:
            endidx = readline.get_endidx()
            buf = readline.get_line_buffer()
            tokens = buf[:endidx].split()
            if not tokens or buf[endidx - 1] == ' ':
                tokens.append('')
            self.results = list(self.traverse(tokens, self))
        try:
            return self.results[state]
        except IndexError:
            return None
