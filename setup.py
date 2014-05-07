#!/usr/bin/python

import os, sys
import subprocess

from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.easy_install import main as install_package

VAR_NAME = 'YICES_PATH'
PKG_NAME = 'pyices'

class PyicesInstaller(install):

    def run(self):
        yices_path = self._find_yices_path()

        # Modify the package to reflect the dependancy on Yices.
        self._generate_lib_file(yices_path)
        self._hardcode_env_variables(yices_path)

        install.run(self)

    def _hardcode_env_variables(self, yices_path):
        """
        NOTE: Incredibly hack-ish, but I can't think of a better solution.
        Modify in-place the `src/__init__.py` file so it would set environmental
        variables properly, depending on the $YICES_PATH var.
        """
        f = open('%s/fix_env.py' % PKG_NAME, 'w+')
        f.write(
            "yices_lib_path = %s" % os.path.join(yices_path, 'lib/')
        )
        f.write(
            """
ld_path = os.getenv('LD_LIBRARY_PATH') or ''
p_path = os.getenv('PYTHONPATH') or ''
os.environ['LD_LIBRARY_PATH'] = '%s:%s' % (yices_lib_path, ld_path)
os.environ['PYTHONPATH'] = '%s:%s' % (yices_lib_path, p_path)
            """
        )
        f.close()

    def _generate_lib_file(self, yices_path):
        """
        Generate the python file from the C header, and write it to a file
        `yices_lib.py`.
        """
        self._ensure_ctypesgen()
        header = os.path.join(yices_path, 'include/yices.h')
        lib_path = os.path.join(yices_path, 'lib')
        subprocess.call(
            ['ctypesgen.py', '-L', lib_path, '-l', 'yices', yices_path,
             '-o', '%s/yices_lib.py' % PKG_NAME])

    def _ensure_ctypesgen(self):
        """
        Ensure that ctypesgen.py is installed and available.
        """
        try:
            subprocess.check_call(
                ['ctypesgen.py', '--help'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        except OSError:
            sys.stderr.write(
                'ctypesgen.py not found in $PATH, attempting installation'
            )
            install_package(['ctypesgen.py'])
        except subprocess.CalledProcessError:
            sys.stderr.write(
                'ctypesgen.py is installed, but not functioning properly, '
                'consider reinstalling.\n'
            )
            sys.exit(1)

    def _find_yices_path(self):
        yices_path = os.getenv(VAR_NAME)
        if not yices_path:
            sys.stderr.write(
                "$YICES_PATH environment variable undefined, "
                "please set it to the location of the Yices folder.\n"
            )
            sys.exit(1)
        return yices_path

setup(
    name="pyices",
    version="0.2",
    description="Python bindings for the Yices SMT solver",
    author="George Karpenkov",
    packages=find_packages(),
    cmdclass={
        'install': PyicesInstaller
    },
    install_requires=['ctypesgen'],
    test_suite='pyices.tests.yices_test:PyicesTests'
)
