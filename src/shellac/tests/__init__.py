#!/usr/bin/python

"""Test suite for shellac.

If this script is executed, it will run a simple User & Group tool demo.
"""

from unittest import TestCase
import rl
import shellac
import sys
import time

class ShellacTests(TestCase):

    def setUp(self):
        pass

    def test_shellac_complete_list(self):
        self.assertEqual(list(shellac.complete_list(["bat", "bird", "cat"],
                                                    "b")),
                         ["bat", "bird"])



class UserGroupToolTests(TestCase):

    def setUp(self):
        pass

    def test_help_user(self):
        self.assertIs(type(UserGroupTool().help_user("")), str)

    def test_do_user_list_users(self):
        # Test list_users returns an appropriate list
        self.assertEqual(list(UserGroupTool()
                           .do_user()
                           .list_users("a")), ["alice", "anne"])

    def test_do_user_do_add(self):
        # Check that a user is added
        UserGroupTool().do_user().do_add("zebedee")
        self.assertEqual(next(UserGroupTool()
                           .do_user()
                           .list_users("zebedee")), "zebedee")

    def test_do_user_do_remove(self):
        # Check that a user is removed
        UserGroupTool().do_user().do_remove("zebedee")
        self.assertEqual(list(UserGroupTool()
                           .do_user()
                           .list_users("zebedee")), [])

    def test_do_user_do_remove_exc(self):
        # Check that a user is removed
        self.assertFalse(UserGroupTool()
                         .do_user()
                         .do_remove("nosuchuser"))

    def test_do_group_list_groups(self):
        # Test list_users returns an appropriate list
        self.assertEqual(list(UserGroupTool()
                              .do_group()
                              .list_groups("s")), ["staff", "students"])


class UserGroupTool(shellac.Shellac):
    """This is a tool which pretends to modify users and groups.

This help is actually the class docstring.

Press <TAB> (or type 'help <TAB>') to see what you can do..."""

    @staticmethod
    def help_user(args):
        """Help for the user command.

        You can use a help_ method if you want to do something
        fancier than can be displayed in a docstring"""

        return "'help user' command run at {h}:{m}".format(
            h=time.localtime()[3],
            m=time.localtime()[4])


    class do_user():
        """Docstring explaining do_user."

        This will not be displayed as help,
        since there is a help_user method above."""

        @staticmethod
        def list_users(token):
            return shellac.complete_list(myData.users.keys(), token)
        @staticmethod
        def do_list(args):
            """Print a list of all users."""
            print(sorted(myData.users.keys()))

        @staticmethod
        def do_add(args):
            """Add a new user."""
            myData.users[args] = ''
            print("Added user: " + args)

        @staticmethod
        @shellac.completer(list_users)
        def do_remove(args):
            """Remove a user."""
            try:
                del myData.users[args.strip()]
                print("Removed user: " + args)
                return True
            except KeyError:
                print("No such user to remove.")
                return False

    class do_group():
        """This command works with groups.

This help is actually the docstring for the do_group class, which is displayed
since there is no help_group method in the parent class."""

        @staticmethod
        def list_groups(token):
            # Long-hand for shellac.complete_list
            return sorted([x for x in myData.groups.keys() if x.startswith(token)])

        @staticmethod
        def do_list(args):
            """Print a list of all groups."""

            print(sorted(myData.groups.keys()))

        @staticmethod
        def do_add(args):
            myData.groups[args] = ''
            print("Added group: " + args)

        @staticmethod
        @shellac.completer(list_groups)
        def do_remove(args):
            try:
                del myData.groups[args.strip()]
                print("Removed group: " + args)
                return True
            except KeyError:
                print("No such group to remove.")
                return False

        class do_member():
            """Modify group membership.

            Note: this method's sub-commands don't actually do anything."""

            @staticmethod
            def do_list(args):
                print("Group membership not implemented!" + args)

            @staticmethod
            def do_add(args):
                print("Added member: " + args)

            @staticmethod
            def do_remove(args):
                print("Removed member: " + args)
                return True


class myData(object):
    """A simple data source."""

    users = {'alice': '',
             'anne': '',
             'bob': '',
             'bruce': '',
             'cliff': '',
             'clive': ''}

    groups = {'staff': '',
              'students': '',
              'visitors': ''}


if __name__ == '__main__':
    # If run, launch usergrouptool command shell as a demo
    if len(sys.argv) > 1:
        UserGroupTool().onecmd(' '.join(sys.argv[1:]))
    else:
        UserGroupTool().cmdloop()
