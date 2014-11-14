#!/usr/bin/env python

import os
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
doclink = """
Documentation
-------------

The full documentation can be found at https://github.com/Ecotrust/harvest-scheduler"""

history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='harvestscheduler',
    version='0.3',
    description='Optimization for forest resource mangement',
    long_description=readme + '\n\n' + doclink + '\n\n' + history,
    author='Matthew Perry, Ecotrust',
    author_email='perrygeo@gmail.com',
    url='https://github.com/Ecotrust/harvest-scheduler',
    packages=[
        'harvestscheduler',
    ],
    package_dir={'harvestscheduler': 'harvestscheduler'},
    include_package_data=True,
    tests_require=[
        'pytest',
        'matplotlib'
    ],
    install_requires=[
        'numpy'
    ],
    license='BSD',
    zip_safe=False,
    cmdclass = {'test': PyTest},
    keywords='harvestscheduler',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3.4',
    ],
)
