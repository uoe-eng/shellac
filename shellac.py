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
            tokens = readline.get_line_buffer().split()
            if not tokens or readline.get_line_buffer()[-1] == ' ':
                tokens.append('')
            self.results = list(self.traverse(tokens, self))
        try:
            return self.results[state]
        except IndexError:
            return None
