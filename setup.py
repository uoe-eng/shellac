import setuptools
import sys
sys.path.append("src/shellac")
import version

# Change the following to represent your package:
pkg_name = 'shellac'
pkg_url = 'http://www.github.com/mrichar1/shellac'
pkg_license = 'AGPL 3'
pkg_description = "+shellac+ is an extension of the standard python library 'cmd', which aims to offer an alternative approach to nesting commands."
pkg_author = 'Matthew Richardson, Bruce Duncan'
pkg_author_email = 'm.richardson@ed.ac.uk'

pkg_classifiers = [
            'Development Status :: 5 - Production/Stable',
            'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 3',
            ]

install_requires = ['rl']

# Neither OSX nor Windows ship with GNU readline
if sys.platform == 'darwin':
    install_requires.append('gnureadline')
elif sys.platform.startswith('win'):
    install_requires.append('pyreadline>=2.0')


def main():

    setuptools.setup(
        name=pkg_name,
        version=version.get_version(),
        url=pkg_url,
        license=pkg_license,
        description=pkg_description,
	    classifiers=pkg_classifiers,
        author=pkg_author,
        author_email=pkg_author_email,
        packages=setuptools.find_packages('src'),
        package_dir={'': 'src'},
        include_package_data=True,
        package_data = {'': ['LICENSE']},
        install_requires=install_requires,
        test_suite="{0}.{1}".format(pkg_name, "tests"),
        )


if __name__ == "__main__":
    main()
