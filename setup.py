from distutils.core import setup
import setuptools

version = __import__('ryppl').__version__

setup(
    name = 'ryppl',
    version = version,
    description = 'The C++ Development Ecosystem',
    author = 'Dave Abrahams',
    author_email = 'dave@boostpro.com',
    license = "Boost Software License 1.0 (BSL 1.0)",
    url = "http://github.com/ryppl/ryppl",
    classifiers = ['Intended Audience :: Developers',
                   'License :: OSI Approved :: Boost Software License 1.0 (BSL 1.0)',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python'],
    packages = ['ryppl', 'ryppl.commands'],
    scripts = ['bin/ryppl'],
    long_description = open('README.rst').read(),
)
