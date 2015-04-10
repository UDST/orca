# Install setuptools if not installed.
try:
    import setuptools
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

from setuptools import setup, find_packages


# read README as the long description
with open('README.rst', 'r') as f:
    long_description = f.read()

setup(
    name='orca',
    version='1.0dev',
    description='A pipeline orchestration tool with Pandas support',
    long_description=long_description,
    author='Synthicity',
    author_email='mdavis@synthicity.com',
    license='BSD',
    url='https://github.com/synthicity/orca',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: BSD License'
    ],
    packages=find_packages(exclude=['*.tests']),
    install_requires=[
        'pandas >= 0.13.1',
        'tables >= 3.1.0',
        'toolz >= 0.7.0',
        'zbox >= 1.2'
    ]
)
