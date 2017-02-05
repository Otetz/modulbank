from codecs import open
from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))


def get_file_content(file_name):
    with open(path.join(here, file_name), encoding='utf-8') as f:
        return f.read()


version = {}
exec(open(path.join(here, 'modulbank/version.py')).read(), version)

setup(
    name="modulbank",
    version=version['__version__'],
    description="Python client for ModulBank REST API",
    long_description=get_file_content('README.rst'),
    url="https://github.com/otetz/modulbank",
    author="Alexey Shevchenko",
    author_email="otetz@me.com",
    license='MIT',
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Information Technology",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    keywords='modulbank bank',
    packages=find_packages(),
    include_package_data=True,
    setup_requires=['pytest-runner'],
    install_requires=get_file_content('requirements.txt'),
    tests_require=get_file_content('requirements_test.txt'),
    test_suite='tests',
)
