import os
import itertools
from distutils.core import setup


here = os.path.abspath(os.path.dirname(__file__))

def get_version():
    with open(os.path.join(here, 'chain_caller.py')) as f:
        variables = {}
        exec(f.read(), variables)

        version = variables.get('__version__')
        if version:
            return version

    raise RuntimeError('No version info found.')


def requirements_getter(filename):
    result = []

    with open(filename) as f:
        requirements = map(lambda x: x.strip(), f.readlines())

        for requirement in requirements:
            if not requirement.startswith('-r'):
                result.append(requirement)
                continue

            result += requirements_getter(
                os.path.join(os.path.dirname(filename), requirement[2:].strip())
            )

    return result


__version__ = get_version()


setup(
    name='Chain Caller',
    license='MIT',
    version=__version__,
    description='Simple utility for lazy call chain resolving',
    long_description=open('README.md').read(),
    author='Alex Tkachenko',
    author_email='preusx.dev@gmail.com',
    url='https://github.com/preusx/python-chain-caller',
    download_url='https://github.com/preusx/python-chain-caller/archive/%s.tar.gz' % __version__,
    py_modules=['chain_caller'],
    install_requires=requirements_getter(os.path.join(here, 'requirements.txt')),
    tests_require=requirements_getter(os.path.join(here, 'requirements/test.txt')),
)