#!/usr/bin/python

from cmd import Cmd
import sys
import readline


class Start(Cmd):

    def greet():
        return ["hello", "hi", "goodday"]

    tree = {'alpha':
                 {'bravo': greet,
                  'charlie': None,
                   },
             'delta':
                 {'echo': None,
                  'foxtrot':
                       {'golf': None,
                        'hotel': None
                        }
                   }
             }

    def do_exit(self, args):
        return True

    do_EOF = do_exit

    # traverse is recursive so needs to be able to find itself through the class.
    @classmethod
    def traverse(cls, tokens, tree):
        if tree is None:
            return []
        elif len(tokens) == 0:
            return tree.keys()
        if len(tokens) == 1:
            return [x + ' ' for x in tree if x.startswith(tokens[0])]
        else:
            if tokens[0] in tree.keys():
                if callable(tree[tokens[0]]):
                    return [x + ' ' for x in tree[tokens[0]]() if x.startswith(tokens[-1])]
                else:
                    return cls.traverse(tokens[1:], tree[tokens[0]])
        return []

    def complete(self, text, state):
        if state == 0:
            tokens = readline.get_line_buffer().split()
            if not tokens or readline.get_line_buffer()[-1] == ' ':
                tokens.append('')
            self.results = self.traverse(tokens, self.tree)
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
