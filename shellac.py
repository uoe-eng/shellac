#!/usr/bin/python

from cmd import Cmd
import sys
import readline
import inspect


class Start(Cmd):

    class do_alpha():
        completions = [
            lambda x: [y + ' ' for y in ['right', 'wrong'] if y.startswith(x)]]

        class do_bravo():

            class do_charlie():
                def do_run():
                    print "charlie run"

    class do_delta():
        def do_run():
            print "delta run"

    def do_exit(self, args):
        return True

    do_EOF = do_exit

    @staticmethod
    def members(obj):
        for f in inspect.getmembers(obj):
            if f[0].startswith('do_'):
                yield f[0][3:]

    @classmethod
    def complete_children(cls, obj, token):
        for x in cls.members(obj):
            if x.startswith(token):
                yield x + ' '

    # traverse is recursive so needs to find itself through the class
    @classmethod
    def traverse(cls, tokens, tree):
        if tree is None:
            return []
        elif len(tokens) == 0:
            return cls.members(tree)
        if len(tokens) == 1:
            if hasattr(tree, 'completions'):
                complist = []
                for f in getattr(tree, 'completions'):
                    complist.extend(f(tokens[0]))
                return complist
            return cls.complete_children(tree, tokens[0])
        elif tokens[0] in cls.members(tree):
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

    def default(self, line):
        # TODO: For testing only - replace with proper methods
        print repr(line)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        Start().onecmd(' '.join(sys.argv[1:]))
    else:
        Start().cmdloop()
