#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'logzero',
    # TODO: put package requirements here
]

setup_requirements = [
    'pytest-runner',
    # TODO(xguse): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    # TODO: put package test requirements here
]

setup(
    name='holographer',
    version='0.0.2',
    description="Holographer copies a filesytem object to a storage location and creates in its place a symlinked decoy pointing to the stored target. Think of when you run out of HDD space and need to move things to free up space but do not want to break everything that may expect to find your target in its old location.",
    long_description=readme + '\n\n' + history,
    author="Gus Dunn",
    author_email='w.gus.dunn@gmail.com',
    url='https://github.com/xguse/holographer',
    packages=find_packages('src'),
    package_dir={"": "src"},
    entry_points={
        'console_scripts': [
            'holo=holographer.cli.main:run'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='holographer',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
