from __future__ import print_function

import subprocess
from setuptools import setup, find_packages
from setuptools.command.sdist import sdist


# these make sure the js distribution bundle is created and
# up-to-date when creating distribution packages.
cmdclass = {}


def build_js_bundle():
    print('Building JS bundle')
    subprocess.check_call(['./bin/build_js_bundle.sh'])


class sdist_(sdist):
    def run(self):
        build_js_bundle()
        sdist.run(self)
cmdclass['sdist'] = sdist_

try:
    from wheel.bdist_wheel import bdist_wheel
except ImportError:
    pass
else:
    class build_wheel(bdist_wheel):
        def run(self):
            build_js_bundle()
            bdist_wheel.run(self)
    cmdclass['bdist_wheel'] = build_wheel

# read README as the long description
with open('README.rst', 'r') as f:
    long_description = f.read()

setup(
    name='orca',
    version='1.6.1',
    description='Python library for task orchestration',
    long_description=long_description,
    author='UrbanSim Inc.',
    author_email='info@urbansim.com',
    license='BSD',
    url='https://github.com/udst/orca',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: BSD License'
    ],
    packages=find_packages(exclude=['*.tests']),
    package_data={
        'orca': [
            'server/static/css/*',
            'server/static/js/dist/*',
            'server/templates/*']
    },
    install_requires=[
        'pandas >= 0.15.0',
        'tables >= 3.1',
        'toolz >= 0.8.1'
    ],
    extras_require={
        'server': ['flask >= 0.10', 'pygments >= 2.0', 'six >= 1.9.0']
    },
    entry_points={
        'console_scripts': [
            'orca-server = orca.server.server:main [server]'
        ]
    },
    cmdclass=cmdclass
)
