#!/usr/bin/python
import shellac
import sys


def complete_charlie_one(token):
    return shellac.complete_list(['ant', 'bee'], token)


def complete_charlie_two(token):
    return shellac.complete_list(['cat', 'dog'], token)


class myShellac(shellac.Shellac):

    class do_alpha():

        class do_bravo():

            @shellac.completer(complete_charlie_one)
            @shellac.completer(complete_charlie_two)
            def do_charlie():
                pass

    class do_delta():
        completions = [
            lambda x: [y + ' ' for y in ['right', 'wrong'] if y.startswith(x)]]

        def do_run():
            print "delta run"

    def do_exit(self, args):
        return True

    do_EOF = do_exit


if __name__ == '__main__':
    if len(sys.argv) > 1:
        myShellac().onecmd(' '.join(sys.argv[1:]))
    else:
        myShellac().cmdloop()
