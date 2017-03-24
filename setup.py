#!/usr/bin/env python

from setuptools import setup

with open('README.md', 'r') as fp:
    readme = fp.read()

with open('requirements.txt', 'r') as fp:
    requirements = list(filter(bool, (line.strip() for line in fp)))

dev_requirements = []
setup_requires = []

setup(
    name='slicer-apidocs-builder',

    description='slicer-apidocs-builder allows to generate and publish the '
                'Slicer API documentation.',
    long_description=readme,

    url='http://apidocs.slicer.org',

    author='Jean-Christophe Fillion-Robin',
    author_email='jchris.fillionr@kitware.com',

    version='0.1.0',

    packages=['slicer_apidocs_builder'],
    include_package_data=True,
    zip_safe=False,

    entry_points={
        'console_scripts': [
            'slicer-apidocs-builder = slicer_apidocs_builder:main',
        ]},

    license="Slicer",

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: Slicer',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Documentation',
    ],

    install_requires=requirements,
    tests_require=dev_requirements,
    setup_requires=setup_requires
)
