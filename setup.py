import setuptools
from setuptools.command import easy_install
import os
import errno
import re
import subprocess
import sys

# Change the following to represent your package:
pkg_name = 'shellac'
pkg_url = 'http://www.github.com/mrichar1/shellac'
pkg_license = 'AGPL 3'
pkg_description = "+shellac+ is an extension of the standard python library 'cmd', which aims to offer an alternative approach to nesting commands."
pkg_author = 'Matthew Richardson, Bruce Duncan'
pkg_author_email = 'm.richardson@ed.ac.uk'

pkg_classifiers = [
            'Development Status :: 4 - Beta',
            'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 3',
            ]

install_requires = []

# Neither OSX nor Windows ship with GNU readline
if sys.platform == 'darwin':
    install_requires.append('gnureadline')
elif sys.platform.startswith('win'):
    install_requires.append('pyreadline>=2.0')


def call_git_describe():
    try:
        p = subprocess.Popen(['git', 'describe'],
                             stdout=subprocess.PIPE)
        return p.communicate()[0].split('\n')[0].strip()
    except Exception:
        return None


def read_release_version():
    try:
        with open("RELEASE-VERSION") as f:
            return f.readlines()[0].strip()
    except Exception:
        return None


def write_release_version(version):
    with open("RELEASE-VERSION", "w") as f:
        f.write("%s\n" % version)


def get_git_version():
    version = call_git_describe()
    release_version = read_release_version()
    if version is None:
        version = release_version

    if version is None:
        raise ValueError("Unable to determine the version number!")

    if version != release_version:
        write_release_version(version)

    return version


def main():

    setuptools.setup(
        name=pkg_name,
        version=get_git_version(),
        url=pkg_url,
        license=pkg_license,
        description=pkg_description,
	    classifiers=pkg_classifiers,
        author=pkg_author,
        author_email=pkg_author_email,
        packages=setuptools.find_packages('src'),
        package_dir={'': 'src'},
        include_package_data=True,
        package_data = {'': ['LICENSE', 'RELEASE-VERSION']},
        install_requires=install_requires,
        )


if __name__ == "__main__":
    main()
