#!/usr/bin/python
import shellac
import sys


def complete_charlie_one(token):
    return shellac.complete_list(['ant', 'bee'], token)


def complete_charlie_two(token):
    return shellac.complete_list(['cat', 'dog'], token)


class myShellac(shellac.Shellac):
    """Documentation about myShellac"""

    def help_alpha(self, args):
        return "help_alpha " + args

    def help_banana(self, args):
        return "Platano"

    class do_alpha():
        """alpha docstring"""
        class do_bravo():
            """bravo docstring"""

            def help_charlie(self, args):
                return "help_charlie " + args

            @shellac.completer(complete_charlie_one)
            @shellac.completer(complete_charlie_two)
            def do_charlie(self, args):
                print(("Charlie says " + args))

    class do_delta():
        """delta docstring"""

        completions = [
            lambda x: [y + ' ' for y in ['right', 'wrong'] if y.startswith(x)]]

        def help_run(self, args):
            return "help_run " + args

        def do_run(self, args):
            """run docstring"""

            print("delta ran")

        def do_stop(self, args):

            print("delta stop")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        myShellac().onecmd(' '.join(sys.argv[1:]))
    else:
        myShellac().cmdloop()
